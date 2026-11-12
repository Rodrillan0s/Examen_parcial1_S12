# Diagramas de Análisis de Clases (UML 2.5 / ICONIX VOPC) — Lote 1 (CU01W a CU05W)
**Proyecto:** AuroraStore SaaS — Arquitectura Multitenant & Cloud POS  
**Destino:** Sparx Enterprise Architect (JavaScript Automation Script)  
**Patrón de Modelado:** Boundary $\rightarrow$ Controllers (Routes & Services) $\rightarrow$ Entity (PostgreSQL)  
**Versión:** 1.0.0 (Lote 1)  

---

## 1. Resumen Ejecutivo y Estructura Arquitectónica

Siguiendo el estándar ICONIX de **Vista de Clases Participantes (VOPC - View of Participating Classes)** y la guía de estilo de diseño presentada en las Figuras del documento del proyecto (Figuras 80 y 81: *Diseño de clases de CU*), cada diagrama de análisis de clases descompone la interacción del caso de uso en 3 niveles de abstracción fuertemente tipados:

```
[ ACTOR ] ---> [ «boundary» VISTAS / MODALES ] ---> [ «control» ROUTES / SERVICES ] ---> [ «entity» TABLAS POSTGRESQL ]
```

1. **Capa Boundary (`«boundary»`):**
   - Vistas maestras de listado (`ListaUsuariosView`, `ListaEmpresasView`, etc.).
   - Modales de edición, creación y confirmación con validación reactiva de formularios.
   - Diálogos universales de error/alerta (`ErrorDialog`).
   - Contienen atributos privados (estados UI, formularios reactivos, filtros) y métodos públicos de ciclo de vida (`ngOnInit`, `onSubmit`, `abrirModal`, etc.).

2. **Capa Control (`«control»`):**
   - **Route Controller (`*_routes`):** Controlador REST / FastAPI encargado de la validación de esquema DTO, deserialización y delegación HTTP.
   - **Domain Service (`*_services`):** Lógica transaccional de negocio, orquestación de queries, control de aislamiento multitenant y hashing de seguridad.
   - **Authorization / Auxiliary Services (`rbac_services`, etc.):** Políticas de acceso y permisos.

3. **Capa Entity (`«entity»`):**
   - Tablas relacionales canónicas de PostgreSQL (`empresa`, `t_usuario`, `t_rol`, `t_sucursal`, `t_ciudad`, `t_producto`, `t_plan`, `t_suscripcion`, `t_bitacora`, etc.).
   - Modelado con clave primaria (`[PK]`), claves foráneas (`[FK]`), atributos de persistencia y métodos de acceso a datos (`findById`, `insert`, `update`, `filterByEmpresa`).
   - Asociaciones dirigidas con multiplicidades formales (`1` a `0..*`, `1` a `1..*`).

---

## 2. Detalle de Casos de Uso del Lote 1

### CU01W — Gestionar usuarios y roles
* **Actor:** `Administrador`
* **Boundaries:**
  - `ListaUsuariosView`: Listado, búsqueda por texto y filtros por rol.
  - `FormularioUsuarioModal`: Creación/edición con asignación de roles y sucursales.
  - `EliminarUsuarioModal`: Desactivación lógica de usuario con auditoría.
  - `ErrorDialog`: Retroalimentación ante conflictos (duplicidad de email/username).
* **Controllers:**
  - `users_routes (RouteController)`: Endpoints `/api/usuarios`.
  - `users_services (DomainService)`: Hash de contraseñas con bcrypt, transacciones multitenant.
  - `rbac_services (Authorization)`: Verificación de permisos y asignación de roles.
* **Entities:**
  - `t_usuario`, `t_rol`, `empresa`, `t_usuario_sucursal`, `t_bitacora`.

### CU02W — Gestionar empresas SaaS
* **Actor:** `SuperAdministrador`
* **Boundaries:**
  - `ListaEmpresasView`: Grilla de tenants con estado, plan activo y vigencia.
  - `FormularioEmpresaModal`: Alta y configuración de tenant y usuario raíz.
  - `EstadoEmpresaModal`: Suspensión o reactivación administrativa de tenants.
  - `ErrorDialog`: Gestión de excepciones por NIT/Razón Social duplicados.
* **Controllers:**
  - `tenant_routes (RouteController)`: Endpoints `/api/tenants`.
  - `tenant_services (DomainService)`: Inicialización de esquema o provisionamiento lógico.
* **Entities:**
  - `empresa`, `t_suscripcion`, `t_plan`, `t_usuario`, `t_bitacora`.

