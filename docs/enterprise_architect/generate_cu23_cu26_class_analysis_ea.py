#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generador Maestro de Diagramas de Análisis de Clases UML 2.5 (ICONIX VOPC) para Sparx Enterprise Architect
Proyecto: AuroraStore SaaS
Lote Final (Lote 6): CU23W, CU26W / CU08M
  - CU23W: Consultar análisis predictivo y patrones comerciales (IA / Forecasting & Apriori)
  - CU26W / CU08M: Registrar valoración de producto (Post-Venta / Reviews & Ratings)

Arquitectura: Boundary -> Controllers (Routes & Services) -> Entity (PostgreSQL)
Formato: Tablas UML Rectangulares (3 compartimentos) con distribución ortogonal en 5 columnas.
"""

import os
import sys

def build_javascript_content():
    return r"""/*
 * =================================================================================================
 * SCRIPT MAESTRO DE AUTOMATIZACIÓN DE DIAGRAMAS DE ANÁLISIS DE CLASES UML 2.5 (ICONIX VOPC) PARA SPARX EA
 * =================================================================================================
 * Proyecto: AuroraStore SaaS
 * Lote Final: CU23W y CU26W / CU08M
 *   - cd CU23W - Consultar análisis predictivo y patrones comerciales (IA)
 *   - cd CU26W / CU08M - Registrar valoración de producto
 * 
 * Estructura de Tablas UML (3 Compartimentos):
 *   1. Cabecera con Estereotipo en texto: «boundary», «control», «entity»
 *   2. Compartimento de Atributos: con tipos tipados (- atributo: tipo)
 *   3. Compartimento de Operaciones: con signaturas tipadas (+ metodo(param: tipo): retorno)
 * 
 * Disposición Espacial Ortogonal en 5 Columnas (Izquierda a Derecha):
 *   [ Col 1: Actor ] -> [ Col 2: «boundary» Vistas/Modales ] -> [ Col 3: «control» RouteController ]
 *                    -> [ Col 4: «control» DomainServices ] -> [ Col 5 & 6: «entity» Tablas PostgreSQL ]
 * =================================================================================================
 */

// -------------------------------------------------------------------------------------------------
// HELPERS PARA CREACIÓN DE ELEMENTOS, ATRIBUTOS Y MÉTODOS EN ENTERPRISE ARCHITECT
// -------------------------------------------------------------------------------------------------

function configurarDiagramaTablasUML(diag) {
    var styleString = "HideRel=0;ShowTags=0;ShowReqs=0;ShowCons=0;OpParams=1;" +
                      "ShowSN=0;ScalePI=0;PPgs.cx=1;PPgs.cy=1;PSize=119;" +
                      "ShowIcons=0;SuppCN=0;HideProps=0;HideParents=0;" +
                      "UseAlias=0;HideAtts=0;HideOps=0;HideStereo=0;HideEStereo=0;FormName=;";
    diag.ExtendedStyle = styleString;
    diag.StyleEx = styleString;
    diag.Update();
}

function agregarActor(pkg, diag, nombre, posX, posY, ancho, alto) {
    var el = pkg.Elements.AddNew(nombre, "Actor");
    el.Update();

    var left = posX;
    var right = posX + ancho;
    var top = -posY;
    var bottom = -(posY + alto);

    var dObj = diag.DiagramObjects.AddNew("l=" + left + ";r=" + right + ";t=" + top + ";b=" + bottom + ";", "");
    dObj.ElementID = el.ElementID;
    dObj.Update();

    return el;
}

