# Diagramas de Secuencia (UML 2.5) Enriquecidos — Lote 1 (CU01W a CU05W)
**Proyecto:** AuroraStore SaaS — Arquitectura Multitenant & Cloud POS  
**Destino:** Sparx Enterprise Architect (JavaScript Automation Script)  
**Estándar:** UML 2.5 / Interacción Dinámica Formal  
**Versión:** 2.0.0 (Edición Enriquecida con UIs Reales y Tablas Participantes)  

---

## 1. Resumen Ejecutivo de la Actualización

En esta versión enriquecida se superó la síntesis de "1 sola UI genérica" para modelar con fidelidad la arquitectura de presentación y persistencia de AuroraStore:
1. **Desglose de Interfaces de Usuario (Boundaries):** Se desdobla la interacción en **Vista Principal** (`*View`) y **Modales Operativos** (`*Modal`), representando el flujo exacto donde el actor abre el modal, envía los datos del formulario al backend, el modal se cierra tras la respuesta satisfactoria y la vista principal actualiza sus datos.
2. **Exclusión Estricta de Ruido:** Se omiten deliberadamente diálogos triviales de error (`errorDialog`), popups genéricos y servicios de autorización transversal (`RBAC services` o middlewares de autenticación), manteniendo el diagrama centrado en la lógica de negocio.
3. **Completitud de Entidades PostgreSQL:** Se incorporan todas las tablas que participan en consultas y validaciones relacionales del backend (incluyendo `empresa`, `t_suscripcion`, `t_sucursal`, `t_ciudad`, `t_categoria`, `t_producto_imagen`, etc.).

---

## 2. Detalle de Casos de Uso del Lote 1 Enriquecido

### CU01W — Gestionar usuarios y roles
* **Actor:** `admin : Administrador`
* **Boundaries Reales:**
  - `view : GestionUsuariosView`: Grilla de usuarios con filtros por estado y botones de acción.
  - `modal : ModalCrearUsuario`: Formulario reactivo para alta/edición de credenciales, roles y permisos.
  - `modal_suc : AsignarSucursalesModal`: Selector modal para vincular al usuario con una o más sucursales.
* **Controllers:**
  - `router : users_routes`
  - `service : users_services`
* **Entities:**
  - `empresa`, `t_usuario`, `t_rol`, `t_usuario_permiso`, `t_usuario_sucursal`, `t_bitacora`.

### CU02W — Gestionar cadena de tiendas (Empresas SaaS)
* **Actor:** `admin : Administrador`
* **Boundaries Reales:**
  - `view : GestionEmpresasView`: Listado con métricas de estado, vigencia de plan y conteo de sucursales.
  - `modal : ModalCrearEmpresa`: Formulario de datos fiscales (NIT, razón social, correo, representante).
* **Controllers:**
  - `router : tenant_routes`
  - `service : tenant_services`
* **Entities:**
  - `empresa`, `t_suscripcion`, `t_sucursal`, `t_bitacora`.

### CU03W — Gestionar sucursales
* **Actor:** `admin : AdminTienda`
* **Boundaries Reales:**
  - `view : GestionSucursalesView`: Visualizador de tiendas activas y mapas.
  - `modal : ModalCrearSucursal`: Formulario para registrar dirección, teléfono y ciudad.
* **Controllers:**
  - `router : sucursales_routes`
  - `service : sucursales_services`
* **Entities:**
  - `empresa`, `t_suscripcion`, `t_plan`, `t_sucursal`, `t_ciudad`, `t_bitacora`.

### CU04W — Gestionar productos
* **Actor:** `admin : AdminTienda`
* **Boundaries Reales:**
  - `view : GestionProductosView`: Catálogo administrativo con filtros por categoría.
  - `modal_prod : ModalCrearProducto`: Formulario para datos base, descripción, categoría y foto de portada.
  - `modal_var : DetalleVariantesModal`: Editor de variantes para tallas, colores, precios específicos y SKUs.
* **Controllers:**
  - `router : productos_routes`
  - `service : productos_services`
* **Entities:**
  - `t_categoria`, `t_producto`, `t_producto_talla_color`, `t_producto_imagen`, `t_bitacora`.

### CU05W — Gestionar categorías
* **Actor:** `admin : AdminTienda`
* **Boundaries Reales:**
  - `view : GestionCategoriasView`: Grilla de categorías con miniaturas y conteo de prendas asociadas.
  - `modal : ModalCrearCategoria`: Formulario para nombre, categoría superior e imagen ilustrativa.
* **Controllers:**
  - `router : categorias_routes`
  - `service : categorias_services`
* **Entities:**
  - `t_categoria`, `t_producto`, `t_bitacora`.

---

## 3. Instrucciones de Ejecución en Enterprise Architect

1. Abrir Sparx Enterprise Architect con el proyecto `AuroraStore`.
2. Abrir la consola de scripting: **Code / Develop > Scripting** (`Ctrl + F9`).
3. Crear un script JavaScript y pegar el contenido de [`AuroraStore_CU01W_CU05W_Sequence_FINAL_EA.js`](file:///d:/Locked%20Files%20--EY/Projectos/Examen_parcial1_S12/AuroraStore_CU01W_CU05W_Sequence_FINAL_EA.js).
4. Seleccionar el paquete destino en el **Project Browser** y ejecutar (**F5**).
5. Enterprise Architect generará el paquete `Diagramas de Secuencia (UML 2.5) - Lote 1 (CU01W-CU05W Enriquecido)`.
