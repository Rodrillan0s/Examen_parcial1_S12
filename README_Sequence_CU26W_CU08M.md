# AuroraStore — Automatización de Diagramas de Secuencia UML 2.5 en Sparx Enterprise Architect (CU26W / CU08M)

## 1. Propósito y Alcance

Este documento describe la generación automatizada del **Diagrama de Secuencia UML 2.5** para el Caso de Uso de **Valoración de Productos y Servicios (CU26W / CU08M)** del sistema **AuroraStore SaaS**:

- **`sd CU26W/CU08M - Registrar valoración de producto`**

El caso de uso está modelado en **un único diagrama general consolidado**, integrando:
- El flujo de conclusión de compra y apertura del pop-up modal (`ui_vta : VentaConfirmadaUI` hacia `ui_val : ModalValoracionUI`).
- El fragmento `opt` para el **Flujo A1** (Cierre voluntario del modal sin registrar valoración).
- El fragmento `alt` distinguiendo el **Flujo A2** (Calificación crítica de 1 estrella, que despliega panel de motivos negativos en rojo y activa la alerta de revisión administrativa `requiere_revision = TRUE`) frente al **Flujo Normal** (Calificación de 2 a 5 estrellas con comentario opcional).
- La validación de compra verificada sobre `t_producto` y `t_producto_talla_color`.
- La persistencia relacional en `t_valoracion` y la auditoría en `t_bitacora`.

---

## 2. Pautas Arquitectónicas y de Estilo Aplicadas

1. **Lifelines Estándar Rectangulares UML (`[ Object1 ]`):**
   - Sin estereotipos `«boundary»`, `«control»` o `«entity»` en las lifelines. EA dibuja la **cabecera rectangular estándar UML** con su línea de vida vertical discontinua.
2. **Controladores con Nombres Reales del Backend FastAPI:**
   - Router: [`router : valoracion_routes`](file:///d:/Locked%20Files%20--EY/Projectos/Examen_parcial1_S12/backend/app/modules/valoraciones/routes/valoracion_routes.py)
   - Servicio: [`service : valoracion_services`](file:///d:/Locked%20Files%20--EY/Projectos/Examen_parcial1_S12/backend/app/modules/valoraciones/services/valoracion_services.py)
3. **Interfaces Limpias y Trazables:**
   - `ui_vta : VentaConfirmadaUI` (correspondiente a `pVenta`)
   - `ui_val : ModalValoracionUI` (correspondiente a `vValoración`)
4. **Entidades Reales de Persistencia PostgreSQL:**
   - `t_producto`, `t_producto_talla_color`, `t_valoracion`, `t_bitacora`.
5. **Coordenadas Milimétricas en 4to Cuadrante:**
   - `top = -topY; bottom = -bottomY` donde `top > bottom`. Los fragmentos combinados (`opt`, `alt`) envuelven con exactitud sus mensajes sin recuadros vacíos.
6. **Compatibilidad COM de Enterprise Architect:**
   - Actualización directa de secuencia (`t_connector.SeqNo`) y formato discontinuo de retornos (`t_connector.PDATA4 = '1'`) mediante `Repository.Execute()`.

---

## 3. Instrucciones de Ejecución en Enterprise Architect

1. En Sparx Enterprise Architect, abrir la consola de scripting: `Specialize` (o `Develop`) → `Tools` → `Scripting` (`Ctrl + F9`).
2. Abrir o crear un script en un grupo JavaScript/JScript y pegar el contenido completo de [`AuroraStore_CU26W_CU08M_Sequence_FINAL_EA.js`](file:///d:/Locked%20Files%20--EY/Projectos/Examen_parcial1_S12/AuroraStore_CU26W_CU08M_Sequence_FINAL_EA.js).
3. Seleccionar el paquete de destino en el **Project Browser** de EA y presionar **Run** (`F5`).
4. Se creará automáticamente el paquete `Diagramas de Secuencia (UML 2.5) - Valoracion de Productos y Servicios` con el diagrama.

---

## 4. Catálogo del Diagrama Generado

| Identificador | Nombre del Diagrama | Lifelines | Mensajes | Fragmentos Combinados |
|---|---|:---:|:---:|:---:|
| **CU26W / CU08M** | `sd CU26W/CU08M - Registrar valoración de producto` | 9 | 29 | `opt` (cierre voluntario sin persistencia), `alt` (1 estrella con motivo crítico vs 2 a 5 estrellas) |
