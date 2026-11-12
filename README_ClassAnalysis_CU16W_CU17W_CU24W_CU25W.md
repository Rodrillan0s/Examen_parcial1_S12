# Diagramas de Análisis de Clases (UML 2.5 / ICONIX VOPC) — Lote 4 (CU16W, CU17W, CU24W, CU25W)
**Proyecto:** AuroraStore SaaS — Arquitectura Multitenant & Cloud POS  
**Destino:** Sparx Enterprise Architect (JavaScript Automation Script)  
**Formato:** Tablas UML Rectangulares (3 compartimentos) con distribución ortogonal en 5 columnas  
**Versión:** 1.0.0 (Lote 4)  

---

## 1. Resumen Ejecutivo y Estructura Arquitectónica

Este cuarto lote aborda el ciclo integral transaccional y post-venta de AuroraStore:
1. Ventas presenciales en punto de venta con control de caja y escáner (**CU16W**).
2. Ventas online por pasarela de pago y despacho/retiro (**CU17W**).
3. Solicitudes de devolución del cliente bajo la Ley N° 453 (**CU24W**).
4. Dictamen administrativo de devoluciones con reintegro a stock y nota de crédito (**CU25W**).

```
[ ACTOR ] ───> [ «boundary» VISTAS / MODALES ] ───> [ «control» ROUTES ] ───> [ «control» SERVICES ] ───> [ «entity» TABLAS POSTGRESQL ]
```

1. **Capa Boundary (`«boundary»`):**
   - Vistas maestras de POS (`CajaPosView`), Checkout (`CheckoutView`), mis devoluciones cliente (`MisDevolucionesView`) y bandeja de dictamen administrativo (`BandejaDevolucionesView`).
   - Modales interactivos con formularios reactivos para cobro en caja, pasarela de tarjetas/QR, solicitud con fotos y dictamen con reintegro a inventario.
   - Diálogos y alertas de negocio (`CajaCerradaDialog`, `ErrorPagoDialog`, `VentanaVencidaDialog`, `ErrorDialog`).

2. **Capa Control (`«control»`):**
   - **Route Controllers (`*_routes`):** Endpoints REST FastAPI para ventas presenciales (`pos_routes`), pagos online (`pago_routes`) y circuito de devoluciones (`devoluciones_routes`).
   - **Domain Services (`*_services`):** Lógica transaccional de caja (`caja_services`), liquidación de ventas (`pos_services`, `pago_services`) y validación de la ventana de 15 días de la Ley 453 con emisión de notas de crédito (`devoluciones_services`).
   - **Client Storage Controllers (`offline_cache_manager`):** Gestor de almacenamiento en cliente para persistencia de borradores y órdenes pendientes.

3. **Capa Entity (`«entity»`):**
   - Tablas reales de PostgreSQL: `t_caja_sesion`, `t_venta`, `t_detalle_venta`, `t_pago`, `t_inventario`, `t_movimiento_inventario`, `t_carrito`, `t_cliente`, `t_devolucion`, `t_bitacora` y `cache_local`.
   - Representadas como **Tablas UML Rectangulares** de 3 compartimentos con clave primaria `[PK]`, claves foráneas `[FK]`, tipos y métodos DAO.

---

## 2. Detalle de Casos de Uso del Lote 4

### CU16W — Registrar venta presencial (POS / Caja)
* **Actor:** `Cajero`
* **Boundaries:**
  - `CajaPosView`: Terminal de venta con escáner de SKU, modificación de cantidades y totalizador.
  - `CobroModal`: Selección de efectivo, tarjeta o QR, cálculo automático de cambio.
  - `ComprobanteVentaModal`: Visualización e impresión de ticket térmico / recibo digital.
  - `CajaCerradaDialog`: Alerta de bloqueo preventivo si no hay sesión de caja activa.
  - `ErrorDialog`: Notificación de stock insuficiente.
* **Controllers:**
  - `pos_routes (RouteController)`: Endpoints `/api/pos/ventas` y `/api/pos/sesion-activa`.
  - `pos_services (DomainService)`: Liquidación transaccional y descuento de existencias físicas.
  - `caja_services (DomainService)`: Acumulación de saldo en la sesión del cajero.
* **Entities:**
  - `t_caja_sesion`, `t_venta`, `t_detalle_venta`, `t_pago`, `t_inventario`, `t_bitacora`.

