# Diagramas de Análisis de Clases (UML 2.5 / ICONIX VOPC) — Lote 5 (CU18W a CU22W)
**Proyecto:** AuroraStore SaaS — Arquitectura Multitenant & Cloud POS  
**Destino:** Sparx Enterprise Architect (JavaScript Automation Script)  
**Formato:** Tablas UML Rectangulares (3 compartimentos) con distribución ortogonal en 5 columnas  
**Versión:** 1.0.0 (Lote 5)  

---

## 1. Resumen Ejecutivo y Estructura Arquitectónica

Este quinto lote cubre los subsistemas críticos de **Resiliencia Operacional (Offline Sync)** y **Business Intelligence & Analítica Estratégica**:
1. Sincronización en lote de operaciones offline y colas de contingencia (**CU18W**).
2. Resolución y conciliación de conflictos de sincronización (**CU19W**).
3. Monitoreo operativo en tienda de ventas, reservas, stock y turnos de caja (**CU20W**).
4. Dashboard ejecutivo multitenant con indicadores estratégicos de ingresos, capital e inventario (**CU21W**).
5. Motor dinámico de reportes bajo demanda con procesamiento en lenguaje natural, vistas analíticas y exportación PDF/Excel (**CU22W**).

```
[ ACTOR ] ───> [ «boundary» VISTAS / MODALES ] ───> [ «control» ROUTES ] ───> [ «control» SERVICES ] ───> [ «entity» TABLAS & VISTAS POSTGRESQL ]
```

1. **Capa Boundary (`«boundary»`):**
   - Vistas maestras de sincronización (`CentroSyncView`), bandeja de incidencias (`BandejaConflictosView`), gestión operativa de tienda (`GestionTiendaView`), dashboard de métricas estratégicas (`DashboardKpisView`) y explorador dinámico de reportes (`MotorReportesView`).
   - Modales interactivos para auditoría de cola offline, resolución de conflictos con estrategia de balance, visor de turnos de caja y generador visual de consultas dinámicas.
   - Widgets y componentes reactivos: `IndicadorConexionWidget`, `PanelCajasTurnoWidget`, `TarjetasKpiExecutiveWidget`, `GraficoVentasSucursalComponent`, `VisorTablaGraficosComponent`.

2. **Capa Control (`«control»`):**
   - **Route Controllers (`*_routes`):** Endpoints REST FastAPI para sincronización por lotes (`sync_routes`), métricas operativas y estratégicas (`kpis_routes`) y motor analítico (`motor_reportes_routes`).
   - **Domain Services (`*_services`):** Sincronización atómica y detección de colisiones (`sync_services`), consolidación de KPIs multitenant (`kpis_services`), y parser NLQ con generador de documentos tabulares/gráficos (`reportes_services`).
   - **Client Storage Services (`cache_local` / IndexedDB):** Adaptador de base de datos offline para control de colas, marcas en tránsito y retención de operaciones conflictivas.

3. **Capa Entity (`«entity»`):**
   - Tablas reales de persistencia y vistas analíticas de PostgreSQL: `t_sync_operacion`, `t_inventario`, `t_venta`, `t_pago`, `t_caja_sesion`, `t_reserva`, `empresa`, `t_sucursal`, `t_valoracion`, `vw_ventas_reporte`, `vw_inventario_reporte`, `vw_rentabilidad_reporte`, `t_bitacora` y `cache_local`.
   - Todas renderizadas como **Tablas UML Rectangulares** estándar (3 compartimentos) con visibilidad, tipos de datos, claves primarias/foráneas y signaturas de métodos DAO.

---

## 2. Detalle de Casos de Uso del Lote 5

### CU18W — Sincronizar operaciones pendientes (Offline Sync & Lotes)
* **Actor:** `Administrador / Cajero`
* **Boundaries:**
  - `CentroSyncView`: Panel de control de conectividad, tamaño de lote en cola y acciones de sincronización.
  - `ColaOfflineModal`: Inspección detallada de payloads pendientes y purga de recibos confirmados.
  - `IndicadorConexionWidget`: Monitoreo de latencia y disparo automático de auto-sync al restablecer conexión.
* **Controllers:**
  - `SyncRouteController (sync_routes)`: Endpoints `/api/v1/sync/lote`, `/api/v1/sync/pendientes-conciliacion` y `/api/v1/sync/heartbeat`.
  - `SyncDomainService (sync_services)`: Procesamiento atómico en lote, deduplicación por fingerprint SHA-256 y detección de contingencias de inventario.
  - `CacheLocalStorageService`: Gestor cliente de IndexedDB para despacho y purga local.
* **Entities:**
  - `t_sync_operacion`, `t_inventario`, `t_venta`, `t_pago`, `t_bitacora`.

