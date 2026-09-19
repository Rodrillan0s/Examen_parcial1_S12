"""
BATERÍA DE PRUEBAS AUTOMATIZADAS: CU/W28 (Procesar Pago en Caja) y CU/W29 (Emitir Comprobante)
=============================================================================================
Valida exhaustivamente:
  [1]  W28: Obtención de métodos de pago activos en POS (Efectivo, Tarjeta, QR).
  [2]  W28: Consulta y validación de venta pendiente de pago para cobro en caja.
  [3]  W28: Rechazo de cobro si el cajero no tiene una sesión de caja ABIERTA.
  [4]  W28: Rechazo de pago en efectivo si el monto recibido es insuficiente.
  [5]  W28: Procesamiento exitoso de pago en efectivo con recálculo exacto del cambio.
  [6]  W28: Inserción atómica en t_pago (APROBADO) y actualización de t_venta (PAGADO).
  [7]  W28: Protección estricta contra doble cobro de la misma venta.
  [8]  W28: Procesamiento exitoso de pago con Tarjeta y registro de referencia de voucher.
  [9]  W29: Consulta de datos para emisión de comprobante de venta pagada.
  [10] W29: Rechazo de emisión de comprobante para ventas en estado PENDIENTE_PAGO.
  [11] W29: Emisión de comprobante con actualización de snapshot fiscal en t_venta.
  [12] W29: Descarga de comprobante PDF generado dinámicamente con ReportLab (%PDF-).
  [13] Integración completa: id_venta W24 = id_venta W28 = id_venta W29.
"""

import sys
import os
import unittest
from decimal import Decimal
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
app = create_app()
from app.classes.postgres import PostgreSQL
from app.config import Config
from app.utils.security import create_access_token
from app.utils.migrate_caja_cu24 import migrar_caja_pos
from app.utils.migrate_pago_caja_cu28_cu29 import migrar_pago_caja_cu28_cu29
from app.repos import caja_repos, pos_repos, caja_pago_repos

schema = Config.SCHEMA or 'comercio'