function agregarClaseTablaUML(pkg, diag, nombre, estereotipo, atributos, operaciones, posX, posY, ancho, alto) {
    var el = pkg.Elements.AddNew(nombre, "Class");
    el.Stereotype = estereotipo; // "boundary", "control", "entity"
    el.Update();

    // 1. Atributos
    if (atributos && atributos.length > 0) {
        for (var i = 0; i < atributos.length; i++) {
            var itemA = atributos[i];
            var attr = el.Attributes.AddNew(itemA.nombre, itemA.tipo);
            attr.Visibility = itemA.vis || "Private";
            attr.Update();
        }
        el.Attributes.Refresh();
    }

    // 2. Operaciones / Métodos
    if (operaciones && operaciones.length > 0) {
        for (var j = 0; j < operaciones.length; j++) {
            var itemM = operaciones[j];
            var meth = el.Methods.AddNew(itemM.nombre, itemM.retorno || "void");
            meth.Visibility = itemM.vis || "Public";
            if (itemM.parametros && itemM.parametros.length > 0) {
                for (var k = 0; k < itemM.parametros.length; k++) {
                    var p = itemM.parametros[k];
                    var param = meth.Parameters.AddNew(p.nombre, p.tipo);
                    param.Update();
                }
                meth.Parameters.Refresh();
            }
            meth.Update();
        }
        el.Methods.Refresh();
    }

    el.Update();

    // 3. Diagram Object con forzado de Notación Rectangular (UCRect=1)
    var left = posX;
    var right = posX + ancho;
    var top = -posY;
    var bottom = -(posY + alto);

    var dObj = diag.DiagramObjects.AddNew("l=" + left + ";r=" + right + ";t=" + top + ";b=" + bottom + ";", "");
    dObj.ElementID = el.ElementID;
    try {
        if (dObj.SetStyleEx) {
            dObj.SetStyleEx("UCRect", "1");
        }
    } catch (e) {}
    dObj.Update();

    return el;
}

function conectarElementos(sourceEl, targetEl, tipo, nombreConector, estereotipo, cardClient, cardSupplier) {
    if (!sourceEl || !targetEl) return null;

    var conn = sourceEl.Connectors.AddNew(nombreConector || "", tipo || "Association");
    conn.SupplierID = targetEl.ElementID;

    if (estereotipo) {
        conn.Stereotype = estereotipo;
    }
    if (cardClient) {
        conn.ClientEnd.Cardinality = cardClient;
    }
    if (cardSupplier) {
        conn.SupplierEnd.Cardinality = cardSupplier;
    }
    conn.Update();
    sourceEl.Connectors.Refresh();
    return conn;
}


