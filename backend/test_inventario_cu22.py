"""
Suite de Pruebas Obligatorias para W22 - CU22: Gestionar Inventario
Verifica:
1. Entrada de inventario
2. Salida de inventario
3. Ajuste de inventario
4. Rechazo por stock insuficiente (respetando reservas)
5. Rechazo por intento de stock negativo
6. Rechazo por inventario inexistente
7. Aislamiento multi-tenant: Bloqueo de sucursal de otro tenant
8. Aislamiento multi-tenant: Bloqueo de variante de otro tenant
9. Registro correcto del movimiento en t_movimiento_inventario
10. Conservación inviolable de stock_reservado
11. Concurrencia atómica con último producto disponible (FOR UPDATE)
12. Rollback y atomicidad ante error
"""

import concurrent.futures
import time
import sys
from typing import Dict, Any
from app.classes.postgres import PostgreSQL
from app.config import Config
from app.repos import inventario_repos
from app.utils.security import create_access_token

def _get_schema():
    return Config.SCHEMA or 'comercio'

def print_result(test_name: str, passed: bool, details: str = ""):
    icon = "✅" if passed else "❌"
    print(f"{icon} [{test_name}]: {'PASÓ' if passed else 'FALLÓ'} - {details}")
    if not passed:
        raise AssertionError(f"Test fallido: {test_name} - {details}")

