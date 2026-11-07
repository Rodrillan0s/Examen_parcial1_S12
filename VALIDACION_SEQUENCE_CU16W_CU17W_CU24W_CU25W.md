# AuroraStore — Validación Estructural y de Consistencia: Diagramas de Secuencia UML 2.5 (CU16W, CU17W, CU24W, CU25W)

## 1. Resumen de Verificación

Se generó la suite de diagramas de secuencia para los casos de uso transaccionales de ventas y devoluciones respetando los patrones acordados:
- **Lifelines estándar UML:** Cabeceras rectangulares sin estereotipos de robustez.
- **Controladores reales:** Mapeo fiel a rutas y servicios del backend FastAPI (`pos_routes`, `pago_routes`, `devoluciones_routes`).
- **Persistencia íntegra:** Tablas de base de datos de los diagramas de robustez y cache local para el modo offline.
- **Validación sintáctica:** Aprobada al 100% con Node.js (`node --check`).

---

## 2. Matriz de Cobertura

| Caso de Uso | Nombre del Diagrama | Lifelines | Mensajes | Fragmentos Combinados | Verificación Estática | Validación Visual EA |
|---|---|:---:|:---:|:---:|:---:|:---:|
| **CU16W** | `sd CU16W - Registrar venta presencial` | 10 | 17 | `alt` (caja abierta/cerrada), `alt` (stock disponible) | **APROBADA** (`node --check`) | **Pendiente de ejecución por el usuario** |
| **CU17W** | `sd CU17W - Registrar venta online` | 10 | 18 | `alt` (stock carrito), `alt` (pago online vs encolado offline) | **APROBADA** (`node --check`) | **Pendiente de ejecución por el usuario** |
| **CU24W** | `sd CU24W - Solicitar devolución` | 8 | 13 | Registro de solicitud y persistencia | **APROBADA** (`node --check`) | **Pendiente de ejecución por el usuario** |
| **CU25W** | `sd CU25W - Gestionar devoluciones` | 8 | 17 | `alt` (dictamen), `opt` (reingreso stock revendible) | **APROBADA** (`node --check`) | **Pendiente de ejecución por el usuario** |

---

## 3. Desglose de Participantes por Caso de Uso

### 3.1. CU16W — Registrar venta presencial (POS / Caja)
- **Actor:** `cajero : Cajero`
- **UI:** `ui : CajaPosUI`
- **Backend:** `router : pos_routes`, `service : pos_services`
- **Entities:** `t_caja_sesion`, `t_inventario`, `t_venta`, `t_detalle_venta`, `t_pago`, `t_bitacora`

### 3.2. CU17W / CU06M — Registrar venta online (E-commerce / Checkout)
- **Actor:** `cliente : Cliente`
- **UI:** `ui : CheckoutUI`
- **Backend:** `router : pago_routes`, `service : pago_services`
- **Entities:** `t_carrito`, `t_inventario`, `t_pago`, `t_venta`, `t_bitacora`, `cache_local`

### 3.3. CU24W / CU12M — Solicitar devolución (Cliente)
- **Actor:** `cliente : Cliente`
- **UI:** `ui : MisDevolucionesUI`
- **Backend:** `router : devoluciones_routes`, `service : devoluciones_services`
- **Entities:** `t_cliente`, `t_venta`, `t_devolucion`, `t_bitacora`

### 3.4. CU25W — Gestionar devoluciones (Bandeja Administrativa)
- **Actor:** `admin : AdminTienda`
- **UI:** `ui : GestionDevolucionesUI`
- **Backend:** `router : devoluciones_routes`, `service : devoluciones_services`
- **Entities:** `t_devolucion`, `t_inventario`, `t_movimiento_inventario`, `t_bitacora`

