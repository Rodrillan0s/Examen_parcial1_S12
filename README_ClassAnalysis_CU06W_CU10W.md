# Diagramas de Análisis de Clases (UML 2.5 / ICONIX VOPC) — Lote 2 (CU06W a CU10W)
**Proyecto:** AuroraStore SaaS — Arquitectura Multitenant & Cloud POS  
**Destino:** Sparx Enterprise Architect (JavaScript Automation Script)  
**Patrón de Modelado:** Boundary $\rightarrow$ Controllers (Routes & Services) $\rightarrow$ Entity (PostgreSQL & Cache Local)  
**Versión:** 1.0.0 (Lote 2)  

---

## 1. Resumen Ejecutivo y Estructura Arquitectónica

Continuando con la descomposición arquitectónica en bloques de 5 casos de uso para **Sparx Enterprise Architect**, este segundo lote cubre los casos de uso críticos de gestión de suscripciones empresariales, monitoreo de cuotas y límites, respaldos de base de datos, asignaciones de personal y consulta de catálogo con soporte híbrido online/offline.

Cada diagrama aplica la regla formal de 3 compartimentos completos:
```
[ ACTOR ] ───> [ «boundary» VISTAS / MODALES ] ───> [ «control» ROUTES & SERVICES ] ───> [ «entity» TABLAS / CACHE ]
```

1. **Capa Boundary (`«boundary»`):**
   - Vistas maestras de listado (`ListaSuscripcionesView`, `AjustesPlanView`, `RespaldosView`, `ListaAsignacionesView`, `CatalogoPublicoView`).
   - Modales de configuración, filtros avanzados y diálogos de confirmación o alerta (`AsignacionSuscripcionModal`, `GenerarRespaldoModal`, `AsignarSucursalesModal`, `FiltroCatalogoSidebar`, etc.).
   - Diálogos y barras de estado reactivas (`ErrorDialog`, `OfflineStatusBar`).

2. **Capa Control (`«control»`):**
   - **Route Controllers (`*_routes`):** Controladores FastAPI que exponen las rutas REST, deserializan DTOs y devuelven respuestas HTTP.
   - **Domain Services (`*_services`):** Lógica transaccional de negocio, validaciones cruzadas de multitenancy, hash de contraseñas, auditoría de eventos y coordinación con `pg_dump`/`pg_restore`.
   - **Client Storage Controllers (`offline_cache_manager`):** Gestor de almacenamiento en cliente (IndexedDB en web / SQLite en móvil) para soporte offline transparente.

3. **Capa Entity (`«entity»`):**
   - Modelos de persistencia relacional PostgreSQL (`empresa`, `t_plan`, `t_suscripcion`, `t_sucursal`, `t_respaldo`, `t_usuario`, `t_empleado`, `t_usuario_sucursal`, `t_producto`, `t_categoria`, `t_producto_talla_color`, `t_talla`, `t_color`, `t_bitacora`).
   - Almacenamiento local estructurado (`cache_local`).
   - Modelado con clave primaria (`[PK]`), claves foráneas (`[FK]`), campos tipados y métodos de persistencia/consulta con cardinalidades formales (`1` a `0..*`, `1` a `1..*`).

---

## 2. Detalle de Casos de Uso del Lote 2

### CU06W — Gestionar suscripciones empresariales
* **Actor:** `Administrador`
* **Boundaries:**
  - `ListaSuscripcionesView`: Grilla de suscripciones de la empresa con fechas de vigencia y estado.
  - `AsignacionSuscripcionModal`: Modal de alta/renovación con selector de planes y cálculo automático de periodo.
  - `CancelarSuscripcionModal`: Modal para rescindir suscripción activa con justificación.
  - `ErrorDialog`: Notificación ante fechas inválidas o empresa suspendida.
* **Controllers:**
  - `saas_routes (RouteController)`: Endpoints `/api/v1/saas/empresas/{id}/suscripciones`.
  - `saas_services (DomainService)`: Reglas de vigencia, cambio de estado y registro en bitácora.
* **Entities:**
  - `empresa`, `t_plan`, `t_suscripcion`, `t_bitacora`.

### CU07W — Consultar plan y límites de suscripción
* **Actor:** `AdminTienda`
* **Boundaries:**
  - `AjustesPlanView`: Panel de telemetría de suscripción con medidores de consumo de recursos.
  - `DetalleLimitesModal`: Desglose detallado de sucursales usadas vs permitidas y capacidades del plan.
  - `ErrorDialog`: Alerta cuando la empresa no cuenta con plan activo.
* **Controllers:**
  - `saas_routes (RouteController)`: Endpoints `/api/v1/saas/mi-empresa/plan`.
  - `saas_services (DomainService)`: Agregación de límites, conteo de sucursales activas y cálculo de días restantes.
* **Entities:**
  - `empresa`, `t_suscripcion`, `t_plan`, `t_sucursal`.

