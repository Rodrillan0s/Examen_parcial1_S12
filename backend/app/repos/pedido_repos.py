import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List
from app.classes.postgres import PostgreSQL
from app.config import Config
from app.repos.carrito_repos import obtener_o_crear_cliente

def _get_schema() -> str:
    return Config.SCHEMA or 'comercio'

def obtener_sucursales_tenant(id_empresa: int) -> List[Dict[str, Any]]:
    """
    Obtiene las sucursales activas pertenecientes exclusivamente al Tenant actual.
    Incluye datos de ubicación geográfica, contacto y horarios de atención.
    """
    db = PostgreSQL()
    db.create_connection()
    try:
        schema = _get_schema()
        q = f"""
            SELECT 
                s.id_sucursal,
                s.id_empresa,
                s.nombre,
                s.codigo_sucursal,
                s.direccion,
                s.telefono,
                s.correo,
                s.horario_apertura,
                s.horario_cierre,
                ci.nombre AS ciudad_nombre,
                s.activo
            FROM {schema}.t_sucursal s
            LEFT JOIN {schema}.t_ciudad ci ON ci.id_ciudad = s.id_ciudad
            WHERE s.id_empresa = %s AND s.activo = TRUE
            ORDER BY s.nombre ASC;
        """
        rows = db.execute_query(q, (id_empresa,), fetchall=True) or []
        resultado = []
        for r in rows:
            resultado.append({
                "id_sucursal": r[0],
                "id_empresa": r[1],
                "nombre": r[2],
                "codigo_sucursal": r[3],
                "direccion": r[4] or "Dirección no registrada",
                "telefono": r[5] or "",
                "correo": r[6] or "",
                "horario": f"{r[7] or '09:00'} - {r[8] or '20:00'}",
                "ciudad": r[9] or "Santa Cruz",
                "activo": bool(r[10])
            })
        return resultado
    finally:
        db.close_connection()