def setup_test_data(db: PostgreSQL) -> Dict[str, Any]:
    """
    Crea o reutiliza datos controlados para las pruebas en schema comercio.
    """
    schema = _get_schema()
    
    # 1. Asegurar empresa 2 existe
    db.execute_query(f"""
        INSERT INTO {schema}.empresa (id_empresa, nombre_empresa, nit, estado)
        VALUES (2, 'EMPRESA TEST TENANT 2', '987654321', 'ACTIVO')
        ON CONFLICT (id_empresa) DO NOTHING;
    """, commit=True)

    # 2. Asegurar sucursal de tenant 1 y sucursal de tenant 2
    res_suc1 = db.execute_query(f"SELECT id_sucursal FROM {schema}.t_sucursal WHERE id_empresa = 1 LIMIT 1;", fetchone=True)
    if not res_suc1:
        res_suc1 = db.execute_query(f"""
            INSERT INTO {schema}.t_sucursal (nombre, id_empresa, direccion, activo)
            VALUES ('Sucursal Test Tenant 1', 1, 'Calle Test 1', TRUE)
            RETURNING id_sucursal;
        """, fetchone=True, commit=True)
    id_sucursal_t1 = res_suc1[0]

    res_suc2 = db.execute_query(f"SELECT id_sucursal FROM {schema}.t_sucursal WHERE id_empresa = 2 LIMIT 1;", fetchone=True)
    if not res_suc2:
        res_suc2 = db.execute_query(f"""
            INSERT INTO {schema}.t_sucursal (nombre, id_empresa, direccion, activo)
            VALUES ('Sucursal Test Tenant 2', 2, 'Calle Test 2', TRUE)
            RETURNING id_sucursal;
        """, fetchone=True, commit=True)
    id_sucursal_t2 = res_suc2[0]

    # 3. Asegurar producto y variante de tenant 1
    res_prod1 = db.execute_query(f"SELECT id_producto FROM {schema}.t_producto WHERE id_empresa = 1 LIMIT 1;", fetchone=True)
    id_producto_t1 = res_prod1[0]

    res_var1 = db.execute_query(f"""
        SELECT ptc.id_variante FROM {schema}.t_producto_talla_color ptc 
        WHERE ptc.id_producto = %s LIMIT 1;
    """, (id_producto_t1,), fetchone=True)
    id_variante_t1 = res_var1[0]

    # 4. Asegurar producto y variante de tenant 2
    res_prod2 = db.execute_query(f"SELECT id_producto FROM {schema}.t_producto WHERE id_empresa = 2 LIMIT 1;", fetchone=True)
    if not res_prod2:
        res_prod2 = db.execute_query(f"""
            INSERT INTO {schema}.t_producto (nombre, codigo_producto, id_empresa, activo, estado)
            VALUES ('Producto Test Tenant 2', 'PROD-T2-01', 2, TRUE, TRUE)
            RETURNING id_producto;
        """, fetchone=True, commit=True)
    id_producto_t2 = res_prod2[0]

    res_var2 = db.execute_query(f"SELECT id_variante FROM {schema}.t_producto_talla_color WHERE id_producto = %s LIMIT 1;", (id_producto_t2,), fetchone=True)
    if not res_var2:
        res_var2 = db.execute_query(f"""
            INSERT INTO {schema}.t_producto_talla_color (id_producto, sku, precio, activo, estado)
            VALUES (%s, 'SKU-T2-TEST', 150.0, TRUE, TRUE)
            RETURNING id_variante;
        """, (id_producto_t2,), fetchone=True, commit=True)
    id_variante_t2 = res_var2[0]

    # 5. Fila controlada de t_inventario para las pruebas en sucursal_t1 + variante_t1
    db.execute_query(f"""
        DELETE FROM {schema}.t_movimiento_inventario
        WHERE id_inventario IN (SELECT id_inventario FROM {schema}.t_inventario WHERE id_sucursal = %s AND id_variante = %s);
    """, (id_sucursal_t1, id_variante_t1), commit=True)
    db.execute_query(f"""
        DELETE FROM {schema}.t_inventario 
        WHERE id_sucursal = %s AND id_variante = %s;
    """, (id_sucursal_t1, id_variante_t1), commit=True)

    res_inv = db.execute_query(f"""
        INSERT INTO {schema}.t_inventario (
            id_sucursal, id_variante, stock_actual, stock_reservado, stock_disponible, stock_minimo, estado
        ) VALUES (
            %s, %s, 10, 2, 8, 3, TRUE
        ) RETURNING id_inventario;
    """, (id_sucursal_t1, id_variante_t1), fetchone=True, commit=True)
    id_inventario = res_inv[0]

    # Fila de inventario para tenant 2
    db.execute_query(f"""
        DELETE FROM {schema}.t_movimiento_inventario
        WHERE id_inventario IN (SELECT id_inventario FROM {schema}.t_inventario WHERE id_sucursal = %s AND id_variante = %s);
    """, (id_sucursal_t2, id_variante_t2), commit=True)
    db.execute_query(f"""
        DELETE FROM {schema}.t_inventario 
        WHERE id_sucursal = %s AND id_variante = %s;
    """, (id_sucursal_t2, id_variante_t2), commit=True)

    db.execute_query(f"""
        INSERT INTO {schema}.t_inventario (
            id_sucursal, id_variante, stock_actual, stock_reservado, stock_disponible, stock_minimo, estado
        ) VALUES (
            %s, %s, 10, 0, 10, 2, TRUE
        );
    """, (id_sucursal_t2, id_variante_t2), commit=True)

    # 6. Obtener usuario existente para auditoría
    res_user = db.execute_query(f"SELECT id_usuario FROM {schema}.t_usuario LIMIT 1;", fetchone=True)
    id_usuario_test = res_user[0] if res_user else 1

    return {
        "id_inventario": id_inventario,
        "id_sucursal_t1": id_sucursal_t1,
        "id_variante_t1": id_variante_t1,
        "id_sucursal_t2": id_sucursal_t2,
        "id_variante_t2": id_variante_t2,
        "id_usuario_test": id_usuario_test
    }

