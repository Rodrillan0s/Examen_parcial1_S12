import unittest
import threading
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from app import create_app
from app.classes.postgres import PostgreSQL
from app.config import Config
from app.utils.security import create_access_token

class TestGestionReservasCU10(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.client = TestClient(cls.app)
        cls.schema = Config.SCHEMA or 'comercio'

        # Tokens para dos clientes distintos
        cls.token_cliente1 = create_access_token(
            nro_usuario=9991,
            username='cliente_test_1',
            id_rol=2,
            id_empresa=1,
            nombre='Cliente',
            apellido='Uno',
            roles=['CLIENTE']
        )
        cls.headers_c1 = {'Authorization': f'Bearer {cls.token_cliente1}'}

        cls.token_cliente2 = create_access_token(
            nro_usuario=9992,
            username='cliente_test_2',
            id_rol=2,
            id_empresa=1,
            nombre='Cliente',
            apellido='Dos',
            roles=['CLIENTE']
        )
        cls.headers_c2 = {'Authorization': f'Bearer {cls.token_cliente2}'}

        # Asegurar usuarios y clientes de prueba en BD
        db = PostgreSQL()
        db.create_connection()
        try:
            # Usuario 1
            db.execute_query(f"""
                INSERT INTO {cls.schema}.t_usuario (id_usuario, correo, username, password_hash, nombre, apellido, estado, id_empresa, id_rol)
                VALUES (9991, 'cliente1@test.com', 'cliente_test_1', 'fakehash', 'Cliente', 'Uno', TRUE, 1, 2)
                ON CONFLICT (id_usuario) DO NOTHING;
            """, commit=True)
            db.execute_query(f"""
                INSERT INTO {cls.schema}.t_cliente (id_usuario, fecha_registro)
                VALUES (9991, NOW())
                ON CONFLICT DO NOTHING;
            """, commit=True)

            # Usuario 2
            db.execute_query(f"""
                INSERT INTO {cls.schema}.t_usuario (id_usuario, correo, username, password_hash, nombre, apellido, estado, id_empresa, id_rol)
                VALUES (9992, 'cliente2@test.com', 'cliente_test_2', 'fakehash', 'Cliente', 'Dos', TRUE, 1, 2)
                ON CONFLICT (id_usuario) DO NOTHING;
            """, commit=True)
            db.execute_query(f"""
                INSERT INTO {cls.schema}.t_cliente (id_usuario, fecha_registro)
                VALUES (9992, NOW())
                ON CONFLICT DO NOTHING;
            """, commit=True)

            # Sucursal de prueba (usamos id_sucursal=1 de Empresa 1)
            cls.id_sucursal = 1

            # Variantes de prueba
            cls.id_variante_a = 15
            cls.id_variante_b = 16

            # Resetear inventario de variante_a y variante_b en sucursal 1 para un estado predecible
            db.execute_query(f"""
                UPDATE {cls.schema}.t_inventario
                SET stock_actual = 10, stock_reservado = 0, stock_disponible = 10, fecha_actualizacion = NOW()
                WHERE id_sucursal = %s AND id_variante = %s;
            """, (cls.id_sucursal, cls.id_variante_a), commit=True)

            db.execute_query(f"""
                UPDATE {cls.schema}.t_inventario
                SET stock_actual = 10, stock_reservado = 0, stock_disponible = 10, fecha_actualizacion = NOW()
                WHERE id_sucursal = %s AND id_variante = %s;
            """, (cls.id_sucursal, cls.id_variante_b), commit=True)
        finally:
            db.close_connection()

    def _consultar_stock(self, id_sucursal, id_variante):
        db = PostgreSQL()
        db.create_connection()
        try:
            cur = db.conn.cursor()
            cur.execute(f"""
                SELECT stock_actual, stock_reservado, stock_disponible
                FROM {self.schema}.t_inventario
                WHERE id_sucursal = %s AND id_variante = %s;
            """, (id_sucursal, id_variante))
            row = cur.fetchone()
            return {"actual": row[0], "reservado": row[1], "disponible": row[2]}
        finally:
            db.close_connection()

    def test_01_reserva_correcta(self):
        """Caso 1: Reserva correcta de 2 unidades -> stock_reservado +2, stock_disponible -2, stock_actual inalterado."""
        fecha_visita = (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d 15:00")
        stock_inicial = self._consultar_stock(self.id_sucursal, self.id_variante_a)

        payload = {
            "id_sucursal": self.id_sucursal,
            "fecha_hora_visita": fecha_visita,
            "observaciones": "Probar en vestidor de gala",
            "items": [
                {"id_variante": self.id_variante_a, "cantidad": 2}
            ]
        }

        resp = self.client.post('/api/reservas', json=payload, headers=self.headers_c1)
        self.assertEqual(resp.status_code, 201, resp.text)
        data = resp.json()
        self.assertTrue(data.get('success'))
        reserva = data.get('data')
        self.assertIn('codigo_reserva', reserva)
        self.assertEqual(reserva['estado'], 'PENDIENTE')
        self.assertEqual(len(reserva['detalles']), 1)

        # Verificar inventario
        stock_final = self._consultar_stock(self.id_sucursal, self.id_variante_a)
        self.assertEqual(stock_final['actual'], stock_inicial['actual'], "stock_actual NO debe disminuir con reserva")
        self.assertEqual(stock_final['reservado'], stock_inicial['reservado'] + 2)
        self.assertEqual(stock_final['disponible'], stock_inicial['disponible'] - 2)

    def test_02_stock_insuficiente(self):
        """Caso 2: Stock insuficiente -> se rechaza y no se modifica inventario."""
        stock_inicial = self._consultar_stock(self.id_sucursal, self.id_variante_a)
        fecha_visita = (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d 16:00")

        # Intentar reservar más del stock disponible
        cantidad_excesiva = stock_inicial['disponible'] + 50
        payload = {
            "id_sucursal": self.id_sucursal,
            "fecha_hora_visita": fecha_visita,
            "items": [
                {"id_variante": self.id_variante_a, "cantidad": cantidad_excesiva}
            ]
        }

        resp = self.client.post('/api/reservas', json=payload, headers=self.headers_c1)
        self.assertEqual(resp.status_code, 400)
        self.assertIn("insuficiente", resp.json().get('detail', '').lower())

        # Verificar que el stock no cambió
        stock_despues = self._consultar_stock(self.id_sucursal, self.id_variante_a)
        self.assertEqual(stock_despues, stock_inicial)

    def test_03_multiples_variantes(self):
        """Caso 3: Múltiples variantes -> cada fila de t_inventario se actualiza de forma independiente."""
        fecha_visita = (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d 11:30")
        stock_ini_a = self._consultar_stock(self.id_sucursal, self.id_variante_a)
        stock_ini_b = self._consultar_stock(self.id_sucursal, self.id_variante_b)

        payload = {
            "id_sucursal": self.id_sucursal,
            "fecha_hora_visita": fecha_visita,
            "observaciones": "Reserva con dos prendas distintas",
            "items": [
                {"id_variante": self.id_variante_a, "cantidad": 1},
                {"id_variante": self.id_variante_b, "cantidad": 3}
            ]
        }

        resp = self.client.post('/api/reservas', json=payload, headers=self.headers_c1)
        self.assertEqual(resp.status_code, 201, resp.text)
        reserva = resp.json().get('data')
        self.assertEqual(len(reserva['detalles']), 2)

        stock_fin_a = self._consultar_stock(self.id_sucursal, self.id_variante_a)
        stock_fin_b = self._consultar_stock(self.id_sucursal, self.id_variante_b)

        self.assertEqual(stock_fin_a['reservado'], stock_ini_a['reservado'] + 1)
        self.assertEqual(stock_fin_a['disponible'], stock_ini_a['disponible'] - 1)
        self.assertEqual(stock_fin_b['reservado'], stock_ini_b['reservado'] + 3)
        self.assertEqual(stock_fin_b['disponible'], stock_ini_b['disponible'] - 3)

    def test_04_rollback_si_falla_una_variante(self):
        """Caso 4: Si falla una de las variantes (ej. segunda variante sin stock), se hace ROLLBACK de todo."""
        fecha_visita = (datetime.now() + timedelta(days=4)).strftime("%Y-%m-%d 14:00")
        stock_ini_a = self._consultar_stock(self.id_sucursal, self.id_variante_a)
        stock_ini_b = self._consultar_stock(self.id_sucursal, self.id_variante_b)

        payload = {
            "id_sucursal": self.id_sucursal,
            "fecha_hora_visita": fecha_visita,
            "items": [
                {"id_variante": self.id_variante_a, "cantidad": 2}, # Tiene stock
                {"id_variante": self.id_variante_b, "cantidad": 9999} # NO tiene stock
            ]
        }

        resp = self.client.post('/api/reservas', json=payload, headers=self.headers_c1)
        self.assertEqual(resp.status_code, 400)

        # Comprobar que la primera variante NO sufrió descuento gracias al ROLLBACK
        stock_fin_a = self._consultar_stock(self.id_sucursal, self.id_variante_a)
        stock_fin_b = self._consultar_stock(self.id_sucursal, self.id_variante_b)
        self.assertEqual(stock_fin_a, stock_ini_a, "La variante A no debió modificarse tras el rollback")
        self.assertEqual(stock_fin_b, stock_ini_b)

    def test_05_cancelacion_libera_stock(self):
        """Caso 5: Cancelación exitosa -> restituye stock disponible y reduce reservado."""
        fecha_visita = (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d 10:00")
        payload = {
            "id_sucursal": self.id_sucursal,
            "fecha_hora_visita": fecha_visita,
            "items": [{"id_variante": self.id_variante_a, "cantidad": 2}]
        }
        crear_resp = self.client.post('/api/reservas', json=payload, headers=self.headers_c1)
        self.assertEqual(crear_resp.status_code, 201)
        id_reserva = crear_resp.json()['data']['id_reserva']

        stock_tras_reserva = self._consultar_stock(self.id_sucursal, self.id_variante_a)

        # Cancelar
        cancel_resp = self.client.post(
            f'/api/reservas/{id_reserva}/cancelar',
            json={"motivo": "Cambio de planes de viaje"},
            headers=self.headers_c1
        )
        self.assertEqual(cancel_resp.status_code, 200, cancel_resp.text)
        self.assertEqual(cancel_resp.json()['data']['estado'], 'CANCELADA')

        # Comprobar liberación en inventario
        stock_tras_cancelar = self._consultar_stock(self.id_sucursal, self.id_variante_a)
        self.assertEqual(stock_tras_cancelar['reservado'], stock_tras_reserva['reservado'] - 2)
        self.assertEqual(stock_tras_cancelar['disponible'], stock_tras_reserva['disponible'] + 2)
        self.assertEqual(stock_tras_cancelar['actual'], stock_tras_reserva['actual'])

    def test_06_evitar_doble_cancelacion(self):
        """Caso 6: Doble cancelación -> se rechaza y no duplica stock liberado."""
        fecha_visita = (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d 10:00")
        crear_resp = self.client.post(
            '/api/reservas',
            json={"id_sucursal": self.id_sucursal, "fecha_hora_visita": fecha_visita, "items": [{"id_variante": self.id_variante_a, "cantidad": 1}]},
            headers=self.headers_c1
        )
        id_reserva = crear_resp.json()['data']['id_reserva']

        # Primera cancelación (exitosa)
        self.client.post(f'/api/reservas/{id_reserva}/cancelar', json={"motivo": "Cancel 1"}, headers=self.headers_c1)
        stock_tras_primera = self._consultar_stock(self.id_sucursal, self.id_variante_a)

        # Segunda cancelación (debe fallar)
        segunda_resp = self.client.post(f'/api/reservas/{id_reserva}/cancelar', json={"motivo": "Cancel 2"}, headers=self.headers_c1)
        self.assertEqual(segunda_resp.status_code, 400)
        self.assertIn("cancelada previamente", segunda_resp.json().get('detail', '').lower())

        # El stock no debe alterarse
        stock_tras_segunda = self._consultar_stock(self.id_sucursal, self.id_variante_a)
        self.assertEqual(stock_tras_segunda, stock_tras_primera)

    def test_07_seguridad_acceso_solo_propias_reservas(self):
        """Caso 7: Cliente A no puede consultar ni cancelar reservas de Cliente B."""
        fecha_visita = (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d 10:00")
        # Creada por Cliente 1
        crear_resp = self.client.post(
            '/api/reservas',
            json={"id_sucursal": self.id_sucursal, "fecha_hora_visita": fecha_visita, "items": [{"id_variante": self.id_variante_a, "cantidad": 1}]},
            headers=self.headers_c1
        )
        id_reserva_c1 = crear_resp.json()['data']['id_reserva']

        # Cliente 2 intenta consultar el detalle de Cliente 1 -> 404
        get_resp = self.client.get(f'/api/reservas/{id_reserva_c1}', headers=self.headers_c2)
        self.assertEqual(get_resp.status_code, 404)

        # Cliente 2 intenta cancelar la reserva de Cliente 1 -> 400 con error de autorización
        canc_resp = self.client.post(f'/api/reservas/{id_reserva_c1}/cancelar', headers=self.headers_c2)
        self.assertEqual(canc_resp.status_code, 400)
        self.assertIn("no tienes autorización", canc_resp.json().get('detail', '').lower())

    def test_08_concurrencia_sobre_ultimo_stock(self):
        """Caso 8: Dos peticiones simultáneas intentando reservar la última unidad disponible (stock_disponible=1)."""
        db = PostgreSQL()
        db.create_connection()
        try:
            # Fijar stock disponible exactamente en 1
            db.execute_query(f"""
                UPDATE {self.schema}.t_inventario
                SET stock_actual = 1, stock_reservado = 0, stock_disponible = 1, fecha_actualizacion = NOW()
                WHERE id_sucursal = %s AND id_variante = %s;
            """, (self.id_sucursal, self.id_variante_a), commit=True)
        finally:
            db.close_connection()

        fecha_visita = (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d 12:00")
        payload = {
            "id_sucursal": self.id_sucursal,
            "fecha_hora_visita": fecha_visita,
            "items": [{"id_variante": self.id_variante_a, "cantidad": 1}]
        }

        resultados = []

        def peticion(token_hdr):
            resp = self.client.post('/api/reservas', json=payload, headers=token_hdr)
            resultados.append(resp.status_code)

        t1 = threading.Thread(target=peticion, args=(self.headers_c1,))
        t2 = threading.Thread(target=peticion, args=(self.headers_c2,))

        t1.start()
        t2.start()
        t1.join()
        t2.join()

        # Exactamente una debe haber tenido éxito (201) y la otra debe haber sido rechazada (400)
        self.assertEqual(sorted(resultados), [201, 400], f"Resultados obtenidos: {resultados}")

        # El stock final debe ser: reservado = 1, disponible = 0
        stock_fin = self._consultar_stock(self.id_sucursal, self.id_variante_a)
        self.assertEqual(stock_fin['reservado'], 1)
        self.assertEqual(stock_fin['disponible'], 0)
        self.assertEqual(stock_fin['actual'], 1)

if __name__ == '__main__':
    unittest.main()
