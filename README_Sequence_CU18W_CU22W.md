# AuroraStore — Automatización de Diagramas de Secuencia UML 2.5 en Sparx Enterprise Architect (CU18W–CU22W)

## 1. Propósito y Alcance

Este documento describe la generación automatizada de los **Diagramas de Secuencia UML 2.5** para los Casos de Uso de **Sincronización Offline, Indicadores Operacionales y Motor Analítico** del sistema **AuroraStore SaaS**:

1. **`sd CU18W - Sincronizar operaciones pendientes`** (PWA Offline / Sincronización en lote con detección de idempotencia y resolución de stock)
2. **`sd CU19W - Resolver conflictos de sincronización`** (Bandeja administrativa de conciliación de operaciones con conflicto)
3. **`sd CU20W - Consultar ventas, reservas e inventario`** (Gestión operativa de tienda: caja activa, ventas del turno, reservas y alertas de stock)
4. **`sd CU21W - Visualizar indicadores empresariales`** (Dashboard ejecutivo: facturación mensual, ranking por sucursales, valoración de inventario y rating)
5. **`sd CU22W - Generar reportes bajo demanda`** (Motor analítico dinámico con interpretación de comandos, consulta a vistas analíticas canónicas y exportación PDF/Excel)

Cada caso de uso está modelado en **un único diagrama general consolidado**, integrando flujos principales, consultas, fragmentos combinados (`loop`, `alt`, `opt`) y control de excepciones.

---

## 2. Pautas Arquitectónicas y de Estilo Aplicadas

1. **Lifelines Estándar Rectangulares UML (`Object1`):**
   - Sin estereotipos `«boundary»`, `«control»` o `«entity»` en las lifelines para evitar que EA dibuje los círculos de robustez. Se renderizan con la **cabecera rectangular estándar** y línea vertical discontinua.
2. **Controladores con Nombres Reales del Backend FastAPI:**
   - **CU18W:** `router : sync_routes`, `service : sync_services`
   - **CU19W:** `router : sync_routes`, `service : sync_services`
   - **CU20W:** `router : kpis_routes`, `service : kpis_services`
   - **CU21W:** `router : kpis_routes`, `service : kpis_services`
   - **CU22W:** `router : motor_reportes_routes`, `service : reportes_services`
3. **Interfaces Limpias (1 UI por diagrama):**
   - `CentroSyncUI`, `ResolucionConflictosUI`, `GestionTiendaUI`, `DashboardKpisUI`, `ReportesUI`.
4. **Entidades Reales de Persistencia PostgreSQL y Vistas Analíticas:**
   - `t_sync_operacion`, `cache_local` (IndexedDB en cliente), `t_caja_sesion`, `t_sucursal`, `empresa`, `t_venta`, `t_pago`, `t_reserva`, `t_inventario`, `t_valoracion`, `t_bitacora`.
   - Vistas SQL analíticas para el motor de reportes: `vw_ventas_reporte`, `vw_inventario_reporte`, `vw_rentabilidad_reporte`.
5. **Coordenadas Milimétricas en 4to Cuadrante:**
   - `top = -topY; bottom = -bottomY` donde algebraicamente `top > bottom`. Sin recuadros vacíos, con márgenes exactos que envuelven los mensajes.

---

## 3. Instrucciones de Ejecución en Enterprise Architect

1. En Sparx Enterprise Architect, abrir la consola de scripting: `Specialize` (o `Develop`) → `Tools` → `Scripting` (`Ctrl + F9`).
2. Abrir o crear un script en un grupo JavaScript/JScript y pegar el contenido completo de [`AuroraStore_CU18W_CU22W_Sequence_FINAL_EA.js`](file:///d:/Locked%20Files%20--EY/Projectos/Examen_parcial1_S12/AuroraStore_CU18W_CU22W_Sequence_FINAL_EA.js).
3. Seleccionar el paquete de destino en el **Project Browser** de EA y presionar **Run** (`F5`).
4. Se creará automáticamente el paquete `Diagramas de Secuencia (UML 2.5) - Sincronizacion y Analitica` con los 5 diagramas.

---

## 4. Catálogo de Diagramas Generados

| Identificador | Nombre del Diagrama | Lifelines | Mensajes | Fragmentos Combinados |
|---|---|:---:|:---:|:---:|
| **CU18W** | `sd CU18W - Sincronizar operaciones pendientes` | 10 | 21 | `loop` (evaluación de lote), `alt` (conflictos vs éxito total) |
| **CU19W** | `sd CU19W - Resolver conflictos de sincronización` | 8 | 23 | `alt` (operación ya resuelta vs conciliación aprobada) |
| **CU20W** | `sd CU20W - Consultar ventas, reservas e inventario` | 9 | 14 | Consolidado multitabla tienda (caja, ventas, reservas, stock) |
| **CU21W** | `sd CU21W - Visualizar indicadores empresariales` | 10 | 16 | Resumen ejecutivo KPI (ingresos, sucursales, valuación, rating) |
| **CU22W** | `sd CU22W - Generar reportes bajo demanda` | 8 | 24 | `alt` (vistas analíticas SQL), `opt` (exportación PDF/Excel) |
