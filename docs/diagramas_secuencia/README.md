# Diagramas de Secuencia — Metodología ICONIX (UML 2.5+)

### Sistema AuroraStore (Aura Atelier) — Arquitectura Multi-tenant SaaS
**Materia:** Sistemas de Información II (SI2) — UAGRM  
**Estándar:** UML 2.5+ + Metodología ICONIX (Doug Rosenberg & Matt Stephens)  
**Archivo Maestro:** [`diagramas_secuencia.drawio`](./diagramas_secuencia.drawio) | [`diagramas_secuencia.xml`](./diagramas_secuencia.xml)  
**Scripts Generadores:**
- [`generate_secuencia_master.py`](./generate_secuencia_master.py) (Compilador principal multi-pestaña)
- [`specs_cu_auth.py`](./specs_cu_auth.py) (Especificaciones CU01, CU02, CU03, CU14)
- [`specs_cu_catalog.py`](./specs_cu_catalog.py) (Especificaciones CU15, CU16, CU17, CU18, CU19, CU20, CU21)
- [`specs_cu_saas.py`](./specs_cu_saas.py) (Especificaciones CU34, CU35, CU36, CU41, CU43)

---

## 1. Fundamento Metodológico: De Robustez a Secuencia

Según Doug Rosenberg (*Use Case Driven Object Modeling with UML - ICONIX Process*):
> *"Robustness analysis bridges the gap between use cases and sequence diagrams. In sequence diagrams, you allocate behavior to classes. The controls from the robustness diagram become methods on the services/controllers/entities. Only message calls (operations/functions with signatures) are sent between lifelines."*

### Reglas Estrictas de Modelado UML 2.5+:
1. **Líneas de Vida Tipadas con Estereotipos BCE:**
   - **Actor:** Usuario iniciador (Cliente, Administrador, Superadmin, etc.).
   - **Boundary (Frontera):** Componente de interfaz de usuario (`«boundary» :IU_*`) en Angular y endpoint de API (`«boundary» :*_routes`) en FastAPI.
   - **Control (Lógica de Negocio):** Servicio de dominio (`«control» :*_services`) y servicios de infraestructura/seguridad (`«control» :security_service`).
   - **Entity (Persistencia):** Repositorios de acceso a datos (`«entity» :*_repos`) mapeados a las tablas del sistema relacional PostgreSQL.
2. **Solo Firmas de Funciones (Sin Procedimientos Internos):**
   - Cada mensaje horizontal representa una **invocación a un método o función** con sus parámetros (ej. `enviar_formulario(datos)`, `buscar_por_id(id)`, `insertar_usuario(datos, hash)`).
   - Los retornos representan el resultado de la ejecución (`return dto`, `HTTP 200 OK`, `HTTP 201 Created`).
   - Los errores y excepciones están claramente tipados (`throw ConflictException(...)`, `HTTP 409 Conflict`, `HTTP 403 Forbidden`).
   - **Queda prohibido** colocar narrativas de procesos o sentencias SQL dentro de las etiquetas de función.
3. **Operadores Combinados UML 2.5+:**
   - **`loop`:** Iteraciones con guardas de condición (ej. `[para cada campo obligatorio]`, `[por cada id_sucursal]`).
   - **`alt`:** Alternativas condicionales mutuamente excluyentes delimitadas por línea discontinua (`---`), separando el Curso Básico exitoso de los Cursos Alternos de error o rechazo.
   - **`opt`:** Bloques de ejecución opcionalmente activados si se cumple una guarda específica (ej. `[huella_dispositivo != null]`, `[plan_codigo == 'PROFESIONAL']`).
4. **Barras de Activación (Execution Specifications):**
   - Rectángulos verticales en las líneas de vida que reflejan con exactitud el periodo en que la clase está activa ejecutando un método o esperando una llamada subordinada.

---

## 2. Catálogo Maestro de los 16 Diagramas de Secuencia

