# AuroraStore — Análisis Crítico del Diagrama de Robustez y Automatización de Secuencia UML 2.5 (CU23W)

## 1. Evaluación y Corrección del Diagrama de Robustez

El diagrama de robustez original que contenía únicamente:
`ADMINISTRADOR` $\rightarrow$ `pPrediccion y Demanda` $\rightarrow$ `consultar datos` $\rightarrow$ `T_RECOMENDACION`
**era efectivamente incompleto e insuficiente** para el alcance técnico de **`CU23W - Consultar análisis predictivo y patrones comerciales`**:

### ¿Por qué estaba incompleto?
1. **Confusión de propósito de `T_RECOMENDACION`:**
   - La tabla `t_recomendacion` almacena sugerencias de producto personalizadas para clientes finales derivadas del modelo de afinidad (Mini-ML).
   - El caso de uso **CU23W** es una herramienta analítica y de decisión comercial para el **Administrador de Tienda**, cuyo propósito central es:
     - **Proyección de demanda futura** mediante series temporales (modelo Holt Linear Trend con intervalos de confianza al 95%).
     - **Cálculo de reposición de inventario y semáforo de riesgo de quiebre de stock** según el tiempo de entrega de proveedores (*lead time*).
     - **Análisis de patrones de compra y reglas de co-ocurrencia / afinidad**.
2. **Entidades reales omitidas:**
   - Para proyectar la demanda, el sistema necesita consultar el histórico de ventas reales: **`t_venta`** y **`t_detalle_venta`**.
   - Para calcular el riesgo de quiebre y las unidades sugeridas a comprar, el sistema necesita contrastar la demanda proyectada con los saldos físicos: **`t_inventario`** y los costos de catálogo en **`t_producto`**.
3. **Controladores reales en backend:**
   - No es un simple "consultar datos" plano; intervienen los módulos matemáticos y de consulta estructurada en FastAPI: [`predicciones_routes`](file:///d:/Locked%20Files%20--EY/Projectos/Examen_parcial1_S12/backend/app/modules/ia/routes/predicciones_routes.py) y [`demanda_forecast_services`](file:///d:/Locked%20Files%20--EY/Projectos/Examen_parcial1_S12/backend/app/modules/ia/services/demanda_forecast_services.py).

---

## 2. Corrección Integral en el Diagrama de Secuencia UML 2.5

Se corrigió la interacción modelando el flujo real y completo dentro de **un único diagrama general consolidado**:

1. **Lifelines Estándar Rectangulares UML (`[ Object1 ]`):**
   - Sin estereotipos de robustez en lifelines para prevenir los círculos en Enterprise Architect.
2. **Controladores con Nombres Reales:**
   - `router : predicciones_routes`
   - `service : demanda_forecast_services`
3. **Persistencia e Histórico Completo de PostgreSQL:**
   - `t_venta` y `t_detalle_venta` (serie temporal de transacciones).
   - `t_inventario` (stock físico y stock de seguridad).
   - `t_producto` (costo unitario para valorizar la orden de reposición sugerida).
   - `t_recomendacion` (patrones de asociación y afinidad entre prendas).
4. **Fragmento Combinado `alt`:**
   - Evalúa el riesgo de quiebre de inventario: `[existen prendas con riesgo CRITICO o ALTO]` vs `[else: stock optimo]`.
5. **Coordenadas Milimétricas en 4to Cuadrante:**
   - Coordenadas negativas `top = -topY; bottom = -bottomY` donde `top > bottom`.

---

## 3. Catálogo del Diagrama Generado

| Identificador | Nombre del Diagrama | Lifelines | Mensajes | Fragmentos Combinados |
|---|---|:---:|:---:|:---:|
| **CU23W** | `sd CU23W - Consultar análisis predictivo y patrones comerciales` | 9 | 33 | `alt` (prendas con riesgo crítico/alto vs stock óptimo) |

---

## 4. Instrucciones de Ejecución en Enterprise Architect

1. En Enterprise Architect, abrir la consola de scripting: `Specialize` (o `Develop`) → `Tools` → `Scripting` (`Ctrl + F9`).
2. Abrir o crear un script en un grupo JavaScript/JScript y pegar el contenido completo de [`AuroraStore_CU23W_Sequence_FINAL_EA.js`](file:///d:/Locked%20Files%20--EY/Projectos/Examen_parcial1_S12/AuroraStore_CU23W_Sequence_FINAL_EA.js).
3. Seleccionar el paquete de destino en el **Project Browser** de EA y presionar **Run** (`F5`).
4. Se creará automáticamente el paquete `Diagramas de Secuencia (UML 2.5) - Analisis Predictivo IA` con el diagrama.
