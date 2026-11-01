"""Local safeguards shared by existing stock writers; no schema changes or repairs."""
import json
from fastapi import HTTPException


def lock_position(db, schema, branch, variant, company=None, allow_missing=False):
    """Serialize absent/present positions and reject historical ambiguous balances.

    Caller must own a transaction. Shared catalogs with NULL tenant retain their
    existing meaning; known foreign tenants are never interchangeable.
    """
    db.execute_query('SELECT pg_advisory_xact_lock(hashtextextended(%s,0))',
                     (json.dumps(['inventory', schema, int(branch), int(variant)]),))
    owner = db.execute_query(f'''
        SELECT s.id_empresa,p.id_empresa,t.id_empresa,c.id_empresa,cat.id_empresa
        FROM {schema}.t_sucursal s
        CROSS JOIN {schema}.t_producto_talla_color v
        JOIN {schema}.t_producto p ON p.id_producto=v.id_producto
        LEFT JOIN {schema}.t_talla t ON t.id_talla=v.id_talla
        LEFT JOIN {schema}.t_color c ON c.id_color=v.id_color
        LEFT JOIN {schema}.t_categoria cat ON cat.id_categoria=p.id_categoria
        WHERE s.id_sucursal=%s AND v.id_variante=%s
        FOR SHARE OF s,p,v
    ''', (branch, variant), fetchone=True)
    if not owner:
        raise HTTPException(404, 'Sucursal o variante no encontrada.')
    tenant = owner[0] if company is None else company
    if tenant is None or owner[0] != tenant or owner[1] != tenant or any(x is not None and x != tenant for x in owner[2:]):
        raise HTTPException(403, 'La sucursal, producto, talla y color no pertenecen al mismo tenant autorizado.')
    rows = db.execute_query(f'''SELECT id_inventario,stock_actual,stock_reservado,stock_disponible
        FROM {schema}.t_inventario WHERE id_sucursal=%s AND id_variante=%s
        ORDER BY id_inventario FOR UPDATE''', (branch, variant), fetchall=True) or []
    if len(rows) > 1:
        raise HTTPException(409, 'INVENTORY_RECONCILIATION_REQUIRED: posición duplicada; no se modificaron saldos.')
    if not rows:
        if allow_missing:
            return None
        raise HTTPException(409, 'No existe inventario para esta variante y sucursal.')
    row = rows[0]
    actual, reserved, available = row[1:]
    if any(x is None for x in row[1:]) or min(actual, reserved, available) < 0 or reserved > actual or available != actual - reserved:
        raise HTTPException(409, 'INVENTORY_RECONCILIATION_REQUIRED: saldo histórico inconsistente; requiere conciliación.')
    return row


def lock_items(db, schema, branch, items, company=None, allow_missing=False):
    totals = {}
    for item in items:
        variant, quantity = int(item['id_variante']), int(item.get('cantidad', 1))
        if variant <= 0 or quantity <= 0:
            raise HTTPException(400, 'Variante y cantidad deben ser positivas.')
        totals[variant] = totals.get(variant, 0) + quantity
    positions = {}
    for variant in sorted(totals):
        positions[variant] = lock_position(db, schema, branch, variant, company, allow_missing)
    return totals, positions