class TestW28W29PagoComprobanteCaja(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        cls.db = PostgreSQL()
        cls.db.create_connection()

        # 1. Asegurar cajero con rol y empresa
        res_u = cls.db.execute_query(
            f"SELECT id_usuario FROM {schema}.t_usuario WHERE correo = 'cajero.w28w29@aurora.bo' LIMIT 1;",
            fetchone=True
        )
        if res_u:
            cls.id_cajero = res_u[0]
            cls.db.execute_query(
                f"UPDATE {schema}.t_usuario SET estado = TRUE, id_rol = 5 WHERE id_usuario = %s;",
                (cls.id_cajero,), commit=True
            )
        else:
            res_ins = cls.db.execute_query(f"""
                INSERT INTO {schema}.t_usuario (nombre, apellido, correo, username, estado, id_empresa, id_rol)
                VALUES ('Cajero', 'Tester W28W29', 'cajero.w28w29@aurora.bo', 'cajero_w28w29', TRUE, 1, 5)
                RETURNING id_usuario;
            """, fetchone=True, commit=True)
            cls.id_cajero = res_ins[0]

        # Asegurar sucursal asignada al cajero
        cls.db.execute_query(f"""
            INSERT INTO {schema}.t_usuario_sucursal (id_usuario, id_sucursal)
            VALUES (%s, 1)
            ON CONFLICT DO NOTHING;
        """, (cls.id_cajero,), commit=True)

        # 2. Token JWT para el cajero
        cls.token_cajero = create_access_token(
            nro_usuario=cls.id_cajero,
            username="cajero_w28w29",
            id_rol=5,
            id_empresa=1,
            nombre="Cajero",
            apellido="Tester W28W29",
            roles=["CAJERO"],
            permisos=["caja.abrir", "caja.cerrar", "caja.ver", "pos.vender", "pos.cobrar", "comprobante.emitir"],
            sucursales=[1]
        )
        cls.headers_cajero = {"Authorization": f"Bearer {cls.token_cajero}"}

        # 3. Asegurar sucursal y caja física
        res_suc = cls.db.execute_query(
            f"SELECT id_sucursal FROM {schema}.t_sucursal WHERE id_empresa = 1 LIMIT 1;",
            fetchone=True
        )
        cls.id_sucursal = res_suc[0] if res_suc else 1

        res_caja = cls.db.execute_query(
            f"SELECT id_caja FROM {schema}.t_caja WHERE id_sucursal = %s LIMIT 1;",
            (cls.id_sucursal,), fetchone=True
        )
        if res_caja:
            cls.id_caja = res_caja[0]
        else:
            res_c = cls.db.execute_query(f"""
                INSERT INTO {schema}.t_caja (id_sucursal, codigo_caja, nombre, estado)
                VALUES (%s, 'CAJA-TEST-W28', 'Caja Pruebas W28', TRUE)
                RETURNING id_caja;
            """, (cls.id_sucursal,), fetchone=True, commit=True)
            cls.id_caja = res_c[0]

        # 4. Asegurar variante con inventario en sucursal
        res_v = cls.db.execute_query(f"""
            SELECT v.id_variante, p.id_producto, p.nombre, COALESCE(v.precio, p.precio)
            FROM {schema}.t_producto_talla_color v
            JOIN {schema}.t_producto p ON p.id_producto = v.id_producto
            WHERE p.id_empresa = 1 AND v.activo = TRUE AND p.activo = TRUE
            LIMIT 1;
        """, fetchone=True)
        assert res_v, "Se requiere al menos 1 variante activa para las pruebas"

        cls.id_variante = res_v[0]
        cls.precio_variante = float(res_v[3])

        # Asegurar stock en t_inventario para la sucursal
        cls.db.execute_query(f"""
            INSERT INTO {schema}.t_inventario (id_sucursal, id_variante, stock_actual, stock_reservado, stock_disponible, estado)
            SELECT %s, %s, 50, 0, 50, TRUE
            WHERE NOT EXISTS (
                SELECT 1 FROM {schema}.t_inventario WHERE id_sucursal = %s AND id_variante = %s
            );
            UPDATE {schema}.t_inventario
            SET stock_actual = 50, stock_reservado = 0, stock_disponible = 50
            WHERE id_sucursal = %s AND id_variante = %s;
        """, (cls.id_sucursal, cls.id_variante, cls.id_sucursal, cls.id_variante, cls.id_sucursal, cls.id_variante), commit=True)

        # 5. Abrir caja para el cajero
        # Cerrar sesiones abiertas previas de este cajero o esta caja para arrancar limpios
        cls.db.execute_query(f"""
            UPDATE {schema}.t_caja_sesion
            SET estado = 'CERRADA', fecha_cierre = NOW()
            WHERE (id_usuario = %s OR id_caja = %s) AND estado = 'ABIERTA';
        """, (cls.id_cajero, cls.id_caja), commit=True)

        res_ses = caja_repos.abrir_caja_sesion(
            id_usuario=cls.id_cajero,
            id_sucursal=cls.id_sucursal,
            id_empresa=1,
            id_caja=cls.id_caja,
            conteo_items=[],
            observacion="Apertura test W28 W29"
        )
        cls.id_sesion_caja = res_ses["id_sesion_caja"]

    @classmethod
    def tearDownClass(cls):
        # Limpieza suave
        cls.db.execute_query(f"""
            UPDATE {schema}.t_caja_sesion
            SET estado = 'CERRADA', fecha_cierre = NOW()
            WHERE id_sesion_caja = %s;
        """, (cls.id_sesion_caja,), commit=True)
        cls.db.close_connection()

    def _crear_venta_pos(self, cantidad=1, id_cliente=None):
        """Helper para crear una venta presencial W24 en estado PENDIENTE_PAGO"""
        items = [{"id_variante": self.id_variante, "cantidad": cantidad}]
        res = pos_repos.ejecutar_registro_venta_pos(
            id_sesion_caja=self.id_sesion_caja,
            id_usuario=self.id_cajero,
            id_sucursal=self.id_sucursal,
            id_empresa=1,
            items=items,
            id_cliente=id_cliente,
            descuento=0.00
        )
        return res["id_venta"], res["total"]

    def test_01_obtener_metodos_pago_caja(self):
        """[1] W28: Obtener métodos de pago activos para caja"""
        resp = self.client.get("/api/caja/pagos/metodos", headers=self.headers_cajero)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data["success"])
        self.assertIsInstance(data["metodos"], list)
        tipos = [m["tipo"] for m in data["metodos"]]
        self.assertIn("EFECTIVO", tipos)
        self.assertIn("TARJETA", tipos)
        self.assertIn("QR", tipos)

    def test_02_validar_venta_para_pago_exitosa(self):
        """[2] W28: Consultar y validar venta pendiente de pago"""
        id_venta, total = self._crear_venta_pos(cantidad=2)

        resp = self.client.get(f"/api/caja/pagos/venta/{id_venta}", headers=self.headers_cajero)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data["success"])
        venta = data["venta"]
        self.assertEqual(venta["id_venta"], id_venta)
        self.assertEqual(venta["estado"], "PENDIENTE_PAGO")
        self.assertGreater(float(venta["total"]), 0)
        self.assertIsInstance(venta["items"], list)
        self.assertGreaterEqual(len(venta["items"]), 1)

    def test_03_validar_venta_rechazo_sin_sesion_caja(self):
        """[3] W28: Rechazo de cobro si el cajero no tiene sesión de caja abierta"""
        id_venta, _ = self._crear_venta_pos(cantidad=1)

        # Crear token de usuario sin caja abierta
        token_sin_caja = create_access_token(
            nro_usuario=9999,
            username="otro_cajero_test",
            id_rol=5,
            id_empresa=1,
            nombre="Otro",
            apellido="Cajero",
            roles=["CAJERO"],
            permisos=["caja.abrir", "caja.cerrar", "caja.ver", "pos.vender", "pos.cobrar", "comprobante.emitir"],
            sucursales=[1]
        )
        headers = {"Authorization": f"Bearer {token_sin_caja}"}

        resp = self.client.get(f"/api/caja/pagos/venta/{id_venta}", headers=headers)
        self.assertEqual(resp.status_code, 400)
        self.assertIn("sesión de caja abierta", resp.json()["detail"].lower())

    def test_04_procesar_pago_efectivo_monto_insuficiente(self):
        """[4] W28: Rechazo si el efectivo recibido es menor al total"""
        id_venta, total = self._crear_venta_pos(cantidad=1)
        total_float = float(total)

        payload = {
            "id_venta": id_venta,
            "id_metodo_pago": 3, # Efectivo
            "monto_recibido": total_float - 1.0 # Insuficiente por 1 Bs.
        }
        resp = self.client.post("/api/caja/pagos/procesar", json=payload, headers=self.headers_cajero)
        self.assertEqual(resp.status_code, 400)
        self.assertIn("insuficiente", resp.json()["detail"].lower())

    def test_05_procesar_pago_efectivo_exitoso_y_cambio(self):
        """[5] W28: Pago exitoso en efectivo, cálculo de cambio y actualización a PAGADO"""
        id_venta, total = self._crear_venta_pos(cantidad=1)
        total_float = float(total)
        monto_recibido = total_float + 20.0 # Sobran 20 Bs.

        payload = {
            "id_venta": id_venta,
            "id_metodo_pago": 3, # Efectivo
            "monto_recibido": monto_recibido,
            "razon_social": "Cliente Final Test",
            "nit_ci": "1234567"
        }
        resp = self.client.post("/api/caja/pagos/procesar", json=payload, headers=self.headers_cajero)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["id_venta"], id_venta)
        self.assertAlmostEqual(data["cambio"], 20.0, places=2)
        self.assertEqual(data["estado_venta"], "PAGADO")

        # Verificar en base de datos
        res_db = self.db.execute_query(
            f"SELECT estado, nit_ci, razon_social FROM {schema}.t_venta WHERE id_venta = %s;",
            (id_venta,), fetchone=True
        )
        self.assertEqual(res_db[0], "PAGADO")
        self.assertEqual(res_db[1], "1234567")
        self.assertEqual(res_db[2], "Cliente Final Test")

        # Verificar en t_pago
        res_pago = self.db.execute_query(
            f"SELECT estado, monto, id_metodo_pago FROM {schema}.t_pago WHERE id_venta = %s;",
            (id_venta,), fetchone=True
        )
        self.assertIsNotNone(res_pago)
        self.db.conn.commit()
        self.assertEqual(res_pago[0], "APROBADO")
        self.assertEqual(res_pago[2], 3)

    def test_06_proteccion_contra_doble_cobro(self):
        """[6] W28: Bloquear intento de cobro a una venta ya pagada"""
        id_venta, total = self._crear_venta_pos(cantidad=1)
        
        # Cobrar por primera vez
        payload = {
            "id_venta": id_venta,
            "id_metodo_pago": 3,
            "monto_recibido": float(total)
        }
        resp1 = self.client.post("/api/caja/pagos/procesar", json=payload, headers=self.headers_cajero)
        self.assertEqual(resp1.status_code, 200)

        # Intentar cobrar por segunda vez
        resp2 = self.client.post("/api/caja/pagos/procesar", json=payload, headers=self.headers_cajero)
        self.assertEqual(resp2.status_code, 400)
        detail_txt = resp2.json()["detail"].lower()
        self.assertTrue(
            "cobrada" in detail_txt or "pagada" in detail_txt or "pago" in detail_txt
        )

    def test_07_procesar_pago_tarjeta_con_referencia(self):
        """[7] W28: Pago exitoso con Tarjeta y registro de referencia de voucher"""
        id_venta, total = self._crear_venta_pos(cantidad=1)

        payload = {
            "id_venta": id_venta,
            "id_metodo_pago": 1, # Tarjeta
            "referencia_externa": "VOUCHER-POS-789012"
        }
        resp = self.client.post("/api/caja/pagos/procesar", json=payload, headers=self.headers_cajero)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["estado_venta"], "PAGADO")

        # Verificar referencia en t_pago
        res_pago = self.db.execute_query(
            f"SELECT referencia_externa, estado FROM {schema}.t_pago WHERE id_venta = %s;",
            (id_venta,), fetchone=True
        )
        self.db.conn.commit()
        self.assertEqual(res_pago[0], "VOUCHER-POS-789012")
        self.assertEqual(res_pago[1], "APROBADO")

    def test_08_obtener_datos_comprobante_w29(self):
        """[8] W29: Consultar datos para emisión de comprobante de venta pagada"""
        id_venta, total = self._crear_venta_pos(cantidad=1)
        # Pagar la venta
        caja_pago_repos.ejecutar_pago_caja(
            id_venta=id_venta,
            id_metodo_pago=3,
            id_sesion_caja=self.id_sesion_caja,
            id_usuario=self.id_cajero,
            id_empresa=1,
            monto_recibido=Decimal(str(total))
        )

        resp = self.client.get(f"/api/comprobantes/venta/{id_venta}/datos", headers=self.headers_cajero)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data["success"])
        venta = data["venta"]
        self.assertEqual(venta["id_venta"], id_venta)
        self.assertEqual(venta["estado"], "PAGADO")
        self.assertIn("pago", venta)
        self.assertIsNotNone(venta["pago"])

    def test_09_obtener_datos_comprobante_venta_no_pagada_falla(self):
        """[9] W29: Rechazo de consulta de comprobante si la venta sigue PENDIENTE_PAGO"""
        id_venta, _ = self._crear_venta_pos(cantidad=1)

        resp = self.client.get(f"/api/comprobantes/venta/{id_venta}/datos", headers=self.headers_cajero)
        self.assertEqual(resp.status_code, 400)
        self.assertIn("no ha sido pagada", resp.json()["detail"].lower())

    def test_10_emitir_comprobante_actualiza_snapshot_y_correo(self):
        """[10] W29: Emitir comprobante, actualizar datos fiscales en t_venta"""
        id_venta, total = self._crear_venta_pos(cantidad=1)
        caja_pago_repos.ejecutar_pago_caja(
            id_venta=id_venta,
            id_metodo_pago=3,
            id_sesion_caja=self.id_sesion_caja,
            id_usuario=self.id_cajero,
            id_empresa=1,
            monto_recibido=Decimal(str(total))
        )

        payload = {
            "razon_social": "Corporación Aurora Test",
            "nit_ci": "44556677",
            "correo_facturacion": "contabilidad@auroratest.bo",
            "tipo_documento": "FACTURA",
            "enviar_correo": False
        }
        resp = self.client.post(f"/api/comprobantes/venta/{id_venta}/emitir", json=payload, headers=self.headers_cajero)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data["success"])
        self.assertIn("pdf_url", data)

        # Verificar persistencia en base de datos
        res_db = self.db.execute_query(
            f"SELECT razon_social, nit_ci, correo_facturacion, tipo_documento FROM {schema}.t_venta WHERE id_venta = %s;",
            (id_venta,), fetchone=True
        )
        self.db.conn.commit()
        self.assertEqual(res_db[0], "Corporación Aurora Test")
        self.assertEqual(res_db[1], "44556677")
        self.assertEqual(res_db[2], "contabilidad@auroratest.bo")
        self.assertEqual(res_db[3], "FACTURA")

    def test_11_descargar_comprobante_pdf_reportlab(self):
        """[11] W29: Descargar comprobante PDF generado con ReportLab"""
        id_venta, total = self._crear_venta_pos(cantidad=1)
        caja_pago_repos.ejecutar_pago_caja(
            id_venta=id_venta,
            id_metodo_pago=3,
            id_sesion_caja=self.id_sesion_caja,
            id_usuario=self.id_cajero,
            id_empresa=1,
            monto_recibido=Decimal(str(total))
        )

        resp = self.client.get(f"/api/comprobantes/venta/{id_venta}/pdf", headers=self.headers_cajero)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.headers.get("content-type"), "application/pdf")
        pdf_bytes = resp.content
        self.assertTrue(pdf_bytes.startswith(b"%PDF-"), "El archivo retornado debe iniciar con la cabecera %PDF-")
        self.assertGreater(len(pdf_bytes), 1000, "El PDF generado debe contener datos visuales completos")

    def test_12_integracion_flujo_completo_w24_w28_w29(self):
        """[12] Integración completa de ciclo: W24 -> W28 -> W29 (id_venta único y coherente)"""
        # Paso 1: W24 Registrar Venta Presencial
        payload_w24 = {
            "id_sesion_caja": self.id_sesion_caja,
            "items": [{"id_variante": self.id_variante, "cantidad": 1}],
            "descuento": 0
        }
        resp_w24 = self.client.post("/api/pos/ventas", json=payload_w24, headers=self.headers_cajero)
        self.assertEqual(resp_w24.status_code, 200)
        id_venta = resp_w24.json()["venta"]["id_venta"]
        total_w24 = float(resp_w24.json()["venta"]["total"])
        self.assertEqual(resp_w24.json()["venta"]["estado"], "PENDIENTE_PAGO")

        # Paso 2: W28 Consultar Venta
        resp_w28_val = self.client.get(f"/api/caja/pagos/venta/{id_venta}", headers=self.headers_cajero)
        self.assertEqual(resp_w28_val.status_code, 200)
        self.assertEqual(resp_w28_val.json()["venta"]["id_venta"], id_venta)

        # Paso 3: W28 Cobrar Venta en Caja (Efectivo)
        payload_pago = {
            "id_venta": id_venta,
            "id_metodo_pago": 3,
            "monto_recibido": total_w24 + 50.0,
            "razon_social": "Cliente E2E",
            "nit_ci": "88776655"
        }
        resp_w28_pago = self.client.post("/api/caja/pagos/procesar", json=payload_pago, headers=self.headers_cajero)
        self.assertEqual(resp_w28_pago.status_code, 200)
        self.assertEqual(resp_w28_pago.json()["estado_venta"], "PAGADO")
        self.assertAlmostEqual(resp_w28_pago.json()["cambio"], 50.0, places=2)

        # Paso 4: W29 Emitir Comprobante
        payload_comprobante = {
            "razon_social": "Cliente E2E Final",
            "nit_ci": "88776655",
            "correo_facturacion": "e2e@aurora.bo",
            "tipo_documento": "FACTURA",
            "enviar_correo": False
        }
        resp_w29_emitir = self.client.post(f"/api/comprobantes/venta/{id_venta}/emitir", json=payload_comprobante, headers=self.headers_cajero)
        self.assertEqual(resp_w29_emitir.status_code, 200)

        # Paso 5: W29 Descargar Comprobante PDF
        resp_w29_pdf = self.client.get(f"/api/comprobantes/venta/{id_venta}/pdf", headers=self.headers_cajero)
        self.assertEqual(resp_w29_pdf.status_code, 200)
        self.assertTrue(resp_w29_pdf.content.startswith(b"%PDF-"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
