# AuroraStore — Automatización de Diagramas de Secuencia UML 2.5 en Sparx Enterprise Architect (CU16W, CU17W, CU24W, CU25W)

## 1. Propósito y Alcance

Este documento describe la generación automatizada de los **Diagramas de Secuencia UML 2.5** para los Casos de Uso transaccionales de **Ventas y Devoluciones** del sistema **AuroraStore SaaS**:

1. **`sd CU16W - Registrar venta presencial`** (POS / Terminal de Caja)
2. **`sd CU17W - Registrar venta online`** (E-commerce Checkout con soporte Offline PWA / Sync)
3. **`sd CU24W - Solicitar devolución`** (Área Cliente / Devoluciones elegibles)
4. **`sd CU25W - Gestionar devoluciones`** (Bandeja Administrativa / Dictamen y Reingreso de Stock)

Cada caso de uso está modelado en **un único diagrama general consolidado**, integrando flujos principales, consultas, bloqueos de concurrencia y stock, y control de excepciones.

---

## 2. Pautas Arquitectónicas y de Estilo Aplicadas

1. **Lifelines Estándar Rectangulares UML (`Object1`):**
   - Sin estereotipos `«boundary»`, `«control»` o `«entity»` en las lifelines para evitar los círculos de robustez de EA. Renderizan la **cabecera rectangular estándar** con línea vertical discontinua.
2. **Controladores con Nombres Reales del Backend FastAPI:**
   - **CU16W:** `router : pos_routes`, `service : pos_services`
   - **CU17W:** `router : pago_routes`, `service : pago_services`
   - **CU24W:** `router : devoluciones_routes`, `service : devoluciones_services`
   - **CU25W:** `router : devoluciones_routes`, `service : devoluciones_services`
3. **Interfaces Limpias (1 UI por diagrama):**
   - `CajaPosUI`, `CheckoutUI`, `MisDevolucionesUI`, `GestionDevolucionesUI`.
4. **Entidades Reales de Persistencia PostgreSQL y Caché Local:**
   - `t_caja_sesion`, `t_venta`, `t_detalle_venta`, `t_pago`, `t_inventario`, `t_movimiento_inventario`, `t_carrito`, `t_devolucion`, `t_detalle_devolucion`, `t_cliente`, `cache_local` y `t_bitacora`.
5. **Coordenadas Milimétricas en 4to Cuadrante:**
   - `top = -topY; bottom = -bottomY` donde algebraicamente `top > bottom`. Sin cajas vacías ni márgenes deformados.

---

## 3. Instrucciones de Ejecución en Enterprise Architect

1. En Sparx Enterprise Architect, abrir la consola de scripting: `Specialize` (o `Develop`) → `Tools` → `Scripting` (`Ctrl + F9`).
2. Abrir o crear un script en un grupo JavaScript/JScript y pegar el contenido completo de [`AuroraStore_CU16W_CU17W_CU24W_CU25W_Sequence_FINAL_EA.js`](file:///d:/Locked%20Files%20--EY/Projectos/Examen_parcial1_S12/AuroraStore_CU16W_CU17W_CU24W_CU25W_Sequence_FINAL_EA.js).
3. Seleccionar el paquete de destino en el **Project Browser** de EA y presionar **Run** (`F5`).
4. Se creará automáticamente el paquete `Diagramas de Secuencia (UML 2.5) - Ventas y Devoluciones` con los 4 diagramas.

---

## 4. Catálogo de Diagramas Generados

| Identificador | Nombre del Diagrama | Lifelines | Mensajes | Fragmentos Combinados |
|---|---|:---:|:---:|:---:|
| **CU16W** | `sd CU16W - Registrar venta presencial` | 10 | 17 | `alt` (caja abierta/cerrada), `alt` (stock disponible) |
| **CU17W** | `sd CU17W - Registrar venta online` | 10 | 18 | `alt` (stock carrito), `alt` (pago online vs encolado offline) |
| **CU24W** | `sd CU24W - Solicitar devolución` | 8 | 13 | Listado compras elegibles y registro de solicitud con ticket |
| **CU25W** | `sd CU25W - Gestionar devoluciones` | 8 | 17 | `alt` (dictamen: rechazada vs aprobada), `opt` (reingreso a stock si revendible) |

