from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import Config
from app.routes import (
    main_routes, auth_routes, users_routes, tenant_routes, 
    roles_routes, rbac_routes, sucursales_routes, bitacora_routes,
    notificaciones_routes, kpis_routes, backup_routes, profile_routes,
    ciudades_routes, media_routes, categorias_routes, tallas_colores_routes,
    productos_routes, catalogo_routes, carrito_routes, pedido_routes,
    reserva_routes,proveedores_routes
)
from app.utils.db_init import inicializar_tablas_seguridad
from app.utils.rbac_migration import ejecutar_migracion_rbac

def create_app() -> FastAPI:
    # Inicializar tablas de seguridad y esquema RBAC si no existen
    try:
        inicializar_tablas_seguridad()
        ejecutar_migracion_rbac()
    except Exception as e:
        print(f"[STARTUP] Advertencia en inicialización de seguridad/RBAC: {e}")

    app = FastAPI(
        title="API E-Commerce Multi-Tenant de Ropa",
        version="2.0.0",
        description="Backend FastAPI para plataforma E-Commerce Multi-Tenant"
    )

    # Configuración CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
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
    app.include_router(proveedores_routes.router)
    return app