// =================================================================================================
// 1. CU23W: Consultar análisis predictivo y patrones comerciales (IA / Demand Forecast & Apriori)
// =================================================================================================
function generarClasesCU23W(pkg) {
    Session.Output(" -> Construyendo: cd CU23W - Consultar análisis predictivo y patrones comerciales");
    var diag = pkg.Diagrams.AddNew("cd CU23W - Consultar análisis predictivo y patrones comerciales", "Logical");
    diag.Update();
    configurarDiagramaTablasUML(diag);

    // --- Columna 1: Actor ---
    var act = agregarActor(pkg, diag, "Administrador", 40, 240, 90, 110);

    // --- Columna 2: Boundary ---
    var b1 = agregarClaseTablaUML(pkg, diag, "PrediccionesDemandaView", "boundary",
        [
            { nombre: "currentTenantId", tipo: "number" },
            { nombre: "forecastPayload", tipo: "DemandForecastDTO" },
            { nombre: "patronesAsociacion", tipo: "AssociationRuleDTO[]" },
            { nombre: "horizonteDias", tipo: "number = 30" },
            { nombre: "isTraining", tipo: "boolean" }
        ],
        [
            { nombre: "cargarAnalisisPredictivo", retorno: "void", parametros: [] },
            { nombre: "cambiarHorizonteForecast", retorno: "void", parametros: [{ nombre: "dias", tipo: "number" }] },
            { nombre: "reentrenarModelosIA", retorno: "void", parametros: [] },
            { nombre: "exportarPlanAbastecimiento", retorno: "void", parametros: [] }
        ],
        180, 50, 240, 150
    );

    var b2 = agregarClaseTablaUML(pkg, diag, "GraficoCurvaDemandaComponent", "boundary",
        [
            { nombre: "seriesHistorica", tipo: "TimePoint[]" },
            { nombre: "seriesPrediccion", tipo: "ForecastPoint[]" },
            { nombre: "intervaloConfianza", tipo: "number = 0.95" }
        ],
        [
            { nombre: "renderChartForecast", retorno: "void", parametros: [] },
            { nombre: "filtrarPorCategoria", retorno: "void", parametros: [{ nombre: "categoriaId", tipo: "number" }] }
        ],
        180, 230, 240, 130
    );

    var b3 = agregarClaseTablaUML(pkg, diag, "TablaRecomendacionesAbastecimientoComponent", "boundary",
        [
            { nombre: "sugerenciasCompra", tipo: "RestockSuggestion[]" },
            { nombre: "selectedPrenda", tipo: "RestockSuggestion" }
        ],
        [
            { nombre: "generarBorradorOrdenCompra", retorno: "void", parametros: [{ nombre: "items", tipo: "RestockSuggestion[]" }] },
            { nombre: "descartarSugerencia", retorno: "void", parametros: [{ nombre: "id", tipo: "number" }] }
        ],
        180, 390, 240, 130
    );

    // --- Columna 3: Controller Principal ---
    var cRoute = agregarClaseTablaUML(pkg, diag, "PrediccionesRouteController", "control",
        [
            { nombre: "prefix", tipo: "string = '/api/v1/ia'" },
            { nombre: "db", tipo: "AsyncSession" },
            { nombre: "aiModelGuard", tipo: "SaasPlanGuard" }
        ],
        [
            { nombre: "getPrediccionesDemanda", retorno: "JSONResponse", parametros: [{ nombre: "dias", tipo: "int" }, { nombre: "categoriaId", tipo: "int" }] },
            { nombre: "getPatronesCompraAsociacion", retorno: "JSONResponse", parametros: [{ nombre: "minConfidence", tipo: "float" }] },
            { nombre: "postReentrenarModelo", retorno: "JSONResponse", parametros: [] }
        ],
        470, 170, 280, 190
    );

    // --- Columna 4: Domain Service ---
    var cDomain = agregarClaseTablaUML(pkg, diag, "DemandaForecastDomainService", "control",
        [
            { nombre: "modelEngine", tipo: "HoltWintersPredictor" },
            { nombre: "aprioriEngine", tipo: "AprioriAssociationMiner" },
            { nombre: "safetyStockFactor", tipo: "float = 1.65" }
        ],
        [
            { nombre: "generarPrediccionDemanda", retorno: "DemandForecastDTO", parametros: [{ nombre: "dias", tipo: "int" }, { nombre: "empresaId", tipo: "int" }] },
            { nombre: "extraerPatronesCoocurrencia", retorno: "AssociationRuleDTO[]", parametros: [{ nombre: "empresaId", tipo: "int" }] },
            { nombre: "calcularSugerenciasReabastecimiento", retorno: "RestockSuggestion[]", parametros: [{ nombre: "empresaId", tipo: "int" }] },
            { nombre: "ejecutarReentrenamientoLote", retorno: "TrainingResultDTO", parametros: [] }
        ],
        790, 160, 280, 210
    );

    // --- Columna 5 & 6: Entities ---
    var e1 = agregarClaseTablaUML(pkg, diag, "t_venta", "entity",
        [
            { nombre: "id_venta", tipo: "serial [PK]" },
            { nombre: "id_empresa", tipo: "integer [FK]" },
            { nombre: "id_sucursal", tipo: "integer [FK]" },
            { nombre: "fecha", tipo: "timestamp" },
            { nombre: "total", tipo: "numeric(12,2)" },
            { nombre: "estado", tipo: "varchar(20)" }
        ],
        [
            { nombre: "getVentasHistoricas", retorno: "VentaRow[]", parametros: [{ nombre: "empresaId", tipo: "int" }, { nombre: "months", tipo: "int" }] }
        ],
        1110, 40, 230, 160
    );

    var e2 = agregarClaseTablaUML(pkg, diag, "t_detalle_venta", "entity",
        [
            { nombre: "id_detalle", tipo: "serial [PK]" },
            { nombre: "id_venta", tipo: "integer [FK]" },
            { nombre: "id_producto_var", tipo: "integer [FK]" },
            { nombre: "cantidad", tipo: "integer" },
            { nombre: "precio_unitario", tipo: "numeric(12,2)" }
        ],
        [
            { nombre: "getTransaccionesParaApriori", retorno: "BasketTransaction[]", parametros: [{ nombre: "empresaId", tipo: "int" }] }
        ],
        1110, 230, 230, 150
    );

    var e3 = agregarClaseTablaUML(pkg, diag, "t_inventario", "entity",
        [
            { nombre: "id_inventario", tipo: "serial [PK]" },
            { nombre: "id_sucursal", tipo: "integer [FK]" },
            { nombre: "id_producto", tipo: "integer [FK]" },
            { nombre: "stock_actual", tipo: "integer" },
            { nombre: "stock_minimo", tipo: "integer" }
        ],
        [
            { nombre: "listStockActual", retorno: "Inventario[]", parametros: [{ nombre: "empresaId", tipo: "int" }] }
        ],
        1110, 410, 230, 140
    );

    var e4 = agregarClaseTablaUML(pkg, diag, "t_producto", "entity",
        [
            { nombre: "id_producto", tipo: "serial [PK]" },
            { nombre: "nombre", tipo: "varchar(150)" },
            { nombre: "categoria_id", tipo: "integer [FK]" },
            { nombre: "precio_base", tipo: "numeric(12,2)" },
            { nombre: "activo", tipo: "boolean" }
        ],
        [
            { nombre: "listActivos", retorno: "Producto[]", parametros: [{ nombre: "empresaId", tipo: "int" }] }
        ],
        1370, 70, 220, 150
    );

    var e5 = agregarClaseTablaUML(pkg, diag, "t_recomendacion", "entity",
        [
            { nombre: "id_recomendacion", tipo: "serial [PK]" },
            { nombre: "id_empresa", tipo: "integer [FK]" },
            { nombre: "producto_antecedente", tipo: "integer [FK]" },
            { nombre: "producto_consecuente", tipo: "integer [FK]" },
            { nombre: "soporte", tipo: "float" },
            { nombre: "confianza", tipo: "float" },
            { nombre: "lift", tipo: "float" },
            { nombre: "fecha_calculo", tipo: "timestamp" }
        ],
        [
            { nombre: "saveBatchReglas", retorno: "void", parametros: [{ nombre: "reglas", tipo: "ReglaItem[]" }] },
            { nombre: "getReglasVigentes", retorno: "ReglaItem[]", parametros: [{ nombre: "empresaId", tipo: "int" }] }
        ],
        1370, 250, 220, 190
    );

    // --- Conexiones Ortogonales ---
    conectarElementos(act, b1, "Association", "consulta analítica", null, "1", "1");
    conectarElementos(act, b2, "Association", "inspecciona gráfico", null, "1", "1");
    conectarElementos(act, b3, "Association", "revisa sugerencias", null, "1", "1");

    conectarElementos(b1, cRoute, "Dependency", "GET predicciones", "use", null, null);
    conectarElementos(b2, cRoute, "Dependency", "GET series", "use", null, null);
    conectarElementos(b3, cRoute, "Dependency", "POST orden compra", "use", null, null);

    conectarElementos(cRoute, cDomain, "Association", "ejecuta modelos", null, "1", "1");
    conectarElementos(cDomain, e1, "Dependency", "lee ventas", "use", null, null);
    conectarElementos(cDomain, e2, "Dependency", "analiza canastas", "use", null, null);
    conectarElementos(cDomain, e3, "Dependency", "compara existencias", "use", null, null);
    conectarElementos(cDomain, e4, "Dependency", "consulta catálogo", "use", null, null);
    conectarElementos(cDomain, e5, "Dependency", "persiste reglas", "use", null, null);

    diag.Update();
    Repository.ReloadDiagram(diag.DiagramID);
}


