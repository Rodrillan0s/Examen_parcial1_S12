# Matriz de Validación de Diagramas de Análisis de Clases (CU11W a CU15W)
**Proyecto:** AuroraStore SaaS  
**Herramienta:** Sparx Enterprise Architect (JavaScript Automation)  
**Estándar:** UML 2.5 / Metodología ICONIX (View of Participating Classes - VOPC)  
**Fecha:** 11 de Noviembre de 2026  

---

## 1. Cobertura Estructural de los 5 Casos de Uso

| Caso de Uso | Actor | Boundaries (Vistas/Modales) | Controllers (Rutas & Servicios) | Entities (Persistencia PostgreSQL / Cache) | Conectores / Multiplicidad | Estado |
| :--- | :--- | :--- | :--- | :--- | :--- | :---: |
| **CU11W**<br>Buscar y filtrar productos | Usuario / Cliente | `BusquedaFiltrosView`<br>`FiltroAvanzadoModal`<br>`ResultadoBusquedaVacioDialog`<br>`ModoOfflineBadge` | `catalogo_routes`<br>`catalogo_services`<br>`offline_cache_manager` | `t_producto`<br>`t_categoria`<br>`t_producto_talla_color`<br>`t_talla`<br>`t_color`<br>`cache_local` | • Association (Actor $\rightarrow$ Boundary)<br>• Dependency `«use»` (Boundary $\rightarrow$ Controller $\rightarrow$ Entity)<br>• DB Associations (1 a 0..*, 1 a 1..*) | **VALIDADO** |
| **CU12W**<br>Consultar detalles de producto | Usuario / Cliente | `DetalleProductoView`<br>`GuiaTallasModal`<br>`VarianteAgotadaDialog` | `catalogo_routes`<br>`catalogo_services`<br>`offline_cache_manager` | `t_producto`<br>`t_categoria`<br>`t_producto_talla_color`<br>`t_producto_imagen`<br>`cache_local` | • Association (Actor $\rightarrow$ Boundary)<br>• Dependency `«use»`<br>• DB Associations (1 a 0..*, 1 a 1..*) | **VALIDADO** |
| **CU13W**<br>Consultar disponibilidad por sucursal | Usuario / Cliente | `DisponibilidadSucursalesView`<br>`MapaUbicacionSucursalModal`<br>`SinStockGlobalDialog` | `inventario_routes`<br>`inventario_services`<br>`offline_cache_manager` | `t_sucursal`<br>`t_producto_talla_color`<br>`t_inventario`<br>`t_ciudad`<br>`cache_local` | • Association (Actor $\rightarrow$ Boundary)<br>• Dependency `«use»`<br>• DB Associations (1 a 0..*) | **VALIDADO** |
| **CU14W**<br>Gestionar reservas | Cliente / Usuario | `MisReservasView`<br>`CrearReservaModal`<br>`CancelarReservaModal`<br>`ErrorDialog` | `reserva_routes`<br>`reserva_services`<br>`offline_cache_manager` | `t_cliente`<br>`t_reserva`<br>`t_detalle_reserva`<br>`t_inventario`<br>`t_bitacora`<br>`cache_local` | • Association (Actor $\rightarrow$ Boundary)<br>• Dependency `«use»`<br>• DB Associations (1 a 0..*, 1 a 1..*) | **VALIDADO** |
| **CU15W**<br>Gestionar inventario | AdminTienda / Encargado | `InventarioSucursalesView`<br>`AjusteInventarioModal`<br>`RecepcionLoteModal`<br>`ErrorDialog` | `inventario_routes`<br>`compras_lotes_routes`<br>`inventario_services` | `t_inventario`<br>`t_movimiento_inventario`<br>`t_orden_compra`<br>`t_sucursal`<br>`t_producto_talla_color`<br>`t_bitacora` | • Association (Actor $\rightarrow$ Boundary)<br>• Dependency `«use»`<br>• DB Associations (1 a 0..*) | **VALIDADO** |

---

## 2. Verificación de Trazabilidad con Diagramas de Secuencia Previos

1. **Correspondencia de Actores:**
   - CU11W, CU12W, CU13W: `Usuario / Cliente` (coincide con la lifeline `user : Usuario`).
   - CU14W: `Cliente / Usuario` (coincide con la lifeline `cliente : Cliente`).
   - CU15W: `AdminTienda / Encargado` (coincide con la lifeline `admin : AdminTienda`).

2. **Correspondencia de Métodos y Operaciones:**
   - Los endpoints REST (`buscar_y_filtrar`, `obtener_detalle_producto`, `consultar_disponibilidad_sucursales`, `crear_reserva`, `consultar_inventario_sucursal`, `ingresar_lote_compras`) coinciden punto por punto con los mensajes HTTP de la secuencia.
   - Las operaciones de servicio (`filtrar_productos_service`, `obtener_ficha_tecnica`, `consultar_stock_por_sucursal`, `registrar_reserva_temporal`, `actualizar_stock_fisico`, `procesar_ingreso_lote`) implementan la lógica de negocio descrita en la secuencia.
   - Los métodos de persistencia DAO de cada entidad (`searchByTextAndFilters`, `findByIdWithDetails`, `findByVarianteGroupBySucursal`, `insert`, `reservarStock`, `updateStock`) formalizan las consultas SQL de las lifelines de base de datos.

3. **Prueba de Sintaxis Node.js:**
   - Comando ejecutado: `node --check AuroraStore_CU11W_CU15W_ClassAnalysis_FINAL_EA.js`
   - Resultado: **Exit Code 0 (Sin errores sintácticos)**.
   - 0 apariciones de `Repository.Execute`.
