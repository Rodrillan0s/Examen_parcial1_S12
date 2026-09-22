from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import Config
from app.routes import (
        main_routes, auth_routes, users_routes, tenant_routes, 
    roles_routes, rbac_routes, sucursales_routes, bitacora_routes,
    notificaciones_routes, kpis_routes, backup_routes, profile_routes,
    ciudades_routes, media_routes, categorias_routes, tallas_colores_routes,
    productos_routes, catalogo_routes, carrito_routes, pedido_routes,
    reserva_routes, inventario_routes, pago_routes, comprobante_routes,
    caja_routes, pos_routes, caja_pago_routes, reportes_routes,
    compras_lotes_routes, asistente_routes,proveedores_routes
)
from app.reports import routes as motor_reportes_routes
from app.reports.engine.views_manager import asegurar_vistas_sql
from app.utils.migrate_compras_lotes import migrar_tablas_compras_lotes
from app.utils.db_init import inicializar_tablas_seguridad
from app.utils.rbac_migration import ejecutar_migracion_rbac
from app.utils.migrate_caja_cu24 import migrar_caja_pos
from app.utils.migrate_pago_caja_cu28_cu29 import migrar_pago_caja_cu28_cu29

def create_app() -> FastAPI:
    app = FastAPI(
        title="API E-Commerce Multi-Tenant de Ropa",
        version="2.0.0",
        description="Backend FastAPI para plataforma E-Commerce Multi-Tenant"
    )

    try:
        asegurar_vistas_sql()
    except Exception as e:
        print(f"Advertencia al asegurar vistas SQL del motor de reportes: {e}")

    try:
        migrar_tablas_compras_lotes()
    except Exception as e:
        print(f"Advertencia al migrar tablas de compras y lotes: {e}")

    try:
        ejecutar_migracion_rbac()
    except Exception as e:
        print(f"Advertencia al migrar RBAC: {e}")

    # Configuración CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:4200",
            "http://127.0.0.1:4200",
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "https://aurora-store-d20q.onrender.com",
            ""
        ],
        allow_origin_regex=r"https?://(localhost|127\.0\.0\.1)(:\d+)?",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Registro de rutas activas e-commerce
    app.include_router(main_routes.router)
    app.include_router(auth_routes.router, prefix='/api/auth')
    app.include_router(users_routes.router, prefix='/api/usuarios')
    app.include_router(tenant_routes.router, prefix='/api/empresas')
    app.include_router(sucursales_routes.router, prefix='/api/sucursales')
    app.include_router(roles_routes.router, prefix='/api/roles')
    app.include_router(rbac_routes.router, prefix='/api/rbac')
    app.include_router(bitacora_routes.router, prefix='/api/bitacora')
    app.include_router(notificaciones_routes.router, prefix='/api/ws')
    app.include_router(kpis_routes.router)
    app.include_router(kpis_routes.kpis_router)
    app.include_router(reportes_routes.router)
    app.include_router(backup_routes.router, prefix='/api/backup')
    app.include_router(profile_routes.router, prefix='/api/perfil')
    app.include_router(ciudades_routes.router, prefix='/api/ciudades')
    app.include_router(media_routes.router)
    app.include_router(categorias_routes.router, prefix='/api/categorias')
    app.include_router(tallas_colores_routes.tallas_router, prefix='/api/tallas')
    app.include_router(tallas_colores_routes.colores_router, prefix='/api/colores')
    app.include_router(productos_routes.router)
    app.include_router(catalogo_routes.router)
    app.include_router(carrito_routes.router)
    app.include_router(pedido_routes.router)
    app.include_router(reserva_routes.router)
    app.include_router(proveedores_routes.router, prefix='/api/proveedores')
    app.include_router(inventario_routes.router)
    app.include_router(pago_routes.router)     

    app.include_router(comprobante_routes.router, prefix='/api/comprobantes')
    app.include_router(caja_routes.router)
    app.include_router(pos_routes.router)
    app.include_router(caja_pago_routes.router)
    app.include_router(compras_lotes_routes.router)
    app.include_router(asistente_routes.router)
    app.include_router(motor_reportes_routes.router)


    return app