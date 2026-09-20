# Catálogo de Diagramas de Máquina de Estados UML 2.5 (SI2 - UAGRM)
## Sistema E-Commerce Multi-Tenant para Venta de Ropa Aura

Este directorio contiene los **17 Diagramas de Estado UML 2.5** que modelan el ciclo de vida, transiciones, eventos desencadenantes, condiciones de guarda y acciones de los **25 Casos de Uso** del sistema Aura:
- **8 Casos de Uso Unificados Web / Móvil** (consultas de catálogo, carrito, compras, reservas, historial y geolocalización).
- **9 Casos de Uso Específicos Web** (gestión administrativa de temporadas y proveedores, control de inventario y disponibilidad, ventas POS, atención de reservas en tienda, pasarela electrónica, cobro en caja y facturación).

---

### Criterios Técnicos y Notación Formal Aplicada (Estándar UAGRM Docente)

1. **Topologías y Arquetipos Diferenciados por Caso de Uso**:
   - **No se utilizó una plantilla genérica repetitiva**. Cada Caso de Uso cuenta con una arquitectura de transición diseñada según su dinámica real:
     * *Bifurcaciones de resultado (Branching)*: e.g. CU05 (resultados encontrados vs sin coincidencias), CU07 (stock local vs red de tiendas vs agotado), CU10 (aprobación vs sin stock), CU_W25 (vencida > 48h vs entregada vs entrega exitosa), CU_W27 (aprobado vs declinado vs desafío 3DS).
     * *Bucles interactivos (Self-Transitions & Retry Loops)*: e.g. CU06 (cambio dinámico de talla/color), CU08 (modificación incremental de cantidad), CU11 (filtrado por estado), CU26_M15 (exploración interactiva de marcadores en mapa), CU_W20/CU_W21 (corrección de errores de validación de fechas/NIT), CU_W23 (conmutación de disponibilidad por tienda), CU_W24 (escaneo continuo de códigos de barra), CU_W28 (reintento por importe insuficiente).
     * *Pipelines Transaccionales Multi-Fase*: e.g. CU09 (flujo completo de checkout, bloqueo de stock, bitácora y confirmación).
     * *Bifurcación Multicamino y Convergencia*: e.g. CU_W22 (rutas independientes para entrada por compra, baja por merma o traspaso entre sucursales, convergiendo en la actualización del saldo de kardex y bitácora).
2. **Notación Gráfica UML 2.5 (Referencia Docente CU23)**:
   - **Estado Inicial**: Círculo negro sólido (`●`).
   - **Estados Discretos**: Cajas rectangulares con esquinas redondeadas (`rx="9" ry="9"`), fondo suave gris claro (`#f4f4f4`) y borde sobrio (`#777777`).
   - **Transiciones**: Flechas directas con flecha de punta triangular cerrada (`marker-end`).
   - **Sintaxis de Transición**: `evento(parámetros) [condición_guarda] / acción()`.
   - **Regla de Cátedra sobre Bitácora**: Las consultas públicas (CU05, CU06, CU07, CU11, CU26_M15) **NO poseen registro en bitácora**. Las operaciones mutacionales y transaccionales asientan formalmente su auditoría en bitácora antes de concluir.
   - **Estado Final**: Diana concéntrica (`circle` exterior sin relleno con grosor `1.4px` y `circle` interior sólido).

---

### Índice de Diagramas Generados