| # | CU | Nombre del Caso de Uso | Prioridad | Pestaña en Draw.io | Lifelines Participantes | Fragmentos UML | Mensajes |
| :---: | :---: | :--- | :---: | :--- | :--- | :---: | :---: |
| 1 | **CU01** | Registrar usuario | P1 | `CU01 - Registrar usuario (Secuencia)` | Cliente, IU_Registro, auth_routes, auth_services, security_service, usuario_repos, bitacora_repos | `loop`, `alt`, `opt` | 25 |
| 2 | **CU02** | Iniciar sesión | P1 | `CU02 - Iniciar sesión (Secuencia)` | Usuario, IU_Login, auth_routes, auth_services, security_service, usuario_repos, bitacora_repos | `alt`, `opt` | 23 |
| 3 | **CU03** | Gestionar perfil | P1 | `CU03 - Gestionar perfil (Secuencia)` | Usuario, IU_Perfil, auth_routes, auth_services, security_service, usuario_repos, bitacora_repos | `alt`, `opt` | 21 |
| 4 | **CU14** | Gestionar usuarios y roles | P1 | `CU14 - Gestionar usuarios y roles (Secuencia)` | Administrador, IU_UsuariosRoles, rbac_routes, rbac_services, usuario_repos, bitacora_repos | `loop`, `alt` | 21 |
| 5 | **CU15** | Gestionar empresas SaaS | P1 (Refac.) | `CU15 - Gestionar empresas SaaS (Secuencia)` | Superadmin, IU_EmpresasSaaS, saas_routes, saas_services, tenant_repos, bitacora_repos | `alt`, `opt` | 19 |
| 6 | **CU16** | Gestionar sucursales y ciudades | P1 | `CU16 - Gestionar sucursales y ciudades (Secuencia)` | Administrador, IU_Sucursales, sucursales_routes, sucursales_services, saas_services, sucursal_repos, bitacora_repos | `alt`, `opt` | 18 |
| 7 | **CU17** | Gestionar productos | P1 | `CU17 - Gestionar productos (Secuencia)` | Administrador, IU_Productos, productos_routes, productos_services, producto_repos, bitacora_repos | `alt`, `opt` | 17 |
| 8 | **CU18** | Gestionar categorías | P1 | `CU18 - Gestionar categorías (Secuencia)` | Administrador, IU_Categorias, categorias_routes, categorias_services, categoria_repos, bitacora_repos | `alt`, `opt` | 16 |
| 9 | **CU19** | Gestionar tallas y colores | P1 | `CU19 - Gestionar tallas y colores (Secuencia)` | Administrador, IU_Variantes, variantes_routes, variantes_services, variante_repos, bitacora_repos | `loop`, `alt` | 16 |
| 10 | **CU20** | Gestionar temporadas y colecciones | P1 | `CU20 - Gestionar temporadas y colecciones (Secuencia)` | Administrador, IU_Temporadas, temporadas_routes, temporadas_services, temporada_repos, bitacora_repos | `alt`, `opt` | 16 |
| 11 | **CU21** | Gestionar proveedores | P1 | `CU21 - Gestionar proveedores (Secuencia)` | Administrador, IU_Proveedores, proveedores_routes, proveedores_services, proveedor_repos, bitacora_repos | `alt`, `opt` | 16 |
| 12 | **CU34** | Gestionar planes de suscripción | P2 (Nuevo) | `CU34 - Gestionar planes de suscripción (Secuencia)` | Superadmin, IU_PlanesSaaS, saas_routes, saas_services, plan_repos, suscripcion_repos, bitacora_repos | `alt`, `opt` | 23 |
| 13 | **CU35** | Gestionar suscripciones empresariales | P2 (Nuevo) | `CU35 - Gestionar suscripciones empresariales (Secuencia)` | Superadmin, IU_Suscripciones, saas_routes, saas_services, plan_repos, sucursal_repos, suscripcion_repos, bitacora_repos | `alt`, `opt` | 19 |
| 14 | **CU36** | Consultar plan y límites de suscripción | P2 (Nuevo) | `CU36 - Consultar plan y límites de suscripción (Secuencia)` | Admin Tienda, IU_MiPlan, saas_routes, saas_services, suscripcion_repos, plan_repos, sucursal_repos | `alt`, `opt` | 17 |
| 15 | **CU41** | Gestionar respaldos y restauraciones | P2 (Nuevo) | `CU41 - Gestionar respaldos y restauraciones (Secuencia)` | Superadmin, IU_Respaldos, backup_routes, backup_services, security_service, respaldo_repos, bitacora_repos | `alt`, `opt` | 16 |
| 16 | **CU43** | Gestionar asignaciones de empleados a sucursales | P2 (Nuevo) | `CU43 - Gestionar asignaciones de empleados a sucursales (Secuencia)` | Admin Empresa, IU_Asignaciones, rbac_routes, asignaciones_services, sucursal_repos, usuario_sucursal_repos, empleado_repos, bitacora_repos | `loop`, `alt`, `opt` | 16 |

