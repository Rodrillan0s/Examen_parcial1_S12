# Suite Completa de Diagramas de Análisis de Clases (UML / ICONIX VOPC) — AuroraStore

## 1. Visión General y Metodología

Los **Diagramas de Análisis de Clases** (denominados en la metodología **ICONIX** de Doug Rosenberg como *View of Participating Classes* o **VOPC**) constituyen el puente formal entre el **Análisis de Robustez** preliminar y el **Diseño Detallado** (Diagramas de Secuencia).

Cada diagrama presenta la colaboración estática de las clases participantes para realizar un Caso de Uso específico, adoptando estrictamente el estilo gráfico y la estructura de tres compartimentos establecida en el modelo de referencia del proyecto:

1. **Clases de Frontera / Interfaz (`Boundary / Form`)**: Representan los formularios y componentes visuales de captura, validación visual y despliegue hacia los actores (usuarios, administradores).
2. **Clases de Control (`Control / Lógica`)**: Orquestadores de la lógica de aplicación, validación de reglas de negocio, políticas de seguridad/RBAC y persistencia.
3. **Clases de Entidad (`Entity / Persistencia`)**: Clases de dominio que mapean directamente a las entidades reales de la base de datos PostgreSQL (`empresa`, `t_usuario`, `t_rol`, `t_plan`, `t_suscripcion`, `t_sucursal`, `t_bitacora`, etc.).

---

## 2. Trazabilidad Metodológica Bidireccional

- **Consistencia con Diagramas de Robustez**: Se utilizan exactamente las mismas entidades de datos y fronteras BCE modeladas en `docs/diagramas_robustez/diagramas_robustez.drawio`.
- **Consistencia con Diagramas de Secuencia**: Los métodos de control, operaciones de entidades y llamadas de frontera corresponden a las operaciones modeladas en `docs/diagramas_secuencia/diagramas_secuencia.drawio`.
- **Relaciones y Multiplicidades**: Asociaciones ortogonales con multiplicidades formales (`1`, `1..*`, `0..*`, `0..1`) conectadas estrictamente al perímetro exterior de las clases, evitando cualquier solapamiento.

---

## 3. Matriz de los 16 Diagramas de Análisis de Clases

