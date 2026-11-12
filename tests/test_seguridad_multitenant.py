import sys
import unittest
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.core.tenant_guard import (
    resolver_tenant_operacion,
    resolver_sucursal_autorizada,
    validar_acceso_recurso_tenant,
    obtener_alcance_usuario
)
from app.modules.ia.routes.predicciones_routes import _validar_permisos_ia
from app.modules.ia.services import demanda_forecast_services

class TestSeguridadMultitenant(unittest.TestCase):

    def setUp(self):
        self.token_admin_global = {
            "nro_usuario": 1,
            "id_usuario": 1,
            "nombre": "SuperAdmin",
            "alcance": "PLATAFORMA",
            "id_empresa": None,
            "id_sucursal": None,
            "nombre_rol": "ADMINISTRADOR",
            "roles": ["ADMINISTRADOR"],
            "permisos": ["*"]
        }

        self.token_tenant_1 = {
            "nro_usuario": 10,
            "id_usuario": 10,
            "nombre": "Admin Boutique 1",
            "alcance": "EMPRESA",
            "id_empresa": 1,
            "id_sucursal": None,
            "nombre_rol": "ADMINISTRADOR_TIENDA",
            "roles": ["ADMINISTRADOR_TIENDA"],
            "permisos": ["pos.vender", "caja.ver", "reportes.ver", "ia.recomendar"]
        }

        self.token_tenant_2 = {
            "nro_usuario": 20,
            "id_usuario": 20,
            "nombre": "Admin Boutique 2",
            "alcance": "EMPRESA",
            "id_empresa": 2,
            "id_sucursal": None,
            "nombre_rol": "ADMINISTRADOR_TIENDA",
            "roles": ["ADMINISTRADOR_TIENDA"],
            "permisos": ["pos.vender", "caja.ver", "reportes.ver"]
        }

        self.token_cajero_suc1 = {
            "nro_usuario": 30,
            "id_usuario": 30,
            "nombre": "Cajero Sucursal 1",
            "alcance": "SUCURSAL",
            "id_empresa": 1,
            "id_sucursal": 1,
            "nombre_rol": "CAJERO",
            "roles": ["CAJERO"],
            "permisos": ["pos.vender", "caja.ver"]
        }

        self.token_cliente = {
            "nro_usuario": 99,
            "id_usuario": 99,
            "nombre": "Cliente Común",
            "alcance": "CLIENTE",
            "id_empresa": None,
            "id_sucursal": None,
            "nombre_rol": "CLIENTE",
            "roles": ["CLIENTE"],
            "permisos": ["catalogo.ver"]
        }

    def test_resolver_tenant_inviolable(self):
        """Un usuario de Tenant 1 nunca puede fijar id_empresa de Tenant 2."""
        # Intenta inyectar id_empresa=2 siendo de Tenant 1 -> Debe lanzar 403 Violación de Tenant
        with self.assertRaises(HTTPException) as ctx:
            resolver_tenant_operacion(self.token_tenant_1, id_empresa_solicitado=2)
        self.assertEqual(ctx.exception.status_code, 403)

    def test_acceso_recurso_cruzado_denegado(self):
        """validar_acceso_recurso_tenant debe arrojar 403 cuando el recurso es de otro tenant."""
        with self.assertRaises(HTTPException) as ctx:
            validar_acceso_recurso_tenant(self.token_tenant_1, id_empresa_recurso=2, nombre_recurso="venta")
        self.assertEqual(ctx.exception.status_code, 403)

    def test_acceso_recurso_propio_permitido(self):
        """validar_acceso_recurso_tenant debe permitir acceso si el recurso pertenece al tenant."""
        try:
            validar_acceso_recurso_tenant(self.token_tenant_1, id_empresa_recurso=1, nombre_recurso="venta")
        except HTTPException:
            self.fail("No debió lanzar excepción al acceder a recurso propio.")

    def test_admin_global_accede_recursos_con_contexto(self):
        """Admin global puede acceder a cualquier tenant explícito."""
        try:
            validar_acceso_recurso_tenant(self.token_admin_global, id_empresa_recurso=2, nombre_recurso="venta")
        except HTTPException:
            self.fail("Admin global debe poder acceder a recursos de cualquier tenant.")

    def test_restriccion_sucursal_cajero(self):
        """Un cajero de sucursal 1 no puede operar sucursal 2."""
        with self.assertRaises(HTTPException) as ctx:
            resolver_sucursal_autorizada(self.token_cajero_suc1, id_sucursal_solicitada=2)
        self.assertEqual(ctx.exception.status_code, 403)

    def test_ia_permisos_deniega_cliente(self):
        """El rol CLIENTE no tiene acceso a endpoints de predicción IA."""
        with self.assertRaises(HTTPException) as ctx:
            _validar_permisos_ia(self.token_cliente)
        self.assertEqual(ctx.exception.status_code, 403)

    def test_ia_permisos_aisla_tenant(self):
        """Admin de Tenant 1 no puede solicitar predicciones de Tenant 2."""
        with self.assertRaises(HTTPException) as ctx:
            _validar_permisos_ia(self.token_tenant_1, id_empresa_param=2)
        self.assertEqual(ctx.exception.status_code, 403)

    def test_exigir_suscripcion_activa_sin_empresa_deniega_operacion(self):
        """exigir_suscripcion_activa sin ID de empresa lanza 403 SUSCRIPCION_NO_VIGENTE."""
        from app.core.tenant_guard import exigir_suscripcion_activa
        with self.assertRaises(HTTPException) as ctx:
            exigir_suscripcion_activa(None, self.token_tenant_1)
        self.assertEqual(ctx.exception.status_code, 403)
        self.assertEqual(ctx.exception.detail.get("code"), "SUSCRIPCION_NO_VIGENTE")

    def test_exigir_suscripcion_activa_vencida_deniega_operacion(self):
        """CU06W: Empresa sin suscripción activa debe ser restringida de realizar operaciones comerciales."""
        from app.core.tenant_guard import exigir_suscripcion_activa
        from unittest.mock import patch

        with patch("app.modules.saas.services.saas_services.consultar_plan") as mock_plan:
            mock_plan.return_value = {
                "id_empresa": 1,
                "estado": "VENCIDA",
                "vigente": False,
                "capacidades": {"reportes_generativos": False}
            }
            with self.assertRaises(HTTPException) as ctx:
                exigir_suscripcion_activa(1, self.token_tenant_1)
            self.assertEqual(ctx.exception.status_code, 403)
            self.assertEqual(ctx.exception.detail.get("code"), "SUSCRIPCION_NO_VIGENTE")

    def test_exigir_suscripcion_activa_vigente_permite_operacion(self):
        """CU06W: Empresa con suscripción vigente realiza operaciones comerciales sin restricción."""
        from app.core.tenant_guard import exigir_suscripcion_activa
        from unittest.mock import patch

        with patch("app.modules.saas.services.saas_services.consultar_plan") as mock_plan:
            mock_plan.return_value = {
                "id_empresa": 1,
                "estado": "VIGENTE",
                "vigente": True,
                "capacidades": {"reportes_generativos": True}
            }
            # No debe lanzar ninguna excepción
            try:
                exigir_suscripcion_activa(1, self.token_tenant_1)
            except HTTPException:
                self.fail("exigir_suscripcion_activa no debió lanzar excepción para una suscripción VIGENTE.")


if __name__ == "__main__":
    unittest.main()
