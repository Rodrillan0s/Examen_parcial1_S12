# AuroraStore — Automatización de Diagramas de Secuencia UML 2.5 en Sparx Enterprise Architect (CU01W–CU05W)

## 1. Propósito y Alcance

Este documento describe la solución definitiva para la generación automatizada de los **Diagramas de Secuencia UML 2.5** correspondientes a los Casos de Uso centrales **CU01W a CU05W** del sistema **AuroraStore SaaS**:

1. **`sd CU01W - Gestionar usuarios y roles`**
2. **`sd CU02W - Gestionar cadena de tiendas` (Empresas SaaS)**
3. **`sd CU03W - Gestionar sucursales`**
4. **`sd CU04W - Gestionar productos`**
5. **`sd CU05W - Gestionar planes de suscripción`**

Cada caso de uso se modela en **un único diagrama general consolidado**, integrando operaciones de consulta/listado, registro/creación, modificación, validación de reglas de negocio, manejo de excepciones (nodo de error de robustez) y borrado lógico mediante fragmentos combinados (`alt`, `opt`, `loop`). Se prohíbe explícitamente dividir un caso de uso en múltiples diagramas independientes.

---

## 2. Ajustes de Estilo UML y Arquitectura de Backend

En atención a la retroalimentación del usuario y las capturas reales de Sparx EA:
1. **Líneas de Vida Rectangulares Estándar UML (sin círculos de robustez):**
   - Se eliminaron los estereotipos `«boundary»`, `«control»` y `«entity»` en las llamadas a `Elements.AddNew(nombre, "Sequence")`. En Enterprise Architect, asignar dichos estereotipos activaba automáticamente el perfil gráfico de Análisis de Robustez (dibujando lollipops, círculos con flecha o círculos con barra). Al omitirlos, EA renderiza **cabeceras rectangulares estándar** (`[ Object1 ]`) con la línea discontinua vertical clásica.
2. **Controladores con Nombres Reales del Backend:**
   - Se sustituyeron nombres conceptuales (`UsuarioControl`, `EmpresaControl`) por los componentes reales de la arquitectura modular de capas de FastAPI:
     - `CU01W`: `router : users_routes`, `service : users_services`
     - `CU02W`: `router : tenant_routes`, `service : tenant_services`
     - `CU03W`: `router : sucursales_routes`, `service : sucursales_services`
     - `CU04W`: `router : productos_routes`, `service : productos_services`
     - `CU05W`: `router : saas_routes`, `service : saas_services`
3. **Sintetización de Interfaces de Usuario (UI):**
   - En lugar de fragmentar la interfaz en múltiples modales y ventanas (URL, Formulario, Lista, Error), cada CU cuenta con una única lifeline representativa de la interfaz Angular (`UsuariosUI`, `EmpresasUI`, `SucursalesUI`, `ProductosUI`, `PlanesUI`), evitando sobrecomplicar el diagrama.
4. **Respeto Estricto de Entidades de Robustez:**
   - Se conservan todas las tablas PostgreSQL reales que intervienen en el flujo funcional: `t_usuario`, `t_rol`, `t_usuario_permiso`, `t_usuario_sucursal`, `empresa`, `t_plan`, `t_suscripcion`, `t_sucursal`, `t_ciudad`, `t_producto`, `t_categoria`, `t_producto_talla_color`, `t_producto_imagen`, `t_bitacora`.
5. **Corrección de Coordenadas de Fragmentos:**
   - Coordenadas de 4to cuadrante negativo (`top = -topY`, `bottom = -bottomY`) calculadas estrictamente sobre el rango vertical de los mensajes contenidos, garantizando que no existan marcos vacíos ni zonas gigantescas en blanco.

---

## 3. Requisitos y Compatibilidad con Enterprise Architect

- **Versiones de Sparx Enterprise Architect soportadas:**
  - EA v14.x, v15.x, v16.x (32-bit y 64-bit), v17.x.
- **Motor de Scripting:**
  - JavaScript / JScript nativo de EA (Motor Microsoft JScript o SpiderMonkey de EA 16+).
- **Dependencias externas:**
  - Ninguna. El script utiliza exclusivamente la API oficial `Repository`, `Session` y consultas de catálogo `t_connector`.

---

## 4. Instrucciones Paso a Paso para la Ejecución en Enterprise Architect

1. **Abrir el proyecto en Enterprise Architect:**
   - Iniciar Sparx Enterprise Architect y cargar el archivo de proyecto.
2. **Abrir la ventana de Scripting:**
   - Ir al menú: `Specialize` (o `Develop`) → `Tools` → `Scripting` (`Ctrl + F9`).
3. **Seleccionar o crear un Script Group:**
   - En la ventana *Script Library*, ubicarse en un grupo tipo **JavaScript** o **JScript**.
4. **Cargar el código fuente:**
   - Crear un nuevo script (o abrir el existente) y reemplazar todo su contenido por:
     [`AuroraStore_CU01W_CU05W_Sequence_FINAL_EA.js`](file:///d:/Locked%20Files%20--EY/Projectos/Examen_parcial1_S12/AuroraStore_CU01W_CU05W_Sequence_FINAL_EA.js).
   - Guardar los cambios (`Ctrl + S`).
5. **Seleccionar el paquete contenedor:**
   - En el **Project Browser**, hacer clic sobre el paquete donde se crearán los diagramas.
6. **Ejecutar el script:**
   - Pulsar **Run** (`F5`).
   - El script creará automáticamente el paquete `Diagramas de Secuencia (UML 2.5) - AuroraStore` con los 5 diagramas.
7. **Visualización:**
   - Abrir cada diagrama con doble clic para verificar las cabeceras rectangulares de las lifelines y los mensajes contenidos.

---

## 5. Catálogo de Diagramas Generados

| Identificador | Nombre del Diagrama | Participantes (Lifelines) | Mensajes | Fragmentos Combinados |
|---|---|:---:|:---:|:---:|
| **CU01W** | `sd CU01W - Gestionar usuarios y roles` | 9 | 26 | `alt` (validación), `loop` (permisos), `opt` (sucursales), `alt` (desactivación) |
| **CU02W** | `sd CU02W - Gestionar cadena de tiendas` | 6 | 15 | `opt` (suscripciones), `alt` (validación NIT/datos) |
| **CU03W** | `sd CU03W - Gestionar sucursales` | 10 | 19 | `alt` (límite plan cuota), `opt` (nueva ciudad) |
| **CU04W** | `sd CU04W - Gestionar productos` | 9 | 24 | `alt` (validación), `loop` (variantes), `opt` (imágenes), `alt` (desactivación) |
| **CU05W** | `sd CU05W - Gestionar planes de suscripción` | 7 | 16 | `alt` (validación / dependencias activas) |

---

## 6. Estado de Validación

- **Verificación Estática y Sintáctica:** Aprobada al 100% con Node.js (`node --check`, código de salida 0).
- **Validación Visual en EA:** Pendiente de ejecución interactiva por el usuario en su entorno local de Enterprise Architect.
