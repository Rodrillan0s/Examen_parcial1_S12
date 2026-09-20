"""
Test Suite Automatizado para Control de Efectivo por Denominaciones:
- W28: Pago en efectivo registrando denominaciones recibidas (ENTRADA_EFECTIVO) y cambio (SALIDA_CAMBIO).
- W29: Arqueo de cierre de caja comparando esperado por denominación vs físico contado.
"""
import sys
import os
import unittest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.classes.postgres import PostgreSQL
from app.config import Config
from app.utils.security import create_access_token
from app.utils.migrate_denominaciones_pago import migrar_denominaciones_pago

class TestControlEfectivoDenominaciones(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        migrar_denominaciones_pago()
        cls.app = create_app()
        cls.client = TestClient(cls.app)
        cls.db = PostgreSQL()
        cls.db.create_connection()
        cls.schema = Config.SCHEMA or 'comercio'
        schema = cls.schema

        # Obtener o crear cajero
        res_u = cls.db.execute_query(
            f"SELECT id_usuario FROM {schema}.t_usuario WHERE username = 'cajero_w28w29';",
            fetchone=True
        )
        if res_u:
            cls.id_cajero = res_u[0]
        else:
            res_ins = cls.db.execute_query(f"""
                INSERT INTO {schema}.t_usuario (nombre, apellido, correo, username, estado, id_empresa, id_rol)
                VALUES ('Cajero', 'Tester W28W29', 'cajero.w28w29@aurora.bo', 'cajero_w28w29', TRUE, 1, 5)
                RETURNING id_usuario;
            """, fetchone=True, commit=True)
            cls.id_cajero = res_ins[0]

        cls.db.execute_query(f"""
            INSERT INTO {schema}.t_usuario_sucursal (id_usuario, id_sucursal)
            VALUES (%s, 1)
            ON CONFLICT DO NOTHING;
        """, (cls.id_cajero,), commit=True)

        cls.token = create_access_token(
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
        cls.headers = {"Authorization": f"Bearer {cls.token}"}

    @classmethod
    def tearDownClass(cls):
        cls.db.close_connection()

    def test_01_flujo_completo_denominaciones_w28_y_cierre_w29(self):
        """
        Ejemplo del requerimiento del usuario:
        VENTA: Bs. 73.00
        RECIBIDO: Bs. 100 x 1 = Bs. 100.00
        CAMBIO: Bs. 20 x 1 = 20, Bs. 5 x 1 = 5, Bs. 2 x 1 = 2 (Total cambio: Bs. 27.00)
        """
        schema = self.schema

        # 1. Obtener denominaciones activas
        res_denoms = self.client.get("/api/caja/denominaciones", headers=self.headers)
        self.assertEqual(res_denoms.status_code, 200)
        denoms = res_denoms.json()["denominaciones"]
        denom_map = {d["valor"]: d["id_denominacion"] for d in denoms}

        id_100 = denom_map[100.0]
        id_50 = denom_map[50.0]
        id_20 = denom_map[20.0]
        id_5 = denom_map[5.0]
        id_2 = denom_map[2.0]

        id_user = self.id_cajero
        id_suc = 1
        id_emp = 1

        self.db.execute_query(
            f"UPDATE {schema}.t_caja_sesion SET estado = 'CERRADA' WHERE id_usuario = %s AND estado = 'ABIERTA';",
            (id_user,), commit=True
        )

        # 3. Apertura de caja con fondo inicial:
        # Fondo: 2 billetes de Bs. 100 + 1 billete de Bs. 50 = Bs. 250.00
        res_caja = self.client.get("/api/caja/estado", headers=self.headers)
        id_caja = res_caja.json()["caja_asignada"]["id_caja"]

        res_abrir = self.client.post("/api/caja/abrir", headers=self.headers, json={
            "id_caja": id_caja,
            "id_sucursal": id_suc,
            "conteo": [
                {"id_denominacion": id_100, "cantidad": 2},
                {"id_denominacion": id_50, "cantidad": 1}
            ],
            "observacion": "Apertura test con denominaciones 250 Bs."
        })
        self.assertEqual(res_abrir.status_code, 200, res_abrir.text)
        id_sesion = res_abrir.json()["sesion"]["id_sesion_caja"]
        self.assertEqual(res_abrir.json()["sesion"]["monto_inicial"], 250.00)

        # 4. Crear venta W24 por Bs. 73.00 en estado PENDIENTE_PAGO
        q_ins_vta = f"""
            INSERT INTO {schema}.t_venta (
                id_empresa, id_sucursal, id_usuario, id_sesion_caja,
                numero_venta, total, subtotal, descuento, estado, fecha_venta
            ) VALUES (
                %s, %s, %s, %s,
                'VTA-TEST-DENOM-73', 73.00, 73.00, 0.00, 'PENDIENTE_PAGO', NOW()
            ) RETURNING id_venta;
        """
        vta_row = self.db.execute_query(q_ins_vta, (id_emp, id_suc, id_user, id_sesion), fetchone=True, commit=True)
        id_venta = vta_row[0]

        # 5. Cobro en efectivo W28 con desglose de billetes:
        # Recibido: 1 billete de 100 (Total recibido: 100.00)
        # Cambio: 1 de 20, 1 de 5, 1 de 2 (Total cambio: 27.00)
        payload_cobro = {
            "id_venta": id_venta,
            "id_metodo_pago": 3, # Efectivo
            "monto_recibido": 100.00,
            "desglose_recibido": [
                {"id_denominacion": id_100, "valor": 100.0, "cantidad": 1, "subtotal": 100.0}
            ],
            "desglose_cambio": [
                {"id_denominacion": id_20, "valor": 20.0, "cantidad": 1, "subtotal": 20.0},
                {"id_denominacion": id_5, "valor": 5.0, "cantidad": 1, "subtotal": 5.0},
                {"id_denominacion": id_2, "valor": 2.0, "cantidad": 1, "subtotal": 2.0}
            ]
        }
        res_cobro = self.client.post("/api/caja/pagos/procesar", headers=self.headers, json=payload_cobro)
        self.assertEqual(res_cobro.status_code, 200, res_cobro.text)
        body_pago = res_cobro.json()
        self.assertEqual(body_pago["cambio"], 27.00)
        self.assertEqual(body_pago["estado_venta"], "PAGADO")

        # 6. Verificar persistencia en t_pago_denominacion
        q_movs = f"""
            SELECT tipo_movimiento, id_denominacion, valor_denominacion, cantidad, subtotal
            FROM {schema}.t_pago_denominacion
            WHERE id_venta = %s
            ORDER BY tipo_movimiento, valor_denominacion DESC;
        """
        movs = self.db.execute_query(q_movs, (id_venta,), fetchall=True)
        self.assertTrue(len(movs) >= 4)
        
        entradas = [m for m in movs if m[0] == 'ENTRADA_EFECTIVO']
        salidas = [m for m in movs if m[0] == 'SALIDA_CAMBIO']
        self.assertEqual(len(entradas), 1)
        self.assertEqual(float(entradas[0][2]), 100.0)
        self.assertEqual(entradas[0][3], 1)

        self.assertEqual(len(salidas), 3)
        salidas_map = {float(s[2]): s[3] for s in salidas}
        self.assertEqual(salidas_map[20.0], 1)
        self.assertEqual(salidas_map[5.0], 1)
        self.assertEqual(salidas_map[2.0], 1)

        # 7. Consultar Resumen Financiero con Denominaciones Esperadas
        res_resumen = self.client.get(f"/api/caja/resumen?id_sesion_caja={id_sesion}", headers=self.headers)
        self.assertEqual(res_resumen.status_code, 200)
        resumen = res_resumen.json()["resumen"]
        
        # Efectivo esperado total: 250 + 73 = 323.00
        self.assertEqual(resumen["efectivo_esperado"], 323.00)
        self.assertEqual(resumen["ventas_efectivo"], 73.00)

        # Verificar desglose esperado por denominación:
        # 100: Apertura=2, Recibido=1, Cambio=0 -> Esperado=3
        # 50: Apertura=1, Recibido=0, Cambio=0 -> Esperado=1
        # 20: Apertura=0, Recibido=0, Cambio=1 -> Esperado=-1
        # 5: Apertura=0, Recibido=0, Cambio=1 -> Esperado=-1
        # 2: Apertura=0, Recibido=0, Cambio=1 -> Esperado=-1
        esp_list = resumen.get("denominaciones_esperadas", [])
        esp_map = {item["id_denominacion"]: item for item in esp_list}

        self.assertEqual(esp_map[id_100]["cantidad_esperada"], 3)
        self.assertEqual(esp_map[id_100]["cantidad_apertura"], 2)
        self.assertEqual(esp_map[id_100]["cantidad_recibida"], 1)

        self.assertEqual(esp_map[id_50]["cantidad_esperada"], 1)
        self.assertEqual(esp_map[id_20]["cantidad_esperada"], -1)
        self.assertEqual(esp_map[id_5]["cantidad_esperada"], -1)
        self.assertEqual(esp_map[id_2]["cantidad_esperada"], -1)

        # 8. Cierre de caja (W29) con conteo físico exacto (CUADRA)
        # 3 de 100 (300) + 1 de 50 (50) - 1 de 20 (-20) - 1 de 5 (-5) - 1 de 2 (-2) = 323.00
        conteo_cierre = []
        for item in esp_list:
            conteo_cierre.append({
                "id_denominacion": item["id_denominacion"],
                "cantidad": max(0, item["cantidad_esperada"]) if item["cantidad_esperada"] > 0 else 0
            })

        # Para que cuadre exacto con Bs. 323: 3x100 (300) + 1x20 (20) + 1x2 (2) + 1x1 (1) = 323
        # Supongamos que en la caja física hay:
        # 3 billetes de 100 = 300
        # 1 billete de 20 = 20
        # 3 monedas de 1 = 3
        # Total contado: 323.00
        id_1 = denom_map[1.0]
        conteo_cuadrado = [
            {"id_denominacion": id_100, "cantidad": 3},
            {"id_denominacion": id_20, "cantidad": 1},
            {"id_denominacion": id_1, "cantidad": 3}
        ]

        res_cierre = self.client.post("/api/caja/cerrar", headers=self.headers, json={
            "id_sesion_caja": id_sesion,
            "conteo": conteo_cuadrado,
            "observacion": "Cierre test cuadrado"
        })
        self.assertEqual(res_cierre.status_code, 200, res_cierre.text)
        cierre = res_cierre.json()["cierre"]
        self.assertEqual(cierre["estado"], "CERRADA")
        self.assertEqual(cierre["efectivo_esperado"], 323.00)
        self.assertEqual(cierre["efectivo_contado"], 323.00)
        self.assertEqual(cierre["diferencia"], 0.00)
        self.assertEqual(cierre["estado_diferencia"], "CUADRA")

        print("\n✅ PASÓ: Flujo completo de control de efectivo por denominaciones (W28 + W29 Arqueo comparativo) verificado.")

if __name__ == "__main__":
    unittest.main()
