# AuroraStore — Validación Estructural y de Consistencia: Diagrama de Secuencia UML 2.5 (CU26W / CU08M)

## 1. Resumen de Verificación

Se generó el diagrama de secuencia para el caso de uso de **Valoración de Productos y Servicios (CU26W / CU08M)** respetando estrictamente los patrones arquitectónicos acordados:
- **Lifelines estándar UML:** Cabeceras rectangulares `[ Object1 ]` sin estereotipos de robustez para prevenir símbolos circulares.
- **Controladores reales:** Mapeo verificado a rutas y servicios FastAPI (`valoracion_routes`, `valoracion_services`).
- **Persistencia íntegra:** Tablas de base de datos (`t_producto`, `t_producto_talla_color`, `t_valoracion`, `t_bitacora`).
- **Validación sintáctica:** Aprobada al 100% con Node.js (`node --check`).

---

## 2. Matriz de Cobertura

| Caso de Uso | Nombre del Diagrama | Lifelines | Mensajes | Fragmentos Combinados | Verificación Estática | Validación Visual EA |
|---|---|:---:|:---:|:---:|:---:|:---:|
| **CU26W / CU08M** | `sd CU26W/CU08M - Registrar valoración de producto` | 9 | 29 | `opt` (cierre voluntario), `alt` (1★ motivo obligatorio vs 2★-5★) | **APROBADA** (`node --check`) | **Pendiente de ejecución por el usuario** |

---

## 3. Desglose de Participantes

- **Actor:** `cliente : Cliente`
- **UI 1:** `ui_vta : VentaConfirmadaUI` (Pantalla de compra/reserva confirmada — `pVenta`)
- **UI 2:** `ui_val : ModalValoracionUI` (Ventana emergente modal — `vValoración`)
- **Backend Router:** `router : valoracion_routes`
- **Backend Service:** `service : valoracion_services`
- **Entidades de Dominio:**
  - `t_producto` (Consulta de datos generales de la prenda)
  - `t_producto_talla_color` (Verificación de la variante adquirida en `t_detalle_pedido` o `t_detalle_venta`)
  - `t_valoracion` (Persistencia del score 1-5, comentario, motivo_negativo y flag de revisión administrativa)
  - `t_bitacora` (Auditoría de registro y alerta de calidad 1★)