### CU19W — Resolver conflictos de sincronización (Bandeja de Conciliación)
* **Actor:** `Administrador`
* **Boundaries:**
  - `BandejaConflictosView`: Grilla de incidencias de sincronización con estado `CONFLICT` y código de error.
  - `ModalResolucionConflicto`: Comparativa de payload local vs estado en base de datos central y selección de estrategia (`FORZAR`, `DESCARTAR`, `AJUSTE_MANUAL`).
  - `AuditoriaResolucionDialog`: Diálogo modal de justificación con firma de supervisor.
* **Controllers:**
  - `SyncConflictRouteController (sync_routes)`: Endpoints `/api/v1/sync/pendientes-conciliacion` y `/api/v1/sync/conciliar/{id}`.
  - `SyncConflictDomainService (sync_services)`: Aplicación transaccional de reglas de conciliación y balance de stock.
* **Entities:**
  - `t_sync_operacion`, `t_inventario`, `cache_local`, `t_bitacora`.

### CU20W — Consultar ventas, reservas e inventario (Gestión Operacional de Tienda)
* **Actor:** `AdminTienda / Encargado`
* **Boundaries:**
  - `GestionTiendaView`: Consolidado operativo por sucursal con alertas de bajo stock en tiempo real.
  - `PanelCajasTurnoWidget`: Estado de la sesión de caja abierta, fondo de apertura y cobros del turno.
  - `TablaVentasReservasComponent`: Lista de tickets emitidos y reservas pendientes de retiro.
* **Controllers:**
  - `KpisOperationalRouteController (kpis_routes)`: Endpoints `/api/v1/kpis/operacionales` y `/api/v1/kpis/caja-turno`.
  - `KpisOperationalDomainService (kpis_services)`: Agregación de transacciones diarias, rotación y alertas de reposición.
* **Entities:**
  - `t_sucursal`, `t_caja_sesion`, `t_venta`, `t_reserva`, `t_inventario`.

### CU21W — Visualizar indicadores empresariales (Dashboard Estratégico Ejecutivo)
* **Actor:** `Administrador`
* **Boundaries:**
  - `DashboardKpisView`: Tablero multitenant con selectores de período y filtros por sucursal.
  - `GraficoVentasSucursalComponent`: Gráfico comparativo de rendimiento comercial y participación por tienda.
  - `TarjetasKpiExecutiveWidget`: Tarjetas ejecutivas de ingresos, ticket promedio, transacciones y CSAT.
* **Controllers:**
  - `KpisExecutiveRouteController (kpis_routes)`: Endpoints `/api/v1/kpis/resumen`, `/api/v1/kpis/ventas-sucursal` y `/api/v1/kpis/satisfaccion`.
  - `KpisExecutiveDomainService (kpis_services)`: Métricas financieras, valuación de inventario y rating promedio.
* **Entities:**
  - `empresa`, `t_sucursal`, `t_venta`, `t_reserva`, `t_inventario`, `t_valoracion`.

### CU22W — Generar reportes bajo demanda (Motor Dinámico & Vistas Analíticas)
* **Actor:** `Administrador`
* **Boundaries:**
  - `MotorReportesView`: Barra de comandos analíticos con procesamiento asistido y ejecución inmediata.
  - `EditorConsultaDinamicaModal`: Constructor visual de reportes con selección de dimensiones, métricas y filtros.
  - `VisorTablaGraficosComponent`: Visualizador tabular con ordenamiento dinámico, totales y gráficos dinámicos.
* **Controllers:**
  - `MotorReportesRouteController (motor_reportes_routes)`: Endpoints `/api/v1/motor-reportes/parse-command`, `/api/v1/motor-reportes/ejecutar` y `/api/v1/motor-reportes/exportar/pdf`.
  - `ReportesDomainService (reportes_services)`: Parser de lenguaje natural, compilador SQL seguro y generador documental.
* **Entities & Vistas Analíticas:**
  - `vw_ventas_reporte`, `vw_inventario_reporte`, `vw_rentabilidad_reporte`, `t_bitacora`.

---

## 3. Instrucciones de Ejecución en Enterprise Architect

1. Abrir Sparx Enterprise Architect con el proyecto `AuroraStore.eap / .feap / .qea`.
2. Abrir la consola de scripting: Menú **Code / Develop > Scripting** (o atajo `Ctrl + F9`).
3. Crear un nuevo script de tipo **JavaScript** dentro de un grupo de scripting de usuario (ej. *Local Scripts*).
4. Copiar y pegar el contenido íntegro del archivo [`AuroraStore_CU18W_CU22W_ClassAnalysis_FINAL_EA.js`](file:///d:/Locked%20Files%20--EY/Projectos/Examen_parcial1_S12/AuroraStore_CU18W_CU22W_ClassAnalysis_FINAL_EA.js).
5. En el **Project Browser**, seleccionar el paquete raíz deseado.
6. Presionar **Run (F5)** en la ventana de Scripting.
7. Al finalizar, Enterprise Architect habrá creado el subpaquete:
   `Diagramas de Análisis de Clases (ICONIX) - Lote 5 (CU18W-CU22W)` con los 5 diagramas ortogonales generados.
