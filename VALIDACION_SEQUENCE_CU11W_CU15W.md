# AuroraStore — Validación Estructural y de Consistencia: Diagramas de Secuencia UML 2.5 (CU11W–CU15W)

## 1. Resumen de Verificación

Se generó la suite de diagramas de secuencia para los casos de uso CU11W a CU15W respetando los patrones acordados:
- **Lifelines estándar UML:** Cabeceras rectangulares sin estereotipos de robustez.
- **Controladores reales:** Mapeo fiel a rutas y servicios del backend FastAPI (`catalogo_routes`, `inventario_routes`, `reserva_routes`, `compras_lotes_routes`).
- **Persistencia íntegra:** Tablas de base de datos de los diagramas de robustez y cache local para el modo offline.
- **Validación sintáctica:** Aprobada al 100% con Node.js (`node --check`).

---

## 2. Matriz de Cobertura

| Caso de Uso | Nombre del Diagrama | Lifelines | Mensajes | Fragmentos Combinados | Verificación Estática | Validación Visual EA |
|---|---|:---:|:---:|:---:|:---:|:---:|
| **CU11W** | `sd CU11W - Buscar y filtrar productos` | 8 | 13 | `alt` (offline vs online) | **APROBADA** (`node --check`) | **Pendiente de ejecución por el usuario** |
| **CU12W** | `sd CU12W - Consultar detalles de producto` | 8 | 13 | `alt` (offline vs online) | **APROBADA** (`node --check`) | **Pendiente de ejecución por el usuario** |
| **CU13W** | `sd CU13W - Consultar disponibilidad por sucursal` | 8 | 12 | `alt` (offline vs online) | **APROBADA** (`node --check`) | **Pendiente de ejecución por el usuario** |
| **CU14W** | `sd CU14W - Gestionar reservas` | 10 | 17 | `alt` (offline/online), `alt` (validación stock), `opt` (cliente nuevo) | **APROBADA** (`node --check`) | **Pendiente de ejecución por el usuario** |
| **CU15W** | `sd CU15W - Gestionar inventario` | 10 | 18 | `alt` (inventario offline/online) | **APROBADA** (`node --check`) | **Pendiente de ejecución por el usuario** |

---

## 3. Desglose de Participantes por Caso de Uso

### 3.1. CU11W / CU02M — Buscar y filtrar productos
- **Actor:** `user : Usuario`
- **UI:** `ui : BusquedaFiltrosUI`
- **Backend:** `router : catalogo_routes`, `service : catalogo_services`
- **Entities:** `t_categoria`, `t_producto`, `t_producto_talla_color`, `cache_local`

### 3.2. CU12W / CU03M — Consultar detalles de producto
- **Actor:** `user : Usuario`
- **UI:** `ui : DetalleProductoUI`
- **Backend:** `router : catalogo_routes`, `service : catalogo_services`
- **Entities:** `t_categoria`, `t_producto`, `t_producto_talla_color`, `cache_local`

### 3.3. CU13W / CU04M — Consultar disponibilidad por sucursal
- **Actor:** `user : Usuario`
- **UI:** `ui : DisponibilidadUI`
- **Backend:** `router : inventario_routes`, `service : inventario_services`
- **Entities:** `t_sucursal`, `t_producto_talla_color`, `t_inventario`, `cache_local`

### 3.4. CU14W / CU05M — Gestionar reservas
- **Actor:** `cliente : Cliente`
- **UI:** `ui : ReservasUI`
- **Backend:** `router : reserva_routes`, `service : reserva_services`
- **Entities:** `t_cliente`, `t_inventario`, `t_reserva`, `t_detalle_reserva`, `t_bitacora`, `cache_local`

### 3.5. CU15W — Gestionar inventario
- **Actor:** `admin : AdminTienda`
- **UI:** `ui : InventarioUI`
- **Backend:** `router : inventario_routes`, `service : inventario_services`, `compras : compras_lotes_routes`
- **Entities:** `t_inventario`, `t_movimiento_inventario`, `t_orden_compra`, `t_bitacora`, `cache_local`

