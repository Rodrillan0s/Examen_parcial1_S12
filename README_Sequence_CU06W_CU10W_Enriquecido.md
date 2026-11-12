# Diagramas de Secuencia (UML 2.5) Enriquecidos — Lote 2 (CU06W a CU10W)
**Proyecto:** AuroraStore SaaS — Arquitectura Multitenant & Cloud POS  
**Destino:** Sparx Enterprise Architect (JavaScript Automation Script)  
**Estándar:** UML 2.5 / Interacción Dinámica Formal  
**Versión:** 2.0.0 (Edición Enriquecida con UIs Reales y Tablas Participantes)  

---

## 1. Resumen Ejecutivo de la Actualización

En este segundo lote enriquecido se profundiza en los subsistemas de **Suscripciones SaaS**, **Seguridad/Respaldos**, **Asignaciones Organizacionales** y **Catálogo Multicanal (Web/Móvil con Resiliencia Offline)**:
1. **Desdoblamiento de Interfaces (`«boundary»`):** Cada caso de uso separa la vista principal (`*View`) de sus diálogos modales o drawers operativos (`*Modal` / `*Drawer`), modelando con exactitud la experiencia de usuario y el intercambio de mensajes asíncronos con el backend.
2. **Exclusión Estricta de Ruido:** Se omiten diálogos de error triviales (`errorDialog`) y capas genéricas transversales (`RBAC services`), reflejando la orquestación directa entre router FastAPI y el servicio de dominio.
3. **Tablas PostgreSQL y Caché Local:** Persistencia completa que incluye `empresa`, `t_plan`, `t_suscripcion`, `t_sucursal`, `t_respaldo`, `t_empleado`, `t_usuario_sucursal`, `t_categoria`, `t_producto`, `t_producto_talla_color` y `cache_local` (IndexedDB / SQLite).

---

## 2. Detalle de Casos de Uso del Lote 2 Enriquecido

### CU06W — Gestionar suscripciones empresariales
* **Actor:** `admin : Administrador`
* **Boundaries Reales:**
  - `view : HistorialSuscripcionesView`: Tabla de suscripciones históricas y activas con estados `ACTIVA`, `VENCIDA`, `CANCELADA`.
  - `modal : ModalAsignarSuscripcion`: Formulario reactivo para asignar un plan o renovar vigencia.
* **Controllers:**
  - `router : saas_routes`
  - `service : saas_services`
* **Entities:**
  - `empresa`, `t_plan`, `t_suscripcion`, `t_bitacora`.

### CU07W — Consultar plan y límites de suscripción
* **Actor:** `admin : AdminTienda`
* **Boundaries Reales:**
  - `view : MiPlanView`: Panel de control con métricas de consumo de sucursales (2/10), días restantes y advertencias.
  - `modal : ModalUpgradePlan`: Modal interactivo para solicitar cambio de plan Básico a Profesional.
* **Controllers:**
  - `router : saas_routes`
  - `service : saas_services`
* **Entities:**
  - `empresa`, `t_suscripcion`, `t_plan`, `t_sucursal`, `t_bitacora`.

### CU08W — Gestionar respaldos y restauraciones
* **Actor:** `admin : Administrador`
* **Boundaries Reales:**
  - `view : RespaldosView`: Panel de telemetría OCI, almacenamiento y botón de generación de volcado `.dump`.
  - `modal : ModalConfirmarRestauracion`: Modal de seguridad crítica que solicita clave de confirmación antes de disparar `pg_restore`.
* **Controllers:**
  - `router : backup_routes`
  - `service : backup_services`
* **Entities:**
  - `t_respaldo`, `t_bitacora`.

### CU09W — Gestionar asignaciones de empleados a sucursales
* **Actor:** `admin : AdminTienda`
* **Boundaries Reales:**
  - `view : ListaEmpleadosView`: Tabla con nómina de empleados y sucursales asignadas.
  - `modal : ModalReasignarSucursales`: Selector modal con lista de sucursales de la empresa para reasignación atómica.
* **Controllers:**
  - `router : users_routes`
  - `service : asignaciones_services`
* **Entities:**
  - `empresa`, `t_sucursal`, `t_empleado`, `t_usuario_sucursal`, `t_bitacora`.

### CU10W / CU01M — Consultar catálogo (Web y Móvil con Soporte Offline)
* **Actor:** `user : Usuario`
* **Boundaries Reales:**
  - `view : CatalogoView`: Grilla paginada de prendas con tarjetas de producto y banner de modo sin conexión.
  - `drawer : FiltrosDrawer`: Drawer lateral reactivo para filtrar por categorías, tallas, colores y búsqueda.
  - `modal : DetalleProductoModal`: Modal interactivo con carrusel de fotos, selector de variantes y ficha técnica.
* **Controllers:**
  - `router : catalogo_routes`
  - `service : catalogo_services`
* **Entities & Caché Local:**
  - `t_categoria`, `t_producto`, `t_producto_talla_color`, `cache_local`.

---

## 3. Instrucciones de Ejecución en Enterprise Architect

1. Abrir Sparx Enterprise Architect con el proyecto `AuroraStore`.
2. Abrir la consola de scripting: **Code / Develop > Scripting** (`Ctrl + F9`).
3. Pegar el contenido del script [`AuroraStore_CU06W_CU10W_Sequence_FINAL_EA.js`](file:///d:/Locked%20Files%20--EY/Projectos/Examen_parcial1_S12/AuroraStore_CU06W_CU10W_Sequence_FINAL_EA.js).
4. Seleccionar el paquete destino en el **Project Browser** y presionar **Run (F5)**.
5. Se generará el paquete `Diagramas de Secuencia (UML 2.5) - Lote 2 (CU06W-CU10W Enriquecido)`.
