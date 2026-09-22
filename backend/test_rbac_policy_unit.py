import unittest

from fastapi import HTTPException

from app.utils.security import require_platform_admin, tiene_permiso
from app.utils.tenant_guard import resolver_sucursal_autorizada


class TestRbacPolicyUnit(unittest.TestCase):
    def test_permission_is_read_from_jwt(self):
        payload = {"id_usuario": 10, "permisos": ["productos.ver"]}
        self.assertTrue(tiene_permiso(payload, "productos.ver"))
        self.assertFalse(tiene_permiso(payload, "productos.eliminar"))

    def test_platform_admin_requires_global_scope(self):
        payload = {
            "id_usuario": 1,
            "id_rol": 1,
            "nombre_rol": "ADMINISTRADOR",
            "roles": ["ADMINISTRADOR"],
            "alcance": "PLATAFORMA",
            "id_empresa": None,
        }
        self.assertIs(require_platform_admin(payload), payload)

    def test_tenant_admin_is_not_platform_admin(self):
        payload = {
            "id_usuario": 2,
            "id_rol": 1,
            "nombre_rol": "ADMINISTRADOR",
            "roles": ["ADMINISTRADOR"],
            "alcance": "EMPRESA",
            "id_empresa": 1,
        }
        with self.assertRaises(HTTPException) as error:
            require_platform_admin(payload)
        self.assertEqual(error.exception.status_code, 403)

    def test_platform_branch_request_does_not_use_jwt_branch_list(self):
        payload = {"alcance": "PLATAFORMA", "sucursales": [1]}
        self.assertEqual(resolver_sucursal_autorizada(payload, 7), 7)

    def test_branch_scope_without_company_is_denied(self):
        payload = {"alcance": "SUCURSAL", "id_usuario": 5}
        with self.assertRaises(HTTPException) as error:
            resolver_sucursal_autorizada(payload, 1)
        self.assertEqual(error.exception.status_code, 403)


if __name__ == "__main__":
    unittest.main()