### CU08W — Gestionar respaldos y restauraciones
* **Actor:** `Administrador`
* **Boundaries:**
  - `RespaldosView`: Consola de volcados de base de datos con tamaño, checksum SHA-256 y descargas.
  - `GenerarRespaldoModal`: Disparador de respaldo `.dump` con inclusión opcional de bitácora.
  - `RestaurarModal`: Diálogo crítico de restauración de base de datos con confirmación de credenciales.
  - `ErrorDialog`: Gestión de excepciones por espacio en disco o fallos en utilidades PostgreSQL.
* **Controllers:**
  - `backup_routes (RouteController)`: Endpoints `/api/v1/admin/respaldos`.
  - `backup_services (DomainService)`: Orquestación segura de `pg_dump` y `pg_restore`, validación de integridad.
* **Entities:**
  - `t_respaldo`, `t_usuario`, `t_bitacora`.

### CU09W — Gestionar asignaciones de empleados a sucursales
* **Actor:** `AdminTienda`
* **Boundaries:**
  - `ListaAsignacionesView`: Grilla de empleados con sucursales asignadas y filtros rápidos.
  - `AsignarSucursalesModal`: Selector multicheckbox para asignación múltiple de sucursales del tenant.
  - `SucursalPrincipalModal`: Selector de tienda por defecto / sede primaria de operaciones.
  - `ErrorDialog`: Alerta ante intentos de asignación a sucursales ajenas a la empresa del tenant.
* **Controllers:**
  - `users_routes (RouteController)`: Endpoints `/api/v1/auth/usuarios/{id}/sucursales`.
  - `asignaciones_services (DomainService)`: Transacciones sobre `t_usuario_sucursal` y actualización de `t_empleado`.
* **Entities:**
  - `empresa`, `t_sucursal`, `t_usuario`, `t_empleado`, `t_usuario_sucursal`, `t_bitacora`.

### CU10W — Consultar catálogo (Web y Móvil con Soporte Offline)
* **Actor:** `Usuario / Cliente`
* **Boundaries:**
  - `CatalogoPublicoView`: Cuadrícula responsiva de prendas con paginación y cards interactivas.
  - `FiltroCatalogoSidebar`: Panel de filtros faceted por categoría, talla, color y rango de precios.
  - `FichaDetalleProductoModal`: Vista emergente con selección de SKU específico por talla/color.
  - `OfflineStatusBar`: Semáforo de conectividad y estado de datos cacheados localmente.
* **Controllers:**
  - `catalogo_routes (RouteController)`: Endpoints `/api/catalogo/productos`.
  - `catalogo_services (DomainService)`: Búsqueda dinámica y construcción de árbol de variantes.
  - `offline_cache_manager (ClientStorage)`: Controlador cliente para resolución y persistencia en IndexedDB/SQLite.
* **Entities:**
  - `t_producto`, `t_categoria`, `t_producto_talla_color`, `t_talla`, `t_color`, `cache_local`.

---

## 3. Instrucciones de Ejecución en Enterprise Architect

1. Abra su proyecto en **Sparx Enterprise Architect**.
2. En el *Project Browser*, seleccione o cree el paquete donde se generarán los diagramas (ejemplo: `Diagramas de Analisis de Clases (UML 2.5) - CU06W a CU10W`).
3. Abra la consola de Scripting presionando **`Ctrl + F9`**.
4. Cree un nuevo script de tipo **JavaScript** (ej. `Generar_ClassAnalysis_CU06_CU10.js`).
5. Copie y pegue el contenido completo de:
   - [`AuroraStore_CU06W_CU10W_ClassAnalysis_FINAL_EA.js`](file:///d:/Locked%20Files%20--EY/Projectos/Examen_parcial1_S12/AuroraStore_CU06W_CU10W_ClassAnalysis_FINAL_EA.js)
6. Presione **Run (F5)**.
7. La consola desplegará:
   ```text
   ======================================================================
   INICIANDO GENERACIÓN DE DIAGRAMAS DE ANÁLISIS DE CLASES (CU06W - CU10W)
   ======================================================================
   Paquete Destino: Diagramas de Analisis de Clases (UML 2.5) - CU06W a CU10W
    -> Construyendo: cd CU06W - Gestionar suscripciones empresariales
    -> Construyendo: cd CU07W - Consultar plan y límites de suscripción
    -> Construyendo: cd CU08W - Gestionar respaldos y restauraciones
    -> Construyendo: cd CU09W - Gestionar asignaciones de empleados a sucursales
    -> Construyendo: cd CU10W - Consultar catálogo
   ======================================================================
   PROCESO COMPLETADO EXITOSAMENTE
   Diagramas de análisis de clases creados: 5
   ======================================================================
   ```
8. Abra cualquiera de los diagramas creados en el árbol para comprobar la visibilidad de atributos y métodos (`ShowAttrs=1`, `ShowOps=1`) y el ruteo limpio de conectores.
