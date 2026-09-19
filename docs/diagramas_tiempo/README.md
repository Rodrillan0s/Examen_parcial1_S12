# Catálogo de Diagramas de Tiempo UML 2.5 (SI2 - UAGRM)
## Sistema E-Commerce Multi-Tenant para Venta de Ropa Aura

Este directorio contiene los **17 Diagramas de Tiempo UML 2.5** que cubren la totalidad de los **25 Casos de Uso** del sistema:
- **8 Casos de Uso Unificados Web / Móvil** (ambas interfaces comparten la misma lógica de negocio, controladores y repositorios en el backend).
- **9 Casos de Uso Específicos Web** (gestión administrativa, operaciones de sucursal, POS físico y facturación).

---

### Criterios Técnicos y Notación Formal Aplicada:
1. **Marco Exterior Formal UML 2.5**: Pestaña en esquina superior izquierda con la cabecera canónica `sd [Nombre del CU]`.
2. **Líneas de Vida Arquitectónicas**:
   - **Actor**: Interacción humana (`CLIENTE`, `ADMINISTRADOR`, `ENCARGADO SUCURSAL`, `CAJERO`).
   - **Interfaz / Boundary**: Componentes de frontend (`IU_Catalogo`, `IU_Checkout`, `IU_POS`, etc.).
   - **Controller**: Enrutador de la API (`catalogo_routes`, `pedidos_routes`, `pos_routes`, etc.).
   - **Service**: Capa de lógica de negocio y reglas (`catalogo_services`, `pedidos_services`, etc.).
   - **Repository**: Capa de acceso a datos y persistencia (`catalogo_repos`, `pedidos_repos`, etc.).
3. **Niveles de Estado Discretos**:
   - Cada participante posee estados operativos claros y ordenados verticalmente.
   - **Forma de onda ortogonal** (`#004499`) que muestra transiciones exactas de estado entre marcas de tiempo.
4. **Marcas Temporales Discretas ($t_0 \dots t_n$)**:
   - Cuadrícula temporal vertical con marcadores continuos y eje horizontal `Tiempo (t)`.
5. **Estímulos Inter-Línea de Vida (Llamadas y Retornos)**:
   - Llamadas sincrónicas con flechas rellenas y retornos con líneas discontinuas.
   - Documentan las **funciones reales** del backend invocadas en el sistema.
   - **Regla de Cátedra**: Las consultas y búsquedas públicas NO poseen registro en bitácora; las mutaciones transaccionales sí registran auditoría.

---

### Índice de Diagramas Generados

