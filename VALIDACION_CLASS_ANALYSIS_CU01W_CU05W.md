# Matriz de Validación de Diagramas de Análisis de Clases (CU01W a CU05W)
**Proyecto:** AuroraStore SaaS  
**Herramienta:** Sparx Enterprise Architect (JavaScript Automation)  
**Estándar:** UML 2.5 / Metodología ICONIX (View of Participating Classes - VOPC)  
**Fecha:** 11 de Noviembre de 2026  

---

## 1. Cobertura Estructural de los 5 Casos de Uso

| Caso de Uso | Actor | Boundaries (Vistas/Modales) | Controllers (Rutas & Servicios) | Entities (Persistencia PostgreSQL) | Conectores / Multiplicidad | Estado |
| :--- | :--- | :--- | :--- | :--- | :--- | :---: |
| **CU01W**<br>Gestionar usuarios y roles | Administrador | `ListaUsuariosView`<br>`FormularioUsuarioModal`<br>`EliminarUsuarioModal`<br>`ErrorDialog` | `users_routes`<br>`users_services`<br>`rbac_services` | `t_usuario`<br>`t_rol`<br>`empresa`<br>`t_usuario_sucursal`<br>`t_bitacora` | • Association (Actor $\rightarrow$ Boundary)<br>• Dependency `«use»` (Boundary $\rightarrow$ Controller $\rightarrow$ Entity)<br>• DB Associations (1 a 0..*) | **VALIDADO** |
| **CU02W**<br>Gestionar empresas SaaS | SuperAdministrador | `ListaEmpresasView`<br>`FormularioEmpresaModal`<br>`EstadoEmpresaModal`<br>`ErrorDialog` | `tenant_routes`<br>`tenant_services` | `empresa`<br>`t_suscripcion`<br>`t_plan`<br>`t_usuario`<br>`t_bitacora` | • Association (Actor $\rightarrow$ Boundary)<br>• Dependency `«use»`<br>• DB Associations (1 a 1..*, 1 a 0..*) | **VALIDADO** |
| **CU03W**<br>Gestionar sucursales y ciudades | Administrador | `ListaSucursalesView`<br>`FormularioSucursalModal`<br>`EstadoSucursalModal`<br>`ErrorDialog` | `sucursales_routes`<br>`sucursales_services` | `t_sucursal`<br>`t_ciudad`<br>`empresa`<br>`t_usuario_sucursal`<br>`t_bitacora` | • Association (Actor $\rightarrow$ Boundary)<br>• Dependency `«use»`<br>• DB Associations (1 a 0..*) | **VALIDADO** |
| **CU04W**<br>Gestionar productos (Prendas y Variantes) | Administrador / Encargado | `ListaProductosView`<br>`FormularioPrendaModal`<br>`TabVariantesTallaColor`<br>`ErrorDialog` | `productos_routes`<br>`productos_services` | `t_producto`<br>`t_producto_talla_color`<br>`t_categoria`<br>`t_talla`<br>`t_color`<br>`t_inventario`<br>`t_bitacora` | • Association (Actor $\rightarrow$ Boundary)<br>• Dependency `«use»`<br>• DB Associations (1 a 0..*, 1 a 1..*) | **VALIDADO** |
| **CU05W**<br>Gestionar planes de suscripción | SuperAdministrador | `CatalogoPlanesView`<br>`FormularioPlanModal`<br>`ErrorDialog` | `saas_routes`<br>`saas_services` | `t_plan`<br>`t_suscripcion`<br>`empresa`<br>`t_bitacora` | • Association (Actor $\rightarrow$ Boundary)<br>• Dependency `«use»`<br>• DB Associations (1 a 0..*) | **VALIDADO** |

---

## 2. Verificación de Reglas ICONIX y Coherencia con Diagramas Previos

1. **Trazabilidad con Diagramas de Robustez y Secuencia:**
   - Cada clase de estereotipo `«boundary»` corresponde biunívocamente a los objetos de frontera (vistas y modales) definidos en la robustez y secuencia de CU01W a CU05W.
   - Cada clase `«control»` mapea directamente a los controladores de endpoints FastAPI (`*_routes`) y los servicios transaccionales de aplicación (`*_services`).
   - Cada clase `«entity»` corresponde fielmente a las tablas existentes en el esquema PostgreSQL de AuroraStore (`empresa`, `t_usuario`, `t_rol`, `t_sucursal`, `t_ciudad`, `t_producto`, `t_producto_talla_color`, `t_categoria`, `t_talla`, `t_color`, `t_inventario`, `t_plan`, `t_suscripcion`, `t_bitacora`).

2. **Visibilidad y Compartimentos:**
   - Atributos con visibilidad `-` (`Private`) y tipos fuertemente declarados.
   - Operaciones con visibilidad `+` (`Public`) y parámetros con tipos primitivos o DTOs.
   - Script configurado para activar automáticamente `ShowAttrs=1` y `ShowOps=1` en las propiedades del diagrama en Sparx EA.

3. **Prueba de Sintaxis Node.js:**
   - Comando ejecutado: `node --check AuroraStore_CU01W_CU05W_ClassAnalysis_FINAL_EA.js`
   - Resultado: **Exit Code 0 (Sin errores sintácticos)**.
