import unittest
from fastapi.testclient import TestClient
from app import create_app
from app.utils.security import create_access_token
from app.services import asistente_services

class TestAsistenteDeepSeek(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = TestClient(self.app)
        
        # Token de Cliente
        self.token_cliente = create_access_token(
            nro_usuario=6,
            username="cliente_test",
            id_rol=2,
            id_empresa=1,
            nombre="Valentina",
            apellido="Ríos",
            roles=["CLIENTE"]
        )
        
        # Token de Administrador
        self.token_admin = create_access_token(
            nro_usuario=1,
            username="admin_test",
            id_rol=1,
            id_empresa=1,
            nombre="Carlos",
            apellido="Administrador",
            roles=["ADMINISTRADOR"]
        )

    def test_01_ejecutar_herramienta_buscar_prendas(self):
        """Verifica que la búsqueda en BD retorne productos reales de la empresa."""
        res = asistente_services._ejecutar_buscar_prendas({"termino": ""}, id_empresa=1)
        self.assertIn("productos", res)
        self.assertIsInstance(res["productos"], list)
        print(f"\n[Test 1] Productos encontrados en BD: {len(res['productos'])}")
        if res["productos"]:
            p = res["productos"][0]
            print(f"         Ejemplo: {p['nombre']} (Bs. {p['precio']}) - Stock: {p['stock_disponible']}")

    def test_02_ejecutar_herramienta_ventas_admin(self):
        """Verifica la consulta de ventas de la empresa en BD."""
        res = asistente_services._ejecutar_consultar_ventas({"periodo": "hoy"}, id_empresa=1)
        self.assertIn("total_ventas", res)
        self.assertIn("facturacion_total_bs", res)
        print(f"\n[Test 2] Ventas de hoy: {res['total_ventas']} transacciones, Bs. {res['facturacion_total_bs']}")

    def test_03_endpoint_chat_publico_o_cliente(self):
        """Verifica el endpoint POST /api/asistente/chat para un cliente."""
        headers = {"Authorization": f"Bearer {self.token_cliente}"}
        payload = {
            "mensaje": "Hola, ¿tienen vestidos o blusas en la tienda?"
        }
        resp = self.client.post("/api/asistente/chat", json=payload, headers=headers)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data.get("success"))
        self.assertIn("respuesta", data)
        print(f"\n[Test 3] Respuesta a Cliente: {data['respuesta'][:120]}... (Tipo: {data.get('tipo')})")

    def test_04_endpoint_chat_admin_ventas(self):
        """Verifica que un administrador pueda consultar métricas de ventas."""
        headers = {"Authorization": f"Bearer {self.token_admin}"}
        payload = {
            "mensaje": "¿Cuánto vendimos hoy?"
        }
        resp = self.client.post("/api/asistente/chat", json=payload, headers=headers)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data.get("success"))
        print(f"\n[Test 4] Respuesta a Admin: {data['respuesta'][:120]}... (Tipo: {data.get('tipo')})")

if __name__ == "__main__":
    unittest.main()
