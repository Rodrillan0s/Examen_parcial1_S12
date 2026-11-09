# AuroraStore — Validación Estructural y de Consistencia: Diagramas de Secuencia UML 2.5 (CU18W–CU22W)

## 1. Resumen de Verificación

Se generó la suite de diagramas de secuencia para los casos de uso de sincronización offline, métricas operacionales e indicadores analíticos respetando estrictamente los patrones acordados:
- **Lifelines estándar UML:** Cabeceras rectangulares `[ Object1 ]` sin estereotipos de robustez para prevenir símbolos circulares/lollipops.
- **Controladores reales:** Mapeo verificado a rutas y servicios FastAPI (`sync_routes`, `sync_services`, `kpis_routes`, `kpis_services`, `motor_reportes_routes`, `reportes_services`).
- **Persistencia íntegra:** Tablas operacionales de base de datos (`t_sync_operacion`, `t_caja_sesion`, `t_sucursal`, `empresa`, `t_venta`, `t_reserva`, `t_inventario`, `t_valoracion`, `t_bitacora`), almacenamiento offline (`cache_local`) y vistas analíticas canónicas (`vw_ventas_reporte`, `vw_inventario_reporte`, `vw_rentabilidad_reporte`).
- **Validación sintáctica:** Aprobada al 100% con Node.js (`node --check`).

---

## 2. Matriz de Cobertura

| Caso de Uso | Nombre del Diagrama | Lifelines | Mensajes | Fragmentos Combinados | Verificación Estática | Validación Visual EA |
|---|---|:---:|:---:|:---:|:---:|:---:|
| **CU18W** | `sd CU18W - Sincronizar operaciones pendientes` | 10 | 21 | `loop` (evaluación de lote), `alt` (conflictos vs confirmación total) | **APROBADA** (`node --check`) | **Pendiente de ejecución por el usuario** |
| **CU19W** | `sd CU19W - Resolver conflictos de sincronización` | 8 | 23 | `alt` (conflicto ya resuelto vs conciliación exitosa) | **APROBADA** (`node --check`) | **Pendiente de ejecución por el usuario** |
| **CU20W** | `sd CU20W - Consultar ventas, reservas e inventario` | 9 | 14 | Consulta consolidada de turno, ventas del día, reservas y stock | **APROBADA** (`node --check`) | **Pendiente de ejecución por el usuario** |
| **CU21W** | `sd CU21W - Visualizar indicadores empresariales` | 10 | 16 | Panel analítico gerencial (ingresos 30d, sucursales, valuación stock, CSAT) | **APROBADA** (`node --check`) | **Pendiente de ejecución por el usuario** |
| **CU22W** | `sd CU22W - Generar reportes bajo demanda` | 8 | 24 | `alt` (ruteo a vistas SQL), `opt` (generación y descarga de PDF) | **APROBADA** (`node --check`) | **Pendiente de ejecución por el usuario** |

---

## 3. Desglose de Participantes por Caso de Uso

### 3.1. CU18W — Sincronizar operaciones pendientes
- **Actor:** `admin : Administrador / Cajero`
- **UI:** `ui : CentroSyncUI`
- **Backend:** `router : sync_routes`, `service : sync_services`
- **Entities & Cache:** `cache_local` (IndexedDB en PWA), `t_sync_operacion`, `t_inventario`, `t_venta`, `t_pago`, `t_bitacora`

### 3.2. CU19W — Resolver conflictos de sincronización
- **Actor:** `admin : Administrador`
- **UI:** `ui : ResolucionConflictosUI`
- **Backend:** `router : sync_routes`, `service : sync_services`
- **Entities & Cache:** `cache_local`, `t_sync_operacion`, `t_inventario`, `t_bitacora`

### 3.3. CU20W — Consultar ventas, reservas e inventario
- **Actor:** `admin : AdminTienda / Encargado`
- **UI:** `ui : GestionTiendaUI`
- **Backend:** `router : kpis_routes`, `service : kpis_services`
- **Entities:** `t_sucursal`, `t_caja_sesion`, `t_venta`, `t_reserva`, `t_inventario`

### 3.4. CU21W — Visualizar indicadores empresariales
- **Actor:** `admin : Administrador`
- **UI:** `ui : DashboardKpisUI`
- **Backend:** `router : kpis_routes`, `service : kpis_services`
- **Entities:** `empresa`, `t_sucursal`, `t_venta`, `t_reserva`, `t_inventario`, `t_valoracion`

### 3.5. CU22W — Generar reportes bajo demanda
- **Actor:** `admin : Administrador`
- **UI:** `ui : ReportesUI`
- **Backend:** `router : motor_reportes_routes`, `service : reportes_services`
- **Entities & Vistas SQL:** `vw_ventas_reporte`, `vw_inventario_reporte`, `vw_rentabilidad_reporte`, `t_bitacora`
