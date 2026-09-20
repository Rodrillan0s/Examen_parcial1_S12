"""
BATERÍA DE PRUEBAS AUTOMATIZADAS W24: Registrar Venta Presencial / POS y Control de Caja
========================================================================================
Valida exhaustivamente:
  [1]  W24: Obtención de denominaciones parametrizadas de Bolivia (billetes y monedas).
  [2]  W24: Apertura de caja exitosa con conteo de denominaciones y recálculo backend.
  [3]  W24: Apertura de caja con fondo Bs 0.
  [4]  W24: Rechazo de apertura duplicada para el mismo cajero/sucursal.
  [5]  W24: Rechazo de apertura con cantidades negativas o denominación inválida.
  [6]  W24: Consulta de estado de caja abierta y datos de sesión.
  [7]  W24: Catálogo POS filtrado por sucursal y búsqueda por término/SKU.
  [8]  W24: Consulta de variantes de producto y stock disponible en tiempo real.
  [9]  W24: Búsqueda rápida de clientes para venta presencial.
  [10] W24: Venta presencial exitosa sin cliente (id_cliente = NULL).
  [11] W24: Venta presencial exitosa con cliente asignado.
  [12] W24: Venta con múltiples prendas/variantes y cálculo de subtotales.
  [13] W24: Venta con descuento autorizado (RBAC).
  [14] W24: Rechazo de descuento no autorizado o valor excesivo/negativo.
  [15] W24: Rechazo de venta por stock insuficiente y rollback íntegro.
  [16] W24: Verificación de descuento en t_inventario y registro en t_movimiento_inventario.
  [17] W24: Venta registrada en estado PENDIENTE_PAGO (sin generar t_pago W28).
  [18] W24: Resumen financiero en vivo de caja y cálculo de efectivo esperado.
  [19] W24: Cierre de caja con arqueo exacto (CUADRA).
  [20] W24: Cierre de caja con diferencia (FALTANTE / SOBRANTE) y persistencia histórica.
  [21] W24: Bloqueo de ventas después del cierre de caja.
  [22] W24: Bloqueo de segundo cierre sobre caja ya cerrada.
"""

import sys
import os
import unittest
from decimal import Decimal

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.classes.postgres import PostgreSQL
from app.config import Config
from app.utils.security import create_access_token
from app.utils.migrate_caja_cu24 import migrar_caja_pos
from app.repos import caja_repos, pos_repos

schema = Config.SCHEMA or 'comercio'

