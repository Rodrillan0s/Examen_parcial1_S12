import unittest
from datetime import datetime, timedelta
from decimal import Decimal
from fastapi.testclient import TestClient
from app import create_app
from app.classes.postgres import PostgreSQL
from app.config import Config
from app.utils.security import create_access_token

class TestConsultaPedidosCU11(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.client = TestClient(cls.app)
        cls.schema = Config.SCHEMA or 'comercio'

        # Cliente 1 (Tenant 1)
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

        # Cliente 2 (Tenant 1)
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

        # Cliente 3 (Sin pedidos)
        cls.token_cliente3 = create_access_token(
            nro_usuario=9993,
            username='cliente_test_3',
            id_rol=2,
            id_empresa=1,
            nombre='Cliente',
            apellido='Tres',
            roles=['CLIENTE']
        )
        cls.headers_c3 = {'Authorization': f'Bearer {cls.token_cliente3}'}

        db = PostgreSQL()
        db.create_connection()
        try:
            # Asegurar usuarios
            for uid, uname, mail in [(9991, 'cliente_test_1', 'cliente1@test.com'), 
                                     (9992, 'cliente_test_2', 'cliente2@test.com'),
                                     (9993, 'cliente_test_3', 'cliente3@test.com')]:
                db.execute_query(f"""
                    INSERT INTO {cls.schema}.t_usuario (id_usuario, correo, username, password_hash, nombre, apellido, estado, id_empresa, id_rol)
                    VALUES (%s, %s, %s, 'hash', 'Test', 'User', TRUE, 1, 2)
                    ON CONFLICT (id_usuario) DO NOTHING;
                """, (uid, mail, uname), commit=True)
                db.execute_query(f"""
                    INSERT INTO {cls.schema}.t_cliente (id_usuario, fecha_registro)
                    VALUES (%s, NOW())
                    ON CONFLICT DO NOTHING;
                """, (uid,), commit=True)

            # Obtener id_cliente de cliente 1 y cliente 2
            row_c1 = db.execute_query(f"SELECT id_cliente FROM {cls.schema}.t_cliente WHERE id_usuario = 9991 LIMIT 1;", fetchone=True)
            cls.id_cliente1 = row_c1[0] if row_c1 else None

            row_c2 = db.execute_query(f"SELECT id_cliente FROM {cls.schema}.t_cliente WHERE id_usuario = 9992 LIMIT 1;", fetchone=True)
            cls.id_cliente2 = row_c2[0] if row_c2 else None

            row_c3 = db.execute_query(f"SELECT id_cliente FROM {cls.schema}.t_cliente WHERE id_usuario = 9993 LIMIT 1;", fetchone=True)
            cls.id_cliente3 = row_c3[0] if row_c3 else None

            # Limpiar pedidos previos de test
            db.execute_query(f"DELETE FROM {cls.schema}.t_detalle_pedido WHERE id_pedido IN (SELECT id_pedido FROM {cls.schema}.t_pedido WHERE codigo_pedido LIKE 'TEST-PED-%');", commit=True)
            db.execute_query(f"DELETE FROM {cls.schema}.t_pedido WHERE codigo_pedido LIKE 'TEST-PED-%';", commit=True)

            # Insertar 3 pedidos de prueba para Cliente 1
            # Pedido 1: PENDIENTE_PAGO, hoy
            db.execute_query(f"""
                INSERT INTO {cls.schema}.t_pedido (
                    id_pedido, codigo_pedido, id_cliente, id_empresa, id_sucursal, fecha_pedido, 
                    estado, estado_pago, modalidad_compra, nombre_contacto, telefono_contacto, subtotal, costo_envio, descuento, total
                ) VALUES (
                    8881, 'TEST-PED-001', {cls.id_cliente1}, 1, 1, NOW(),
                    'PENDIENTE_PAGO', 'PENDIENTE', 'RETIRO_SUCURSAL', 'Juan Perez', '70011223', 500.0, 0.0, 0.0, 500.0
                ) ON CONFLICT (id_pedido) DO NOTHING;
            """, commit=True)
            db.execute_query(f"""
                INSERT INTO {cls.schema}.t_detalle_pedido (id_pedido, id_variante, cantidad, precio_unitario, subtotal)
                VALUES (8881, 15, 2, 250.0, 500.0)
                ON CONFLICT DO NOTHING;
            """, commit=True)

            # Pedido 2: CONFIRMADO, hace 5 días
            db.execute_query(f"""
                INSERT INTO {cls.schema}.t_pedido (
                    id_pedido, codigo_pedido, id_cliente, id_empresa, id_sucursal, fecha_pedido, 
                    estado, estado_pago, modalidad_compra, nombre_contacto, telefono_contacto, subtotal, costo_envio, descuento, total
                ) VALUES (
                    8882, 'TEST-PED-002', {cls.id_cliente1}, 1, 2, NOW() - INTERVAL '5 days',
                    'CONFIRMADO', 'PAGADO', 'ENTREGADO_DOMICILIO', 'Juan Perez', '70011223', 1200.0, 30.0, 50.0, 1180.0
                ) ON CONFLICT (id_pedido) DO NOTHING;
            """, commit=True)
            db.execute_query(f"""
                INSERT INTO {cls.schema}.t_detalle_pedido (id_pedido, id_variante, cantidad, precio_unitario, subtotal)
                VALUES (8882, 16, 1, 1200.0, 1200.0)
                ON CONFLICT DO NOTHING;
            """, commit=True)

            # Pedido 3: CANCELADO, hace 20 días
            db.execute_query(f"""
                INSERT INTO {cls.schema}.t_pedido (
                    id_pedido, codigo_pedido, id_cliente, id_empresa, id_sucursal, fecha_pedido, 
                    estado, estado_pago, modalidad_compra, nombre_contacto, telefono_contacto, subtotal, costo_envio, descuento, total
                ) VALUES (
                    8883, 'TEST-PED-003', {cls.id_cliente1}, 1, 1, NOW() - INTERVAL '20 days',
                    'CANCELADO', 'CANCELADO', 'RETIRO_SUCURSAL', 'Juan Perez', '70011223', 300.0, 0.0, 0.0, 300.0
                ) ON CONFLICT (id_pedido) DO NOTHING;
            """, commit=True)

            # Insertar 1 pedido para Cliente 2 (para probar aislamiento)
            db.execute_query(f"""
                INSERT INTO {cls.schema}.t_pedido (
                    id_pedido, codigo_pedido, id_cliente, id_empresa, id_sucursal, fecha_pedido, 
                    estado, estado_pago, modalidad_compra, nombre_contacto, telefono_contacto, subtotal, costo_envio, descuento, total
                ) VALUES (
                    8884, 'TEST-PED-004', {cls.id_cliente2}, 1, 1, NOW(),
                    'PENDIENTE_PAGO', 'PENDIENTE', 'RETIRO_SUCURSAL', 'Pedro Lopez', '71122334', 450.0, 0.0, 0.0, 450.0
                ) ON CONFLICT (id_pedido) DO NOTHING;
            """, commit=True)

        finally:
            db.close_connection()

    # --------------------------------------------------------------------------
    # 1. LISTADO CORRECTO DE PEDIDOS DEL CLIENTE
    # --------------------------------------------------------------------------
    def test_01_listar_pedidos_cliente(self):
        resp = self.client.get('/api/pedidos', headers=self.headers_c1)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data['success'])
        self.assertGreaterEqual(data['total'], 3)
        # Verificar que todos los pedidos devueltos pertenezcan a id_cliente1
        codigos = [p['codigo_pedido'] for p in data['data']]
        self.assertIn('TEST-PED-001', codigos)
        self.assertIn('TEST-PED-002', codigos)
        self.assertIn('TEST-PED-003', codigos)
        # El pedido de cliente 2 no debe aparecer
        self.assertNotIn('TEST-PED-004', codigos)

    # --------------------------------------------------------------------------
    # 2. DETALLE CORRECTO DE UN PEDIDO CON PRECIOS HISTÓRICOS
    # --------------------------------------------------------------------------
    def test_02_consultar_detalle_pedido(self):
        resp = self.client.get('/api/pedidos/8881', headers=self.headers_c1)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data['success'])
        pedido = data['data']
        self.assertEqual(pedido['id_pedido'], 8881)
        self.assertEqual(pedido['codigo_pedido'], 'TEST-PED-001')
        self.assertEqual(pedido['estado'], 'PENDIENTE_PAGO')
        self.assertEqual(pedido['total'], 500.0)
        self.assertIn('sucursal_nombre', pedido)
        self.assertIn('items', pedido)
        self.assertGreaterEqual(len(pedido['items']), 1)
        item = pedido['items'][0]
        self.assertEqual(item['precio_unitario'], 250.0)
        self.assertEqual(item['cantidad'], 2)
        self.assertEqual(item['subtotal'], 500.0)

    # --------------------------------------------------------------------------
    # 3. PAGINACIÓN CORRECTA
    # --------------------------------------------------------------------------
    def test_03_paginacion_pedidos(self):
        # Solicitar con limit 1
        resp = self.client.get('/api/pedidos?limit=1&page=1', headers=self.headers_c1)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(len(data['data']), 1)
        self.assertEqual(data['page'], 1)
        self.assertEqual(data['limit'], 1)
        self.assertGreaterEqual(data['total_paginas'], 3)

        # Página 2
        resp2 = self.client.get('/api/pedidos?limit=1&page=2', headers=self.headers_c1)
        self.assertEqual(resp2.status_code, 200)
        data2 = resp2.json()
        self.assertEqual(len(data2['data']), 1)
        self.assertNotEqual(data['data'][0]['id_pedido'], data2['data'][0]['id_pedido'])

    # --------------------------------------------------------------------------
    # 4. FILTRAR POR ESTADO
    # --------------------------------------------------------------------------
    def test_04_filtrar_por_estado(self):
        resp = self.client.get('/api/pedidos?estado=CONFIRMADO', headers=self.headers_c1)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data['success'])
        for p in data['data']:
            self.assertEqual(p['estado'], 'CONFIRMADO')
        codigos = [p['codigo_pedido'] for p in data['data']]
        self.assertIn('TEST-PED-002', codigos)
        self.assertNotIn('TEST-PED-001', codigos)

    # --------------------------------------------------------------------------
    # 5. FILTRAR POR FECHA
    # --------------------------------------------------------------------------
    def test_05_filtrar_por_fecha(self):
        hoy = datetime.now().strftime('%Y-%m-%d')
        resp = self.client.get(f'/api/pedidos?fecha_inicio={hoy}&fecha_fin={hoy}', headers=self.headers_c1)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        codigos = [p['codigo_pedido'] for p in data['data']]
        self.assertIn('TEST-PED-001', codigos)
        self.assertNotIn('TEST-PED-003', codigos)

    # --------------------------------------------------------------------------
    # 6. BUSCAR POR CÓDIGO DE PEDIDO
    # --------------------------------------------------------------------------
    def test_06_buscar_por_codigo(self):
        resp = self.client.get('/api/pedidos?codigo=PED-003', headers=self.headers_c1)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(len(data['data']), 1)
        self.assertEqual(data['data'][0]['codigo_pedido'], 'TEST-PED-003')

    # --------------------------------------------------------------------------
    # 7. CLIENTE SIN PEDIDOS
    # --------------------------------------------------------------------------
    def test_07_cliente_sin_pedidos(self):
        resp = self.client.get('/api/pedidos', headers=self.headers_c3)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['total'], 0)
        self.assertEqual(len(data['data']), 0)

    # --------------------------------------------------------------------------
    # 8. ACCESO A PEDIDO DE OTRO CLIENTE (404/403)
    # --------------------------------------------------------------------------
    def test_08_seguridad_acceso_pedido_otro_cliente(self):
        # Cliente 1 intenta consultar el pedido 8884 (que pertenece a Cliente 2)
        resp = self.client.get('/api/pedidos/8884', headers=self.headers_c1)
        self.assertIn(resp.status_code, [403, 404])

    # --------------------------------------------------------------------------
    # 9. AISLAMIENTO ENTRE TENANTS
    # --------------------------------------------------------------------------
    def test_09_aislamiento_multitenant(self):
        # Consultar con un id_empresa distinto (ej. 999) no debe devolver los pedidos del tenant 1
        resp = self.client.get('/api/pedidos?id_empresa=999', headers=self.headers_c1)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data['total'], 0)
        self.assertEqual(len(data['data']), 0)

if __name__ == '__main__':
    unittest.main()