**Totales del Paquete:** 16 Pestañas | 366 Elementos Gráficos | 299 Mensajes de Comunicación Funcional | Tamaño: ~291 KB

---

## 3. Resumen de Flujos por Módulos Arquitectónicos

### Módulo 1: Autenticación, Seguridad y Control de Acceso (CU01, CU02, CU03, CU14)
- **CU01 (Registrar usuario):** Validación de datos de entrada en UI (`loop`), verificación de política de contraseña en `security_service`, consulta de unicidad por email en `usuario_repos`. Si es válido (`alt`), cálculo de hash Bcrypt, inserción en `t_usuario`, asignación de rol, registro opcional de hardware confiable (`opt`), emisión de JWT y registro en `bitacora_repos`. En caso alterno, retorno de error 409 Conflict.
- **CU02 (Iniciar sesión):** Búsqueda de credenciales por email. Verificación criptográfica de contraseña (`verify_hash`). Si las credenciales son válidas (`alt`), verificación opcional de MFA / hardware (`opt`), reseteo de contador de intentos, emisión de token JWT y registro en auditoría. En caso alterno, incremento de intentos fallidos, posible bloqueo temporal de cuenta y retorno de error 401 Unauthorized.
- **CU03 (Gestionar perfil):** Extracción de identidad desde JWT, validación de contraseña actual antes de actualizar credenciales. Bloque `alt` para validar que el nuevo email no esté ocupado por otro usuario. Si se actualiza contraseña (`opt`), recálculo de hash y revocación de sesiones previas.
- **CU14 (Gestionar usuarios y roles):** Validación de alcance RBAC `usuarios.gestionar`. Consulta de catálogo de roles e iteración de asignación múltiple de roles (`loop`). Bloque `alt` que impide la auto-revocación del rol administrador y previene la duplicidad de cuentas.

### Módulo 2: Catálogo, Sucursales y Modelado de Negocio (CU15, CU16, CU17, CU18, CU19, CU20, CU21)
- **CU15 (Gestionar empresas SaaS):** Alta y modificación de tenants por Superadmin. Consulta de NIT único y validación de alcance de plataforma. Bloque `opt` para inicialización de esquema tenant en base de datos. Bloque `alt` para rechazo en caso de conflicto por NIT existente o intento de borrado físico.
- **CU16 (Gestionar sucursales y ciudades):** Coordinación crítica entre `sucursales_services` y `saas_services`. Antes de persistir una nueva sucursal, se valida la cuota activa permitida por el plan de suscripción (`sucursales_activas < max_sucursales_plan`). Bloque `opt` para baja lógica operativa (`activo = false`). Bloque `alt` para rechazo 409 cuando se alcanza el tope máximo.
- **CU17 (Gestionar productos):** Verificación de código SKU único por empresa. Persistencia en `producto_repos` y vinculación opcional con categoría principal y proveedor (`opt`). Bloque `alt` para rechazo por SKU repetido o precio negativo.
- **CU18 (Gestionar categorías):** Control de árbol jerárquico (`id_categoria_padre`). Bloque `opt` para evitar referencias circulares en el árbol de categorías. Bloque `alt` para impedir la eliminación si existen productos asociados.
- **CU19 (Gestionar tallas y colores):** Creación y administración de atributos de variantes de prendas. Iteración (`loop`) sobre la lista de valores de talla/color. Bloque `alt` para validación de unicidad de nombre de variante.
- **CU20 (Gestionar temporadas y colecciones):** Control de periodos de moda [fecha_inicio, fecha_fin]. Bloque `opt` para activación de colección vigente. Bloque `alt` para rechazo en caso de fechas inconsistentes (fin < inicio).
- **CU21 (Gestionar proveedores):** Registro de suministradores de mercancía. Validación de RUC/NIT del proveedor. Bloque `alt` para evitar duplicidad de proveedores activos.

