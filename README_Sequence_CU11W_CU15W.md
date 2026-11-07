# AuroraStore — Automatización de Diagramas de Secuencia UML 2.5 en Sparx Enterprise Architect (CU11W–CU15W)

## 1. Propósito y Alcance

Este documento describe la generación automatizada de los **Diagramas de Secuencia UML 2.5** para los Casos de Uso **CU11W a CU15W** del sistema **AuroraStore SaaS**:

1. **`sd CU11W - Buscar y filtrar productos`** (Web y Móvil CU02M)
2. **`sd CU12W - Consultar detalles de producto`** (Web y Móvil CU03M)
3. **`sd CU13W - Consultar disponibilidad por sucursal`** (Web y Móvil CU04M)
4. **`sd CU14W - Gestionar reservas`** (Web y Móvil CU05M)
5. **`sd CU15W - Gestionar inventario`**

Cada caso de uso está modelado en **un único diagrama general consolidado**, integrando flujos principales, consultas con soporte offline (PWA / SQLite), validaciones de stock con bloqueos transaccionales y compras por lote/reposición.

---

## 2. Pautas Arquitectónicas y de Estilo Aplicadas

1. **Lifelines Estándar Rectangulares UML (`Object1`):**
   - Sin estereotipos `«boundary»`, `«control»` o `«entity»` en las lifelines para evitar los símbolos circulares de robustez en EA. Renderizan la **cabecera rectangular estándar** con línea vertical discontinua.
2. **Controladores con Nombres Reales del Backend FastAPI:**
   - **CU11W:** `router : catalogo_routes`, `service : catalogo_services`
   - **CU12W:** `router : catalogo_routes`, `service : catalogo_services`
   - **CU13W:** `router : inventario_routes`, `service : inventario_services`
   - **CU14W:** `router : reserva_routes`, `service : reserva_services`
   - **CU15W:** `router : inventario_routes`, `service : inventario_services`, `compras : compras_lotes_routes`
3. **Interfaces Limpias (1 UI por diagrama):**
   - `BusquedaFiltrosUI`, `DetalleProductoUI`, `DisponibilidadUI`, `ReservasUI`, `InventarioUI`.
4. **Entidades Reales de Persistencia PostgreSQL y Caché Local:**
   - `t_producto`, `t_categoria`, `t_producto_talla_color`, `t_inventario`, `t_movimiento_inventario`, `t_orden_compra`, `t_cliente`, `t_reserva`, `t_detalle_reserva`, `cache_local` y `t_bitacora`.
5. **Coordenadas Milimétricas en 4to Cuadrante:**
   - `top = -topY; bottom = -bottomY` donde algebraicamente `top > bottom`. Sin cajas vacías ni márgenes deformados.

---

## 3. Instrucciones de Ejecución en Enterprise Architect

1. En Sparx Enterprise Architect, abrir la consola de scripting: `Specialize` (o `Develop`) → `Tools` → `Scripting` (`Ctrl + F9`).
2. Abrir o crear un script en un grupo JavaScript/JScript y pegar el contenido completo de [`AuroraStore_CU11W_CU15W_Sequence_FINAL_EA.js`](file:///d:/Locked%20Files%20--EY/Projectos/Examen_parcial1_S12/AuroraStore_CU11W_CU15W_Sequence_FINAL_EA.js).
3. Seleccionar el paquete de destino en el **Project Browser** de EA y presionar **Run** (`F5`).
4. Se creará automáticamente el paquete `Diagramas de Secuencia (UML 2.5) - CU11W a CU15W` con los 5 diagramas.

---

## 4. Catálogo de Diagramas Generados

| Identificador | Nombre del Diagrama | Lifelines | Mensajes | Fragmentos Combinados |
|---|---|:---:|:---:|:---:|
| **CU11W** | `sd CU11W - Buscar y filtrar productos` | 8 | 13 | `alt` (conectividad offline/online en búsqueda) |
| **CU12W** | `sd CU12W - Consultar detalles de producto` | 8 | 13 | `alt` (conectividad offline/online en detalle) |
| **CU13W** | `sd CU13W - Consultar disponibilidad por sucursal` | 8 | 12 | `alt` (stock estimado offline vs stock real online) |
| **CU14W** | `sd CU14W - Gestionar reservas` | 10 | 17 | `alt` (reserva offline/online), `alt` (validación stock), `opt` (cliente nuevo) |
| **CU15W** | `sd CU15W - Gestionar inventario` | 10 | 18 | `alt` (inventario offline/online), movimientos manuales y orden compra |

