# Diagramas de Análisis de Clases (UML 2.5 / ICONIX VOPC) — Lote 3 (CU11W a CU15W)
**Proyecto:** AuroraStore SaaS — Arquitectura Multitenant & Cloud POS  
**Destino:** Sparx Enterprise Architect (JavaScript Automation Script)  
**Formato:** Tablas UML Rectangulares (3 compartimentos) con distribución ortogonal en 5 columnas  
**Versión:** 1.0.0 (Lote 3)  

---

## 1. Resumen Ejecutivo y Estructura Arquitectónica

Este tercer lote formaliza estáticamente en **Sparx Enterprise Architect** los casos de uso correspondientes al núcleo de operaciones de catálogo, fichas de producto, disponibilidad multitienda, reservas y control de inventario/kardex:

```
[ ACTOR ] ───> [ «boundary» VISTAS / MODALES ] ───> [ «control» ROUTES ] ───> [ «control» SERVICES ] ───> [ «entity» TABLAS POSTGRESQL ]
```

1. **Capa Boundary (`«boundary»`):**
   - Vistas maestras de catálogo interactivo, fichas de detalle, grillas de sucursales, reservas de clientes y control de existencias en tiendas.
   - Modales de filtrado faceted, guía de tallas, selección de fecha/hora de probador y recepción de lotes.
   - Diálogos y banners de conectividad (`ResultadoBusquedaVacioDialog`, `VarianteAgotadaDialog`, `ModoOfflineBadge`, `SinStockGlobalDialog`, `ErrorDialog`).

2. **Capa Control (`«control»`):**
   - **Route Controllers (`*_routes`):** Endpoints REST FastAPI para búsqueda de catálogo (`catalogo_routes`), verificación de existencias (`inventario_routes`), reserva de prendas (`reserva_routes`) e ingreso de compras (`compras_lotes_routes`).
   - **Domain Services (`*_services`):** Lógica transaccional de negocio para búsqueda con facetas, resolución de fichas de prenda, bloqueo temporal de stock por reserva y generación de kardex en `t_movimiento_inventario`.
   - **Client Storage Controllers (`offline_cache_manager`):** Gestor de base de datos local (IndexedDB en Angular / SQLite en Flutter) para resiliencia offline.

3. **Capa Entity (`«entity»`):**
   - Tablas reales de PostgreSQL: `t_producto`, `t_categoria`, `t_producto_talla_color`, `t_talla`, `t_color`, `t_producto_imagen`, `t_sucursal`, `t_ciudad`, `t_inventario`, `t_cliente`, `t_reserva`, `t_detalle_reserva`, `t_movimiento_inventario`, `t_orden_compra`, `t_bitacora` y `cache_local`.
   - Modeladas como **Tablas UML Rectangulares** con claves primarias `[PK]`, claves foráneas `[FK]`, tipos y métodos DAO.

---

## 2. Detalle de Casos de Uso del Lote 3

### CU11W / CU02M — Buscar y filtrar productos (Web y Móvil)
* **Actor:** `Usuario / Cliente`
* **Boundaries:**
  - `BusquedaFiltrosView`: Búsqueda reactiva por texto, chips de filtros y paginación.
  - `FiltroAvanzadoModal`: Selectores de categorías, tallas, colores y slider de precios.
  - `ResultadoBusquedaVacioDialog`: Alerta con sugerencias ortográficas cuando no hay coincidencias.
  - `ModoOfflineBadge`: Indicador de estado de base de datos local.
* **Controllers:**
  - `catalogo_routes (RouteController)`: Endpoints `/api/catalogo/buscar`.
  - `catalogo_services (DomainService)`: Motor de filtros combinados y agregación de facetas.
  - `offline_cache_manager (ClientStorage)`: Búsqueda local por tokens en SQLite / IndexedDB.
* **Entities:**
  - `t_producto`, `t_categoria`, `t_producto_talla_color`, `t_talla`, `t_color`, `cache_local`.

### CU12W / CU03M — Consultar detalles de producto (Web y Móvil)
* **Actor:** `Usuario / Cliente`
* **Boundaries:**
  - `DetalleProductoView`: Galería fotográfica en carrusel, selector de talla/color y precio dinámico.
  - `GuiaTallasModal`: Tabla de correspondencia de medidas corporales.
  - `VarianteAgotadaDialog`: Notificación de SKU sin stock con sugerencia de variante disponible.
* **Controllers:**
  - `catalogo_routes (RouteController)`: Endpoints `/api/catalogo/productos/{id}`.
  - `catalogo_services (DomainService)`: Síntesis de ficha técnica y empaquetado de galería.
  - `offline_cache_manager (ClientStorage)`: Recuperación de ficha desde caché local.
* **Entities:**
  - `t_producto`, `t_categoria`, `t_producto_talla_color`, `t_producto_imagen`, `cache_local`.

