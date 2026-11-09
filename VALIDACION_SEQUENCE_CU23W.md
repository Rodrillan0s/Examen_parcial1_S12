# AuroraStore — Validación Estructural y de Consistencia: Diagrama de Secuencia UML 2.5 (CU23W)

## 1. Resumen de Verificación

Se generó el diagrama de secuencia para el caso de uso **`CU23W - Consultar análisis predictivo y patrones comerciales`** corrigiendo las omisiones del diagrama de robustez original y reflejando con exactitud el comportamiento del backend FastAPI:
- **Lifelines estándar UML:** Cabeceras rectangulares `[ Object1 ]` sin estereotipos de robustez para evitar los iconos circulares.
- **Controladores reales:** Mapeo verificado a rutas y servicios analíticos (`predicciones_routes`, `demanda_forecast_services`).
- **Persistencia íntegra:** Inclusión de todas las tablas de PostgreSQL necesarias para series temporales y cálculo de abastecimiento (`t_venta`, `t_detalle_venta`, `t_inventario`, `t_producto`, `t_recomendacion`).
- **Validación sintáctica:** Aprobada al 100% con Node.js (`node --check`).

---

## 2. Matriz de Cobertura

| Caso de Uso | Nombre del Diagrama | Lifelines | Mensajes | Fragmentos Combinados | Verificación Estática | Validación Visual EA |
|---|---|:---:|:---:|:---:|:---:|:---:|
| **CU23W** | `sd CU23W - Consultar análisis predictivo y patrones comerciales` | 9 | 33 | `alt` (prendas con riesgo crítico/alto vs stock óptimo) | **APROBADA** (`node --check`) | **Pendiente de ejecución por el usuario** |

---

## 3. Desglose de Participantes

- **Actor:** `admin : Administrador / AdminTienda`
- **UI:** `ui : PrediccionesDemandaUI` (Pantalla de Predicciones y Demanda — `/admin/predicciones`)
- **Backend Router:** `router : predicciones_routes`
- **Backend Service:** `service : demanda_forecast_services`
- **Entidades de Dominio:**
  - `t_venta`: Registro de transacciones históricas para el modelado temporal diario.
  - `t_detalle_venta`: Unidades vendidas por prenda y variante.
  - `t_inventario`: Existencias físicas actuales y stock de seguridad por sucursal.
  - `t_producto`: Catálogo activo y costos para cálculo de presupuesto de reposición.
  - `t_recomendacion`: Reglas de asociación y afinidad entre prendas.
