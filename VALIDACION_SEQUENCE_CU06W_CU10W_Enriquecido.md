# Matriz de Validación de Diagramas de Secuencia Enriquecidos (CU06W a CU10W)
**Proyecto:** AuroraStore SaaS  
**Herramienta:** Sparx Enterprise Architect (JavaScript Automation)  
**Estándar:** UML 2.5 / Interacción Dinámica  
**Fecha:** 11 de Noviembre de 2026  

---

## 1. Cobertura Estructural del Lote 2 Enriquecido

| Caso de Uso | Actor | Vistas y Modales Participantes *(Sin errorDialog)* | Controllers *(Sin RBAC Services)* | Entidades PostgreSQL / Caché Local | Fragmentos Combinados | Estado |
| :--- | :--- | :--- | :--- | :--- | :--- | :---: |
| **CU06W**<br>Gestionar suscripciones | `Administrador` | `view : HistorialSuscripcionesView`<br>`modal : ModalAsignarSuscripcion` | `saas_routes`<br>`saas_services` | `empresa`<br>`t_plan`<br>`t_suscripcion`<br>`t_bitacora` | `alt` (validación empresa activa/fechas) | **VALIDADO** |
| **CU07W**<br>Consultar plan y límites | `AdminTienda` | `view : MiPlanView`<br>`modal : ModalUpgradePlan` | `saas_routes`<br>`saas_services` | `empresa`<br>`t_suscripcion`<br>`t_plan`<br>`t_sucursal`<br>`t_bitacora` | `alt` (verificación plan vigente) | **VALIDADO** |
| **CU08W**<br>Gestionar respaldos | `Administrador` | `view : RespaldosView`<br>`modal : ModalConfirmarRestauracion` | `backup_routes`<br>`backup_services` | `t_respaldo`<br>`t_bitacora` | `alt` (espacio/I-O al generar backup) | **VALIDADO** |
| **CU09W**<br>Asignaciones empleados | `AdminTienda` | `view : ListaEmpleadosView`<br>`modal : ModalReasignarSucursales` | `users_routes`<br>`asignaciones_services` | `empresa`<br>`t_sucursal`<br>`t_empleado`<br>`t_usuario_sucursal`<br>`t_bitacora` | `alt` (validación pertenencia de sucursales) | **VALIDADO** |
| **CU10W / CU01M**<br>Consultar catálogo | `Usuario` | `view : CatalogoView`<br>`drawer : FiltrosDrawer`<br>`modal : DetalleProductoModal` | `catalogo_routes`<br>`catalogo_services` | `t_categoria`<br>`t_producto`<br>`t_producto_talla_color`<br>`cache_local` | `alt` (detección conectividad filtros)<br>`alt` (detección conectividad detalle) | **VALIDADO** |

---

## 2. Verificaciones Técnicas y Reglas de Modelado

1. **Desdoblamiento de Interfaz (Boundary):**
   - En cada caso de uso se modela la secuencia completa: `Actor` interactúa con la `View`, abre el `Modal` o `Drawer`, el componente de captura envía la petición HTTP al `Router`, y al recibir `200/201`, el `Modal` se cierra y la `View` se actualiza.
2. **Exclusión de Diálogos Triviales:**
   - 0 lifelines para `errorDialog` o toasts. Los errores se devuelven desde el router a la UI correspondiente.
3. **Exclusión de Middleware Transversal:**
   - 0 lifelines para `RBAC services` o guards de sesión.
4. **Validación Sintáctica con Node.js:**
   - Comando: `node --check AuroraStore_CU06W_CU10W_Sequence_FINAL_EA.js`
   - Resultado: **Exit Code 0 (100% aprobado)**.
