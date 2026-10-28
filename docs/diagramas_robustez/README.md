# Diagramas de Robustez Unificados — Metodología ICONIX (UML 2.5)

### Sistema AuroraStore (Aura Atelier) — Arquitectura Multi-tenant SaaS
**Materia:** Sistemas de Información II (SI2) — UAGRM  
**Estándar:** UML 2.5 + Metodología ICONIX (Doug Rosenberg & Matt Stephens)  
**Formato de Entrega:** Archivo maestro unificado en Draw.io (`.drawio` / `.xml`) con pestañas independientes para los 16 Casos de Uso.

---

## 1. Fundamento Metodológico ICONIX

Siguiendo el estándar riguroso de la metodología ICONIX y las directrices docentes de la cátedra:
- **Panel Lateral de Especificación (Izquierda):** Cuadro descriptivo formal con el **Curso Básico (Basic Course)** numerado secuencialmente y los **Cursos Alternativos (Alternate Courses)** en viñetas.
- **Simbología y Roles BCE (Boundary - Control - Entity):**
  - **Actor:** Rol humano o externo que interactúa con la frontera del sistema (`shape=umlActor`).
  - **Boundary (`├○`):** Pantallas, formularios, vistas o interfaces de usuario (`shape=umlBoundary`).
  - **Control (`↺○`):** Lógica transaccional de negocio, validaciones, orquestación y reglas (`shape=umlControl`).
  - **Entity (`○_`):** Entidades persistentes de la base de datos relacional PostgreSQL mapeadas al esquema real (`empresa`, `t_usuario`, `t_suscripcion`, etc.) (`shape=umlEntity`).
- **Flujos Alternativos y Excepciones en ROJO:**
  - Controladores alternativos y pantallas de error/alerta resaltados en color **ROJO (`fillColor=#ea4335`, `strokeColor=#b91c1c`)**.
  - Conexiones de excepción representadas con líneas segmentadas rojas (`strokeColor=#dc2626`, `dashed=1`).
- **Disposición Espacial Ortogonal:**
  - Distribución por capas o niveles horizontales (`y=145`, `y=370`, `y=550`, `y=740`) garantizando cero solapamiento de cajas, etiquetas ni líneas.

---

## 2. Archivo Maestro Unificado Draw.io

Todos los diagramas solicitados se encuentran consolidados en un **único archivo multi-pestaña**:

- **Archivo Maestro:** [`diagramas_robustez.drawio`](./diagramas_robustez.drawio)
- **Copia XML Estándar:** [`diagramas_robustez.xml`](./diagramas_robustez.xml)
- **Script Generador Reproducible:** [`generate_robustez_master.py`](./generate_robustez_master.py)

---

## 3. Matriz de los 16 Casos de Uso Modelados

| N° | Código | Nombre del Caso de Uso | Tipo / Prioridad | Actor Principal | Entidades PostgreSQL Involucradas |
| :---: | :---: | :--- | :---: | :--- | :--- |
| **1** | `CU01W / CU01M` | Registrar usuario | P1 | Cliente | `t_usuario`, `t_usuario_rol`, `t_rol`, `t_dispositivo_usuario`, `t_bitacora` |
| **2** | `CU02W / CU02M` | Iniciar sesión | P1 | Usuario | `t_usuario`, `t_seguridad_usuario`, `t_usuario_rol`, `t_usuario_sucursal`, `t_bitacora` |
| **3** | `CU03W / CU03M` | Gestionar perfil | P1 | Usuario Autenticado | `t_usuario`, `t_seguridad_usuario`, `t_bitacora` |
| **4** | `CU14W` | Gestionar usuarios y roles | P1 | Administrador | `t_usuario`, `t_rol`, `t_usuario_rol`, `empresa`, `t_bitacora` |
| **5** | `CU15W` | Gestionar empresas SaaS | P1 — Refactorización | Superadmin Plataforma | `empresa`, `t_suscripcion`, `t_sucursal`, `t_bitacora` |
| **6** | `CU16W` | Gestionar sucursales y ciudades | P1 | Administrador Empresa | `t_sucursal`, `t_ciudad`, `t_suscripcion`, `t_plan`, `t_bitacora` |
| **7** | `CU17W` | Gestionar productos | P1 | Encargado Catálogo | `t_producto`, `t_categoria`, `t_marca`, `t_bitacora` |
| **8** | `CU18W` | Gestionar categorías | P1 | Encargado Catálogo | `t_categoria`, `t_producto`, `t_bitacora` |
| **9** | `CU19W` | Gestionar tallas y colores | P1 | Encargado Inventario | `t_producto_talla_color`, `t_talla`, `t_color`, `t_inventario`, `t_bitacora` |
| **10** | `CU20W` | Gestionar temporadas y colecciones | P1 | Encargado Catálogo | `t_temporada`, `t_coleccion`, `t_producto`, `t_bitacora` |
| **11** | `CU21W` | Gestionar proveedores | P1 | Encargado Compras | `t_proveedor`, `t_orden_compra`, `t_bitacora` |
| **12** | `CU34W` | Gestionar planes de suscripción | P2 — Nuevo | Superadmin Plataforma | `t_plan`, `t_suscripcion`, `t_bitacora` |
| **13** | `CU35W` | Gestionar suscripciones empresariales | P2 — Nuevo | Superadmin Plataforma | `t_suscripcion`, `t_plan`, `t_sucursal`, `t_bitacora` |
| **14** | `CU36W` | Consultar plan y límites de suscripción | P2 — Nuevo | Administrador Tienda | `empresa`, `t_suscripcion`, `t_plan`, `t_sucursal` |
| **15** | `CU41W` | Gestionar respaldos y restauraciones | P2 — Nuevo | Administrador Sistema | `t_respaldo_sistema`, `t_seguridad_usuario`, `t_bitacora` |
| **16** | `CU43W` | Gestionar asignaciones de empleados | P2 — Nuevo | Administrador Empresa | `t_empleado`, `t_usuario`, `t_sucursal`, `t_usuario_sucursal`, `t_bitacora` |