// =================================================================================================
// 2. CU26W / CU08M: Registrar valoración de producto (Post-Venta / Reviews & Ratings)
// =================================================================================================
function generarClasesCU26W(pkg) {
    Session.Output(" -> Construyendo: cd CU26W - Registrar valoración de producto");
    var diag = pkg.Diagrams.AddNew("cd CU26W - Registrar valoración de producto", "Logical");
    diag.Update();
    configurarDiagramaTablasUML(diag);

    // --- Columna 1: Actor ---
    var act = agregarActor(pkg, diag, "Cliente / Usuario", 40, 220, 90, 110);

    // --- Columna 2: Boundary ---
    var b1 = agregarClaseTablaUML(pkg, diag, "VentaConfirmadaView", "boundary",
        [
            { nombre: "pedidoId", tipo: "number" },
            { nombre: "itemsComprados", tipo: "ItemCompradoDTO[]" },
            { nombre: "valoracionesRealizadas", tipo: "Map<number, boolean>" }
        ],
        [
            { nombre: "abrirModalValoracion", retorno: "void", parametros: [{ nombre: "productoId", tipo: "number" }] },
            { nombre: "marcarItemComoValorado", retorno: "void", parametros: [{ nombre: "productoId", tipo: "number" }] }
        ],
        180, 50, 240, 130
    );

    var b2 = agregarClaseTablaUML(pkg, diag, "ModalValoracionProducto", "boundary",
        [
            { nombre: "selectedProductoId", tipo: "number" },
            { nombre: "puntuacionEstrellas", tipo: "number = 5" },
            { nombre: "comentarioTexto", tipo: "string" },
            { nombre: "fotosAdjuntas", tipo: "File[]" },
            { nombre: "isSubmitting", tipo: "boolean" }
        ],
        [
            { nombre: "seleccionarCalificacion", retorno: "void", parametros: [{ nombre: "stars", tipo: "number" }] },
            { nombre: "enviarValoracion", retorno: "void", parametros: [] },
            { nombre: "cancelar", retorno: "void", parametros: [] }
        ],
        180, 210, 240, 150
    );

    var b3 = agregarClaseTablaUML(pkg, diag, "AlertaValoracionDuplicadaDialog", "boundary",
        [
            { nombre: "mensajeError", tipo: "string" }
        ],
        [
            { nombre: "mostrarDialogo", retorno: "void", parametros: [{ nombre: "msg", tipo: "string" }] },
            { nombre: "cerrar", retorno: "void", parametros: [] }
        ],
        180, 390, 240, 100
    );

    // --- Columna 3: Controller Principal ---
    var cRoute = agregarClaseTablaUML(pkg, diag, "ValoracionRouteController", "control",
        [
            { nombre: "prefix", tipo: "string = '/api/v1/catalogo'" },
            { nombre: "db", tipo: "AsyncSession" },
            { nombre: "clientAuth", tipo: "JWTBearer" }
        ],
        [
            { nombre: "postRegistrarValoracion", retorno: "JSONResponse", parametros: [{ nombre: "body", tipo: "ValoracionCreateDTO" }, { nombre: "user", tipo: "UserToken" }] },
            { nombre: "getValoracionesProducto", retorno: "JSONResponse", parametros: [{ nombre: "productoId", tipo: "int" }, { nombre: "page", tipo: "int" }] }
        ],
        470, 170, 280, 170
    );

    // --- Columna 4: Domain Service ---
    var cDomain = agregarClaseTablaUML(pkg, diag, "ValoracionDomainService", "control",
        [
            { nombre: "profanityFilter", tipo: "ContentModerator" },
            { nombre: "mediaStorage", tipo: "CloudinaryUploader" },
            { nombre: "auditLogger", tipo: "AuditService" }
        ],
        [
            { nombre: "registrarValoracionCliente", retorno: "ValoracionReceiptDTO", parametros: [{ nombre: "data", tipo: "ValoracionData" }, { nombre: "clienteId", tipo: "int" }] },
            { nombre: "validarCompraPrevia", retorno: "boolean", parametros: [{ nombre: "clienteId", tipo: "int" }, { nombre: "productoId", tipo: "int" }] },
            { nombre: "recalcularRatingProductoCache", retorno: "void", parametros: [{ nombre: "productoId", tipo: "int" }] }
        ],
        790, 160, 280, 180
    );

    // --- Columna 5 & 6: Entities ---
    var e1 = agregarClaseTablaUML(pkg, diag, "t_valoracion", "entity",
        [
            { nombre: "id_valoracion", tipo: "serial [PK]" },
            { nombre: "id_producto", tipo: "integer [FK]" },
            { nombre: "id_cliente", tipo: "integer [FK]" },
            { nombre: "id_venta", tipo: "integer [FK]" },
            { nombre: "calificacion", tipo: "integer" },
            { nombre: "comentario", tipo: "text" },
            { nombre: "fecha", tipo: "timestamp" },
            { nombre: "estado", tipo: "varchar(20)" }
        ],
        [
            { nombre: "findByClienteProducto", retorno: "Valoracion", parametros: [{ nombre: "cliId", tipo: "int" }, { nombre: "prodId", tipo: "int" }] },
            { nombre: "insertValoracion", retorno: "int", parametros: [{ nombre: "val", tipo: "ValoracionData" }] },
            { nombre: "listByProducto", retorno: "Valoracion[]", parametros: [{ nombre: "prodId", tipo: "int" }] }
        ],
        1110, 60, 230, 200
    );

    var e2 = agregarClaseTablaUML(pkg, diag, "t_producto", "entity",
        [
            { nombre: "id_producto", tipo: "serial [PK]" },
            { nombre: "nombre", tipo: "varchar(150)" },
            { nombre: "rating_promedio", tipo: "numeric(3,2)" },
            { nombre: "total_reviews", tipo: "integer" },
            { nombre: "activo", tipo: "boolean" }
        ],
        [
            { nombre: "updateRatingCache", retorno: "void", parametros: [{ nombre: "id", tipo: "int" }, { nombre: "rating", tipo: "numeric" }, { nombre: "count", tipo: "int" }] },
            { nombre: "findById", retorno: "Producto", parametros: [{ nombre: "id", tipo: "int" }] }
        ],
        1110, 290, 230, 160
    );

    var e3 = agregarClaseTablaUML(pkg, diag, "t_producto_talla_color", "entity",
        [
            { nombre: "id_variante", tipo: "serial [PK]" },
            { nombre: "id_producto", tipo: "integer [FK]" },
            { nombre: "id_talla", tipo: "integer [FK]" },
            { nombre: "id_color", tipo: "integer [FK]" },
            { nombre: "codigo_sku", tipo: "varchar(50)" }
        ],
        [
            { nombre: "findByProducto", retorno: "Variante[]", parametros: [{ nombre: "prodId", tipo: "int" }] }
        ],
        1370, 100, 220, 150
    );

    var e4 = agregarClaseTablaUML(pkg, diag, "t_bitacora", "entity",
        [
            { nombre: "id_bitacora", tipo: "serial [PK]" },
            { nombre: "id_usuario", tipo: "integer [FK]" },
            { nombre: "accion", tipo: "varchar(100)" },
            { nombre: "modulo", tipo: "varchar(50)" },
            { nombre: "detalle", tipo: "text" },
            { nombre: "fecha", tipo: "timestamp" }
        ],
        [
            { nombre: "registrar", retorno: "void", parametros: [{ nombre: "modulo", tipo: "string" }, { nombre: "accion", tipo: "string" }, { nombre: "detalle", tipo: "string" }] }
        ],
        1370, 280, 220, 150
    );

    // --- Conexiones Ortogonales ---
    conectarElementos(act, b1, "Association", "revisa pedido", null, "1", "1");
    conectarElementos(act, b2, "Association", "califica prenda", null, "1", "1");
    conectarElementos(act, b3, "Association", "recibe alerta", null, "1", "1");

    conectarElementos(b1, cRoute, "Dependency", "GET historial", "use", null, null);
    conectarElementos(b2, cRoute, "Dependency", "POST valoracion", "use", null, null);

    conectarElementos(cRoute, cDomain, "Association", "delega valoracion", null, "1", "1");
    conectarElementos(cDomain, e1, "Dependency", "persiste calificacion", "use", null, null);
    conectarElementos(cDomain, e2, "Dependency", "recalcula rating", "use", null, null);
    conectarElementos(cDomain, e3, "Dependency", "valida variante", "use", null, null);
    conectarElementos(cDomain, e4, "Dependency", "audita calificacion", "use", null, null);

    diag.Update();
    Repository.ReloadDiagram(diag.DiagramID);
}