| CU Código | Nombre del Caso de Uso | Prioridad | Clases Participantes (Boundary, Control, Entidades) | Enlaces Vectoriales y Gráficos |
| :--- | :--- | :---: | :--- | :--- |
| **CU01 W/M** | Registrar usuario | P1 | `Form Registro_Usuario`, `Control Registro`, `T_USUARIO`, `T_PERSONA`, `T_ROL`, `T_BITACORA` | [SVG](file:///d:/Locked%20Files%20--EY/Projectos/Examen_parcial1_S12/docs/diagramas_analisis_clases/CU01_WM_Registrar_Usuario_Clases.svg) \| [PNG](file:///d:/Locked%20Files%20--EY/Projectos/Examen_parcial1_S12/docs/diagramas_analisis_clases/CU01_WM_Registrar_Usuario_Clases.png) |
| **CU02 W/M** | Iniciar sesión | P1 | `Form Login_Autenticacion`, `Control Autenticacion`, `T_USUARIO`, `T_SEGURIDAD_USUARIO`, `T_DISPOSITIVO_USUARIO`, `T_BITACORA` | [SVG](file:///d:/Locked%20Files%20--EY/Projectos/Examen_parcial1_S12/docs/diagramas_analisis_clases/CU02_WM_Iniciar_Sesion_Clases.svg) \| [PNG](file:///d:/Locked%20Files%20--EY/Projectos/Examen_parcial1_S12/docs/diagramas_analisis_clases/CU02_WM_Iniciar_Sesion_Clases.png) |
| **CU03 W/M** | Gestionar perfil | P1 | `Form Gestion_Perfil`, `Control Perfil`, `T_USUARIO`, `T_SEGURIDAD_USUARIO`, `T_BITACORA` | [SVG](file:///d:/Locked%20Files%20--EY/Projectos/Examen_parcial1_S12/docs/diagramas_analisis_clases/CU03_WM_Gestionar_Perfil_Clases.svg) \| [PNG](file:///d:/Locked%20Files%20--EY/Projectos/Examen_parcial1_S12/docs/diagramas_analisis_clases/CU03_WM_Gestionar_Perfil_Clases.png) |
| **CU14 W** | Gestionar usuarios y roles | P1 | `Form Asignar_Rol/Modificar_Rol`, `Registro`, `ROL`, `Permisos`, `Modulos`, `USUARIO`, `T_BITACORA` | [SVG](file:///d:/Locked%20Files%20--EY/Projectos/Examen_parcial1_S12/docs/diagramas_analisis_clases/CU14_W_Gestionar_Usuarios_Roles_Clases.svg) \| [PNG](file:///d:/Locked%20Files%20--EY/Projectos/Examen_parcial1_S12/docs/diagramas_analisis_clases/CU14_W_Gestionar_Usuarios_Roles_Clases.png) |
| **CU15 W** | Gestionar empresas SaaS | P1 (Refact.) | `Form Empresas_SaaS`, `Control Empresas_SaaS`, `EMPRESA`, `T_SUCURSAL`, `T_SUSCRIPCION`, `T_PLAN`, `T_BITACORA` | [SVG](file:///d:/Locked%20Files%20--EY/Projectos/Examen_parcial1_S12/docs/diagramas_analisis_clases/CU15_W_Gestionar_Empresas_SaaS_Clases.svg) \| [PNG](file:///d:/Locked%20Files%20--EY/Projectos/Examen_parcial1_S12/docs/diagramas_analisis_clases/CU15_W_Gestionar_Empresas_SaaS_Clases.png) |
| **CU16 W** | Gestionar sucursales y ciudades | P1 | `Form Sucursales`, `Control Sucursales`, `T_SUCURSAL`, `EMPRESA`, `T_PLAN`, `T_SUSCRIPCION`, `T_BITACORA` | [SVG](file:///d:/Locked%20Files%20--EY/Projectos/Examen_parcial1_S12/docs/diagramas_analisis_clases/CU16_W_Gestionar_Sucursales_Ciudades_Clases.svg) \| [PNG](file:///d:/Locked%20Files%20--EY/Projectos/Examen_parcial1_S12/docs/diagramas_analisis_clases/CU16_W_Gestionar_Sucursales_Ciudades_Clases.png) |
| **CU17 W** | Gestionar productos | P1 | `Form Productos`, `Control Productos`, `T_PRODUCTO`, `T_CATEGORIA`, `T_PROVEEDOR`, `T_BITACORA` | [SVG](file:///d:/Locked%20Files%20--EY/Projectos/Examen_parcial1_S12/docs/diagramas_analisis_clases/CU17_W_Gestionar_Productos_Clases.svg) \| [PNG](file:///d:/Locked%20Files%20--EY/Projectos/Examen_parcial1_S12/docs/diagramas_analisis_clases/CU17_W_Gestionar_Productos_Clases.png) |
| **CU18 W** | Gestionar categorías | P1 | `Form Categorias`, `Control Categorias`, `T_CATEGORIA`, `T_PRODUCTO`, `T_BITACORA` | [SVG](file:///d:/Locked%20Files%20--EY/Projectos/Examen_parcial1_S12/docs/diagramas_analisis_clases/CU18_W_Gestionar_Categorias_Clases.svg) \| [PNG](file:///d:/Locked%20Files%20--EY/Projectos/Examen_parcial1_S12/docs/diagramas_analisis_clases/CU18_W_Gestionar_Categorias_Clases.png) |
| **CU19 W** | Gestionar tallas y colores | P1 | `Form Tallas_Colores`, `Control Variantes`, `T_PRODUCTO_VARIANTE`, `T_TALLA`, `T_COLOR`, `T_PRODUCTO`, `T_BITACORA` | [SVG](file:///d:/Locked%20Files%20--EY/Projectos/Examen_parcial1_S12/docs/diagramas_analisis_clases/CU19_W_Gestionar_Tallas_Colores_Clases.svg) \| [PNG](file:///d:/Locked%20Files%20--EY/Projectos/Examen_parcial1_S12/docs/diagramas_analisis_clases/CU19_W_Gestionar_Tallas_Colores_Clases.png) |
| **CU20 W** | Gestionar temporadas y colecciones | P1 | `Form Temporadas_Colecciones`, `Control Temporadas_Colecciones`, `T_TEMPORADA`, `T_COLECCION`, `T_PRODUCTO`, `T_BITACORA` | [SVG](file:///d:/Locked%20Files%20--EY/Projectos/Examen_parcial1_S12/docs/diagramas_analisis_clases/CU20_W_Gestionar_Temporadas_Colecciones_Clases.svg) \| [PNG](file:///d:/Locked%20Files%20--EY/Projectos/Examen_parcial1_S12/docs/diagramas_analisis_clases/CU20_W_Gestionar_Temporadas_Colecciones_Clases.png) |
| **CU21 W** | Gestionar proveedores | P1 | `Form Proveedores`, `Control Proveedores`, `T_PROVEEDOR`, `T_PRODUCTO`, `EMPRESA`, `T_BITACORA` | [SVG](file:///d:/Locked%20Files%20--EY/Projectos/Examen_parcial1_S12/docs/diagramas_analisis_clases/CU21_W_Gestionar_Proveedores_Clases.svg) \| [PNG](file:///d:/Locked%20Files%20--EY/Projectos/Examen_parcial1_S12/docs/diagramas_analisis_clases/CU21_W_Gestionar_Proveedores_Clases.png) |
| **CU34 W** | Gestionar planes de suscripción | P2 (Nuevo) | `Form Planes_SaaS`, `Control Planes_SaaS`, `T_PLAN`, `T_SUSCRIPCION`, `EMPRESA`, `T_BITACORA` | [SVG](file:///d:/Locked%20Files%20--EY/Projectos/Examen_parcial1_S12/docs/diagramas_analisis_clases/CU34_W_Gestionar_Planes_Suscripcion_Clases.svg) \| [PNG](file:///d:/Locked%20Files%20--EY/Projectos/Examen_parcial1_S12/docs/diagramas_analisis_clases/CU34_W_Gestionar_Planes_Suscripcion_Clases.png) |
| **CU35 W** | Gestionar suscripciones empresariales | P2 (Nuevo) | `Form Suscripcion_Empresarial`, `Control Suscripciones`, `T_SUSCRIPCION`, `T_PLAN`, `EMPRESA`, `T_SUCURSAL`, `T_BITACORA` | [SVG](file:///d:/Locked%20Files%20--EY/Projectos/Examen_parcial1_S12/docs/diagramas_analisis_clases/CU35_W_Gestionar_Suscripciones_Empresariales_Clases.svg) \| [PNG](file:///d:/Locked%20Files%20--EY/Projectos/Examen_parcial1_S12/docs/diagramas_analisis_clases/CU35_W_Gestionar_Suscripciones_Empresariales_Clases.png) |
| **CU36 W** | Consultar plan y límites de suscripción | P2 (Nuevo) | `Form Mi_Plan_Limites`, `Control Consulta_Plan`, `T_SUSCRIPCION`, `T_PLAN`, `EMPRESA`, `T_SUCURSAL`, `T_BITACORA` | [SVG](file:///d:/Locked%20Files%20--EY/Projectos/Examen_parcial1_S12/docs/diagramas_analisis_clases/CU36_W_Consultar_Plan_Limites_Suscripcion_Clases.svg) \| [PNG](file:///d:/Locked%20Files%20--EY/Projectos/Examen_parcial1_S12/docs/diagramas_analisis_clases/CU36_W_Consultar_Plan_Limites_Suscripcion_Clases.png) |
| **CU41 W** | Gestionar respaldos y restauraciones | P2 (Nuevo) | `Form Respaldos_Restauracion`, `Control Respaldos`, `T_RESPALDO_SISTEMA`, `T_SEGURIDAD_USUARIO`, `T_USUARIO`, `T_BITACORA` | [SVG](file:///d:/Locked%20Files%20--EY/Projectos/Examen_parcial1_S12/docs/diagramas_analisis_clases/CU41_W_Gestionar_Respaldos_Restauraciones_Clases.svg) \| [PNG](file:///d:/Locked%20Files%20--EY/Projectos/Examen_parcial1_S12/docs/diagramas_analisis_clases/CU41_W_Gestionar_Respaldos_Restauraciones_Clases.png) |
| **CU43 W** | Gestionar asignaciones de empleados a sucursales | P2 (Nuevo) | `Form Asignacion_Sucursales`, `Control Asignaciones`, `T_USUARIO_SUCURSAL`, `T_EMPLEADO / T_USUARIO`, `T_SUCURSAL`, `EMPRESA`, `T_BITACORA` | [SVG](file:///d:/Locked%20Files%20--EY/Projectos/Examen_parcial1_S12/docs/diagramas_analisis_clases/CU43_W_Gestionar_Asignaciones_Empleados_Sucursales_Clases.svg) \| [PNG](file:///d:/Locked%20Files%20--EY/Projectos/Examen_parcial1_S12/docs/diagramas_analisis_clases/CU43_W_Gestionar_Asignaciones_Empleados_Sucursales_Clases.png) |

---

## 4. Estructura de Archivos del Módulo

- `render_clases_base.py`: Motor de dibujo vectorial SVG y enrutamiento ortogonal con cálculo de perímetros exteriores y posicionamiento de multiplicidades.
- `generate_analisis_clases_master.py`: Script ejecutor maestro que genera y exporta en lote los 16 diagramas a SVG y PNG (2x de densidad con `resvg_py`).
- `specs_clases_auth.py`: Especificaciones de clases para Autenticación, Usuarios y Roles (CU01, CU02, CU03, CU14).
- `specs_clases_catalog.py`: Especificaciones de clases para Catálogo y Sucursales (CU15 a CU21).
- `specs_clases_saas.py`: Especificaciones de clases para Gestión SaaS y Operaciones Críticas (CU34, CU35, CU36, CU41, CU43).