| # | Código CU | Título del Caso de Uso | Ámbito | Archivo SVG | Archivo PNG (2x) |
|---|---|---|---|---|---|
| 01 | **CU05 W/M** | Buscar y filtrar productos | Web / Móvil | [`CU05_WM_Buscar_Filtrar_Productos_Tiempo.svg`](./CU05_WM_Buscar_Filtrar_Productos_Tiempo.svg) | [`CU05_WM_Buscar_Filtrar_Productos_Tiempo.png`](./CU05_WM_Buscar_Filtrar_Productos_Tiempo.png) |
| 02 | **CU06 W/M** | Consultar detalle de producto | Web / Móvil | [`CU06_WM_Consultar_Detalle_Producto_Tiempo.svg`](./CU06_WM_Consultar_Detalle_Producto_Tiempo.svg) | [`CU06_WM_Consultar_Detalle_Producto_Tiempo.png`](./CU06_WM_Consultar_Detalle_Producto_Tiempo.png) |
| 03 | **CU07 W/M** | Consultar disponibilidad por sucursal | Web / Móvil | [`CU07_WM_Consultar_Disponibilidad_Sucursal_Tiempo.svg`](./CU07_WM_Consultar_Disponibilidad_Sucursal_Tiempo.svg) | [`CU07_WM_Consultar_Disponibilidad_Sucursal_Tiempo.png`](./CU07_WM_Consultar_Disponibilidad_Sucursal_Tiempo.png) |
| 04 | **CU08 W/M** | Gestionar carrito de compras | Web / Móvil | [`CU08_WM_Gestionar_Carrito_Compras_Tiempo.svg`](./CU08_WM_Gestionar_Carrito_Compras_Tiempo.svg) | [`CU08_WM_Gestionar_Carrito_Compras_Tiempo.png`](./CU08_WM_Gestionar_Carrito_Compras_Tiempo.png) |
| 05 | **CU09 W/M** | Realizar compra | Web / Móvil | [`CU09_WM_Realizar_Compra_Tiempo.svg`](./CU09_WM_Realizar_Compra_Tiempo.svg) | [`CU09_WM_Realizar_Compra_Tiempo.png`](./CU09_WM_Realizar_Compra_Tiempo.png) |
| 06 | **CU10 W/M** | Gestionar reservas | Web / Móvil | [`CU10_WM_Gestionar_Reservas_Tiempo.svg`](./CU10_WM_Gestionar_Reservas_Tiempo.svg) | [`CU10_WM_Gestionar_Reservas_Tiempo.png`](./CU10_WM_Gestionar_Reservas_Tiempo.png) |
| 07 | **CU11 W/M** | Consultar pedidos e historial | Web / Móvil | [`CU11_WM_Consultar_Pedidos_Historial_Tiempo.svg`](./CU11_WM_Consultar_Pedidos_Historial_Tiempo.svg) | [`CU11_WM_Consultar_Pedidos_Historial_Tiempo.png`](./CU11_WM_Consultar_Pedidos_Historial_Tiempo.png) |
| 08 | **CU26/M15 W/M** | Mostrar ubicaciones de sucursales | Web / Móvil | [`CU26_M15_WM_Mostrar_Ubicaciones_Sucursales_Tiempo.svg`](./CU26_M15_WM_Mostrar_Ubicaciones_Sucursales_Tiempo.svg) | [`CU26_M15_WM_Mostrar_Ubicaciones_Sucursales_Tiempo.png`](./CU26_M15_WM_Mostrar_Ubicaciones_Sucursales_Tiempo.png) |
| 09 | **CU_W20** | Gestionar temporadas y colecciones | Solo Web | [`CU_W20_Gestionar_Temporadas_Colecciones_Tiempo.svg`](./CU_W20_Gestionar_Temporadas_Colecciones_Tiempo.svg) | [`CU_W20_Gestionar_Temporadas_Colecciones_Tiempo.png`](./CU_W20_Gestionar_Temporadas_Colecciones_Tiempo.png) |
| 10 | **CU_W21** | Gestionar proveedores | Solo Web | [`CU_W21_Gestionar_Proveedores_Tiempo.svg`](./CU_W21_Gestionar_Proveedores_Tiempo.svg) | [`CU_W21_Gestionar_Proveedores_Tiempo.png`](./CU_W21_Gestionar_Proveedores_Tiempo.png) |
| 11 | **CU_W22** | Gestionar inventario | Solo Web | [`CU_W22_Gestionar_Inventario_Tiempo.svg`](./CU_W22_Gestionar_Inventario_Tiempo.svg) | [`CU_W22_Gestionar_Inventario_Tiempo.png`](./CU_W22_Gestionar_Inventario_Tiempo.png) |
| 12 | **CU_W23** | Gestionar disponibilidad de prendas | Solo Web | [`CU_W23_Gestionar_Disponibilidad_Prendas_Tiempo.svg`](./CU_W23_Gestionar_Disponibilidad_Prendas_Tiempo.svg) | [`CU_W23_Gestionar_Disponibilidad_Prendas_Tiempo.png`](./CU_W23_Gestionar_Disponibilidad_Prendas_Tiempo.png) |
| 13 | **CU_W24** | Registrar venta presencial POS | Solo Web | [`CU_W24_Registrar_Venta_Presencial_Tiempo.svg`](./CU_W24_Registrar_Venta_Presencial_Tiempo.svg) | [`CU_W24_Registrar_Venta_Presencial_Tiempo.png`](./CU_W24_Registrar_Venta_Presencial_Tiempo.png) |
| 14 | **CU_W25** | Atender reservas en sucursal | Solo Web | [`CU_W25_Atender_Reservas_Tiempo.svg`](./CU_W25_Atender_Reservas_Tiempo.svg) | [`CU_W25_Atender_Reservas_Tiempo.png`](./CU_W25_Atender_Reservas_Tiempo.png) |
| 15 | **CU_W27** | Procesar pago electrónico | Solo Web | [`CU_W27_Procesar_Pago_Electronico_Tiempo.svg`](./CU_W27_Procesar_Pago_Electronico_Tiempo.svg) | [`CU_W27_Procesar_Pago_Electronico_Tiempo.png`](./CU_W27_Procesar_Pago_Electronico_Tiempo.png) |
| 16 | **CU_W28** | Procesar pago en caja | Solo Web | [`CU_W28_Procesar_Pago_Caja_Tiempo.svg`](./CU_W28_Procesar_Pago_Caja_Tiempo.svg) | [`CU_W28_Procesar_Pago_Caja_Tiempo.png`](./CU_W28_Procesar_Pago_Caja_Tiempo.png) |
| 17 | **CU_W29** | Emitir comprobante de venta | Solo Web | [`CU_W29_Emitir_Comprobante_Venta_Tiempo.svg`](./CU_W29_Emitir_Comprobante_Venta_Tiempo.svg) | [`CU_W29_Emitir_Comprobante_Venta_Tiempo.png`](./CU_W29_Emitir_Comprobante_Venta_Tiempo.png) |
