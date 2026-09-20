"""
Migración para soporte de control de efectivo por denominaciones en W28 y W29.
Crea la tabla t_pago_denominacion para registrar separadamente:
- ENTRADA_EFECTIVO (billetes y monedas recibidos del comprador)
- SALIDA_CAMBIO (billetes y monedas entregados como cambio al comprador)
"""
import logging
from app.classes.postgres import PostgreSQL
from app.config import Config

logger = logging.getLogger(__name__)

def _get_schema() -> str:
    return Config.SCHEMA or 'comercio'

def migrar_denominaciones_pago():
    db = PostgreSQL()
    db.create_connection()
    try:
        schema = _get_schema()
        logger.info(f"Iniciando migración de denominaciones de pago en esquema: {schema}")

        # 1. Crear tabla de desglose de denominaciones por pago
        db.execute_query(f"""
            CREATE TABLE IF NOT EXISTS {schema}.t_pago_denominacion (
                id_pago_denominacion SERIAL PRIMARY KEY,
                id_pago INT NOT NULL REFERENCES {schema}.t_pago(id_pago) ON DELETE CASCADE,
                id_venta INT NOT NULL REFERENCES {schema}.t_venta(id_venta) ON DELETE CASCADE,
                id_sesion_caja INT REFERENCES {schema}.t_caja_sesion(id_sesion_caja) ON DELETE SET NULL,
                tipo_movimiento VARCHAR(20) NOT NULL CHECK (tipo_movimiento IN ('ENTRADA_EFECTIVO', 'SALIDA_CAMBIO')),
                id_denominacion INT REFERENCES {schema}.t_denominacion(id_denominacion),
                valor_denominacion NUMERIC(10, 2) NOT NULL,
                cantidad INT NOT NULL CHECK (cantidad >= 0),
                subtotal NUMERIC(12, 2) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """, commit=True)

        # 2. Índices para acelerar cálculos de arqueo
        db.execute_query(f"""
            CREATE INDEX IF NOT EXISTS idx_pago_denom_sesion 
            ON {schema}.t_pago_denominacion(id_sesion_caja, tipo_movimiento);
        """, commit=True)
        db.execute_query(f"""
            CREATE INDEX IF NOT EXISTS idx_pago_denom_pago 
            ON {schema}.t_pago_denominacion(id_pago);
        """, commit=True)

        logger.info("✅ Tabla t_pago_denominacion e índices creados exitosamente.")
    except Exception as e:
        logger.error(f"❌ Error en migrar_denominaciones_pago: {e}")
        raise
    finally:
        db.close_connection()

if __name__ == "__main__":
    migrar_denominaciones_pago()