### CU13W / CU04M — Consultar disponibilidad por sucursal (Web y Móvil)
* **Actor:** `Usuario / Cliente`
* **Boundaries:**
  - `DisponibilidadSucursalesView`: Listado de tiendas del tenant con existencias físicas en tiempo real.
  - `MapaUbicacionSucursalModal`: Modal informativo con dirección, teléfono y horarios de atención.
  - `SinStockGlobalDialog`: Notificación de agotamiento total de la variante en todas las tiendas.
* **Controllers:**
  - `inventario_routes (RouteController)`: Endpoints `/api/inventario/disponibilidad`.
  - `inventario_services (DomainService)`: Agrupación de stock por tienda y verificación de umbral mínimo.
  - `offline_cache_manager (ClientStorage)`: Consulta de sucursales precargadas sin conexión.
* **Entities:**
  - `t_sucursal`, `t_producto_talla_color`, `t_inventario`, `t_ciudad`, `cache_local`.

### CU14W / CU05M — Gestionar reservas (Web y Móvil)
* **Actor:** `Cliente / Usuario`
* **Boundaries:**
  - `MisReservasView`: Historial de reservas con semáforo de estado (Pendiente, Confirmada, Vencida).
  - `CrearReservaModal`: Selección de tienda, fecha/hora y prendas para prueba en vestidor.
  - `CancelarReservaModal`: Diálogo para anulación anticipada y liberación inmediata de existencias.
  - `ErrorDialog`: Alerta por falta de stock o superación del límite de reservas activas.
* **Controllers:**
  - `reserva_routes (RouteController)`: Endpoints `/api/reservas`.
  - `reserva_services (DomainService)`: Transacciones de reserva, bloqueo de stock y expiración a 48h.
  - `offline_cache_manager (ClientStorage)`: Almacenamiento local de borradores y encolamiento a `SyncCoordinator`.
* **Entities:**
  - `t_cliente`, `t_reserva`, `t_detalle_reserva`, `t_inventario`, `t_bitacora`, `cache_local`.

### CU15W — Gestionar inventario (Movimientos y Lotes)
* **Actor:** `AdminTienda / Encargado`
* **Boundaries:**
  - `InventarioSucursalesView`: Grilla de stock actual, alertas de punto de reorden y selector de tienda.
  - `AjusteInventarioModal`: Formulario de corrección manual de stock (merma, ajuste físico, daño).
  - `RecepcionLoteModal`: Ingreso masivo de mercadería vinculado a orden de compra.
  - `ErrorDialog`: Bloqueo ante stock negativo o falta de permisos en la sucursal.
* **Controllers:**
  - `inventario_routes (RouteController)`: Endpoints `/api/inventario/sucursal/{id}`.
  - `compras_lotes_routes (RouteController)`: Endpoints `/api/compras/lotes`.
  - `inventario_services (DomainService)`: Modificación de `stock_actual` y registro en kardex.
* **Entities:**
  - `t_inventario`, `t_movimiento_inventario`, `t_orden_compra`, `t_sucursal`, `t_producto_talla_color`, `t_bitacora`.

---

## 3. Instrucciones de Ejecución en Enterprise Architect

1. Abra su proyecto en **Sparx Enterprise Architect**.
2. En el *Project Browser*, cree o seleccione el paquete destino (ejemplo: `Diagramas de Analisis de Clases (UML 2.5) - CU11W a CU15W`).
3. Abra la consola de Scripting presionando **`Ctrl + F9`**.
4. Cree un nuevo script **JavaScript** y pegue el contenido completo de:
   - [`AuroraStore_CU11W_CU15W_ClassAnalysis_FINAL_EA.js`](file:///d:/Locked%20Files%20--EY/Projectos/Examen_parcial1_S12/AuroraStore_CU11W_CU15W_ClassAnalysis_FINAL_EA.js)
5. Presione **Run (F5)**.
6. La consola mostrará:
   ```text
   ======================================================================
   INICIANDO GENERACIÓN DE DIAGRAMAS DE ANÁLISIS DE CLASES (CU11W - CU15W)
   Formato: Tablas UML Rectangulares (Boundary -> Controllers -> Entity)
   ======================================================================
   Paquete Destino: Diagramas de Analisis de Clases (UML 2.5) - CU11W a CU15W
    -> Construyendo: cd CU11W - Buscar y filtrar productos
    -> Construyendo: cd CU12W - Consultar detalles de producto
    -> Construyendo: cd CU13W - Consultar disponibilidad por sucursal
    -> Construyendo: cd CU14W - Gestionar reservas
    -> Construyendo: cd CU15W - Gestionar inventario
   ======================================================================
   PROCESO COMPLETADO EXITOSAMENTE
   Diagramas creados: 5
   ======================================================================
   ```