---

## 4. Detalle de Especificación por Caso de Uso

### 1. CU01W / CU01M — Registrar usuario
- **Pestaña Draw.io:** `CU01 - Registrar usuario`
- **Curso Básico:** El Cliente ingresa sus datos personales, correo, contraseña Bcrypt y acepta términos; el sistema valida unicidad en `t_usuario`, crea la cuenta con rol CLIENTE, registra el dispositivo en `t_dispositivo_usuario`, audita en `t_bitacora` y emite el JWT redirigiendo a la bienvenida.
- **Cursos Alternos (Rojo):**
  - *Datos inválidos / password no coincide* ➔ Redirige a `Página Error Validación`.
  - *Correo o username duplicado* ➔ Redirige a `Página Cuenta Existente`.

### 2. CU02W / CU02M — Iniciar sesión
- **Pestaña Draw.io:** `CU02 - Iniciar sesión`
- **Curso Básico:** El Usuario ingresa credenciales; el sistema valida formato, comprueba que la cuenta no esté bloqueada en `t_seguridad_usuario`, evalúa hash Bcrypt, reinicia contador de fallos a 0, carga contexto RBAC y sucursales, audita en `t_bitacora` y emite el token JWT al Menú Principal.
- **Cursos Alternos (Rojo):**
  - *Credenciales inválidas / 3er fallo consecutivo* ➔ Bloqueo por 15 min y `Página Error / Bloqueo`.
  - *Dispositivo nuevo no reconocido* ➔ `Página Verificación Dispositivo` (código OTP).

### 3. CU03W / CU03M — Gestionar perfil
- **Pestaña Draw.io:** `CU03 - Gestionar perfil`
- **Curso Básico:** El Usuario autenticado solicita consultar su perfil; el sistema carga sus datos de `t_usuario`, permite editar información de contacto o password en el formulario, valida sintaxis, comprueba password actual, actualiza registro y audita en `t_bitacora`.
- **Cursos Alternos (Rojo):**
  - *Formato de teléfono o datos inválidos* ➔ `Página Error Validación Perfil`.
  - *Contraseña actual no coincide* ➔ `Página Error Contraseña Actual`.

### 4. CU14W — Gestionar usuarios y roles
- **Pestaña Draw.io:** `CU14 - Gestionar usuarios y roles`
- **Curso Básico:** El Administrador consulta el personal filtrado por su empresa en `t_usuario` y `t_rol`; ingresa nuevo usuario con rol y sucursales asignadas; el sistema valida pertenencia a la empresa y unicidad, persiste con Bcrypt y `t_usuario_rol`, o ejecuta baja lógica (`activo = false`) revocando sesiones.
- **Cursos Alternos (Rojo):**
  - *Usuario o email duplicado* ➔ `Página Error Validación / Duplicado`.
  - *Intento de modificar usuario de otra empresa o rol de plataforma* ➔ `Página Error Ámbito` (403 Forbidden).

### 5. CU15W — Gestionar empresas SaaS (Refactorización)
- **Pestaña Draw.io:** `CU15 - Gestionar empresas SaaS`
- **Curso Básico:** El Superadmin consulta las empresas tenant en `empresa`; registra o actualiza razón social, NIT y datos comerciales; ante solicitud de baja ejecuta una **baja lógica** (`activo = false`) preservando integridad referencial con sucursales e historial.
- **Cursos Alternos (Rojo):**
  - *NIT o nombre comercial duplicado* ➔ `Página Error NIT Duplicado`.
  - *Intento de borrado físico destructivo (DELETE cascade)* ➔ Interceptado y rechazado en `Página Rechazo Supresión Física`.

