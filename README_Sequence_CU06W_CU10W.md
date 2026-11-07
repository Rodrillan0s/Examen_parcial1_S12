# AuroraStore — Automatización de Diagramas de Secuencia UML 2.5 en Sparx Enterprise Architect (CU06W–CU10W)

## 1. Propósito y Alcance

Este documento describe la generación automatizada de los **Diagramas de Secuencia UML 2.5** para los Casos de Uso **CU06W a CU10W** del sistema **AuroraStore SaaS**:

1. **`sd CU06W - Gestionar suscripciones empresariales`**
2. **`sd CU07W - Consultar plan y límites de suscripción`**
3. **`sd CU08W - Gestionar respaldos y restauraciones`** (Diseño arquitectónico coherente para el CU futuro)
4. **`sd CU09W - Gestionar asignaciones de empleados a sucursales`**
5. **`sd CU10W - Consultar catálogo`** (Web y Móvil con soporte Offline)

Cada caso de uso está modelado en **un único diagrama general consolidado**, integrando flujos principales, consultas, validaciones, ramas de error/excepción y fragmentos combinados (`alt`, `opt`, `loop`).

---

## 2. Pautas Arquitectónicas y de Estilo Aplicadas

1. **Lifelines Estándar Rectangulares UML (`Object1`):**
   - Sin estereotipos `«boundary»`, `«control»` o `«entity»` en las lifelines para evitar que EA dibuje los símbolos de robustez. EA dibuja la **cabecera rectangular estándar** con línea vertical discontinua.
2. **Controladores con Nombres Reales del Backend FastAPI:**
   - **CU06W:** `router : saas_routes`, `service : saas_services`
   - **CU07W:** `router : saas_routes`, `service : saas_services`
   - **CU08W:** `router : backup_routes`, `service : backup_services`
   - **CU09W:** `router : users_routes`, `service : asignaciones_services`
   - **CU10W:** `router : catalogo_routes`, `service : catalogo_services`
3. **Interfaces Limpias (1 UI por diagrama):**
   - `SuscripcionesUI`, `AjustesPlanUI`, `RespaldosUI`, `AsignacionesUI`, `CatalogoUI`.
4. **Respeto a Entidades de Robustez y Persistencia PostgreSQL:**
   - Se conservan `empresa`, `t_plan`, `t_suscripcion`, `t_sucursal`, `t_respaldo`, `t_empleado`, `t_usuario_sucursal`, `t_producto`, `t_categoria`, `t_producto_talla_color`, `cache_local` y `t_bitacora`.
5. **Coordenadas Milimétricas en 4to Cuadrante:**
   - `top = -topY; bottom = -bottomY` donde algebraicamente `top > bottom`. Sin cajas vacías ni marcos descomunales.

---

## 3. Instrucciones de Ejecución en Enterprise Architect

1. En Sparx Enterprise Architect, abrir la consola de scripting: `Specialize` (o `Develop`) → `Tools` → `Scripting` (`Ctrl + F9`).
2. En un grupo JavaScript/JScript, crear o abrir un script y pegar el contenido completo de [`AuroraStore_CU06W_CU10W_Sequence_FINAL_EA.js`](file:///d:/Locked%20Files%20--EY/Projectos/Examen_parcial1_S12/AuroraStore_CU06W_CU10W_Sequence_FINAL_EA.js).
3. Seleccionar el paquete de destino en el **Project Browser** de EA y pulsar **Run** (`F5`).
4. Se creará automáticamente el paquete `Diagramas de Secuencia (UML 2.5) - CU06W a CU10W` con los 5 diagramas.

---

## 4. Catálogo de Diagramas Generados

| Identificador | Nombre del Diagrama | Lifelines | Mensajes | Fragmentos Combinados |
|---|---|:---:|:---:|:---:|
| **CU06W** | `sd CU06W - Gestionar suscripciones empresariales` | 8 | 19 | `alt` (validación empresa/fechas) |
| **CU07W** | `sd CU07W - Consultar plan y límites de suscripción` | 8 | 14 | `alt` (suscripción activa vs sin plan) |
| **CU08W** | `sd CU08W - Gestionar respaldos y restauraciones` | 6 | 17 | `alt` (generación respaldo y restauración) |
| **CU09W** | `sd CU09W - Gestionar asignaciones de empleados a sucursales` | 9 | 18 | `alt` (validación sucursal/empleado) |
| **CU10W** | `sd CU10W - Consultar catálogo` | 8 | 20 | `alt` (conectividad offline/online), `alt` (detalle offline/online) |

