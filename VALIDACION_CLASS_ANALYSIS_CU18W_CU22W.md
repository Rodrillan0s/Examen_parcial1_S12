# Matriz de Validación de Diagramas de Análisis de Clases (CU18W a CU22W)
**Proyecto:** AuroraStore SaaS  
**Herramienta:** Sparx Enterprise Architect (JavaScript Automation)  
**Estándar:** UML 2.5 / Metodología ICONIX (View of Participating Classes - VOPC)  
**Fecha:** 11 de Noviembre de 2026  

---

## 1. Cobertura Estructural de los 5 Casos de Uso

| Caso de Uso | Actor | Boundaries (Vistas/Modales) | Controllers (Rutas & Servicios) | Entities (Persistencia PostgreSQL / Cache / Vistas) | Conectores / Multiplicidad | Estado |
| :--- | :--- | :--- | :--- | :--- | :--- | :---: |
| **CU18W**<br>Sincronizar operaciones pendientes | Administrador / Cajero | `CentroSyncView`<br>`ColaOfflineModal`<br>`IndicadorConexionWidget` | `SyncRouteController`<br>`SyncDomainService`<br>`CacheLocalStorageService` | `t_sync_operacion`<br>`t_inventario`<br>`t_venta`<br>`t_pago`<br>`t_bitacora` | • Association (Actor $\rightarrow$ Boundary)<br>• Dependency `«use»` (Boundary $\rightarrow$ Controller $\rightarrow$ Entity)<br>• DB Associations (1 a 1..*, 1 a 0..*) | **VALIDADO** |
| **CU19W**<br>Resolver conflictos de sincronización | Administrador | `BandejaConflictosView`<br>`ModalResolucionConflicto`<br>`AuditoriaResolucionDialog` | `SyncConflictRouteController`<br>`SyncConflictDomainService` | `t_sync_operacion`<br>`t_inventario`<br>`cache_local`<br>`t_bitacora` | • Association (Actor $\rightarrow$ Boundary)<br>• Dependency `«use»`<br>• DB Associations (1 a 0..*) | **VALIDADO** |
| **CU20W**<br>Consultar ventas, reservas e inventario | AdminTienda / Encargado | `GestionTiendaView`<br>`PanelCajasTurnoWidget`<br>`TablaVentasReservasComponent` | `KpisOperationalRouteController`<br>`KpisOperationalDomainService` | `t_sucursal`<br>`t_caja_sesion`<br>`t_venta`<br>`t_reserva`<br>`t_inventario` | • Association (Actor $\rightarrow$ Boundary)<br>• Dependency `«use»`<br>• DB Associations (1 a 1..*) | **VALIDADO** |
| **CU21W**<br>Visualizar indicadores empresariales | Administrador | `DashboardKpisView`<br>`GraficoVentasSucursalComponent`<br>`TarjetasKpiExecutiveWidget` | `KpisExecutiveRouteController`<br>`KpisExecutiveDomainService` | `empresa`<br>`t_sucursal`<br>`t_venta`<br>`t_reserva`<br>`t_inventario`<br>`t_valoracion` | • Association (Actor $\rightarrow$ Boundary)<br>• Dependency `«use»`<br>• DB Associations (1 a 1..*) | **VALIDADO** |
| **CU22W**<br>Generar reportes bajo demanda | Administrador | `MotorReportesView`<br>`EditorConsultaDinamicaModal`<br>`VisorTablaGraficosComponent` | `MotorReportesRouteController`<br>`ReportesDomainService` | `vw_ventas_reporte`<br>`vw_inventario_reporte`<br>`vw_rentabilidad_reporte`<br>`t_bitacora` | • Association (Actor $\rightarrow$ Boundary)<br>• Dependency `«use»`<br>• DB Associations (1 a 0..*) | **VALIDADO** |

---

## 2. Verificación de Trazabilidad con Diagramas de Secuencia Previos

1. **Correspondencia de Actores:**
   - CU18W: `Administrador / Cajero` (coincide con la lifeline `admin : Administrador / Cajero`).
   - CU19W: `Administrador` (coincide con la lifeline `admin : Administrador`).
   - CU20W: `AdminTienda / Encargado` (coincide con la lifeline `admin : AdminTienda / Encargado`).
   - CU21W: `Administrador` (coincide con la lifeline `admin : Administrador`).
   - CU22W: `Administrador` (coincide con la lifeline `admin : Administrador`).

2. **Correspondencia de Métodos y Operaciones:**
   - Los endpoints REST (`postLoteSync`, `getPendientesConciliacion`, `postConciliarConflicto`, `getKpisOperacionales`, `getKpisResumen`, `postParseCommand`, `postEjecutarReporte`, `postExportarPDF`) reflejan exactamente los mensajes HTTP de los diagramas de secuencia.
   - Las operaciones de dominio (`_ejecutar_lote_sync`, `validarFingerprint`, `procesarConciliacion`, `generarDashboardOperacional`, `generarKpisResumen`, `parsearComandoReporte`, `ejecutarReporte`) contienen la lógica de orquestación transaccional.
   - Las operaciones sobre tablas y vistas analíticas (`findById`, `updateStatus`, `sumVentasDia`, `sumValuacionCapital`, `executeQuery`) ejecutan las operaciones DAO identificadas en las consultas SQL de la secuencia.

3. **Prueba de Sintaxis Node.js:**
   - Comando ejecutado: `node --check AuroraStore_CU18W_CU22W_ClassAnalysis_FINAL_EA.js`
   - Resultado: **Exit Code 0 (Sin errores sintácticos)**.
   - 0 llamadas a `Repository.Execute` (libre de errores `DAO.Database [3061]`).
   - `UCRect=1` y `ShowIcons=0` aplicados en todos los elementos y diagramas para forzar notación de tabla rectangular UML.