def validar_y_crear_pedido(id_usuario: int, id_empresa: int, datos: Dict[str, Any]) -> Dict[str, Any]:
    """
    Crea un nuevo pedido formal a partir del carrito activo del cliente.
    Realiza la re-validación completa en tiempo real de productos, variantes,
    pertenencia al Tenant y stock disponible antes de persistir la orden.
    El inventario NO se descuenta en este punto (permanece inalterado hasta W27/W28).
    """
    schema = _get_schema()

    # 1. Obtener cliente autenticado
    id_cliente = obtener_o_crear_cliente(id_usuario)

    # 2. Validar sucursal seleccionada
    id_sucursal = datos.get('id_sucursal')
    if not id_sucursal:
        raise ValueError("Debe seleccionar una sucursal para la compra.")

    db = PostgreSQL()
    db.create_connection()
    try:
        # Verificar pertenencia y estado activo de la sucursal
        q_suc = f"""
            SELECT id_sucursal, nombre, direccion 
            FROM {schema}.t_sucursal 
            WHERE id_sucursal = %s AND id_empresa = %s AND activo = TRUE 
            LIMIT 1;
        """
        suc_row = db.execute_query(q_suc, (id_sucursal, id_empresa), fetchone=True)
        if not suc_row:
            raise ValueError("La sucursal seleccionada no está disponible o no pertenece a esta tienda.")

        # 3. Validar modalidad de compra y datos de entrega
        modalidad = str(datos.get('modalidad_compra', 'RETIRO_SUCURSAL')).upper()
        if modalidad not in ['RETIRO_SUCURSAL', 'ENTREGA_DOMICILIO']:
            raise ValueError("Modalidad de compra inválida. Opciones: RETIRO_SUCURSAL o ENTREGA_DOMICILIO.")

        nombre_contacto = (datos.get('nombre_contacto') or '').strip()
        telefono_contacto = (datos.get('telefono_contacto') or '').strip()
        correo_contacto = (datos.get('correo_contacto') or '').strip()
        direccion_entrega = (datos.get('direccion_entrega') or '').strip()
        ciudad_entrega = (datos.get('ciudad_entrega') or '').strip()
        notas_entrega = (datos.get('notas_entrega') or '').strip()

        if not nombre_contacto:
            raise ValueError("Debe ingresar el nombre de la persona que recibe o retira el pedido.")
        if not telefono_contacto:
            raise ValueError("Debe ingresar un teléfono de contacto válido.")

        if modalidad == 'ENTREGA_DOMICILIO':
            if not direccion_entrega:
                raise ValueError("Para entrega a domicilio, debe especificar la dirección de entrega.")
            if not ciudad_entrega:
                raise ValueError("Para entrega a domicilio, debe indicar la ciudad.")

        # 4. Obtener el carrito activo del cliente para este Tenant
        q_car = f"""
            SELECT id_carrito 
            FROM {schema}.t_carrito 
            WHERE id_cliente = %s AND id_empresa = %s AND estado = 'ACTIVO' 
            LIMIT 1;
        """
        car_row = db.execute_query(q_car, (id_cliente, id_empresa), fetchone=True)
        if not car_row:
            raise ValueError("No tienes un carrito de compras activo en esta tienda.")

        id_carrito = car_row[0]

        # 5. Obtener los detalles del carrito
        q_items = f"""
            SELECT 
                d.id_detalle_carrito,
                d.id_variante,
                d.cantidad,
                p.id_producto,
                p.nombre AS producto_nombre,
                p.id_empresa AS producto_empresa,
                p.activo AS producto_activo,
                v.activo AS variante_activa,
                t.activo AS talla_activa,
                col.activo AS color_activo,
                t.nombre AS talla_nombre,
                col.nombre AS color_nombre,
                col.codigo_hex,
                v.sku,
                COALESCE(v.precio, p.precio) AS precio_vigente
            FROM {schema}.t_detalle_carrito d
            JOIN {schema}.t_producto_talla_color v ON v.id_variante = d.id_variante
            JOIN {schema}.t_producto p ON p.id_producto = v.id_producto
            JOIN {schema}.t_talla t ON t.id_talla = v.id_talla
            JOIN {schema}.t_color col ON col.id_color = v.id_color
            WHERE d.id_carrito = %s
            ORDER BY d.id_detalle_carrito ASC;
        """
        items_cart = db.execute_query(q_items, (id_carrito,), fetchall=True) or []
        if not items_cart:
            raise ValueError("Tu bolsa de compras se encuentra vacía. Agrega prendas antes de proceder al checkout.")

        # 6. Re-validación estricta de variantes, tenant y stock disponible vigente
        items_a_guardar = []
        subtotal_acumulado = 0.0

        for r in items_cart:
            id_det_car = r[0]
            id_var = r[1]
            cant = int(r[2])
            id_prod = r[3]
            p_nombre = r[4]
            prod_emp = r[5]
            prod_activo = bool(r[6])
            var_activa = bool(r[7])
            talla_activa = bool(r[8])
            col_activa = bool(r[9])
            t_nombre = r[10]
            c_nombre = r[11]
            sku = r[13]
            precio_vigente = float(r[14]) if r[14] is not None else 0.0

            if cant <= 0:
                raise ValueError(f"La prenda '{p_nombre}' tiene una cantidad no válida ({cant}).")

            if prod_emp != id_empresa:
                raise ValueError(f"La prenda '{p_nombre}' no pertenece a la tienda actual.")

            if not prod_activo or not var_activa or not talla_activa or not col_activa:
                raise ValueError(f"La prenda '{p_nombre}' ({t_nombre} / {c_nombre}) ha sido descontinuada o inactivada.")

            # Consultar stock disponible actual en las sucursales activas del Tenant
            q_stk = f"""
                SELECT COALESCE(SUM(GREATEST(0, inv.stock_disponible)), 0)
                FROM {schema}.t_inventario inv
                JOIN {schema}.t_sucursal s ON s.id_sucursal = inv.id_sucursal
                WHERE inv.id_variante = %s AND s.id_empresa = %s AND s.activo = TRUE AND inv.estado = TRUE;
            """
            stk_res = db.execute_query(q_stk, (id_var, id_empresa), fetchone=True)
            stock_disp = int(stk_res[0]) if stk_res else 0

            if stock_disp < cant:
                raise ValueError(
                    f"Stock insuficiente para '{p_nombre}' ({t_nombre} / {c_nombre}). "
                    f"Solicitaste {cant} unidad(es), pero solo quedan {stock_disp} disponible(s) en tienda."
                )

            line_subtotal = round(cant * precio_vigente, 2)
            subtotal_acumulado += line_subtotal

            items_a_guardar.append({
                "id_variante": id_var,
                "cantidad": cant,
                "precio_unitario": precio_vigente,
                "subtotal": line_subtotal,
                "producto_nombre": p_nombre,
                "talla_nombre": t_nombre,
                "color_nombre": c_nombre,
                "sku": sku
            })

        subtotal_final = round(subtotal_acumulado, 2)
        costo_envio = 0.0 # Envío bonificado o calculado
        descuento = 0.0
        total_final = round(subtotal_final + costo_envio - descuento, 2)

        # 7. Generar código único de pedido
        fecha_str = datetime.now().strftime('%Y%m%d')
        random_suffix = uuid.uuid4().hex[:6].upper()
        codigo_pedido = f"PED-{fecha_str}-{random_suffix}"

        # 8. Insertar cabecera t_pedido en estado inicial PENDIENTE_PAGO
        q_ins_ped = f"""
            INSERT INTO {schema}.t_pedido (
                codigo_pedido,
                id_cliente,
                id_empresa,
                id_sucursal,
                id_carrito_origen,
                fecha_pedido,
                fecha_actualizacion,
                estado,
                estado_pago,
                modalidad_compra,
                nombre_contacto,
                telefono_contacto,
                correo_contacto,
                direccion_entrega,
                ciudad_entrega,
                notas_entrega,
                subtotal,
                costo_envio,
                descuento,
                total
            ) VALUES (
                %s, %s, %s, %s, %s, NOW(), NOW(),
                'PENDIENTE_PAGO', 'PENDIENTE', %s,
                %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s
            ) RETURNING id_pedido, fecha_pedido;
        """
        ped_res = db.execute_query(
            q_ins_ped,
            (
                codigo_pedido,
                id_cliente,
                id_empresa,
                id_sucursal,
                id_carrito,
                modalidad,
                nombre_contacto,
                telefono_contacto,
                correo_contacto,
                direccion_entrega if modalidad == 'ENTREGA_DOMICILIO' else None,
                ciudad_entrega if modalidad == 'ENTREGA_DOMICILIO' else None,
                notas_entrega,
                subtotal_final,
                costo_envio,
                descuento,
                total_final
            ),
            fetchone=True,
            commit=True
        )
        id_pedido = ped_res[0]
        fecha_pedido = ped_res[1]

        # 9. Insertar líneas en t_detalle_pedido conservando el precio unitario histórico
        for it in items_a_guardar:
            q_ins_det = f"""
                INSERT INTO {schema}.t_detalle_pedido (
                    id_pedido, id_variante, cantidad, precio_unitario, subtotal
                ) VALUES (%s, %s, %s, %s, %s);
            """
            db.execute_query(
                q_ins_det,
                (id_pedido, it["id_variante"], it["cantidad"], it["precio_unitario"], it["subtotal"]),
                commit=True
            )

        # 10. Limpiar / procesar el carrito para evitar pedidos duplicados
        # El carrito origen queda en estado PROCESADO y sus detalles se vacían
        db.execute_query(
            f"UPDATE {schema}.t_carrito SET estado = 'PROCESADO', fecha_actualizacion = NOW() WHERE id_carrito = %s;",
            (id_carrito,),
            commit=True
        )
        db.execute_query(
            f"DELETE FROM {schema}.t_detalle_carrito WHERE id_carrito = %s;",
            (id_carrito,),
            commit=True
        )

        # Confirmar transacción completa
        db.close_connection(commit=True)

        return {
            "id_pedido": id_pedido,
            "codigo_pedido": codigo_pedido,
            "id_empresa": id_empresa,
            "id_sucursal": id_sucursal,
            "sucursal_nombre": suc_row[1],
            "fecha_pedido": fecha_pedido.isoformat() if hasattr(fecha_pedido, 'isoformat') else str(fecha_pedido),
            "estado": "PENDIENTE_PAGO",
            "estado_pago": "PENDIENTE",
            "modalidad_compra": modalidad,
            "nombre_contacto": nombre_contacto,
            "telefono_contacto": telefono_contacto,
            "correo_contacto": correo_contacto,
            "direccion_entrega": direccion_entrega if modalidad == 'ENTREGA_DOMICILIO' else None,
            "ciudad_entrega": ciudad_entrega if modalidad == 'ENTREGA_DOMICILIO' else None,
            "notas_entrega": notas_entrega,
            "subtotal": subtotal_final,
            "costo_envio": costo_envio,
            "descuento": descuento,
            "total": total_final,
            "total_items": sum(it["cantidad"] for it in items_a_guardar),
            "items": items_a_guardar
        }

    except Exception:
        db.close_connection(commit=False)
        raise