// =================================================================================================
// FUNCIÓN PRINCIPAL DE EJECUCIÓN EN ENTERPRISE ARCHITECT
// =================================================================================================
function Main() {
    Repository.EnsureOutputVisible("Script");
    Session.Output("================================================================================");
    Session.Output("Iniciando generación de Diagramas de Análisis de Clases (CU23W & CU26W) en EA...");
    Session.Output("================================================================================");

    var pkg = Repository.GetTreeSelectedPackage();
    if (pkg == null) {
        Session.Prompt("ERROR: Por favor seleccione un paquete en el Project Browser antes de ejecutar.", 0);
        return;
    }

    var pkgName = "Diagramas de Análisis de Clases (ICONIX) - Lote Final (CU23W y CU26W)";
    var subPkg = null;
    for (var i = 0; i < pkg.Packages.Count; i++) {
        var p = pkg.Packages.GetAt(i);
        if (p.Name == pkgName) {
            subPkg = p;
            break;
        }
    }
    if (subPkg == null) {
        subPkg = pkg.Packages.AddNew(pkgName, "");
        subPkg.Update();
        pkg.Packages.Refresh();
    }

    Session.Output("Paquete destino: " + subPkg.Name);

    generarClasesCU23W(subPkg);
    generarClasesCU26W(subPkg);

    Repository.RefreshModelView(subPkg.PackageID);
    Session.Output("================================================================================");
    Session.Output(" [OK] Se generaron exitosamente los diagramas finales de análisis de clases (CU23W y CU26W/CU08M).");
    Session.Output(" Paquete: " + subPkg.Name);
    Session.Output("================================================================================");
}

Main();
"""

def main():
    js_content = build_javascript_content()
    
    # 1. Write docs/enterprise_architect
    js_path = os.path.join("docs", "enterprise_architect", "AuroraStore_CU23W_CU26W_ClassAnalysis_FINAL_EA.js")
    with open(js_path, "w", encoding="utf-8") as f:
        f.write(js_content)
    print(f"[OK] Archivo JavaScript generado: {js_path} ({len(js_content)} bytes)")

    # 2. Write root
    root_js_path = "AuroraStore_CU23W_CU26W_ClassAnalysis_FINAL_EA.js"
    with open(root_js_path, "w", encoding="utf-8") as f:
        f.write(js_content)
    print(f"[OK] Copia en raíz generada: {root_js_path}")

if __name__ == "__main__":
    main()
