# Diagramas de Análisis de Clases (UML 2.5 / ICONIX VOPC) — Lote Final (CU23W y CU26W / CU08M)
**Proyecto:** AuroraStore SaaS — Arquitectura Multitenant & Cloud POS  
**Destino:** Sparx Enterprise Architect (JavaScript Automation Script)  
**Formato:** Tablas UML Rectangulares (3 compartimentos) con distribución ortogonal en 5 columnas  
**Versión:** 1.0.0 (Lote Final)  

---

## 1. Resumen Ejecutivo y Estructura Arquitectónica

Este lote final culmina el modelado completo de los Casos de Uso del sistema AuroraStore, abordando la **Inteligencia Artificial Predictiva** y la **Valoración Post-Venta**:
1. Análisis predictivo de demanda con series temporales y minería de reglas de asociación Apriori (**CU23W**).
2. Registro de valoraciones, reseñas con fotos y recálculo dinámico de reputación del producto (**CU26W / CU08M**).

```
[ ACTOR ] ───> [ «boundary» VISTAS / MODALES ] ───> [ «control» ROUTES ] ───> [ «control» SERVICES ] ───> [ «entity» TABLAS POSTGRESQL ]
```

---

## 2. Detalle de Casos de Uso del Lote Final

### CU23W — Consultar análisis predictivo y patrones comerciales (IA)
* **Actor:** `Administrador`
* **Boundaries:**
  - `PrediccionesDemandaView`: Panel analítico con selectores de horizonte (30/60/90 días) y disparador de reentrenamiento.
  - `GraficoCurvaDemandaComponent`: Visualizador de series temporales históricas y proyección con bandas de confianza.
  - `TablaRecomendacionesAbastecimientoComponent`: Propuestas automáticas de compra de stock basadas en velocidad de venta.
* **Controllers:**
  - `PrediccionesRouteController (predicciones_routes)`: Endpoints `/api/v1/ia/predicciones/demanda`, `/api/v1/ia/patrones-compra` y `/api/v1/ia/reentrenar-modelo`.
  - `DemandaForecastDomainService (demanda_forecast_services)`: Modelos Holt-Winters para proyección estacional y minería Apriori para reglas de coocurrencia de prendas en canasta.
* **Entities:**
  - `t_venta`, `t_detalle_venta`, `t_inventario`, `t_producto`, `t_recomendacion`.

### CU26W / CU08M — Registrar valoración de producto (Post-Venta / Reviews)
* **Actor:** `Cliente / Usuario`
* **Boundaries:**
  - `VentaConfirmadaView`: Pantalla de detalle de compra con listado de prendas adquiridas aptas para calificar.
  - `ModalValoracionProducto`: Formulario interactivo con estrellas (1 a 5), comentario y carga de fotografías.
  - `AlertaValoracionDuplicadaDialog`: Notificación ante intentos de re-calificación de un mismo producto en el mismo pedido.
* **Controllers:**
  - `ValoracionRouteController (valoracion_routes)`: Endpoints `/api/v1/catalogo/valoraciones` y `/api/v1/catalogo/productos/{id}/valoraciones`.
  - `ValoracionDomainService (valoracion_services)`: Moderación de contenido, orquestación de imágenes en Cloudinary y recálculo acumulativo de rating.
* **Entities:**
  - `t_valoracion`, `t_producto`, `t_producto_talla_color`, `t_bitacora`.

---

## 3. Instrucciones de Ejecución en Enterprise Architect

1. Abrir Sparx Enterprise Architect con el proyecto `AuroraStore.eap / .feap / .qea`.
2. Abrir la consola de scripting: Menú **Code / Develop > Scripting** (`Ctrl + F9`).
3. Pegar el código de [`AuroraStore_CU23W_CU26W_ClassAnalysis_FINAL_EA.js`](file:///d:/Locked%20Files%20--EY/Projectos/Examen_parcial1_S12/AuroraStore_CU23W_CU26W_ClassAnalysis_FINAL_EA.js).
4. Seleccionar el paquete de destino en el **Project Browser** y presionar **Run (F5)**.
5. Se generará el paquete `Diagramas de Análisis de Clases (ICONIX) - Lote Final (CU23W y CU26W)`.
