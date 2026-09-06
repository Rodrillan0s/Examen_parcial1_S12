from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import Config
from app.routes import (
    main_routes, auth_routes, users_routes, tenant_routes, 
    roles_routes, rbac_routes, sucursales_routes, bitacora_routes,
    notificaciones_routes, kpis_routes, backup_routes, profile_routes
)
from app.utils.db_init import inicializar_tablas_seguridad
from app.utils.rbac_migration import ejecutar_migracion_rbac

def create_app() -> FastAPI:
    # Inicializar tablas de seguridad y esquema RBAC si no existen
    inicializar_tablas_seguridad()
    ejecutar_migracion_rbac()

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

    return app