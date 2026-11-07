# AuroraStore — Validación Estructural y de Consistencia: Diagramas de Secuencia UML 2.5 (CU06W–CU10W)

## 1. Resumen de Verificación

Se generó la suite de diagramas de secuencia para los casos de uso CU06W a CU10W respetando los patrones acordados:
- **Lifelines estándar UML:** Cabeceras rectangulares sin estereotipos de robustez.
- **Controladores reales:** Mapeo fiel a rutas y servicios del backend FastAPI (`saas_routes`, `users_routes`, `catalogo_routes`, etc.).
- **Persistencia íntegra:** Tablas de base de datos de los diagramas de robustez y cache local para el modo offline.
- **Validación sintáctica:** Aprobada al 100% con Node.js (`node --check`).

---

## 2. Matriz de Cobertura

| Caso de Uso | Nombre del Diagrama | Lifelines | Mensajes | Fragmentos Combinados | Verificación Estática | Validación Visual EA |
|---|---|:---:|:---:|:---:|:---:|:---:|
| **CU06W** | `sd CU06W - Gestionar suscripciones empresariales` | 8 | 19 | `alt` (validación fechas/empresa) | **APROBADA** (`node --check`) | **Pendiente de ejecución por el usuario** |
| **CU07W** | `sd CU07W - Consultar plan y límites de suscripción` | 8 | 14 | `alt` (verificación suscripción activa) | **APROBADA** (`node --check`) | **Pendiente de ejecución por el usuario** |
| **CU08W** | `sd CU08W - Gestionar respaldos y restauraciones` | 6 | 17 | `alt` (resultado pg_dump/pg_restore) | **APROBADA** (`node --check`) | **Pendiente de ejecución por el usuario** |
| **CU09W** | `sd CU09W - Gestionar asignaciones de empleados a sucursales` | 9 | 18 | `alt` (validación de pertenencia de sucursal) | **APROBADA** (`node --check`) | **Pendiente de ejecución por el usuario** |
| **CU10W** | `sd CU10W - Consultar catálogo` | 8 | 20 | 2 `alt` (conectividad offline/online listado y detalle) | **APROBADA** (`node --check`) | **Pendiente de ejecución por el usuario** |

---

## 3. Desglose de Participantes por Caso de Uso

### 3.1. CU06W — Gestionar suscripciones empresariales
- **Actor:** `admin : Administrador`
- **UI:** `ui : SuscripcionesUI`
- **Backend:** `router : saas_routes`, `service : saas_services`
- **Entities:** `empresa`, `t_plan`, `t_suscripcion`, `t_bitacora`

### 3.2. CU07W — Consultar plan y límites de suscripción
- **Actor:** `admin : AdminTienda`
- **UI:** `ui : AjustesPlanUI`
- **Backend:** `router : saas_routes`, `service : saas_services`
- **Entities:** `empresa`, `t_suscripcion`, `t_plan`, `t_sucursal`

### 3.3. CU08W — Gestionar respaldos y restauraciones
- **Actor:** `admin : Administrador`
- **UI:** `ui : RespaldosUI`
- **Backend:** `router : backup_routes`, `service : backup_services`
- **Entities:** `t_respaldo`, `t_bitacora`

### 3.4. CU09W — Gestionar asignaciones de empleados a sucursales
- **Actor:** `admin : AdminTienda`
- **UI:** `ui : AsignacionesUI`
- **Backend:** `router : users_routes`, `service : asignaciones_services`
- **Entities:** `empresa`, `t_sucursal`, `t_empleado`, `t_usuario_sucursal`, `t_bitacora`

### 3.5. CU10W / CU01M — Consultar catálogo
- **Actor:** `user : Usuario`
- **UI:** `ui : CatalogoUI`
- **Backend:** `router : catalogo_routes`, `service : catalogo_services`
- **Entities:** `t_categoria`, `t_producto`, `t_producto_talla_color`, `cache_local`