def run_all_tests():
    print("=" * 70)
    print("🚀 INICIANDO BATERÍA DE PRUEBAS OBLIGATORIAS: W22 - GESTIÓN DE INVENTARIO")
    print("=" * 70)

    db = PostgreSQL()
    db.create_connection()
    schema = _get_schema()

    try:
        data = setup_test_data(db)
        suc1 = data["id_sucursal_t1"]
        var1 = data["id_variante_t1"]
        suc2 = data["id_sucursal_t2"]
        var2 = data["id_variante_t2"]
        uid = data["id_usuario_test"]

        # -------------------------------------------------------------
        # 1. PRUEBA DE ENTRADA
        # -------------------------------------------------------------
        # Stock inicial: actual=10, reservado=2, disponible=8
        # Entrada de 5 unidades -> actual=15, reservado=2, disponible=13
        res1 = inventario_repos.registrar_movimiento_inventario(
            id_sucursal=suc1, id_variante=var1, tipo_movimiento="ENTRADA",
            cantidad=5, id_usuario=uid, motivo="Recepción proveedor test", id_empresa=1
        )
        passed1 = (
            res1.get("success") is True and
            res1.get("stock_anterior") == 10 and
            res1.get("stock_nuevo") == 15 and
            res1.get("stock_actual") == 15 and
            res1.get("stock_reservado") == 2 and
            res1.get("stock_disponible") == 13
        )
        print_result("1. Entrada de inventario", passed1, f"Actual: {res1.get('stock_actual')}, Disp: {res1.get('stock_disponible')}")

        # -------------------------------------------------------------
        # 2. PRUEBA DE SALIDA
        # -------------------------------------------------------------
        # Stock actual=15, reservado=2, disponible=13
        # Salida de 4 unidades -> actual=11, reservado=2, disponible=9
        res2 = inventario_repos.registrar_movimiento_inventario(
            id_sucursal=suc1, id_variante=var1, tipo_movimiento="SALIDA",
            cantidad=4, id_usuario=uid, motivo="Salida por merma/traslado", id_empresa=1
        )
        passed2 = (
            res2.get("success") is True and
            res2.get("stock_anterior") == 15 and
            res2.get("stock_nuevo") == 11 and
            res2.get("stock_actual") == 11 and
            res2.get("stock_reservado") == 2 and
            res2.get("stock_disponible") == 9
        )
        print_result("2. Salida de inventario", passed2, f"Actual: {res2.get('stock_actual')}, Disp: {res2.get('stock_disponible')}")

        # -------------------------------------------------------------
        # 3. PRUEBA DE AJUSTE
        # -------------------------------------------------------------
        # Stock actual=11, reservado=2, disponible=9
        # Ajuste a stock físico 20 -> actual=20, reservado=2, disponible=18
        res3 = inventario_repos.registrar_movimiento_inventario(
            id_sucursal=suc1, id_variante=var1, tipo_movimiento="AJUSTE",
            cantidad=20, id_usuario=uid, motivo="Auditoría física de inventario", id_empresa=1
        )
        passed3 = (
            res3.get("success") is True and
            res3.get("stock_anterior") == 11 and
            res3.get("stock_nuevo") == 20 and
            res3.get("stock_actual") == 20 and
            res3.get("stock_reservado") == 2 and
            res3.get("stock_disponible") == 18
        )
        print_result("3. Ajuste de inventario", passed3, f"Nuevo actual: {res3.get('stock_actual')}, Disp: {res3.get('stock_disponible')}")

        # -------------------------------------------------------------
        # 4. PRUEBA DE STOCK INSUFICIENTE (RESPETANDO RESERVAS)
        # -------------------------------------------------------------
        # Stock actual=20, reservado=2, disponible=18
        # Salida solicitada: 19 (excede disponible=18, consumiría unidades reservadas)
        res4 = inventario_repos.registrar_movimiento_inventario(
            id_sucursal=suc1, id_variante=var1, tipo_movimiento="SALIDA",
            cantidad=19, id_usuario=uid, motivo="Intento de sobre-salida", id_empresa=1
        )
        passed4 = (
            res4.get("success") is False and
            res4.get("error") == "STOCK_INSUFICIENTE"
        )
        # Verificar que el stock no cambió
        inv_check = db.execute_query(f"SELECT stock_actual, stock_disponible FROM {schema}.t_inventario WHERE id_sucursal=%s AND id_variante=%s;", (suc1, var1), fetchone=True)
        passed4 = passed4 and (inv_check[0] == 20 and inv_check[1] == 18)
        print_result("4. Stock insuficiente (protección de reservas)", passed4, f"Respuesta error: {res4.get('error')}, Stock intacto: {inv_check}")

        # -------------------------------------------------------------
        # 5. PRUEBA DE INTENTO DE STOCK NEGATIVO
        # -------------------------------------------------------------
        # Ajuste a -5 unidades o salida gigantesca
        res5_a = inventario_repos.registrar_movimiento_inventario(
            id_sucursal=suc1, id_variante=var1, tipo_movimiento="AJUSTE",
            cantidad=-5, id_usuario=uid, motivo="Intento negativo", id_empresa=1
        )
        res5_b = inventario_repos.registrar_movimiento_inventario(
            id_sucursal=suc1, id_variante=var1, tipo_movimiento="SALIDA",
            cantidad=1000, id_usuario=uid, motivo="Intento salida gigante", id_empresa=1
        )
        passed5 = (
            res5_a.get("success") is False and
            res5_b.get("success") is False and
            res5_a.get("error") in ("STOCK_NEGATIVO_NO_PERMITIDO", "CANTIDAD_INVALIDA")
        )
        print_result("5. Intento de stock negativo", passed5, "Operaciones con valores negativos o sobre-stock rechazadas.")

        # -------------------------------------------------------------
        # 6. PRUEBA DE INVENTARIO INEXISTENTE
        # -------------------------------------------------------------
        res6 = inventario_repos.registrar_movimiento_inventario(
            id_sucursal=99999, id_variante=99999, tipo_movimiento="ENTRADA",
            cantidad=5, id_usuario=uid, motivo="Inventario inexistente", id_empresa=None
        )
        passed6 = (
            res6.get("success") is False and
            res6.get("error") in ("SUCURSAL_NO_ENCONTRADA", "INVENTARIO_NO_ENCONTRADO")
        )
        print_result("6. Inventario inexistente", passed6, f"Error devuelto: {res6.get('error')}")

        # -------------------------------------------------------------
        # 7. MULTI-TENANT: SUCURSAL DE OTRO TENANT
        # -------------------------------------------------------------
        # Usuario de Empresa 1 intenta mover stock en Sucursal de Empresa 2
        res7 = inventario_repos.registrar_movimiento_inventario(
            id_sucursal=suc2, id_variante=var1, tipo_movimiento="ENTRADA",
            cantidad=5, id_usuario=uid, motivo="Ataque cross-tenant sucursal", id_empresa=1
        )
        passed7 = (
            res7.get("success") is False and
            res7.get("error") in ("SUCURSAL_AJENA_TENANT", "TENANT_MISMATCH")
        )
        print_result("7. Sucursal de otro tenant", passed7, f"Bloqueado multi-tenant: {res7.get('error')}")

        # -------------------------------------------------------------
        # 8. MULTI-TENANT: VARIANTE DE OTRO TENANT
        # -------------------------------------------------------------
        # Usuario de Empresa 1 intenta mover stock de Producto de Empresa 2
        res8 = inventario_repos.registrar_movimiento_inventario(
            id_sucursal=suc1, id_variante=var2, tipo_movimiento="ENTRADA",
            cantidad=5, id_usuario=uid, motivo="Ataque cross-tenant variante", id_empresa=1
        )
        passed8 = (
            res8.get("success") is False and
            res8.get("error") in ("VARIANTE_AJENA_TENANT", "TENANT_MISMATCH")
        )
        print_result("8. Variante de otro tenant", passed8, f"Bloqueado multi-tenant: {res8.get('error')}")

        # -------------------------------------------------------------
        # 9. REGISTRO CORRECTO DEL MOVIMIENTO EN t_movimiento_inventario
        # -------------------------------------------------------------
        mov_check = db.execute_query(f"""
            SELECT id_movimiento, id_inventario, id_usuario, tipo_movimiento, cantidad, stock_anterior, stock_nuevo, motivo, fecha_movimiento
            FROM {schema}.t_movimiento_inventario
            WHERE id_inventario = (
                SELECT id_inventario FROM {schema}.t_inventario WHERE id_sucursal = %s AND id_variante = %s
            )
            ORDER BY id_movimiento DESC LIMIT 1;
        """, (suc1, var1), fetchone=True)
        passed9 = (
            mov_check is not None and
            mov_check[3] == "AJUSTE" and
            mov_check[5] == 11 and
            mov_check[6] == 20 and
            mov_check[7] == "Auditoría física de inventario" and
            mov_check[8] is not None
        )
        print_result("9. Registro correcto del movimiento", passed9, f"Movimiento ID {mov_check[0] if mov_check else 'None'}: {mov_check[3]} {mov_check[5]}->{mov_check[6]}")

        # -------------------------------------------------------------
        # 10. CONSERVACIÓN INVIOLABLE DE stock_reservado
        # -------------------------------------------------------------
        # Fijar stock actual=5, reservado=5, disponible=0
        db.execute_query(f"""
            UPDATE {schema}.t_inventario
            SET stock_actual = 5, stock_reservado = 5, stock_disponible = 0
            WHERE id_sucursal = %s AND id_variante = %s;
        """, (suc1, var1), commit=True)

        res10 = inventario_repos.registrar_movimiento_inventario(
            id_sucursal=suc1, id_variante=var1, tipo_movimiento="SALIDA",
            cantidad=1, id_usuario=uid, motivo="Intento consumir reserva", id_empresa=1
        )
        passed10 = (
            res10.get("success") is False and
            res10.get("error") == "STOCK_INSUFICIENTE"
        )
        inv_check10 = db.execute_query(f"SELECT stock_actual, stock_reservado, stock_disponible FROM {schema}.t_inventario WHERE id_sucursal=%s AND id_variante=%s;", (suc1, var1), fetchone=True)
        passed10 = passed10 and (inv_check10[0] == 5 and inv_check10[1] == 5 and inv_check10[2] == 0)
        print_result("10. Conservación de stock_reservado", passed10, f"Reserva protegida: actual={inv_check10[0]}, reservado={inv_check10[1]}, disp={inv_check10[2]}")

        # -------------------------------------------------------------
        # 11. CONCURRENCIA CON ÚLTIMO PRODUCTO DISPONIBLE
        # -------------------------------------------------------------
        # Preparar: stock_actual = 1, stock_reservado = 0, stock_disponible = 1
        db.execute_query(f"""
            UPDATE {schema}.t_inventario
            SET stock_actual = 1, stock_reservado = 0, stock_disponible = 1
            WHERE id_sucursal = %s AND id_variante = %s;
        """, (suc1, var1), commit=True)

        num_hilos = 5
        resultados_concurrencia = []

        def worker_salida(idx):
            # Crea su propia conexión y realiza la salida
            return inventario_repos.registrar_movimiento_inventario(
                id_sucursal=suc1,
                id_variante=var1,
                tipo_movimiento="SALIDA",
                cantidad=1,
                id_usuario=uid,
                motivo=f"Intento concurrente hilo {idx}",
                id_empresa=1
            )

        with concurrent.futures.ThreadPoolExecutor(max_workers=num_hilos) as executor:
            futuros = [executor.submit(worker_salida, i) for i in range(num_hilos)]
            for f in concurrent.futures.as_completed(futuros):
                resultados_concurrencia.append(f.result())

        exitos = [r for r in resultados_concurrencia if r.get("success") is True]
        fallos = [r for r in resultados_concurrencia if r.get("success") is False and r.get("error") == "STOCK_INSUFICIENTE"]

        inv_final = db.execute_query(f"SELECT stock_actual, stock_disponible FROM {schema}.t_inventario WHERE id_sucursal=%s AND id_variante=%s;", (suc1, var1), fetchone=True)

        passed11 = (
            len(exitos) == 1 and
            len(fallos) == (num_hilos - 1) and
            inv_final[0] == 0 and
            inv_final[1] == 0
        )
        print_result("11. Concurrencia atómica (Último producto)", passed11, f"Éxitos: {len(exitos)}, Rechazos: {len(fallos)}, Stock final: {inv_final[0]} (NUNCA negativo)")

        # -------------------------------------------------------------
        # 12. ROLLBACK ANTE ERROR
        # -------------------------------------------------------------
        # Probar que una transacción fallida en Postgres nunca deja stock corrupto
        # Poner stock en 5
        db.execute_query(f"""
            UPDATE {schema}.t_inventario
            SET stock_actual = 5, stock_reservado = 0, stock_disponible = 5
            WHERE id_sucursal = %s AND id_variante = %s;
        """, (suc1, var1), commit=True)

        # Disparamos salida inválida (cantidad > disponible)
        res12 = inventario_repos.registrar_movimiento_inventario(
            id_sucursal=suc1, id_variante=var1, tipo_movimiento="SALIDA",
            cantidad=10, id_usuario=uid, motivo="Transacción que debe rebotar", id_empresa=1
        )
        inv_check12 = db.execute_query(f"SELECT stock_actual, stock_disponible FROM {schema}.t_inventario WHERE id_sucursal=%s AND id_variante=%s;", (suc1, var1), fetchone=True)
        passed12 = (
            res12.get("success") is False and
            inv_check12[0] == 5 and
            inv_check12[1] == 5
        )
        print_result("12. Rollback y atomicidad ante error", passed12, f"Stock intacto tras error: {inv_check12}")

        print("=" * 70)
        print("🎉 TODAS LAS 12 PRUEBAS OBLIGATORIAS PASARON EXITOSAMENTE (100% OK)")
        print("=" * 70)

    finally:
        db.close_connection()

if __name__ == "__main__":
    run_all_tests()