### Módulo 3: SaaS Multitenancy, Suscripciones y Resiliencia (CU34, CU35, CU36, CU41, CU43)
- **CU34 (Gestionar planes de suscripción):** Consulta de planes inmutables (`BASICO` y `PROFESIONAL`). El Superadmin solo puede modificar disponibilidad para nuevas contrataciones o descripción pública. Bloque `opt` que garantiza la inmutabilidad de suscripciones activas previamente adquiridas. Bloque `alt` para rechazar cualquier intento de crear planes con códigos arbitrarios o alterar los límites de sucursales codificados (2 y 10).
- **CU35 (Gestionar suscripciones empresariales):** Asignación administrativa de periodos [inicio, fin) a empresas cliente. Validación de no-solapamiento con periodos activos. Verificación de capacidad: `sucursales_activas <= max_sucursales_plan`. Bloque `opt` para cancelación explícita preservando el historial. Bloque `alt` para bloqueo 409 si la empresa tiene más sucursales activas que las que permite el nuevo plan solicitado.
- **CU36 (Consultar plan y límites de suscripción):** Consulta invocada por el Administrador de Tienda. Extracción segura de `id_empresa` desde el token JWT. Lectura de vigencia en `t_suscripcion`, límites en `t_plan` y conteo de sucursales en `t_sucursal`. Bloque `opt` para reportar si el plan contratado habilita reportes con IA (`PROFESIONAL`). Bloque `alt` para desplegar alertas de vencimiento o empresa suspendida.
- **CU41 (Gestionar respaldos y restauraciones):** Invocación por Superadmin con verificación estricta de permisos de infraestructura en `security_service`. Ejecución segura de volcado estructurado (`pg_dump`), cálculo de checksum SHA-256 (`opt`) y almacenamiento de metadatos en `respaldo_repos`. Bloque `alt` para captura y notificación en caso de fallo en el motor o espacio insuficiente en disco.
- **CU43 (Gestionar asignaciones de empleados a sucursales):** Recepción de array de IDs de sucursales. Iteración (`loop`) para verificar que cada sucursal pertenezca a la empresa del administrador y esté activa. Bloque `opt` para revocación total si la lista es vacía (`[]`). Bloque `alt` para ejecutar el reemplazo atómico en `t_usuario_sucursal` manteniendo intacto el registro laboral en `t_empleado`, o rechazar con 403 Forbidden si se detecta una sucursal perteneciente a otra empresa.

---

## 4. Instrucciones de Apertura y Validación

1. **Abrir en Draw.io / Diagrams.net:**
   - Navegue a [app.diagrams.net](https://app.diagrams.net/) o instale la extensión de Draw.io en su IDE.
   - Abra el archivo [`diagramas_secuencia.drawio`](./diagramas_secuencia.drawio).
   - En la barra inferior, encontrará las **16 pestañas**, cada una correspondiente a un caso de uso con su diagrama de secuencia perfectamente diagramado y separado.
2. **Re-generación o Modificación por Script:**
   - Si requiere regenerar o ajustar parámetros, ejecute desde la raíz del proyecto:
     ```bash
     python docs/diagramas_secuencia/generate_secuencia_master.py
     ```
   - El script ejecutará la validación sintáctica de Python `xml.etree.ElementTree` garantizando cero corrupción de etiquetas.