### 6. CU16W — Gestionar sucursales y ciudades
- **Pestaña Draw.io:** `CU16 - Gestionar sucursales y ciudades`
- **Curso Básico:** El Administrador consulta `t_sucursal` y `t_ciudad` para su empresa; registra nueva sucursal con código y ciudad; el sistema verifica en `t_suscripcion` y `t_plan` que las sucursales activas no superen el límite contratado (Básico: 2, Profesional: 10), persiste el registro y audita en `t_bitacora`.
- **Cursos Alternos (Rojo):**
  - *Límite de sucursales activas del plan excedido* ➔ Bloqueo con 409 Conflict en `Página Error Límite Plan`.
  - *Código de sucursal duplicado* ➔ `Página Error Código Duplicado`.

### 7. CU17W — Gestionar productos
- **Pestaña Draw.io:** `CU17 - Gestionar productos`
- **Curso Básico:** El Encargado de Catálogo lista las prendas de `t_producto` y `t_categoria`; registra nuevo producto con código SKU, nombre, descripción y precio; valida que precio > 0 y SKU único; persiste con estado activo y disponibilidad en tienda.
- **Cursos Alternos (Rojo):**
  - *Precio <= 0 o campos obligatorios vacíos* ➔ `Página Error Precio / Campos`.
  - *Código SKU ya registrado* ➔ `Página Error SKU Duplicado`.

### 8. CU18W — Gestionar categorías
- **Pestaña Draw.io:** `CU18 - Gestionar categorías`
- **Curso Básico:** El Encargado de Catálogo visualiza el árbol jerárquico en `t_categoria`; ingresa nueva categoría con nombre único; el sistema valida y persiste; en caso de eliminación comprueba ausencia de prendas asociadas en `t_producto`.
- **Cursos Alternos (Rojo):**
  - *Nombre de categoría duplicado* ➔ `Página Error Nombre Duplicado`.
  - *Categoría con prendas activas asociadas* ➔ Bloqueo de baja en `Página Error Dependencias Productos`.

### 9. CU19W — Gestionar tallas y colores
- **Pestaña Draw.io:** `CU19 - Gestionar tallas y colores`
- **Curso Básico:** El Encargado de Inventario selecciona una prenda; consulta `t_producto_talla_color`, `t_talla`, `t_color` y `t_inventario`; asocia una nueva combinación de talla y color indicando stock inicial >= 0; persiste e inicializa stock por sucursal.
- **Cursos Alternos (Rojo):**
  - *Combinación talla-color ya existente en la prenda* ➔ `Página Error Variante Duplicada`.
  - *Stock ingresado negativo (< 0)* ➔ `Página Error Stock Inválido`.

### 10. CU20W — Gestionar temporadas y colecciones
- **Pestaña Draw.io:** `CU20 - Gestionar temporadas y colecciones`
- **Curso Básico:** El Encargado de Catálogo lista las campañas en `t_temporada` y `t_coleccion`; registra nueva colección con nombre y rango de fechas [inicio, fin); valida coherencia cronológica y asocia lista de prendas `t_producto`.
- **Cursos Alternos (Rojo):**
  - *Fecha de inicio posterior a la fecha de fin* ➔ `Página Error Rango de Fechas`.
  - *Nombre de colección duplicado* ➔ `Página Error Colección Duplicada`.

### 11. CU21W — Gestionar proveedores
- **Pestaña Draw.io:** `CU21 - Gestionar proveedores`
- **Curso Básico:** El Encargado de Compras consulta el directorio en `t_proveedor`; ingresa datos fiscales y NIT de nuevo proveedor; valida formato y unicidad; ante baja comprueba que no existan órdenes de compra abiertas en `t_orden_compra`.
- **Cursos Alternos (Rojo):**
  - *NIT duplicado o formato de contacto inválido* ➔ `Página Error NIT Duplicado`.
  - *Proveedor con órdenes de compra activas* ➔ Bloqueo en `Página Error Compras Activas`.

### 12. CU34W — Gestionar planes de suscripción (Nuevo)
- **Pestaña Draw.io:** `CU34 - Gestionar planes de suscripción`
- **Curso Básico:** El Superadmin accede con alcance PLATAFORMA y permiso `planes.ver`; consulta `t_plan` (`BASICO` y `PROFESIONAL`); actualiza nombre descriptivo o disponibilidad para nuevas suscripciones preservando límites duros y suscripciones activas.
- **Cursos Alternos (Rojo):**
  - *Intento de registrar códigos arbitrarios o alterar capacidades fijas* ➔ `Página Rechazo Código Arbitrario`.
  - *Usuario sin alcance PLATAFORMA* ➔ 403 Forbidden en `Página Error Permisos Plataforma`.

