from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import Config
from app.routes import main_routes,escrow_routes,triaje_routes,auth_routes, users_routes, tenant_routes, roles_routes, backup_routes,profile_routes, vehiculos_routes, talleres_routes, emergencias_routes, notificaciones_routes, tarifas_routes, cobros_routes, diagnostico_routes, kpis_routes,ofertas_routes
from app.routes import crm_routes



def create_app() -> FastAPI:
    app = FastAPI(
        title="API de Emergencias Vehiculares - Examen 2",
        version="1.0.0",
        description="Backend FastAPI estructurado en 3 capas"
    )

    #CONFIGURACION DE CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    #REGISTRO DE RUTAS
    app.include_router(main_routes.router)
    app.include_router(auth_routes.router,prefix='/api/auth')
    app.include_router(users_routes.router,prefix='/api/usuarios')
    app.include_router(tenant_routes.router,prefix='/api/empresas')
    app.include_router(roles_routes.router,prefix='/api/roles')
    app.include_router(backup_routes.router,prefix='/api/backup')
    app.include_router(profile_routes.router,prefix='/api/perfil')
    app.include_router(vehiculos_routes.router,prefix='/api/vehiculos')
    app.include_router(talleres_routes.router,prefix='/api/talleres')
    app.include_router(emergencias_routes.router,prefix='/api/emergencias')
    app.include_router(notificaciones_routes.router,prefix='/api/ws')
    app.include_router(tarifas_routes.router,prefix='/api/tarifas')
    app.include_router(cobros_routes.router,prefix='/api/cobros')
    app.include_router(diagnostico_routes.router) 
    app.include_router(kpis_routes.router)
    app.include_router(ofertas_routes.router,prefix='/api/ofertas')
    app.include_router(crm_routes.router,prefix="/api/crm")
    app.include_router(triaje_routes.router,prefix="/api/triaje")
    app.include_router(escrow_routes.router,prefix="/api/escrow")
    
    return app