def obtener_pedido_por_id(id_pedido: int, id_usuario: int, id_empresa: Optional[int] = None) -> Optional[Dict[str, Any]]:
    """
    Obtiene los datos completos de un pedido específico.
    Verifica estrictamente que el pedido pertenezca al cliente autenticado
    y al Tenant correspondiente.
    """
    id_cliente = obtener_o_crear_cliente(id_usuario)

    db = PostgreSQL()
    db.create_connection()
    try:
        schema = _get_schema()

        condiciones = ["p.id_pedido = %s", "p.id_cliente = %s"]
        params: List[Any] = [id_pedido, id_cliente]

        if id_empresa and id_empresa > 0:
            condiciones.append("p.id_empresa = %s")
            params.append(id_empresa)

        where_clause = " AND ".join(condiciones)

        q_head = f"""
            SELECT 
                p.id_pedido,
                p.codigo_pedido,
                p.id_cliente,
                p.id_empresa,
                emp.nombre_empresa,
                p.id_sucursal,
                s.nombre AS sucursal_nombre,
                s.direccion AS sucursal_direccion,
                s.telefono AS sucursal_telefono,
                p.fecha_pedido,
                p.estado,
                p.estado_pago,
                p.modalidad_compra,
                p.nombre_contacto,
                p.telefono_contacto,
                p.correo_contacto,
                p.direccion_entrega,
                p.ciudad_entrega,
                p.notas_entrega,
                p.subtotal,
                p.costo_envio,
                p.descuento,
                p.total
            FROM {schema}.t_pedido p
            JOIN {schema}.empresa emp ON emp.id_empresa = p.id_empresa
            JOIN {schema}.t_sucursal s ON s.id_sucursal = p.id_sucursal
            WHERE {where_clause}
            LIMIT 1;
        """
        row = db.execute_query(q_head, tuple(params), fetchone=True)
        if not row:
            return None

        # Consultar detalles del pedido
        q_det = f"""
            SELECT 
                d.id_detalle_pedido,
                d.id_variante,
                d.cantidad,
                d.precio_unitario,
                d.subtotal,
                prod.id_producto,
                prod.nombre AS producto_nombre,
                t.nombre AS talla_nombre,
                col.nombre AS color_nombre,
                col.codigo_hex,
                v.sku,
                (
                    SELECT img.imagen_url 
                    FROM {schema}.t_producto_imagen img 
                    WHERE img.id_producto = prod.id_producto 
                    ORDER BY img.es_principal DESC, img.orden ASC, img.id_imagen ASC 
                    LIMIT 1
                ) AS imagen_url
            FROM {schema}.t_detalle_pedido d
            JOIN {schema}.t_producto_talla_color v ON v.id_variante = d.id_variante
            JOIN {schema}.t_producto prod ON prod.id_producto = v.id_producto
            JOIN {schema}.t_talla t ON t.id_talla = v.id_talla
            JOIN {schema}.t_color col ON col.id_color = v.id_color
            WHERE d.id_pedido = %s
            ORDER BY d.id_detalle_pedido ASC;
        """
        items_rows = db.execute_query(q_det, (id_pedido,), fetchall=True) or []
        items = []
        total_items = 0

        for ir in items_rows:
            cant = ir[2]
            total_items += cant
            items.append({
                "id_detalle_pedido": ir[0],
                "id_variante": ir[1],
                "cantidad": cant,
                "precio_unitario": float(ir[3]),
                "subtotal": float(ir[4]),
                "id_producto": ir[5],
                "producto_nombre": ir[6],
                "talla_nombre": ir[7],
                "color_nombre": ir[8],
                "codigo_hex": ir[9],
                "sku": ir[10],
                "imagen_url": ir[11]
            })

        fecha = row[9]
        return {
            "id_pedido": row[0],
            "codigo_pedido": row[1],
            "id_cliente": row[2],
            "id_empresa": row[3],
            "nombre_empresa": row[4],
            "id_sucursal": row[5],
            "sucursal_nombre": row[6],
            "sucursal_direccion": row[7],
            "sucursal_telefono": row[8],
            "fecha_pedido": fecha.isoformat() if hasattr(fecha, 'isoformat') else str(fecha),
            "estado": row[10],
            "estado_pago": row[11],
            "modalidad_compra": row[12],
            "nombre_contacto": row[13],
            "telefono_contacto": row[14],
            "correo_contacto": row[15],
            "direccion_entrega": row[16],
            "ciudad_entrega": row[17],
            "notas_entrega": row[18],
            "subtotal": float(row[19]),
            "costo_envio": float(row[20]),
            "descuento": float(row[21]),
            "total": float(row[22]),
            "total_items": total_items,
            "items": items
        }
    finally:
        db.close_connection()