### CU17W / CU06M — Registrar venta online (E-commerce / Checkout)
* **Actor:** `Cliente / Usuario`
* **Boundaries:**
  - `CheckoutView`: Pantalla de checkout con selección de retiro en sucursal o envío a domicilio.
  - `PasarelaPagoModal`: Simulación/procesamiento de tarjeta de crédito/débito o QR.
  - `ConfirmacionOrdenModal`: Pantalla de éxito con código de seguimiento del pedido.
  - `ErrorPagoDialog`: Alerta de denegación o fondos insuficientes.
* **Controllers:**
  - `pago_routes (RouteController)`: Endpoints `/api/pagos/checkout` y `/api/pagos/procesar`.
  - `pago_services (DomainService)`: Reserva temporal de stock, cargo y vaciado de cesta.
  - `offline_cache_manager (ClientStorage)`: Almacenamiento local de pedidos offline (`PENDIENTE_SYNC`).
* **Entities:**
  - `t_carrito`, `t_venta`, `t_detalle_venta`, `t_pago`, `t_inventario`, `t_bitacora`.

### CU24W / CU12M — Solicitar devolución (Cliente bajo Ley 453)
* **Actor:** `Cliente / Usuario`
* **Boundaries:**
  - `MisDevolucionesView`: Grilla de devoluciones del cliente con estado y montos a favor.
  - `SolicitudDevolucionModal`: Formulario con selección de factura/ticket previo, prendas y motivo.
  - `VentanaVencidaDialog`: Alerta legal cuando se superan los 15 días calendario de la compra.
  - `ErrorDialog`: Error ante solicitudes duplicadas.
* **Controllers:**
  - `devoluciones_routes (RouteController)`: Endpoints `/api/devoluciones/mis-solicitudes` y `/api/devoluciones/solicitar`.
  - `devoluciones_services (DomainService)`: Validación de elegibilidad Ley 453 y generación de solicitud.
* **Entities:**
  - `t_cliente`, `t_venta`, `t_detalle_venta`, `t_devolucion`, `t_bitacora`.

### CU25W — Gestionar devoluciones (Bandeja Administrativa)
* **Actor:** `AdminTienda`
* **Boundaries:**
  - `BandejaDevolucionesView`: Listado de solicitudes de devolución pendientes de auditoría física.
  - `RevisionDevolucionModal`: Modal de dictamen técnico (Aprobar con reintegro a inventario / Rechazar).
  - `ComprobanteCreditoModal`: Emisión de nota de crédito / cupón digital de saldo a favor.
  - `ErrorDialog`: Alerta ante resoluciones incompletas o sin justificación.
* **Controllers:**
  - `devoluciones_routes (RouteController)`: Endpoints `/api/admin/devoluciones`.
  - `devoluciones_services (DomainService)`: Proceso de dictamen, ajuste de inventario y kardex.
* **Entities:**
  - `t_devolucion`, `t_inventario`, `t_movimiento_inventario`, `t_bitacora`.

---

## 3. Instrucciones de Ejecución en Enterprise Architect

1. Abra su proyecto en **Sparx Enterprise Architect**.
2. En el *Project Browser*, cree o seleccione el paquete destino (ejemplo: `Diagramas de Analisis de Clases (UML 2.5) - CU16W, CU17W, CU24W, CU25W`).
3. Abra la consola de Scripting presionando **`Ctrl + F9`**.
4. Cree un nuevo script **JavaScript** y pegue el contenido completo de:
   - [`AuroraStore_CU16W_CU17W_CU24W_CU25W_ClassAnalysis_FINAL_EA.js`](file:///d:/Locked%20Files%20--EY/Projectos/Examen_parcial1_S12/AuroraStore_CU16W_CU17W_CU24W_CU25W_ClassAnalysis_FINAL_EA.js)
5. Presione **Run (F5)**.
6. La consola mostrará:
   ```text
   ======================================================================
   INICIANDO GENERACIÓN DE DIAGRAMAS DE ANÁLISIS DE CLASES (CU16W, CU17W, CU24W, CU25W)
   Formato: Tablas UML Rectangulares (Boundary -> Controllers -> Entity)
   ======================================================================
   Paquete Destino: Diagramas de Analisis de Clases (UML 2.5) - CU16W, CU17W, CU24W, CU25W
    -> Construyendo: cd CU16W - Registrar venta presencial
    -> Construyendo: cd CU17W - Registrar venta online
    -> Construyendo: cd CU24W - Solicitar devolución
    -> Construyendo: cd CU25W - Gestionar devoluciones
   ======================================================================
   PROCESO COMPLETADO EXITOSAMENTE
   Diagramas creados: 4
   ======================================================================
   ```
