import sys
import os
import requests

BASE_URL = "http://127.0.0.1:5000"

def log_test(name: str, passed: bool, detail: str = ""):
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status} | {name}")
    if detail:
        print(f"       -> {detail}")

def run_tests():
    print("=" * 70)
    print("VERIFICACIÓN DE REGLAS DE ACCESO: ADMINISTRADOR vs ADMINISTRADOR_TIENDA")
    print("=" * 70)

    from app.classes.postgres import PostgreSQL
    from app.utils.security import hash_password
    from app.config import Config

    schema = Config.SCHEMA or 'comercio'
    db = PostgreSQL()
    db.create_connection()
    try:
        # Asegurar credenciales y resetear intentos para eddyst
        pw_hash = hash_password("Password123!")
        db.execute_query(
            f"UPDATE {schema}.t_usuario SET password_hash = %s, estado = TRUE WHERE username = 'eddyst';",
            (pw_hash,),
            commit=True
        )
        db.execute_query(
            f"UPDATE {schema}.t_seguridad_usuario SET intentos_fallidos = 0, bloqueado_hasta = NULL WHERE id_usuario = (SELECT id_usuario FROM {schema}.t_usuario WHERE username = 'eddyst');",
            commit=True
        )

        # Asegurar usuario Administrador de Tienda (id_empresa=1, id_rol=3)
        res_t = db.execute_query(
            f"SELECT id_usuario FROM {schema}.t_usuario WHERE LOWER(username) = 'tienda_admin1';",
            fetchone=True
        )
        if not res_t:
            db.execute_query(
                f"""
                INSERT INTO {schema}.t_usuario (
                    correo, username, password_hash, nombre, apellido, telefono, 
                    estado, id_empresa, id_rol
                ) VALUES (
                    'admin1@aurora.bo', 'tienda_admin1', %s, 'Admin', 'Tienda 1', '77000001',
                    TRUE, 1, 3
                );
                """,
                (pw_hash,),
                commit=True
            )
            res_t = db.execute_query(
                f"SELECT id_usuario FROM {schema}.t_usuario WHERE username = 'tienda_admin1';",
                fetchone=True
            )
            id_t = res_t[0]
            db.execute_query(
                f"INSERT INTO {schema}.t_seguridad_usuario (id_usuario, intentos_fallidos) VALUES (%s, 0) ON CONFLICT DO NOTHING;",
                (id_t,),
                commit=True
            )
        else:
            id_t = res_t[0]
            db.execute_query(
                f"UPDATE {schema}.t_usuario SET password_hash = %s, id_empresa = 1, id_rol = 3, estado = TRUE WHERE id_usuario = %s;",
                (pw_hash, id_t),
                commit=True
            )
            db.execute_query(
                f"UPDATE {schema}.t_seguridad_usuario SET intentos_fallidos = 0, bloqueado_hasta = NULL WHERE id_usuario = %s;",
                (id_t,),
                commit=True
            )
    finally:
        db.close_connection()

    # 1. Login Global SuperAdmin (eddyst)
    login_admin = requests.post(f"{BASE_URL}/api/auth/login", json={
        "username": "eddyst",
        "password": "Password123!"
    })
    if login_admin.status_code != 200:
        print("Error: No se pudo autenticar usuario eddyst:", login_admin.text)
        return

    admin_data = login_admin.json()
    token_admin = admin_data.get("token")
    headers_admin = {"Authorization": f"Bearer {token_admin}"}

    usuario_admin = admin_data.get("usuario", {})
    log_test(
        "SuperAdmin Global tiene alcance PLATAFORMA e id_empresa None",
        usuario_admin.get("alcance") == "PLATAFORMA" and usuario_admin.get("id_empresa") is None,
        f"alcance={usuario_admin.get('alcance')}, id_empresa={usuario_admin.get('id_empresa')}"
    )

    # Login Administrador de Tienda (Empresa 1)
    login_tienda = requests.post(f"{BASE_URL}/api/auth/login", json={
        "username": "tienda_admin1",
        "password": "Password123!"
    })
    if login_tienda.status_code != 200:
        print("Error: No se pudo autenticar tienda_admin1:", login_tienda.text)
        return

    tienda_data = login_tienda.json()
    token_tienda = tienda_data.get("token")
    headers_tienda = {"Authorization": f"Bearer {token_tienda}"}
    usuario_tienda = tienda_data.get("usuario", {})

    log_test(
        "Administrador de Tienda tiene alcance EMPRESA e id_empresa=1",
        usuario_tienda.get("alcance") == "EMPRESA" and usuario_tienda.get("id_empresa") == 1,
        f"alcance={usuario_tienda.get('alcance')}, id_empresa={usuario_tienda.get('id_empresa')}"
    )

    # --------------------------------------------------------------------------
    # 3. AISLAMIENTO DE TENANTS (EMPRESAS)
    # --------------------------------------------------------------------------
    # Global Admin lista empresas: debe ver todas
    r_emp_admin = requests.get(f"{BASE_URL}/api/empresas/", headers=headers_admin)
    log_test(
        "SuperAdmin puede listar todos los Tenants del sistema",
        r_emp_admin.status_code == 200 and len(r_emp_admin.json().get("data", [])) >= 2,
        f"Tenants recuperados: {len(r_emp_admin.json().get('data', []))}"
    )

    # Store Admin lista empresas: SOLO debe ver la suya (id_empresa=1)
    r_emp_tienda = requests.get(f"{BASE_URL}/api/empresas/", headers=headers_tienda)
    empresas_visibles = r_emp_tienda.json().get("data", [])
    log_test(
        "Admin Tienda SOLO ve su propio Tenant al listar empresas",
        r_emp_tienda.status_code == 200 and len(empresas_visibles) == 1 and empresas_visibles[0]["id_empresa"] == 1,
        f"Tenants visibles: {[e['id_empresa'] for e in empresas_visibles]}"
    )

    # Store Admin consulta su empresa: 200 OK
    r_emp1 = requests.get(f"{BASE_URL}/api/empresas/1", headers=headers_tienda)
    log_test("Admin Tienda puede consultar su propia empresa (ID: 1)", r_emp1.status_code == 200)

    # Store Admin intenta consultar la empresa de otro Tenant (ID: 2): DEBE RECHAZAR CON 403
    r_emp2 = requests.get(f"{BASE_URL}/api/empresas/2", headers=headers_tienda)
    log_test(
        "Admin Tienda recibe 403 Forbidden al consultar empresa ajena (ID: 2)",
        r_emp2.status_code == 403,
        f"Código devuelto: {r_emp2.status_code} - {r_emp2.text}"
    )

    # --------------------------------------------------------------------------
    # 4. AISLAMIENTO DE SUCURSALES
    # --------------------------------------------------------------------------
    # Store Admin consulta sucursales con id_empresa=1: 200 OK
    r_suc1 = requests.get(f"{BASE_URL}/api/sucursales/?id_empresa=1", headers=headers_tienda)
    log_test("Admin Tienda consulta sus sucursales autorizadas (id_empresa=1)", r_suc1.status_code == 200)

    # Store Admin intenta consultar sucursales de empresa 2 en la URL: 403 Forbidden
    r_suc2 = requests.get(f"{BASE_URL}/api/sucursales/?id_empresa=2", headers=headers_tienda)
    log_test(
        "Admin Tienda recibe 403 Forbidden al intentar listar sucursales de Tenant ajeno (?id_empresa=2)",
        r_suc2.status_code == 403,
        f"Código devuelto: {r_suc2.status_code}"
    )

    # Store Admin intenta registrar una sucursal para empresa 2 en el cuerpo: 403 Forbidden
    r_create_suc = requests.post(f"{BASE_URL}/api/sucursales/", headers=headers_tienda, json={
        "id_empresa": 2,
        "nombre_sucursal": "Sucursal Ilegal Cross Tenant",
        "direccion": "Av. Prohibida 123",
        "telefono": "77112233",
        "id_ciudad": 1,
        "es_casa_matriz": False
    })
    log_test(
        "Admin Tienda recibe 403 Forbidden al intentar crear sucursal en Tenant ajeno",
        r_create_suc.status_code == 403,
        f"Código devuelto: {r_create_suc.status_code} - {r_create_suc.text}"
    )

    # --------------------------------------------------------------------------
    # 5. AISLAMIENTO DE USUARIOS
    # --------------------------------------------------------------------------
    # Store Admin intenta listar usuarios de empresa 2: 403 Forbidden
    r_usr_ajeno = requests.get(f"{BASE_URL}/api/usuarios/?id_empresa=2", headers=headers_tienda)
    log_test(
        "Admin Tienda recibe 403 Forbidden al intentar listar usuarios de Tenant ajeno (?id_empresa=2)",
        r_usr_ajeno.status_code == 403,
        f"Código devuelto: {r_usr_ajeno.status_code}"
    )

    # --------------------------------------------------------------------------
    # 6. JERARQUÍA RBAC Y ASIGNACIÓN DE ROLES
    # --------------------------------------------------------------------------
    # Store Admin consulta roles delegables: NO debe incluir ADMINISTRADOR (id_rol=1, jerarquia < 3)
    r_roles_del = requests.get(f"{BASE_URL}/api/rbac/roles-delegables", headers=headers_tienda)
    if r_roles_del.status_code == 200:
        roles_del = r_roles_del.json().get("roles", [])
        nombres_roles = [r["nombre"].upper() for r in roles_del]
        tiene_superadmin = "ADMINISTRADOR" in nombres_roles or any(r.get("nivel_jerarquia", 99) < 3 for r in roles_del)
        log_test(
            "Roles delegables para Admin Tienda NO incluyen ADMINISTRADOR ni niveles superiores",
            not tiene_superadmin and len(roles_del) > 0,
            f"Roles delegables disponibles: {nombres_roles}"
        )
    else:
        log_test("Consulta de roles delegables", False, f"Status: {r_roles_del.status_code}")

    # --------------------------------------------------------------------------
    # 7. AISLAMIENTO DE CATEGORÍAS, TALLAS Y COLORES
    # --------------------------------------------------------------------------
    # Store Admin intenta listar categorías de Empresa 2: 403 Forbidden
    r_cat_ajena = requests.get(f"{BASE_URL}/api/categorias/?id_empresa=2", headers=headers_tienda)
    log_test(
        "Admin Tienda recibe 403 Forbidden al consultar categorías de Tenant ajeno (?id_empresa=2)",
        r_cat_ajena.status_code == 403,
        f"Código devuelto: {r_cat_ajena.status_code}"
    )

    # Store Admin intenta registrar categoría con id_empresa=2 en el payload: 403 Forbidden
    r_create_cat = requests.post(f"{BASE_URL}/api/categorias/", headers=headers_tienda, json={
        "id_empresa": 2,
        "nombre": "Categoría No Autorizada",
        "descripcion": "Intento cross-tenant"
    })
    log_test(
        "Admin Tienda recibe 403 Forbidden al registrar categoría para Tenant ajeno",
        r_create_cat.status_code == 403,
        f"Código devuelto: {r_create_cat.status_code}"
    )

    # --------------------------------------------------------------------------
    # 8. AISLAMIENTO DE PRODUCTOS Y VALIDACIÓN DE RELACIONES CROSS-TENANT
    # --------------------------------------------------------------------------
    # Primero obtenemos una categoría existente de Empresa 2 (como SuperAdmin)
    r_cat_emp2 = requests.get(f"{BASE_URL}/api/categorias/?id_empresa=2", headers=headers_admin)
    cats_emp2 = r_cat_emp2.json().get("data", [])
    id_cat_emp2 = None
    if cats_emp2:
        id_cat_emp2 = cats_emp2[0]["id_categoria"]
    else:
        # Creamos una categoría en empresa 2 como SuperAdmin
        r_new_cat2 = requests.post(f"{BASE_URL}/api/categorias/", headers=headers_admin, json={
            "id_empresa": 2,
            "nombre": "Gala Exclusiva Emp 2",
            "descripcion": "Categoría propia de Empresa 2"
        })
        if r_new_cat2.status_code in [200, 201]:
            id_cat_emp2 = r_new_cat2.json().get("id_categoria")

    # Store Admin de Empresa 1 intenta crear un producto en Empresa 1 asociando la categoría de Empresa 2!
    if id_cat_emp2:
        r_cross_prod = requests.post(f"{BASE_URL}/api/productos/", headers=headers_tienda, json={
            "id_empresa": 1,
            "id_categoria": id_cat_emp2,  # Categoría ajena!
            "nombre": "Vestido Intruso Cross-Tenant",
            "precio": 450.00,
            "descripcion": "Violación intencional de relaciones",
            "tallas_ids": [],
            "colores_ids": []
        })
        log_test(
            "Validación de relaciones: Rechaza producto de Empresa 1 con categoría de Empresa 2 (403)",
            r_cross_prod.status_code == 403,
            f"Código devuelto: {r_cross_prod.status_code} - {r_cross_prod.text}"
        )
    else:
        print("Aviso: No se pudo obtener categoría de Empresa 2 para prueba de relaciones.")

    # Store Admin intenta consultar productos de empresa 2 en la query: 403 Forbidden
    r_prod_emp2 = requests.get(f"{BASE_URL}/api/productos/?id_empresa=2", headers=headers_tienda)
    log_test(
        "Admin Tienda recibe 403 Forbidden al consultar productos de Tenant ajeno (?id_empresa=2)",
        r_prod_emp2.status_code == 403,
        f"Código devuelto: {r_prod_emp2.status_code}"
    )

    print("=" * 70)
    print("TODAS LAS PRUEBAS DE ACCESO Y SEPARACIÓN DE TENANTS FINALIZADAS.")
    print("=" * 70)

if __name__ == "__main__":
    run_tests()