### 13. CU35W — Gestionar suscripciones empresariales (Nuevo)
- **Pestaña Draw.io:** `CU35 - Gestionar suscripciones empresariales`
- **Curso Básico:** El Superadmin consulta el historial de suscripciones en `t_suscripcion` y `t_plan` para una empresa; asigna o renueva periodo [inicio, fin) validando no solapamiento y verificando que las sucursales activas no superen el límite del nuevo plan; en cancelación actualiza a `CANCELADA`.
- **Cursos Alternos (Rojo):**
  - *Capacidad del plan inferior al uso actual de sucursales activas* ➔ 409 Conflict en `Página Error Capacidad Insuficiente`.
  - *Fechas solapadas con suscripción vigente* ➔ `Página Error Solapamiento`.

### 14. CU36W — Consultar plan y límites de suscripción (Nuevo)
- **Pestaña Draw.io:** `CU36 - Consultar plan y límites de suscripción`
- **Curso Básico:** El Administrador de Tienda ingresa a 'Mi Plan y Límites'; el sistema obtiene el `id_empresa` del token JWT; consulta en `t_suscripcion` el periodo vigente dentro de `[inicio, fin)`; recupera límites en `t_plan` y cuenta sucursales activas en `t_sucursal`; despliega dashboard con capacidades e indicadores de uso.
- **Cursos Alternos (Rojo):**
  - *Periodo vencido o inexistente* ➔ `Página Sin Suscripción Vigente`.
  - *Empresa dada de baja (`activo = false`)* ➔ `Página Empresa Inactiva`.

### 15. CU41W — Gestionar respaldos y restauraciones (Nuevo)
- **Pestaña Draw.io:** `CU41 - Gestionar respaldos y restauraciones`
- **Curso Básico:** El Administrador de Sistema consulta snapshots en `t_respaldo_sistema`; genera nuevo volcado estructurado (pg_dump), calcula checksum SHA256 y cifra el archivo; ante restauración valida credencial de superusuario, verifica integridad y restaura esquemas/datos auditando en `t_bitacora`.
- **Cursos Alternos (Rojo):**
  - *Falla en motor de volcado / Espacio insuficiente* ➔ `Página Error Motor Respaldo`.
  - *Checksum corrupto o versión incompatible* ➔ Bloqueo en `Página Error Verificación Integridad`.

### 16. CU43W — Gestionar asignaciones de empleados a sucursales (Nuevo)
- **Pestaña Draw.io:** `CU43 - Gestionar asignaciones de empleados`
- **Curso Básico:** El Administrador de Empresa lista personal y sucursales activas; selecciona un empleado e ingresa lista `[id_sucursal]`; valida pertenencia a la empresa y estado activo; ejecuta reemplazo atómico en `t_usuario_sucursal` preservando el dato laboral en `t_empleado.id_sucursal`; lista vacía `[]` revoca accesos; audita antes/después en `t_bitacora`.
- **Cursos Alternos (Rojo):**
  - *Sucursal de otra empresa o actor sin jerarquía* ➔ 403 Forbidden en `Página Error Sucursal Ajena`.
  - *Sucursal inactiva o formato de IDs no numérico* ➔ 422/409 en `Página Error Validación Sucursal`.

---

## 5. Instrucciones de Apertura y Navegación

1. Abrir **[app.diagrams.net](https://app.diagrams.net/)** en cualquier navegador web moderno (o mediante la extensión de Draw.io en VS Code / Antigravity IDE).
2. Arrastrar y soltar el archivo [`diagramas_robustez.drawio`](./diagramas_robustez.drawio).
3. En la **barra inferior de pestañas**, navegar libremente entre los 16 diagramas:
   - `CU01 - Registrar usuario`
   - `CU02 - Iniciar sesión`
   - `CU03 - Gestionar perfil`
   - `CU14 - Gestionar usuarios y roles`
   - `CU15 - Gestionar empresas SaaS`
   - `CU16 - Gestionar sucursales y ciudades`
   - `CU17 - Gestionar productos`
   - `CU18 - Gestionar categorías`
   - `CU19 - Gestionar tallas y colores`
   - `CU20 - Gestionar temporadas y colecciones`
   - `CU21 - Gestionar proveedores`
   - `CU34 - Gestionar planes de suscripción`
   - `CU35 - Gestionar suscripciones empresariales`
   - `CU36 - Consultar plan y límites de suscripción`
   - `CU41 - Gestionar respaldos y restauraciones`
   - `CU43 - Gestionar asignaciones de empleados`