| # | Código CU | Título del Caso de Uso | Topología del Ciclo de Vida | SVG | PNG (2x) |
|---|---|---|---|---|---|
| 01 | **CU05 W/M** | Buscar y filtrar productos | Bifurcación 2 Caminos (Con Resultados vs Sin Coincidencias) | [`CU05_WM_Buscar_Filtrar_Productos_Estado.svg`](./CU05_WM_Buscar_Filtrar_Productos_Estado.svg) | [`CU05_WM_Buscar_Filtrar_Productos_Estado.png`](./CU05_WM_Buscar_Filtrar_Productos_Estado.png) |
| 02 | **CU06 W/M** | Consultar detalle de producto | Pipeline con Bucle Interactivo de Variante (Talla/Color) | [`CU06_WM_Consultar_Detalle_Producto_Estado.svg`](./CU06_WM_Consultar_Detalle_Producto_Estado.svg) | [`CU06_WM_Consultar_Detalle_Producto_Estado.png`](./CU06_WM_Consultar_Detalle_Producto_Estado.png) |
| 03 | **CU07 W/M** | Consultar disponibilidad por sucursal | Bifurcación 3 Caminos (Local / Otras Tiendas / Agotado Red) | [`CU07_WM_Consultar_Disponibilidad_Sucursal_Estado.svg`](./CU07_WM_Consultar_Disponibilidad_Sucursal_Estado.svg) | [`CU07_WM_Consultar_Disponibilidad_Sucursal_Estado.png`](./CU07_WM_Consultar_Disponibilidad_Sucursal_Estado.png) |
| 04 | **CU08 W/M** | Gestionar carrito de compras | Bucle de Cantidad + Bifurcación (Eliminar vs Checkout) | [`CU08_WM_Gestionar_Carrito_Compras_Estado.svg`](./CU08_WM_Gestionar_Carrito_Compras_Estado.svg) | [`CU08_WM_Gestionar_Carrito_Compras_Estado.png`](./CU08_WM_Gestionar_Carrito_Compras_Estado.png) |
| 05 | **CU09 W/M** | Realizar compra | Pipeline Transaccional Multi-Paso + Apartado Kardex + Bitácora | [`CU09_WM_Realizar_Compra_Estado.svg`](./CU09_WM_Realizar_Compra_Estado.svg) | [`CU09_WM_Realizar_Compra_Estado.png`](./CU09_WM_Realizar_Compra_Estado.png) |
| 06 | **CU10 W/M** | Gestionar reservas | Bifurcación de Stock + Retención Activa 48h + Bitácora | [`CU10_WM_Gestionar_Reservas_Estado.svg`](./CU10_WM_Gestionar_Reservas_Estado.svg) | [`CU10_WM_Gestionar_Reservas_Estado.png`](./CU10_WM_Gestionar_Reservas_Estado.png) |
| 07 | **CU11 W/M** | Consultar pedidos e historial | Bucle de Filtro por Estado + Consulta Detallada de Seguimiento | [`CU11_WM_Consultar_Pedidos_Historial_Estado.svg`](./CU11_WM_Consultar_Pedidos_Historial_Estado.svg) | [`CU11_WM_Consultar_Pedidos_Historial_Estado.png`](./CU11_WM_Consultar_Pedidos_Historial_Estado.png) |
| 08 | **CU26/M15 W/M** | Mostrar ubicaciones de sucursales | Bucle de Selección de Pines en Mapa + Trazado de Ruta GPS | [`CU26_M15_WM_Mostrar_Ubicaciones_Sucursales_Estado.svg`](./CU26_M15_WM_Mostrar_Ubicaciones_Sucursales_Estado.svg) | [`CU26_M15_WM_Mostrar_Ubicaciones_Sucursales_Estado.png`](./CU26_M15_WM_Mostrar_Ubicaciones_Sucursales_Estado.png) |
| 09 | **CU_W20** | Gestionar temporadas y colecciones | Bucle de Validación de Rango de Fechas + Bitácora Admin | [`CU_W20_Gestionar_Temporadas_Colecciones_Estado.svg`](./CU_W20_Gestionar_Temporadas_Colecciones_Estado.svg) | [`CU_W20_Gestionar_Temporadas_Colecciones_Estado.png`](./CU_W20_Gestionar_Temporadas_Colecciones_Estado.png) |
| 10 | **CU_W21** | Gestionar proveedores | Bucle de Validación de NIT Único + Asiento en Bitácora | [`CU_W21_Gestionar_Proveedores_Estado.svg`](./CU_W21_Gestionar_Proveedores_Estado.svg) | [`CU_W21_Gestionar_Proveedores_Estado.png`](./CU_W21_Gestionar_Proveedores_Estado.png) |
| 11 | **CU_W22** | Gestionar inventario | Bifurcación 3 Vías (Entrada / Baja / Traspaso) + Kardex + Bitácora | [`CU_W22_Gestionar_Inventario_Estado.svg`](./CU_W22_Gestionar_Inventario_Estado.svg) | [`CU_W22_Gestionar_Inventario_Estado.png`](./CU_W22_Gestionar_Inventario_Estado.png) |
| 12 | **CU_W23** | Gestionar disponibilidad de prendas | Bucle Toggle por Sucursal + Política de Catálogo + Bitácora | [`CU_W23_Gestionar_Disponibilidad_Prendas_Estado.svg`](./CU_W23_Gestionar_Disponibilidad_Prendas_Estado.svg) | [`CU_W23_Gestionar_Disponibilidad_Prendas_Estado.png`](./CU_W23_Gestionar_Disponibilidad_Prendas_Estado.png) |
| 13 | **CU_W24** | Registrar venta presencial POS | Bucle Escaneo Código Barras + Descuento Inmediato + Ticket POS | [`CU_W24_Registrar_Venta_Presencial_Estado.svg`](./CU_W24_Registrar_Venta_Presencial_Estado.svg) | [`CU_W24_Registrar_Venta_Presencial_Estado.png`](./CU_W24_Registrar_Venta_Presencial_Estado.png) |
| 14 | **CU_W25** | Atender reservas en sucursal | Validación 3 Caminos (Vencida > 48h / Ya Atendida / Entrega OK) | [`CU_W25_Atender_Reservas_Estado.svg`](./CU_W25_Atender_Reservas_Estado.svg) | [`CU_W25_Atender_Reservas_Estado.png`](./CU_W25_Atender_Reservas_Estado.png) |
| 15 | **CU_W27** | Procesar pago electrónico | Pasarela 3 Caminos (Aprobado / Declinado / Desafío 3DS) + Token | [`CU_W27_Procesar_Pago_Electronico_Estado.svg`](./CU_W27_Procesar_Pago_Electronico_Estado.svg) | [`CU_W27_Procesar_Pago_Electronico_Estado.png`](./CU_W27_Procesar_Pago_Electronico_Estado.png) |
| 16 | **CU_W28** | Procesar pago en caja | Cálculo de Cambio + Reintento por Importe Insuficiente + Arqueo | [`CU_W28_Procesar_Pago_Caja_Estado.svg`](./CU_W28_Procesar_Pago_Caja_Estado.svg) | [`CU_W28_Procesar_Pago_Caja_Estado.png`](./CU_W28_Procesar_Pago_Caja_Estado.png) |
| 17 | **CU_W29** | Emitir comprobante de venta | Bifurcación (Factura Oficial con NIT/CUF vs Recibo Simple) | [`CU_W29_Emitir_Comprobante_Venta_Estado.svg`](./CU_W29_Emitir_Comprobante_Venta_Estado.svg) | [`CU_W29_Emitir_Comprobante_Venta_Estado.png`](./CU_W29_Emitir_Comprobante_Venta_Estado.png) |
