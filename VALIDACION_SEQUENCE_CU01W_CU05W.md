# AuroraStore — Validación Estructural y de Consistencia: Diagramas de Secuencia UML 2.5 (CU01W–CU05W)

## 1. Resumen Ejecutivo de Verificación

En cumplimiento con los requerimientos de UML 2.5, el marco metodológico ICONIX y la arquitectura real de AuroraStore SaaS:
- Se implementó el generador en JavaScript nativo: `AuroraStore_CU01W_CU05W_Sequence_FINAL_EA.js`.
- Se adaptaron las líneas de vida para renderizar la cabecera rectangular estándar de UML (sin estereotipos `«boundary»`, `«control»` o `«entity»` que causaban que EA dibujara círculos de robustez).
- Se mapearon los controladores con los módulos reales de FastAPI (`routes` y `services`).
- Se sintetizó la interfaz de usuario en una lifeline por caso de uso para no sobrecomplicar la secuencia.
- Se preservaron íntegramente las entidades de los diagramas de robustez y las tablas reales de base de datos (`backend/app/modules/`).
- Cada caso de uso se modela en un único diagrama que integra consultas, registros, modificaciones, borrados lógicos y flujos alternativos.

---

## 2. Matriz de Cobertura y Verificación por Caso de Uso

| Caso de Uso | Nombre del Diagrama | Lifelines | Mensajes | Fragmentos `alt` | Fragmentos `opt` | Fragmentos `loop` | Verificación Estática (Node / JS) | Validación Visual EA |
|---|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **CU01W** | `sd CU01W - Gestionar usuarios y roles` | 9 | 26 | 2 (`alt_registro_usuario`, `alt_eliminar`) | 1 (`opt_sucursales`) | 1 (`loop_permisos`) | **APROBADA** (`node --check`) | **Pendiente de ejecución por el usuario** |
| **CU02W** | `sd CU02W - Gestionar cadena de tiendas` | 6 | 15 | 1 (`alt_validar_nit`) | 1 (`opt_suscripciones`) | 0 | **APROBADA** (`node --check`) | **Pendiente de ejecución por el usuario** |
| **CU03W** | `sd CU03W - Gestionar sucursales` | 10 | 19 | 1 (`alt_limite_sucursales`) | 1 (`opt_nueva_ciudad`) | 0 | **APROBADA** (`node --check`) | **Pendiente de ejecución por el usuario** |
| **CU04W** | `sd CU04W - Gestionar productos` | 9 | 24 | 2 (`alt_validar_producto`, `alt_desactivar_producto`) | 1 (`opt_imagenes`) | 1 (`loop_variantes`) | **APROBADA** (`node --check`) | **Pendiente de ejecución por el usuario** |
| **CU05W** | `sd CU05W - Gestionar planes de suscripción` | 7 | 16 | 1 (`alt_validar_plan`) | 0 | 0 | **APROBADA** (`node --check`) | **Pendiente de ejecución por el usuario** |

---

## 3. Desglose Detallado de Participantes Reales por Caso de Uso

### 3.1. CU01W — Gestionar usuarios y roles
- **Actor:** `admin : Administrador`
- **UI:** `ui : UsuariosUI`
- **Backend:** `router : users_routes`, `service : users_services`
- **Entities:** `t_usuario`, `t_rol`, `t_usuario_permiso`, `t_usuario_sucursal`, `t_bitacora`

### 3.2. CU02W — Gestionar cadena de tiendas (Empresas SaaS)
- **Actor:** `admin : Administrador`
- **UI:** `ui : EmpresasUI`
- **Backend:** `router : tenant_routes`, `service : tenant_services`
- **Entities:** `empresa`, `t_bitacora`

### 3.3. CU03W — Gestionar sucursales
- **Actor:** `admin : AdminTienda`
- **UI:** `ui : SucursalesUI`
- **Backend:** `router : sucursales_routes`, `service : sucursales_services`
- **Entities:** `empresa`, `t_suscripcion`, `t_plan`, `t_sucursal`, `t_ciudad`, `t_bitacora`

### 3.4. CU04W — Gestionar productos
- **Actor:** `admin : AdminTienda`
- **UI:** `ui : ProductosUI`
- **Backend:** `router : productos_routes`, `service : productos_services`
- **Entities:** `t_categoria`, `t_producto`, `t_producto_talla_color`, `t_producto_imagen`, `t_bitacora`

### 3.5. CU05W — Gestionar planes de suscripción
- **Actor:** `admin : Administrador`
- **UI:** `ui : PlanesUI`
- **Backend:** `router : saas_routes`, `service : saas_services`
- **Entities:** `t_plan`, `t_suscripcion`, `t_bitacora`

---

## 4. Estado de la Verificación Visual

> [!IMPORTANT]
> **Declaración de Estado:**
> - **Verificación Estática y Sintáctica:** **COMPLETADA** con éxito (código de retorno 0 en Node.js, balanceo de llaves, resolución de variables y verificación estricta de diagramas y objetos).
> - **Validación Visual en Enterprise Architect:** **PENDIENTE DE EJECUCIÓN POR EL USUARIO**. Ejecutar el script en EA según [`README_Sequence_CU01W_CU05W.md`](README_Sequence_CU01W_CU05W.md).