### CU03W — Gestionar sucursales y ciudades
* **Actor:** `Administrador`
* **Boundaries:**
  - `ListaSucursalesView`: Catálogo de tiendas/puntos de venta activos.
  - `FormularioSucursalModal`: Asignación de ciudad, dirección, teléfono y límites de plan.
  - `EstadoSucursalModal`: Activación/desactivación de sucursal.
  - `ErrorDialog`: Validación de cuota de sucursales según el plan contratado.
* **Controllers:**
  - `sucursales_routes (RouteController)`: Endpoints `/api/sucursales`.
  - `sucursales_services (DomainService)`: Validación de límites de sucursales (`max_sucursales`) y pertenencia a empresa.
* **Entities:**
  - `t_sucursal`, `t_ciudad`, `empresa`, `t_usuario_sucursal`, `t_bitacora`.

### CU04W — Gestionar productos (Prendas y Variantes)
* **Actor:** `Administrador / Encargado`
* **Boundaries:**
  - `ListaProductosView`: Grilla de prendas con buscador, categorías y stock consolidado.
  - `FormularioPrendaModal`: Alta de prenda matriz, SKU base, precio y descripción.
  - `TabVariantesTallaColor`: Matriz de variantes por talla y color con código de barras.
  - `ErrorDialog`: Alerta de código de barras o SKU duplicado.
* **Controllers:**
  - `productos_routes (RouteController)`: Endpoints `/api/productos`.
  - `productos_services (DomainService)`: Transacciones complejas producto-variante e inventario inicial.
* **Entities:**
  - `t_producto`, `t_producto_talla_color`, `t_categoria`, `t_talla`, `t_color`, `t_inventario`, `t_bitacora`.

### CU05W — Gestionar planes de suscripción
* **Actor:** `SuperAdministrador`
* **Boundaries:**
  - `CatalogoPlanesView`: Tarjetas comparativas de planes (Básico, Profesional, Corporativo).
  - `FormularioPlanModal`: Edición de límites (sucursales, usuarios, reportes avanzados).
  - `ErrorDialog`: Bloqueo de modificación si existen suscripciones activas vinculadas.
* **Controllers:**
  - `saas_routes (RouteController)`: Endpoints `/api/saas/planes`.
  - `saas_services (DomainService)`: Mantenimiento de tarifas y restricciones funcionales.
* **Entities:**
  - `t_plan`, `t_suscripcion`, `empresa`, `t_bitacora`.

---

## 3. Instrucciones de Ejecución en Enterprise Architect

1. Abra **Sparx Enterprise Architect** con el proyecto `.eap` / `.feap` o repositorio de base de datos de AuroraStore.
2. En el *Project Browser*, cree o seleccione el paquete raíz donde residirán los diagramas de análisis (por ejemplo, `Diagramas de Analisis de Clases (UML 2.5) - CU01W a CU05W`).
3. Abra la consola de Scripting de EA:
   - Atajo de teclado: `Ctrl + F9` (o menú `Execute` $\rightarrow$ `Scripting` / `Tools` $\rightarrow$ `Scripting`).
4. Cree un nuevo script de tipo **JavaScript** (o use uno existente) y pegue el contenido completo de:
   - [`AuroraStore_CU01W_CU05W_ClassAnalysis_FINAL_EA.js`](file:///d:/Locked%20Files%20--EY/Projectos/Examen_parcial1_S12/AuroraStore_CU01W_CU05W_ClassAnalysis_FINAL_EA.js)
5. Haga clic en **Run (F5)** o en el botón de reproducción de la barra de Scripting.
6. Verifique en la ventana **System Output** (`Ctrl + Shift + 8`) que los 5 diagramas se hayan generado con éxito:
   ```text
   ======================================================================
   INICIANDO GENERACIÓN DE DIAGRAMAS DE ANÁLISIS DE CLASES (CU01W - CU05W)
   Paquete Destino: Diagramas de Analisis de Clases (UML 2.5) - CU01W a CU05W
   ======================================================================
    -> Construyendo: cd CU01W - Gestionar usuarios y roles
    -> Construyendo: cd CU02W - Gestionar empresas SaaS
    -> Construyendo: cd CU03W - Gestionar sucursales y ciudades
    -> Construyendo: cd CU04W - Gestionar productos
    -> Construyendo: cd CU05W - Gestionar planes de suscripción
   ======================================================================
   PROCESO COMPLETADO EXITOSAMENTE
   Diagramas de clases creados: 5
   ======================================================================
   ```
7. En el *Project Browser*, despliegue el paquete generado y haga doble clic en cualquiera de los diagramas para visualizar la disposición ortogonal y la visualización de compartimentos de atributos y operaciones.
