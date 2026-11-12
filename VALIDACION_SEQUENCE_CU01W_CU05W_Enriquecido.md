# Matriz de Validación de Diagramas de Secuencia Enriquecidos (CU01W a CU05W)
**Proyecto:** AuroraStore SaaS  
**Herramienta:** Sparx Enterprise Architect (JavaScript Automation)  
**Estándar:** UML 2.5 / Interacción Dinámica  
**Fecha:** 11 de Noviembre de 2026  

---

## 1. Cobertura Estructural del Lote 1 Enriquecido

| Caso de Uso | Actor | Vistas y Modales Participantes *(Sin errorDialog)* | Controllers *(Sin RBAC Services)* | Entidades PostgreSQL Participantes | Fragmentos Combinados | Estado |
| :--- | :--- | :--- | :--- | :--- | :--- | :---: |
| **CU01W**<br>Gestionar usuarios y roles | `Administrador` | `view : GestionUsuariosView`<br>`modal : ModalCrearUsuario`<br>`modal_suc : AsignarSucursalesModal` | `users_routes`<br>`users_services` | `empresa`<br>`t_usuario`<br>`t_rol`<br>`t_usuario_permiso`<br>`t_usuario_sucursal`<br>`t_bitacora` | `alt` (validación datos/duplicado)<br>`loop` (permisos)<br>`alt` (baja lógica/protegido) | **VALIDADO** |
| **CU02W**<br>Gestionar cadena de tiendas | `Administrador` | `view : GestionEmpresasView`<br>`modal : ModalCrearEmpresa` | `tenant_routes`<br>`tenant_services` | `empresa`<br>`t_suscripcion`<br>`t_sucursal`<br>`t_bitacora` | `alt` (validación NIT)<br>`alt` (baja con sucursales activas) | **VALIDADO** |
| **CU03W**<br>Gestionar sucursales | `AdminTienda` | `view : GestionSucursalesView`<br>`modal : ModalCrearSucursal` | `sucursales_routes`<br>`sucursales_services` | `empresa`<br>`t_suscripcion`<br>`t_plan`<br>`t_sucursal`<br>`t_ciudad`<br>`t_bitacora` | `alt` (límite de plan contratado)<br>`opt` (ciudad no registrada) | **VALIDADO** |
| **CU04W**<br>Gestionar productos | `AdminTienda` | `view : GestionProductosView`<br>`modal_prod : ModalCrearProducto`<br>`modal_var : DetalleVariantesModal` | `productos_routes`<br>`productos_services` | `t_categoria`<br>`t_producto`<br>`t_producto_talla_color`<br>`t_producto_imagen`<br>`t_bitacora` | `loop` (sincronización variantes) | **VALIDADO** |
| **CU05W**<br>Gestionar categorías | `AdminTienda` | `view : GestionCategoriasView`<br>`modal : ModalCrearCategoria` | `categorias_routes`<br>`categorias_services` | `t_categoria`<br>`t_producto`<br>`t_bitacora` | `alt` (nombre duplicado)<br>`alt` (bloqueo por prendas asociadas) | **VALIDADO** |

---

## 2. Verificaciones Técnicas y Reglas de Modelado

1. **Desdoblamiento de Interfaz (Boundary):**
   - En cada caso de uso se modela la secuencia completa: `Actor` pulsa acción en la `View`, la `View` instancia/abre el `Modal`, el `Actor` diligencia el formulario en el `Modal`, el `Modal` envía la petición HTTP al `Router`, y al recibir `200/201`, el `Modal` se cierra y la `View` se refresca.
2. **Exclusión de Diálogos Triviales:**
   - 0 lifelines para `errorDialog` o toasts. Los errores se devuelven desde el router a la UI correspondiente donde se muestra el mensaje de fallo.
3. **Exclusión de Middleware Transversal:**
   - 0 lifelines para `RBAC services` o guards de sesión.
4. **Validación Sintáctica con Node.js:**
   - Comando: `node --check AuroraStore_CU01W_CU05W_Sequence_FINAL_EA.js`
   - Resultado: **Exit Code 0 (100% aprobado)**.
