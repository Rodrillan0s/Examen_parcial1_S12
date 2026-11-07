# Changelog — Módulo de Devoluciones y Garantías (AuroraStore)

**Módulo:** Devoluciones en Mostrador y Storefront (`CU24W`, `CU25W`)  
**Marco Legal:** Ley N.º 453 (Ley General de los Derechos de las Usuarias y los Usuarios y de las Consumidoras y los Consumidores — Bolivia)  
**Ubicación:** `backend/app/modules/pedidos/services/devoluciones_services.py`, `frontend/src/app/pages/devoluciones/`  
**Base de Datos:** PostgreSQL (`t_devolucion`, `t_detalle_devolucion`, `t_movimiento_inventario`, `t_caja_sesion`)  
**Estado:** Estable / Auditoría y Especificación de Mostrador Implementadas  

---

## [2026-11-06] — Diseño de Mostrador, Búsqueda Multicriterio y Cumplimiento Ley 453

### 1. Diagnóstico del Flujo Anterior
- El cajero dependía de ingresar un identificador numérico interno (`id_venta`) que el cliente o el comprobante en mostrador rara vez conocen directamente.
- No existía una vista previa de confirmación antes de iniciar la carga de prendas devueltas.
- No se distinguían con claridad las tres consecuencias comerciales y financieras (cambio, saldo a favor o reembolso de dinero) ni el tratamiento de prendas defectuosas vs prendas en perfecto estado (Ley 453).

### 2. Cambios Implementados

#### A. Buscador Multicriterio de Ventas en Mostrador
- Se reemplazó el campo rígido de `id_venta` por un componente de búsqueda flexible con múltiples criterios:
  - **Número de comprobante/venta:** formato `V-2026-00125`.
  - **Código de seguimiento / pedido web.**
  - **Nombre o apellido del cliente.**
  - **Documento de identidad (CI / NIT).**
  - **Soporte de escáner:** lectura directa de código QR o código de barras impreso en el comprobante fiscal/recibo.

#### B. Ficha de Confirmación de Venta Encontrada
- Al encontrar una venta válida, el sistema presenta una ficha informativa previa que muestra:
  - Número de venta y fecha/hora exacta de la transacción.
  - Nombre del cliente y documento.
  - Sucursal de emisión y método de pago original (Efectivo, QR, Tarjeta).
  - Listado de productos adquiridos con desglose de:
    - Unidades compradas originalmente.
    - Unidades devueltas en solicitudes previas.
    - Unidades actualmente disponibles para devolución.

#### C. Las Tres Resoluciones de Devolución
1. **Cambio de Prenda (Sustitución):**
   - El cliente entrega la prenda adquirida y recibe otra talla o prenda equivalente.
   - Ajusta inventario: la prenda entrante se clasifica como `REVENDIBLE` o `DEFECTUOSO`, y la prenda saliente descuenta `stock_disponible`. Si existe diferencia de precio a favor de la tienda, se cobra en caja; si es a favor del cliente, se emite crédito o reembolso.
2. **Saldo a Favor (Crédito en Tienda):**
   - Se emite un crédito comercial vinculado al cliente para futuras compras en cualquiera de las sucursales del tenant.
   - No hay salida física de dinero de la caja registradora.
3. **Reembolso de Dinero:**
   - La tienda devuelve el importe exacto al cliente según el método acordado (efectivo desde la sesión activa de caja o pasarela original).
   - Genera movimiento de egreso en el arqueo de caja con motivo auditable.

#### D. Tratamiento de Prendas y Cumplimiento Ley 453
- **Prendas en buen estado (`REVENDIBLE`):** se reintegran inmediatamente al inventario vendible (`stock_disponible += cant`).
- **Defectos de fábrica (`DEFECTUOSO`):** conforme al Art. 26 y Art. 62 del Reglamento de la Ley 453, el cliente tiene derecho a reclamar la reposición o devolución sin que la falta de etiqueta o empaque original sea una causal de rechazo para vicios de fabricación. Las prendas defectuosas no ingresan a inventario vendible; se registran en cuarentena para reporte al proveedor.

---

## [2026-10-31] — Migración 005 e Integración con POS (Iteración 3)
- Aplicación de la migración `005_iter3_devoluciones.up.sql`.
- Extensión de `t_devolucion` con campos `codigo_devolucion`, `tipo_devolucion`, `evidencia_url`, `metodo_reembolso`.
- Extensión de `t_detalle_devolucion` con `condicion` (`REVENDIBLE` | `DEFECTUOSO`) y `monto_reembolso`.