def listar_pedidos_cliente(
    id_usuario: int,
    id_empresa: Optional[int] = None,
    estado: Optional[str] = None,
    estado_pago: Optional[str] = None,
    fecha_inicio: Optional[str] = None,
    fecha_fin: Optional[str] = None,
    codigo: Optional[str] = None,
    limit: int = 10,
    offset: int = 0
) -> Dict[str, Any]:
    """
    W11 - CU11: Consulta el historial de pedidos del cliente autenticado.
    Soporta filtros por estado, estado de pago, rango de fechas y código de pedido,
    además de paginación y aislamiento multitenant.
    """
    id_cliente = obtener_o_crear_cliente(id_usuario)

    db = PostgreSQL()
    db.create_connection()
    try:
        schema = _get_schema()

        condiciones = ["p.id_cliente = %s"]
        params: List[Any] = [id_cliente]

        if id_empresa and id_empresa > 0:
            condiciones.append("p.id_empresa = %s")
            params.append(id_empresa)

        if estado and estado.strip() and estado.strip().upper() != 'TODOS':
            condiciones.append("p.estado = %s")
            params.append(estado.strip().upper())

        if estado_pago and estado_pago.strip() and estado_pago.strip().upper() != 'TODOS':
            condiciones.append("p.estado_pago = %s")
            params.append(estado_pago.strip().upper())

        if fecha_inicio and fecha_inicio.strip():
            condiciones.append("p.fecha_pedido >= %s")
            params.append(f"{fecha_inicio.strip()} 00:00:00")

        if fecha_fin and fecha_fin.strip():
            condiciones.append("p.fecha_pedido <= %s")
            params.append(f"{fecha_fin.strip()} 23:59:59")

        if codigo and codigo.strip():
            condiciones.append("p.codigo_pedido ILIKE %s")
            params.append(f"%{codigo.strip()}%")

        where_clause = " AND ".join(condiciones)

        # 1. Obtener total de registros para paginación
        q_count = f"SELECT COUNT(*) FROM {schema}.t_pedido p WHERE {where_clause};"
        count_row = db.execute_query(q_count, tuple(params), fetchone=True)
        total_pedidos = count_row[0] if count_row else 0

        if total_pedidos == 0:
            return {
                "total": 0,
                "data": []
            }

        # 2. Consultar pedidos de la página solicitada
        q_list = f"""
            SELECT 
                p.id_pedido,
                p.codigo_pedido,
                p.id_cliente,
                p.id_empresa,
                emp.nombre_empresa,
                p.id_sucursal,
                s.nombre AS sucursal_nombre,
                ci.nombre AS sucursal_ciudad,
                p.fecha_pedido,
                p.estado,
                p.estado_pago,
                p.modalidad_compra,
                p.subtotal,
                p.costo_envio,
                p.descuento,
                p.total,
                (
                    SELECT COALESCE(SUM(d.cantidad), 0)
                    FROM {schema}.t_detalle_pedido d
                    WHERE d.id_pedido = p.id_pedido
                ) AS total_items
            FROM {schema}.t_pedido p
            JOIN {schema}.empresa emp ON emp.id_empresa = p.id_empresa
            JOIN {schema}.t_sucursal s ON s.id_sucursal = p.id_sucursal
            LEFT JOIN {schema}.t_ciudad ci ON ci.id_ciudad = s.id_ciudad
            WHERE {where_clause}
            ORDER BY p.fecha_pedido DESC, p.id_pedido DESC
            LIMIT %s OFFSET %s;
        """
        params_list = list(params) + [limit, offset]
        rows = db.execute_query(q_list, tuple(params_list), fetchall=True) or []

        if not rows:
            return {
                "total": total_pedidos,
                "data": []
            }

        id_pedidos = [r[0] for r in rows]

        # 3. Consultar items en lote para las tarjetas
        q_items = f"""
            SELECT 
                d.id_pedido,
                d.id_detalle_pedido,
                d.id_variante,
                d.cantidad,
                d.precio_unitario,
                d.subtotal,
                prod.nombre AS producto_nombre,
                t.nombre AS talla_nombre,
                col.nombre AS color_nombre,
                col.codigo_hex,
                (
                    SELECT img.imagen_url 
                    FROM {schema}.t_producto_imagen img 
                    WHERE img.id_producto = prod.id_producto 
                    ORDER BY img.es_principal DESC, img.orden ASC, img.id_imagen ASC 
                    LIMIT 1
                ) AS imagen_url
            FROM {schema}.t_detalle_pedido d
            JOIN {schema}.t_producto_talla_color v ON v.id_variante = d.id_variante
            JOIN {schema}.t_producto prod ON prod.id_producto = v.id_producto
            JOIN {schema}.t_talla t ON t.id_talla = v.id_talla
            JOIN {schema}.t_color col ON col.id_color = v.id_color
            WHERE d.id_pedido = ANY(%s)
            ORDER BY d.id_detalle_pedido ASC;
        """
        items_rows = db.execute_query(q_items, (id_pedidos,), fetchall=True) or []
        items_por_pedido: Dict[int, List[Dict[str, Any]]] = {}
        for ir in items_rows:
            ped_id = ir[0]
            if ped_id not in items_por_pedido:
                items_por_pedido[ped_id] = []
            items_por_pedido[ped_id].append({
                "id_detalle_pedido": ir[1],
                "id_variante": ir[2],
                "cantidad": ir[3],
                "precio_unitario": float(ir[4]),
                "subtotal": float(ir[5]),
                "producto_nombre": ir[6],
                "talla_nombre": ir[7],
                "color_nombre": ir[8],
                "codigo_hex": ir[9],
                "imagen_url": ir[10]
            })

        data = []
        for r in rows:
            p_id = r[0]
            f_ped = r[8]
            data.append({
                "id_pedido": p_id,
                "codigo_pedido": r[1],
                "id_cliente": r[2],
                "id_empresa": r[3],
                "nombre_empresa": r[4],
                "id_sucursal": r[5],
                "sucursal_nombre": r[6],
                "sucursal_ciudad": r[7] or "Bolivia",
                "fecha_pedido": f_ped.isoformat() if hasattr(f_ped, 'isoformat') else str(f_ped),
                "estado": r[9],
                "estado_pago": r[10],
                "modalidad_compra": r[11],
                "subtotal": float(r[12]),
                "costo_envio": float(r[13]),
                "descuento": float(r[14]),
                "total": float(r[15]),
                "total_items": int(r[16]),
                "items_resumen": items_por_pedido.get(p_id, [])
            })

        return {
            "total": total_pedidos,
            "data": data
        }
    finally:
        db.close_connection()

