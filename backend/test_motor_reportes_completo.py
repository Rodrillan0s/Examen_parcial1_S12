import unittest
import io
from fastapi.testclient import TestClient

from app import create_app
from app.utils.security import create_access_token
from app.reports.engine.catalog import CATALOGO_REPORTES
from app.reports.engine.report_engine import (
    ejecutar_reporte_dinamico,
    generar_pdf_reporte_dinamico
)
from app.reports.parser.command_parser import interpretar_comando_reporte

class TestMotorReportesDinamico(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.client = TestClient(cls.app)
        cls.token = create_access_token(
            nro_usuario=1,
            username='admin',
            id_rol=1,
            id_empresa=1,
            nombre='Admin',
            apellido='Aurora',
            roles=['ADMINISTRADOR']
        )
        cls.headers = {'Authorization': f'Bearer {cls.token}'}
        cls.token_data = {
            'id_empresa': 1,
            'rol': 'ADMINISTRADOR',
            'nombre': 'Admin',
            'apellido': 'Aurora'
        }

    # --------------------------------------------------------------------------
    # 1. PARSER DETERMINISTA (SIN IA NI TOKENS)
    # --------------------------------------------------------------------------
    def test_01_parser_ventas_con_agrupacion_y_fecha(self):
        cmd = "Dame las ventas de esta semana por sucursal"
        res = interpretar_comando_reporte(cmd, id_empresa=1)
        self.assertTrue(res['valido'])
        req = res['report_request']
        self.assertEqual(req['tipo_reporte'], 'ventas')
        self.assertEqual(req['groupBy'], 'sucursal')
        self.assertIn('fechaDesde', req['filtros'])
        self.assertIn('fechaHasta', req['filtros'])

    def test_02_parser_inventario_agotado(self):
        cmd = "Dame el inventario de prendas agotadas"
        res = interpretar_comando_reporte(cmd, id_empresa=1)
        self.assertTrue(res['valido'])
        req = res['report_request']
        self.assertEqual(req['tipo_reporte'], 'inventario')
        self.assertEqual(req['filtros'].get('estadoStock'), 'agotado')

    def test_03_parser_resolucion_entidad_sucursal(self):
        cmd = "Ventas de la sucursal Equipetrol"
        res = interpretar_comando_reporte(cmd, id_empresa=1)
        self.assertTrue(res['valido'])
        self.assertEqual(res['report_request']['tipo_reporte'], 'ventas')
        self.assertIsNotNone(res['report_request']['filtros'].get('sucursalId'))

    # --------------------------------------------------------------------------
    # 2. EJECUCIÓN DINÁMICA DE REPORTES SOBRE VISTAS SQL
    # --------------------------------------------------------------------------
    def test_04_ejecutar_reporte_ventas_detalle(self):
        req = {'tipo_reporte': 'ventas', 'filtros': {}}
        res = ejecutar_reporte_dinamico(req, self.token_data)
        self.assertEqual(res['tipo_reporte'], 'ventas')
        self.assertGreater(len(res['items']), 0)
        self.assertIn('total_monto', res['resumen'])
        self.assertGreater(res['resumen']['total_monto'], 0)

    def test_05_ejecutar_reporte_con_group_by(self):
        req = {
            'tipo_reporte': 'ventas',
            'groupBy': 'sucursal',
            'filtros': {}
        }
        res = ejecutar_reporte_dinamico(req, self.token_data)
        self.assertEqual(res['groupBy'], 'sucursal')
        campos = [c['campo'] for c in res['columnas']]
        self.assertIn('sucursal', campos)
        self.assertIn('cantidad_registros', campos)
        self.assertIn('total_monto', campos)

    def test_06_ejecutar_todos_los_reportes_del_catalogo(self):
        for codigo in CATALOGO_REPORTES:
            req = {'tipo_reporte': codigo, 'filtros': {}}
            res = ejecutar_reporte_dinamico(req, self.token_data)
            self.assertIn('items', res)
            self.assertIn('resumen', res)
            self.assertIn('columnas', res)

    # --------------------------------------------------------------------------
    # 3. GENERACIÓN DE PDF PROFESIONAL CON REPORTLAB
    # --------------------------------------------------------------------------
    def test_07_generar_pdf_reportlab(self):
        req = {'tipo_reporte': 'ventas', 'filtros': {}}
        datos = ejecutar_reporte_dinamico(req, self.token_data)
        pdf_buf = generar_pdf_reporte_dinamico(datos, self.token_data)
        self.assertIsInstance(pdf_buf, io.BytesIO)
        pdf_bytes = pdf_buf.getvalue()
        self.assertTrue(pdf_bytes.startswith(b'%PDF-'))
        self.assertGreater(len(pdf_bytes), 1000)

    # --------------------------------------------------------------------------
    # 4. ENDPOINTS REST FASTAPI
    # --------------------------------------------------------------------------
    def test_08_api_catalogo(self):
        resp = self.client.get('/api/motor-reportes/catalogo', headers=self.headers)
        self.assertEqual(resp.status_code, 200)
        json_data = resp.json()
        self.assertTrue(json_data['success'])
        self.assertEqual(json_data['total'], len(CATALOGO_REPORTES))

    def test_09_api_parse_command(self):
        payload = {'command': 'Ventas de hoy por sucursal'}
        resp = self.client.post('/api/motor-reportes/parse-command', headers=self.headers, json=payload)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data['success'])
        self.assertTrue(data['valido'])
        self.assertEqual(data['report_request']['tipo_reporte'], 'ventas')
        self.assertEqual(data['report_request']['groupBy'], 'sucursal')

    def test_10_api_ejecutar(self):
        payload = {
            'tipo_reporte': 'inventario',
            'filtros': {'estadoStock': 'agotado'}
        }
        resp = self.client.post('/api/motor-reportes/ejecutar', headers=self.headers, json=payload)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data['success'])
        self.assertIn('items', data['data'])
        self.assertIn('resumen', data['data'])

    def test_11_api_exportar_pdf_streaming(self):
        payload = {
            'tipo_reporte': 'ventas',
            'filtros': {}
        }
        resp = self.client.post('/api/motor-reportes/exportar/pdf', headers=self.headers, json=payload)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.headers.get('content-type'), 'application/pdf')
        self.assertTrue(resp.content.startswith(b'%PDF-'))


if __name__ == '__main__':
    unittest.main()
