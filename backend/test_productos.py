import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.classes.postgres import PostgreSQL
from app.config import Config
from app.services import productos_services
from app.repos import productos_repos

def run_tests():
    print("=== INICIANDO PRUEBAS AUTOMATIZADAS DE PRODUCTOS ===")
    db = PostgreSQL()
    db.create_connection()
    schema = Config.SCHEMA or 'comercio'

    user_row = db.execute_query(f"SELECT id_usuario, correo FROM {schema}.t_usuario LIMIT 1;", fetchone=True)
    real_user_id = user_row[0] if user_row else 3
    real_user_email = user_row[1] if user_row else "admin@aurora.com"

    # Mock tokens
    superadmin_token = {
        "id_usuario": real_user_id,
        "email": real_user_email,
        "alcance": "PLATAFORMA",
        "id_empresa": 1
    }

    try:
        # Obtener una categoría activa del tenant 1
        cat_row = db.execute_query(
            f"SELECT id_categoria, nombre FROM {schema}.t_categoria WHERE id_empresa = 1 AND activo = TRUE LIMIT 1;",
            fetchone=True
        )
        if not cat_row:
            print("Creando categoría activa de prueba...")
            cat_id = db.execute_query(
                f"INSERT INTO {schema}.t_categoria (nombre, id_empresa, activo, estado) VALUES ('Categoría Test Moda', 1, TRUE, TRUE) RETURNING id_categoria;",
                fetchone=True, commit=True
            )[0]
        else:
            cat_id = cat_row[0]

        # Obtener 2 tallas activas del tenant 1
        tallas_rows = db.execute_query(
            f"SELECT id_talla, nombre FROM {schema}.t_talla WHERE id_empresa = 1 AND activo = TRUE LIMIT 2;",
            fetchall=True
        )
        tallas_ids = [t[0] for t in tallas_rows]

        # Obtener 3 colores activos del tenant 1
        colores_rows = db.execute_query(
            f"SELECT id_color, nombre FROM {schema}.t_color WHERE id_empresa = 1 AND activo = TRUE LIMIT 3;",
            fetchall=True
        )
        colores_ids = [c[0] for c in colores_rows]

        print(f"Usando categoría ID {cat_id}, Tallas: {tallas_ids}, Colores: {colores_ids}")

        # PRUEBA 1: Listar productos
        print("\n--- PRUEBA 1: Listar productos ---")
        prods = productos_services.listar_productos_service(superadmin_token, id_empresa=1)
        print(f"Productos listados actualmente: {len(prods)}")
        assert isinstance(prods, list), "El resultado debe ser una lista"
        print("✔ Prueba 1 superada.")

        # PRUEBA 2: Crear producto con variantes (2 tallas x 3 colores = 6 combinaciones)
        print("\n--- PRUEBA 2: Crear producto y generar variantes ---")
        nombre_test = "Vestido Test Gala Seda"
        # Limpiar si existía de prueba previa
        id_antiguo = db.execute_query(
            f"SELECT id_producto FROM {schema}.t_producto WHERE nombre = %s AND id_empresa = 1;",
            (nombre_test,), fetchone=True
        )
        if id_antiguo:
            productos_repos.eliminar_producto_seguro(id_antiguo[0])

        datos_nuevo = {
            "id_empresa": 1,
            "id_categoria": cat_id,
            "nombre": nombre_test,
            "descripcion": "Vestido de noche en seda de alta costura.",
            "precio": 1250.0,
            "temporada": "Otoño 2026",
            "coleccion": "Gala Exclusiva",
            "tallas_ids": tallas_ids,
            "colores_ids": colores_ids,
            "activo": True
        }
        res_crear = productos_services.crear_producto_service(datos_nuevo, superadmin_token)
        assert res_crear["success"] is True, "Creación debió ser exitosa"
        id_prod = res_crear["id_producto"]
        print(f"✔ Producto creado con ID: {id_prod}")

        # Comprobar variantes
        prod_det = productos_services.obtener_producto_service(id_prod, superadmin_token)
        variantes = prod_det["variantes"]
        print(f"Variantes generadas: {len(variantes)} (esperadas: {len(tallas_ids) * len(colores_ids)})")
        assert len(variantes) == len(tallas_ids) * len(colores_ids), "Las combinaciones generadas deben coincidir exactamente"
        print("✔ Prueba 2 superada.")

        # PRUEBA 3: Unicidad de nombre por Tenant
        print("\n--- PRUEBA 3: Validación de unicidad de nombre en el Tenant ---")
        try:
            productos_services.crear_producto_service(datos_nuevo, superadmin_token)
            assert False, "Debió lanzar excepción por nombre duplicado"
        except Exception as e:
            print(f"✔ Excepción esperada capturada: {e.detail if hasattr(e, 'detail') else e}")
        print("✔ Prueba 3 superada.")

        # PRUEBA 4: Gestión de Imágenes (Agregar y Portada)
        print("\n--- PRUEBA 4: Galería de Imágenes ---")
        img1 = productos_repos.agregar_imagen_producto(
            id_producto=id_prod,
            imagen_url="https://res.cloudinary.com/demo/image/upload/sample.jpg",
            public_id="sample_test_1",
            es_principal=True
        )
        img2 = productos_repos.agregar_imagen_producto(
            id_producto=id_prod,
            imagen_url="https://res.cloudinary.com/demo/image/upload/sample2.jpg",
            public_id="sample_test_2",
            es_principal=False
        )
        det_img = productos_services.obtener_producto_service(id_prod, superadmin_token)
        assert len(det_img["imagenes"]) == 2, "Debe tener 2 imágenes"
        assert det_img["imagen_principal"] == "https://res.cloudinary.com/demo/image/upload/sample.jpg", "La principal debe ser la portada"
        print("✔ 2 imágenes vinculadas correctamente a la galería.")

        # Cambiar portada a la segunda
        productos_repos.marcar_imagen_principal(img2, id_prod)
        det_img2 = productos_services.obtener_producto_service(id_prod, superadmin_token)
        assert det_img2["imagen_principal"] == "https://res.cloudinary.com/demo/image/upload/sample2.jpg", "Portada debe actualizarse a img2"
        print("✔ Cambio de portada verificado.")

        # Eliminar una imagen
        pub_id_borrado = productos_repos.eliminar_imagen_producto(img1, id_prod)
        assert pub_id_borrado == "sample_test_1", "Debe retornar el public_id borrado"
        det_img3 = productos_services.obtener_producto_service(id_prod, superadmin_token)
        assert len(det_img3["imagenes"]) == 1, "Debe quedar 1 imagen"
        print("✔ Eliminación de imagen verificada.")

        # PRUEBA 5: Cambiar estado Activo / Inactivo y filtro solo_activos
        print("\n--- PRUEBA 5: Alternar estado y filtro solo_activos ---")
        productos_services.cambiar_estado_service(id_prod, activo=False, token_data=superadmin_token)
        lista_activas = productos_services.listar_productos_service(superadmin_token, id_empresa=1, solo_activos=True)
        assert not any(p["id_producto"] == id_prod for p in lista_activas), "El producto inactivo no debe aparecer con solo_activos=true"
        print("✔ Ocultamiento de producto inactivo verificado.")

        # Reactivar
        productos_services.cambiar_estado_service(id_prod, activo=True, token_data=superadmin_token)

        # PRUEBA 6: Sincronización de Variantes en Edición
        print("\n--- PRUEBA 6: Actualizar producto y sincronizar variantes ---")
        # Dejar solo 1 talla y 1 color
        datos_edit = {
            "nombre": nombre_test + " Edición Limitada",
            "id_categoria": cat_id,
            "precio": 1399.0,
            "tallas_ids": [tallas_ids[0]],
            "colores_ids": [colores_ids[0]],
            "activo": True
        }
        res_act = productos_services.actualizar_producto_service(id_prod, datos_edit, superadmin_token)
        assert res_act["success"] is True
        det_edit = productos_services.obtener_producto_service(id_prod, superadmin_token)
        vars_activas = [v for v in det_edit["variantes"] if v["activo"]]
        assert len(vars_activas) == 1, "Solo 1 variante debe quedar activa"
        print("✔ Sincronización de variantes en edición verificada.")

        # PRUEBA 7: Eliminación limpia
        print("\n--- PRUEBA 7: Eliminación limpia sin inventario ---")
        res_del = productos_services.eliminar_producto_service(id_prod, superadmin_token)
        assert res_del["action"] == "ELIMINADO"
        assert productos_repos.obtener_producto_por_id(id_prod) is None
        print("✔ Eliminación limpia verificada.")

        print("\n========================================================")
        print("✅ TODAS LAS 7 PRUEBAS DE PRODUCTOS PASARON CON ÉXITO")
        print("========================================================")
    finally:
        db.close_connection()

if __name__ == '__main__':
    run_tests()
