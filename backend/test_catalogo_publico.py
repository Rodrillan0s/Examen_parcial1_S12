import unittest
from fastapi.testclient import TestClient
from app import create_app

class TestCatalogoPublico(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.client = TestClient(cls.app)

    def test_01_acceso_publico_sin_token(self):
        """Verifica que el catálogo público responde 200 OK sin requerir cabecera Authorization."""
        resp = self.client.get('/api/catalogo/productos')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data.get('success'))
        self.assertIn('data', data)
        self.assertIn('total', data)
        self.assertIn('empresa', data)

    def test_02_listar_tenants_publicos(self):
        """Verifica que se listen las tiendas activas para selección pública."""
        resp = self.client.get('/api/catalogo/tenants')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data.get('success'))
        self.assertGreaterEqual(len(data.get('data', [])), 1)

    def test_03_filtros_disponibles_por_tenant(self):
        """Verifica la obtención dinámica de categorías, tallas, colores, temporadas y colecciones."""
        resp = self.client.get('/api/catalogo/filtros?id_empresa=1')
        self.assertEqual(resp.status_code, 200)
        d = resp.json().get('data', {})
        self.assertIn('categorias', d)
        self.assertIn('tallas', d)
        self.assertIn('colores', d)
        self.assertIn('temporadas', d)
        self.assertIn('colecciones', d)

    def test_04_busqueda_por_nombre(self):
        """Verifica que la búsqueda por término filtre adecuadamente."""
        resp = self.client.get('/api/catalogo/productos?id_empresa=1&busqueda=abrigo')
        self.assertEqual(resp.status_code, 200)
        prods = resp.json().get('data', [])
        for p in prods:
            self.assertTrue('abrigo' in p['nombre'].lower() or 'abrigo' in p['descripcion'].lower() or 'abrigo' in p['categoria_nombre'].lower())

    def test_05_ordenamiento_por_precio(self):
        """Verifica el ordenamiento ascendente y descendente por precio."""
        resp_asc = self.client.get('/api/catalogo/productos?id_empresa=1&orden=precio_asc')
        self.assertEqual(resp_asc.status_code, 200)
        prods_asc = resp_asc.json().get('data', [])
        precios_asc = [p['precio'] for p in prods_asc]
        self.assertEqual(precios_asc, sorted(precios_asc))

        resp_desc = self.client.get('/api/catalogo/productos?id_empresa=1&orden=precio_desc')
        self.assertEqual(resp_desc.status_code, 200)
        prods_desc = resp_desc.json().get('data', [])
        precios_desc = [p['precio'] for p in prods_desc]
        self.assertEqual(precios_desc, sorted(precios_desc, reverse=True))

    def test_06_detalle_producto_publico_con_stock(self):
        """Verifica que el detalle de producto retorne variantes y disponibilidad por sucursal."""
        # Consultar producto 7 (Abrigo Midi)
        resp = self.client.get('/api/catalogo/productos/7')
        self.assertEqual(resp.status_code, 200)
        d = resp.json().get('data', {})
        self.assertEqual(d.get('id_producto'), 7)
        self.assertIn('variantes', d)
        self.assertIn('sucursales_stock', d)
        self.assertTrue(d.get('permite_reserva'))
        self.assertTrue(d.get('permite_compra'))

        # Verificar que las sucursales tengan información de horario y stock
        sucs = d.get('sucursales_stock', [])
        self.assertGreaterEqual(len(sucs), 1)
        for s in sucs:
            self.assertIn('nombre', s)
            self.assertIn('stock_total_sucursal', s)
            self.assertIn('horario', s)

    def test_07_producto_inexistente_retorna_404(self):
        """Verifica que un ID inválido retorne 404 Not Found."""
        resp = self.client.get('/api/catalogo/productos/999999')
        self.assertEqual(resp.status_code, 404)

if __name__ == '__main__':
    unittest.main()
