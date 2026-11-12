# Matriz de Validación de Diagramas de Análisis de Clases (CU06W a CU10W)
**Proyecto:** AuroraStore SaaS  
**Herramienta:** Sparx Enterprise Architect (JavaScript Automation)  
**Estándar:** UML 2.5 / Metodología ICONIX (View of Participating Classes - VOPC)  
**Fecha:** 11 de Noviembre de 2026  

---

## 1. Cobertura Estructural de los 5 Casos de Uso

| Caso de Uso | Actor | Boundaries (Vistas/Modales) | Controllers (Rutas & Servicios) | Entities (Persistencia PostgreSQL / Cache) | Conectores / Multiplicidad | Estado |
| :--- | :--- | :--- | :--- | :--- | :--- | :---: |
| **CU06W**<br>Gestionar suscripciones empresariales | Administrador | `ListaSuscripcionesView`<br>`AsignacionSuscripcionModal`<br>`CancelarSuscripcionModal`<br>`ErrorDialog` | `saas_routes`<br>`saas_services` | `empresa`<br>`t_plan`<br>`t_suscripcion`<br>`t_bitacora` | • Association (Actor $\rightarrow$ Boundary)<br>• Dependency `«use»` (Boundary $\rightarrow$ Controller $\rightarrow$ Entity)<br>• DB Associations (1 a 0..*) | **VALIDADO** |
| **CU07W**<br>Consultar plan y límites de suscripción | AdminTienda | `AjustesPlanView`<br>`DetalleLimitesModal`<br>`ErrorDialog` | `saas_routes`<br>`saas_services` | `empresa`<br>`t_suscripcion`<br>`t_plan`<br>`t_sucursal` | • Association (Actor $\rightarrow$ Boundary)<br>• Dependency `«use»`<br>• DB Associations (1 a 0..*) | **VALIDADO** |
| **CU08W**<br>Gestionar respaldos y restauraciones | Administrador | `RespaldosView`<br>`GenerarRespaldoModal`<br>`RestaurarModal`<br>`ErrorDialog` | `backup_routes`<br>`backup_services` | `t_respaldo`<br>`t_usuario`<br>`t_bitacora` | • Association (Actor $\rightarrow$ Boundary)<br>• Dependency `«use»`<br>• DB Associations (1 a 0..*) | **VALIDADO** |
| **CU09W**<br>Gestionar asignaciones de empleados a sucursales | AdminTienda | `ListaAsignacionesView`<br>`AsignarSucursalesModal`<br>`SucursalPrincipalModal`<br>`ErrorDialog` | `users_routes`<br>`asignaciones_services` | `empresa`<br>`t_sucursal`<br>`t_usuario`<br>`t_empleado`<br>`t_usuario_sucursal`<br>`t_bitacora` | • Association (Actor $\rightarrow$ Boundary)<br>• Dependency `«use»`<br>• DB Associations (1 a 0..*, 1 a 0..1) | **VALIDADO** |
| **CU10W**<br>Consultar catálogo (Web y Móvil) | Usuario / Cliente | `CatalogoPublicoView`<br>`FiltroCatalogoSidebar`<br>`FichaDetalleProductoModal`<br>`OfflineStatusBar` | `catalogo_routes`<br>`catalogo_services`<br>`offline_cache_manager` | `t_producto`<br>`t_categoria`<br>`t_producto_talla_color`<br>`t_talla`<br>`t_color`<br>`cache_local` | • Association (Actor $\rightarrow$ Boundary)<br>• Dependency `«use»`<br>• DB Associations (1 a 0..*, 1 a 1..*) | **VALIDADO** |

---

## 2. Verificación de Reglas ICONIX y Coherencia con Diagramas Previos

1. **Correspondencia con Diagramas de Secuencia y Robustez:**
   - Cada clase de estereotipo `«boundary»` implementa los componentes de interfaz de usuario establecidos en los diagramas de robustez previos y la secuencia aprobada de CU06W a CU10W.
   - Cada clase `«control»` modela con exactitud los endpoints FastAPI (`*_routes`), servicios transaccionales (`*_services`) y coordinadores locales (`offline_cache_manager`).
   - Cada clase `«entity»` reproduce la estructura real de PostgreSQL (`empresa`, `t_plan`, `t_suscripcion`, `t_sucursal`, `t_respaldo`, `t_usuario`, `t_empleado`, `t_usuario_sucursal`, `t_producto`, `t_categoria`, `t_producto_talla_color`, `t_talla`, `t_color`, `t_bitacora`) y la persistencia local en cliente (`cache_local`).

2. **Visibilidad y Compartimentos:**
   - Atributos privados (`-`) fuertemente tipados.
   - Métodos públicos (`+`) con parámetros tipados y valores de retorno definidos.
   - Script con forzado de visibilidad de compartimentos (`ShowAttrs=1`, `ShowOps=1`) en la tabla `t_diagram` de Enterprise Architect.

3. **Prueba de Sintaxis Node.js:**
   - Comando ejecutado: `node --check AuroraStore_CU06W_CU10W_ClassAnalysis_FINAL_EA.js`
   - Resultado: **Exit Code 0 (Sin errores de compilación ni de sintaxis)**.