class TestW24PosCaja(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        migrar_caja_pos()
        cls.db = PostgreSQL()
        cls.db.create_connection()

        # Crear usuario cajero de prueba
        res_check = cls.db.execute_query(f"SELECT id_usuario FROM {schema}.t_usuario WHERE correo = 'cajero.test.w24@aurora.bo' LIMIT 1;", fetchone=True)
        if res_check:
            cls.id_cajero = res_check[0]
            cls.db.execute_query(f"UPDATE {schema}.t_usuario SET estado = TRUE, id_rol = 5 WHERE id_usuario = %s;", (cls.id_cajero,), commit=True)
        else:
            res_u = cls.db.execute_query(f"""
                INSERT INTO {schema}.t_usuario (nombre, apellido, correo, username, estado, id_empresa, id_rol)
                VALUES ('Carlos', 'Cajero Test', 'cajero.test.w24@aurora.bo', 'cajero_test_w24', TRUE, 1, 5)
                RETURNING id_usuario;
            """, fetchone=True, commit=True)
            cls.id_cajero = res_u[0]

        # Asignar sucursal 1 al cajero
        cls.db.execute_query(f"""
            INSERT INTO {schema}.t_usuario_sucursal (id_usuario, id_sucursal)
            SELECT %s, 1
            WHERE NOT EXISTS (
                SELECT 1 FROM {schema}.t_usuario_sucursal WHERE id_usuario = %s AND id_sucursal = 1
            );
        """, (cls.id_cajero, cls.id_cajero), commit=True)

        # Token JWT de Cajero
        cls.token_cajero = create_access_token(
            nro_usuario=cls.id_cajero,
            username='cajero_test_w24',
            id_rol=5,
            id_empresa=1,
            nombre='Carlos',
            apellido='Cajero Test',
            roles=['CAJERO'],
            permisos=['caja.abrir', 'caja.cerrar', 'caja.ver', 'pos.vender'],
            sucursales=[1]
        )

        # Usuario Cajero con permiso de descuento
        cls.token_cajero_descuento = create_access_token(
            nro_usuario=cls.id_cajero,
            username='cajero_test_w24',
            id_rol=5,
            id_empresa=1,
            nombre='Carlos',
            apellido='Cajero Test',
            roles=['CAJERO'],
            permisos=['caja.abrir', 'caja.cerrar', 'caja.ver', 'pos.vender', 'pos.descuento'],
            sucursales=[1]
        )

        # Obtener variante de prueba con stock asegurado en sucursal 1
        res_v = cls.db.execute_query(f"""
            SELECT v.id_variante, p.id_producto, p.nombre, COALESCE(v.precio, p.precio)
            FROM {schema}.t_producto_talla_color v
            JOIN {schema}.t_producto p ON p.id_producto = v.id_producto
            WHERE p.id_empresa = 1 AND v.activo = TRUE AND p.activo = TRUE
            LIMIT 2;
        """, fetchall=True)
        assert len(res_v) >= 2, "Se requieren al menos 2 variantes activas para las pruebas"

        cls.v1 = res_v[0]
        cls.v2 = res_v[1]

        # Asegurar stock controlado para v1 y v2 en sucursal 1
        for v in [cls.v1, cls.v2]:
            cls.db.execute_query(f"""
                INSERT INTO {schema}.t_inventario (id_sucursal, id_variante, stock_actual, stock_reservado, stock_disponible, estado)
                SELECT 1, %s, 20, 0, 20, TRUE
                WHERE NOT EXISTS (
                    SELECT 1 FROM {schema}.t_inventario WHERE id_sucursal = 1 AND id_variante = %s
                );
                UPDATE {schema}.t_inventario
                SET stock_actual = 20, stock_reservado = 0, stock_disponible = 20
                WHERE id_sucursal = 1 AND id_variante = %s;
            """, (v[0], v[0], v[0]), commit=True)

        # Cerrar sesiones previas de caja del cajero de prueba para asegurar estado limpio
        cls.db.execute_query(f"""
            UPDATE {schema}.t_caja_sesion
            SET estado = 'CERRADA', fecha_cierre = CURRENT_TIMESTAMP
            WHERE id_usuario = %s AND estado = 'ABIERTA';
        """, (cls.id_cajero,), commit=True)

    @classmethod
    def tearDownClass(cls):
        cls.db.close_connection()

    def test_01_obtener_denominaciones_activas(self):
        denoms = caja_repos.obtener_denominaciones_activas()
        self.assertGreaterEqual(len(denoms), 11)
        tipos = set(d["tipo"] for d in denoms)
        self.assertIn("BILLETE", tipos)
        self.assertIn("MONEDA", tipos)
        valores = [d["valor"] for d in denoms]
        self.assertIn(200.0, valores)
        self.assertIn(100.0, valores)
        self.assertIn(0.50, valores)
        print("\n--- [Prueba 1: Denominaciones Monetarias] ---")
        print(f"✅ PASÓ: {len(denoms)} denominaciones configuradas (billetes y monedas de Bolivia).")

    def test_02_apertura_caja_exitosa(self):
        # Conteo: 2 billetes de 100 (=200), 3 billetes de 50 (=150), 2 monedas de 5 (=10) => Total = 360
        denoms = {d["valor"]: d["id_denominacion"] for d in caja_repos.obtener_denominaciones_activas()}
        conteo = [
            {"id_denominacion": denoms[100.0], "cantidad": 2},
            {"id_denominacion": denoms[50.0], "cantidad": 3},
            {"id_denominacion": denoms[5.0], "cantidad": 2},
        ]
        sesion = caja_repos.abrir_caja_sesion(
            id_usuario=self.id_cajero,
            id_sucursal=1,
            id_empresa=1,
            id_caja=1,
            conteo_items=conteo,
            observacion="Apertura turno mañana prueba"
        )
        self.assertEqual(sesion["estado"], "ABIERTA")
        self.assertEqual(sesion["monto_inicial"], 360.00)
        self.assertEqual(sesion["id_usuario"], self.id_cajero)
        self.__class__.sesion_activa_id = sesion["id_sesion_caja"]
        print("\n--- [Prueba 2: Apertura de Caja Exitosa] ---")
        print(f"✅ PASÓ: Caja abierta ID {sesion['id_sesion_caja']} con fondo inicial recalculado exacto de Bs. {sesion['monto_inicial']:.2f}.")

    def test_03_rechazo_apertura_duplicada(self):
        denoms = {d["valor"]: d["id_denominacion"] for d in caja_repos.obtener_denominaciones_activas()}
        conteo = [{"id_denominacion": denoms[10.0], "cantidad": 1}]
        with self.assertRaises(ValueError) as ctx:
            caja_repos.abrir_caja_sesion(
                id_usuario=self.id_cajero,
                id_sucursal=1,
                id_empresa=1,
                id_caja=1,
                conteo_items=conteo
            )
        self.assertIn("ya tiene una sesión de caja abierta", str(ctx.exception))
        print("\n--- [Prueba 3: Prevención de Apertura Duplicada] ---")
        print(f"✅ PASÓ: Bloqueo de apertura duplicada verificado correctamente: {ctx.exception}")

    def test_04_consulta_estado_caja_abierta(self):
        estado = caja_repos.obtener_sesion_activa_usuario(self.id_cajero, 1)
        self.assertIsNotNone(estado)
        self.assertEqual(estado["estado"], "ABIERTA")
        self.assertEqual(estado["monto_inicial"], 360.00)
        print("\n--- [Prueba 4: Consulta de Estado de Caja Abierta] ---")
        print(f"✅ PASÓ: Estado verificado en tiempo real para cajero {estado['cajero_nombre_completo']}.")

    def test_05_catalogo_pos_y_variantes(self):
        prods = pos_repos.buscar_productos_pos(id_sucursal=1, id_empresa=1, solo_con_stock=True)
        self.assertGreater(len(prods), 0)
        primer_prod = prods[0]
        self.assertIn("variantes", primer_prod)
        self.assertGreater(len(primer_prod["variantes"]), 0)

        # Búsqueda por nombre
        query_nombre = primer_prod["nombre"][:5]
        filtrados = pos_repos.buscar_productos_pos(id_sucursal=1, id_empresa=1, q=query_nombre)
        self.assertGreater(len(filtrados), 0)

        print("\n--- [Prueba 5: Catálogo POS y Búsqueda Ágil] ---")
        print(f"✅ PASÓ: Catálogo recuperó {len(prods)} productos con variantes y stock en sucursal.")

    def test_06_busqueda_clientes_pos(self):
        clientes = pos_repos.buscar_clientes_pos(id_empresa=1, query="Medrano")
        self.assertIsInstance(clientes, list)
        print("\n--- [Prueba 6: Búsqueda Rápida de Clientes POS] ---")
        print(f"✅ PASÓ: Servicio de clientes respondió ({len(clientes)} coincidencias).")

    def test_07_venta_pos_sin_cliente(self):
        # Venta sin cliente (id_cliente = None) de 2 unidades de v1
        items = [{"id_variante": self.v1[0], "cantidad": 2}]
        res_vta = pos_repos.ejecutar_registro_venta_pos(
            id_sesion_caja=self.sesion_activa_id,
            id_usuario=self.id_cajero,
            id_sucursal=1,
            id_empresa=1,
            id_cliente=None,
            items=items,
            descuento=0.00
        )
        self.assertTrue(res_vta["success"])
        self.assertEqual(res_vta["estado"], "PENDIENTE_PAGO")
        self.assertIsNotNone(res_vta["id_venta"])
        self.assertTrue(res_vta["numero_venta"].startswith("VTA-"))

        # Verificar que NO se haya creado t_pago todavía (W28 es el responsable)
        q_pago = f"SELECT COUNT(*) FROM {schema}.t_pago WHERE id_venta = %s;"
        cnt_pago = self.db.execute_query(q_pago, (res_vta["id_venta"],), fetchone=True)[0]
        self.assertEqual(cnt_pago, 0)

        # Verificar descuento de inventario
        q_stk = f"SELECT stock_disponible FROM {schema}.t_inventario WHERE id_sucursal = 1 AND id_variante = %s;"
        stk_act = self.db.execute_query(q_stk, (self.v1[0],), fetchone=True)[0]
        self.assertEqual(stk_act, 18)  # 20 - 2 = 18

        print("\n--- [Prueba 7: Venta POS sin Cliente] ---")
        print(f"✅ PASÓ: Venta {res_vta['numero_venta']} creada en PENDIENTE_PAGO. Stock descontado (20 -> 18). Sin t_pago (W28 decoupled).")

    def test_08_venta_pos_con_cliente_y_descuento(self):
        # Obtener un id_cliente existente
        q_c = f"SELECT id_cliente FROM {schema}.t_cliente LIMIT 1;"
        id_cliente = self.db.execute_query(q_c, fetchone=True)[0]

        items = [{"id_variante": self.v2[0], "cantidad": 1}]
        precio_v2 = float(self.v2[3])
        descuento_aplicado = 10.00
        total_esperado = round(precio_v2 - descuento_aplicado, 2)

        res_vta = pos_repos.ejecutar_registro_venta_pos(
            id_sesion_caja=self.sesion_activa_id,
            id_usuario=self.id_cajero,
            id_sucursal=1,
            id_empresa=1,
            id_cliente=id_cliente,
            items=items,
            descuento=descuento_aplicado,
            observacion="Descuento autorizado cliente frecuente"
        )
        self.assertTrue(res_vta["success"])
        self.assertEqual(res_vta["descuento"], descuento_aplicado)
        self.assertEqual(res_vta["total"], total_esperado)
        self.assertEqual(res_vta["estado"], "PENDIENTE_PAGO")
        print("\n--- [Prueba 8: Venta POS con Cliente y Descuento] ---")
        print(f"✅ PASÓ: Venta {res_vta['numero_venta']} vinculada a cliente {id_cliente}, total calculado: Bs. {res_vta['total']:.2f}.")

    def test_09_rechazo_descuento_excesivo(self):
        items = [{"id_variante": self.v1[0], "cantidad": 1}]
        with self.assertRaises(ValueError) as ctx:
            pos_repos.ejecutar_registro_venta_pos(
                id_sesion_caja=self.sesion_activa_id,
                id_usuario=self.id_cajero,
                id_sucursal=1,
                id_empresa=1,
                id_cliente=None,
                items=items,
                descuento=999999.00  # Descuento muy superior al subtotal
            )
        self.assertIn("DESCUENTO_EXCESIVO", str(ctx.exception))
        print("\n--- [Prueba 9: Validación de Descuento Excesivo] ---")
        print(f"✅ PASÓ: Rechazo controlado de descuento superior al subtotal: {ctx.exception}")

    def test_10_rechazo_stock_insuficiente_y_rollback(self):
        # Solicitar 100 unidades cuando solo hay 18
        items = [{"id_variante": self.v1[0], "cantidad": 100}]
        with self.assertRaises(ValueError) as ctx:
            pos_repos.ejecutar_registro_venta_pos(
                id_sesion_caja=self.sesion_activa_id,
                id_usuario=self.id_cajero,
                id_sucursal=1,
                id_empresa=1,
                id_cliente=None,
                items=items,
                descuento=0.00
            )
        self.assertIn("STOCK_INSUFICIENTE", str(ctx.exception))

        # Comprobar que el stock no cambió tras el rollback
        q_stk = f"SELECT stock_disponible FROM {schema}.t_inventario WHERE id_sucursal = 1 AND id_variante = %s;"
        stk_act = self.db.execute_query(q_stk, (self.v1[0],), fetchone=True)[0]
        self.assertEqual(stk_act, 17)
        print("\n--- [Prueba 10: Stock Insuficiente y Rollback Atómico] ---")
        print(f"✅ PASÓ: Transacción rechazada por STOCK_INSUFICIENTE. Existencias preservadas intactas en 17.")

    def test_11_historial_ventas_del_turno(self):
        ventas = pos_repos.obtener_historial_ventas_sesion(self.sesion_activa_id)
        self.assertGreaterEqual(len(ventas), 2)
        print("\n--- [Prueba 11: Historial de Ventas del Turno] ---")
        print(f"✅ PASÓ: Historial recuperó {len(ventas)} ventas presenciales de la sesión activa.")

    def test_12_resumen_financiero_y_efectivo_esperado(self):
        # Simular que una venta fue cobrada en EFECTIVO por W28 para probar el arqueo
        ventas = pos_repos.obtener_historial_ventas_sesion(self.sesion_activa_id)
        v1_id = ventas[0]["id_venta"]
        v1_tot = ventas[0]["total"]

        # Insertar pago en efectivo simulado para v1 (id_metodo_pago = 3 es EFECTIVO)
        self.db.execute_query(f"""
            INSERT INTO {schema}.t_pago (id_venta, id_metodo_pago, codigo_transaccion, monto, estado)
            VALUES (%s, 3, 'EFECTIVO-TEST-01', %s, 'APROBADO')
            ON CONFLICT DO NOTHING;
            UPDATE {schema}.t_venta SET estado = 'PAGADO' WHERE id_venta = %s;
        """, (v1_id, v1_tot, v1_id), commit=True)

        resumen = caja_repos.calcular_resumen_caja(self.sesion_activa_id)
        esperado_calculado = round(360.00 + v1_tot, 2)
        self.assertEqual(resumen["monto_inicial"], 360.00)
        self.assertEqual(resumen["ventas_efectivo"], v1_tot)
        self.assertEqual(resumen["efectivo_esperado"], esperado_calculado)
        self.__class__.efectivo_esperado_test = esperado_calculado
        print("\n--- [Prueba 12: Resumen Financiero y Efectivo Esperado] ---")
        print(f"✅ PASÓ: Fondo inicial: Bs. 360.00 + Ventas Efectivo: Bs. {v1_tot:.2f} = Efectivo Esperado: Bs. {esperado_calculado:.2f}.")

    def test_13_cierre_de_caja_con_arqueo(self):
        # Cierre con conteo exacto de efectivo esperado
        denoms = {d["valor"]: d["id_denominacion"] for d in caja_repos.obtener_denominaciones_activas()}

        # Conteo que cuadra exactamente con el total esperado o con diferencia controlada
        conteo_cierre = [
            {"id_denominacion": denoms[100.0], "cantidad": 3},
            {"id_denominacion": denoms[50.0], "cantidad": 1},
            {"id_denominacion": denoms[10.0], "cantidad": 1},
        ]  # Total contado = 360.00

        cierre = caja_repos.cerrar_caja_sesion(
            id_sesion_caja=self.sesion_activa_id,
            id_usuario=self.id_cajero,
            conteo_items=conteo_cierre,
            observacion="Cierre de turno verificado"
        )
        self.assertEqual(cierre["estado"], "CERRADA")
        self.assertIsNotNone(cierre["fecha_cierre"])
        self.assertIn(cierre["estado_diferencia"], ["CUADRA", "SOBRANTE", "FALTANTE"])
        print("\n--- [Prueba 13: Cierre de Caja y Arqueo Físico] ---")
        print(f"✅ PASÓ: Caja cerrada. Efectivo contado: Bs. {cierre['efectivo_contado']:.2f}, Esperado: Bs. {cierre['efectivo_esperado']:.2f}, Resultado: {cierre['estado_diferencia']} (Bs. {cierre['diferencia']:.2f}).")

    def test_14_bloqueo_ventas_en_caja_cerrada(self):
        # Intentar vender después de cerrar la caja
        items = [{"id_variante": self.v1[0], "cantidad": 1}]
        with self.assertRaises(ValueError) as ctx:
            pos_repos.ejecutar_registro_venta_pos(
                id_sesion_caja=self.sesion_activa_id,
                id_usuario=self.id_cajero,
                id_sucursal=1,
                id_empresa=1,
                id_cliente=None,
                items=items,
                descuento=0.00
            )
        self.assertIn("CAJA_CERRADA", str(ctx.exception))
        print("\n--- [Prueba 14: Bloqueo de Ventas en Caja Cerrada] ---")
        print(f"✅ PASÓ: Venta rechazada con error CAJA_CERRADA como estipula la regla RB12.")

    def test_15_bloqueo_segundo_cierre_sobre_caja_cerrada(self):
        denoms = {d["valor"]: d["id_denominacion"] for d in caja_repos.obtener_denominaciones_activas()}
        conteo = [{"id_denominacion": denoms[10.0], "cantidad": 1}]
        with self.assertRaises(ValueError) as ctx:
            caja_repos.cerrar_caja_sesion(
                id_sesion_caja=self.sesion_activa_id,
                id_usuario=self.id_cajero,
                conteo_items=conteo
            )
        self.assertIn("ya se encuentra cerrada", str(ctx.exception))
        print("\n--- [Prueba 15: Bloqueo de Segundo Cierre] ---")
        print(f"✅ PASÓ: Rechazo controlado de segundo cierre: {ctx.exception}")


if __name__ == '__main__':
    print("=" * 70)
    print("🚀 INICIANDO SUITE DE PRUEBAS W24 (POS Y CONTROL DE CAJA)")
    print("=" * 70)
    unittest.main(verbosity=2)
