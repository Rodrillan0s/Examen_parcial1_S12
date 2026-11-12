/*
 * =================================================================================================
 * SCRIPT MAESTRO DE AUTOMATIZACIÓN DE DIAGRAMAS DE ANÁLISIS DE CLASES UML 2.5 (ICONIX VOPC) PARA SPARX EA
 * =================================================================================================
 * Proyecto: AuroraStore SaaS
 * Lote 3: CU11W a CU15W
 *   - cd CU11W - Buscar y filtrar productos
 *   - cd CU12W - Consultar detalles de producto
 *   - cd CU13W - Consultar disponibilidad por sucursal
 *   - cd CU14W - Gestionar reservas
 *   - cd CU15W - Gestionar inventario
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
// 1. CU11W / CU02M: Buscar y filtrar productos (Web y Móvil)
// =================================================================================================
function generarCU11W(pkg) {
    Session.Output(" -> Construyendo: cd CU11W - Buscar y filtrar productos");
    var diag = pkg.Diagrams.AddNew("cd CU11W - Buscar y filtrar productos", "Logical");
    configurarDiagramaTablasUML(diag);

    // Col 1: Actor
    var actor = agregarActor(pkg, diag, "Usuario / Cliente", 40, 240, 90, 100);

    // Col 2: Boundaries (Vistas y Modales)
    var b1 = agregarClaseTablaUML(pkg, diag, "BusquedaFiltrosView", "boundary",
        [
            { nombre: "id_empresa", tipo: "int", vis: "Private" },
            { nombre: "query_busqueda", tipo: "string", vis: "Private" },
            { nombre: "filtros_activos", tipo: "FiltroDTO", vis: "Private" },
            { nombre: "resultados", tipo: "List<ProductoCardDTO>", vis: "Private" },
            { nombre: "modo_offline", tipo: "boolean", vis: "Private" }
        ],
        [
            { nombre: "ngOnInit", retorno: "void" },
            { nombre: "onBuscarInput", retorno: "void", parametros: [{ nombre: "q", tipo: "string" }] },
            { nombre: "abrirModalFiltros", retorno: "void" },
            { nombre: "seleccionarProducto", retorno: "void", parametros: [{ nombre: "id", tipo: "int" }] }
        ],
        180, 40, 240, 160
    );

    var b2 = agregarClaseTablaUML(pkg, diag, "FiltroAvanzadoModal", "boundary",
        [
            { nombre: "visible", tipo: "boolean", vis: "Private" },
            { nombre: "rango_precios", tipo: "Range<decimal>", vis: "Private" },
            { nombre: "tallas_seleccionadas", tipo: "List<int>", vis: "Private" },
            { nombre: "colores_seleccionados", tipo: "List<int>", vis: "Private" }
        ],
        [
            { nombre: "abrir", retorno: "void" },
            { nombre: "aplicarFiltros", retorno: "void" },
            { nombre: "limpiar", retorno: "void" }
        ],
        180, 230, 240, 150
    );

    var b3 = agregarClaseTablaUML(pkg, diag, "ResultadoBusquedaVacioDialog", "boundary",
        [
            { nombre: "visible", tipo: "boolean", vis: "Private" },
            { nombre: "termino_fallido", tipo: "string", vis: "Private" },
            { nombre: "sugerencias", tipo: "List<string>", vis: "Private" }
        ],
        [
            { nombre: "mostrar", retorno: "void", parametros: [{ nombre: "sug", tipo: "List<string>" }] },
            { nombre: "reintentar", retorno: "void" }
        ],
        180, 410, 240, 130
    );

    var b4 = agregarClaseTablaUML(pkg, diag, "ModoOfflineBadge", "boundary",
        [
            { nombre: "sin_conexion", tipo: "boolean", vis: "Private" },
            { nombre: "total_productos_locales", tipo: "int", vis: "Private" }
        ],
        [
            { nombre: "actualizarEstadoRed", retorno: "void", parametros: [{ nombre: "online", tipo: "boolean" }] }
        ],
        180, 570, 240, 100
    );

    // Col 3: Main Route Controller
    var cRoutes = agregarClaseTablaUML(pkg, diag, "catalogo_routes (RouteController)", "control",
        [
            { nombre: "router", tipo: "APIRouter", vis: "Private" },
            { nombre: "prefix", tipo: "string = '/api/catalogo'", vis: "Private" }
        ],
        [
            { nombre: "buscar_y_filtrar", retorno: "Response", parametros: [{ nombre: "id_empresa", tipo: "int" }, { nombre: "params", tipo: "FiltroDTO" }] },
            { nombre: "obtener_sugerencias", retorno: "Response", parametros: [{ nombre: "id_empresa", tipo: "int" }, { nombre: "q", tipo: "string" }] }
        ],
        470, 200, 280, 170
    );

    // Col 4: Domain Service & Offline Storage
    var cServices = agregarClaseTablaUML(pkg, diag, "catalogo_services (DomainService)", "control",
        [
            { nombre: "db", tipo: "PostgreSQL", vis: "Private" },
            { nombre: "cache", tipo: "CacheService", vis: "Private" }
        ],
        [
            { nombre: "filtrar_productos_service", retorno: "List<ProductoCardDTO>", parametros: [{ nombre: "id_empresa", tipo: "int" }, { nombre: "params", tipo: "dict" }] },
            { nombre: "generar_facetas_activas", retorno: "dict", parametros: [{ nombre: "id_empresa", tipo: "int" }] }
        ],
        790, 110, 280, 160
    );

    var cOffline = agregarClaseTablaUML(pkg, diag, "offline_cache_manager (ClientStorage)", "control",
        [
            { nombre: "db_local", tipo: "IndexedDB / SQLite", vis: "Private" }
        ],
        [
            { nombre: "buscarEnCacheLocal", retorno: "List<ProductoCardDTO>", parametros: [{ nombre: "query", tipo: "string" }, { nombre: "filtros", tipo: "dict" }] }
        ],
        790, 300, 280, 140
    );

    // Col 5 & 6: Entities
    var eProducto = agregarClaseTablaUML(pkg, diag, "t_producto", "entity",
        [
            { nombre: "id_producto [PK]", tipo: "int", vis: "Public" },
            { nombre: "id_empresa [FK]", tipo: "int", vis: "Public" },
            { nombre: "id_categoria [FK]", tipo: "int", vis: "Public" },
            { nombre: "nombre", tipo: "string", vis: "Public" },
            { nombre: "precio_base", tipo: "decimal", vis: "Public" }
        ],
        [
            { nombre: "searchByTextAndFilters", retorno: "List<t_producto>", parametros: [{ nombre: "id_empresa", tipo: "int" }, { nombre: "f", tipo: "dict" }] }
        ],
        1110, 40, 230, 150
    );

    var eCategoria = agregarClaseTablaUML(pkg, diag, "t_categoria", "entity",
        [
            { nombre: "id_categoria [PK]", tipo: "int", vis: "Public" },
            { nombre: "nombre", tipo: "string", vis: "Public" }
        ],
        [
            { nombre: "findByEmpresa", retorno: "List<t_categoria>", parametros: [{ nombre: "id_empresa", tipo: "int" }] }
        ],
        1110, 220, 230, 120
    );

    var eVariante = agregarClaseTablaUML(pkg, diag, "t_producto_talla_color", "entity",
        [
            { nombre: "id_producto_talla_color [PK]", tipo: "int", vis: "Public" },
            { nombre: "id_producto [FK]", tipo: "int", vis: "Public" },
            { nombre: "id_talla [FK]", tipo: "int", vis: "Public" },
            { nombre: "id_color [FK]", tipo: "int", vis: "Public" }
        ],
        [
            { nombre: "filterByTallaColor", retorno: "List<int>", parametros: [{ nombre: "tallas", tipo: "List<int>" }, { nombre: "colores", tipo: "List<int>" }] }
        ],
        1110, 370, 230, 150
    );

    var eTalla = agregarClaseTablaUML(pkg, diag, "t_talla", "entity",
        [
            { nombre: "id_talla [PK]", tipo: "int", vis: "Public" },
            { nombre: "nombre", tipo: "string", vis: "Public" }
        ],
        [
            { nombre: "findAll", retorno: "List<t_talla>" }
        ],
        1370, 100, 220, 100
    );

    var eColor = agregarClaseTablaUML(pkg, diag, "t_color", "entity",
        [
            { nombre: "id_color [PK]", tipo: "int", vis: "Public" },
            { nombre: "nombre", tipo: "string", vis: "Public" }
        ],
        [
            { nombre: "findAll", retorno: "List<t_color>" }
        ],
        1370, 230, 220, 100
    );

    var eCacheLocal = agregarClaseTablaUML(pkg, diag, "cache_local (IndexedDB / SQLite)", "entity",
        [
            { nombre: "id [PK]", tipo: "int", vis: "Public" },
            { nombre: "payload_json", tipo: "text", vis: "Public" }
        ],
        [
            { nombre: "searchProductsOffline", retorno: "List<dict>", parametros: [{ nombre: "tokens", tipo: "List<string>" }] }
        ],
        1370, 360, 220, 120
    );

    // Conexiones
    conectarElementos(actor, b1, "Association", "", "");
    conectarElementos(b1, b2, "Dependency", "abre", "«use»");
    conectarElementos(b1, b4, "Dependency", "monitorea", "«use»");

    conectarElementos(b1, cRoutes, "Dependency", "consume_online", "«use»");
    conectarElementos(b1, cOffline, "Dependency", "fallback_offline", "«use»");
    conectarElementos(cRoutes, b3, "Dependency", "notifica_vacio", "«use»");

    conectarElementos(cRoutes, cServices, "Dependency", "delega", "«use»");

    conectarElementos(cServices, eProducto, "Dependency", "consulta", "«use»");
    conectarElementos(cServices, eCategoria, "Dependency", "consulta", "«use»");
    conectarElementos(cServices, eVariante, "Dependency", "consulta", "«use»");
    conectarElementos(cOffline, eCacheLocal, "Dependency", "consulta_local", "«use»");

    conectarElementos(eCategoria, eProducto, "Association", "clasifica", "", "1", "0..*");
    conectarElementos(eProducto, eVariante, "Association", "contiene", "", "1", "1..*");
    conectarElementos(eTalla, eVariante, "Association", "dimensiona", "", "1", "0..*");
    conectarElementos(eColor, eVariante, "Association", "matiza", "", "1", "0..*");

    diag.Update();
    Repository.ReloadDiagram(diag.DiagramID);
}

// =================================================================================================
// 2. CU12W / CU03M: Consultar detalles de producto (Web y Móvil)
// =================================================================================================
function generarCU12W(pkg) {
    Session.Output(" -> Construyendo: cd CU12W - Consultar detalles de producto");
    var diag = pkg.Diagrams.AddNew("cd CU12W - Consultar detalles de producto", "Logical");
    configurarDiagramaTablasUML(diag);

    var actor = agregarActor(pkg, diag, "Usuario / Cliente", 40, 240, 90, 100);

    var b1 = agregarClaseTablaUML(pkg, diag, "DetalleProductoView", "boundary",
        [
            { nombre: "id_producto", tipo: "int", vis: "Private" },
            { nombre: "producto", tipo: "ProductoDetalleDTO", vis: "Private" },
            { nombre: "variante_seleccionada", tipo: "VarianteDTO", vis: "Private" },
            { nombre: "cargando", tipo: "boolean", vis: "Private" }
        ],
        [
            { nombre: "ngOnInit", retorno: "void" },
            { nombre: "cargarFicha", retorno: "void", parametros: [{ nombre: "id", tipo: "int" }] },
            { nombre: "onSeleccionarTalla", retorno: "void", parametros: [{ nombre: "id_talla", tipo: "int" }] },
            { nombre: "abrirGuiaTallas", retorno: "void" }
        ],
        180, 40, 240, 160
    );

    var b2 = agregarClaseTablaUML(pkg, diag, "GuiaTallasModal", "boundary",
        [
            { nombre: "visible", tipo: "boolean", vis: "Private" },
            { nombre: "tabla_medidas", tipo: "List<MedidaDTO>", vis: "Private" }
        ],
        [
            { nombre: "abrir", retorno: "void", parametros: [{ nombre: "id_categoria", tipo: "int" }] },
            { nombre: "cerrar", retorno: "void" }
        ],
        180, 230, 240, 130
    );

    var b3 = agregarClaseTablaUML(pkg, diag, "VarianteAgotadaDialog", "boundary",
        [
            { nombre: "visible", tipo: "boolean", vis: "Private" },
            { nombre: "mensaje", tipo: "string", vis: "Private" }
        ],
        [
            { nombre: "mostrar", retorno: "void", parametros: [{ nombre: "alt", tipo: "VarianteDTO" }] },
            { nombre: "cerrar", retorno: "void" }
        ],
        180, 390, 240, 120
    );

    // Col 3: Route Controller
    var cRoutes = agregarClaseTablaUML(pkg, diag, "catalogo_routes (RouteController)", "control",
        [
            { nombre: "router", tipo: "APIRouter", vis: "Private" },
            { nombre: "prefix", tipo: "string = '/api/catalogo'", vis: "Private" }
        ],
        [
            { nombre: "obtener_detalle_producto", retorno: "Response", parametros: [{ nombre: "id_producto", tipo: "int" }] },
            { nombre: "consultar_imagenes_galeria", retorno: "Response", parametros: [{ nombre: "id_producto", tipo: "int" }] }
        ],
        470, 200, 280, 160
    );

    // Col 4: Domain Service & Offline Storage
    var cServices = agregarClaseTablaUML(pkg, diag, "catalogo_services (DomainService)", "control",
        [
            { nombre: "db", tipo: "PostgreSQL", vis: "Private" }
        ],
        [
            { nombre: "obtener_ficha_tecnica", retorno: "ProductoDetalleDTO", parametros: [{ nombre: "id_producto", tipo: "int" }] },
            { nombre: "sintetizar_detalle_desde_prenda", retorno: "ProductoDetalleDTO", parametros: [{ nombre: "p", tipo: "dict" }] }
        ],
        790, 110, 280, 160
    );

    var cOffline = agregarClaseTablaUML(pkg, diag, "offline_cache_manager (ClientStorage)", "control",
        [
            { nombre: "db_local", tipo: "IndexedDB / SQLite", vis: "Private" }
        ],
        [
            { nombre: "getProductDetail", retorno: "ProductoDetalleDTO", parametros: [{ nombre: "id", tipo: "int" }] },
            { nombre: "cacheProductView", retorno: "void", parametros: [{ nombre: "id", tipo: "int" }] }
        ],
        790, 300, 280, 140
    );

    // Col 5 & 6: Entities
    var eProducto = agregarClaseTablaUML(pkg, diag, "t_producto", "entity",
        [
            { nombre: "id_producto [PK]", tipo: "int", vis: "Public" },
            { nombre: "id_categoria [FK]", tipo: "int", vis: "Public" },
            { nombre: "nombre", tipo: "string", vis: "Public" },
            { nombre: "descripcion", tipo: "text", vis: "Public" },
            { nombre: "precio_base", tipo: "decimal", vis: "Public" }
        ],
        [
            { nombre: "findByIdWithDetails", retorno: "t_producto", parametros: [{ nombre: "id", tipo: "int" }] }
        ],
        1110, 40, 230, 160
    );

    var eCategoria = agregarClaseTablaUML(pkg, diag, "t_categoria", "entity",
        [
            { nombre: "id_categoria [PK]", tipo: "int", vis: "Public" },
            { nombre: "nombre", tipo: "string", vis: "Public" }
        ],
        [
            { nombre: "findById", retorno: "t_categoria", parametros: [{ nombre: "id", tipo: "int" }] }
        ],
        1110, 230, 230, 120
    );

    var eVariante = agregarClaseTablaUML(pkg, diag, "t_producto_talla_color", "entity",
        [
            { nombre: "id_producto_talla_color [PK]", tipo: "int", vis: "Public" },
            { nombre: "id_producto [FK]", tipo: "int", vis: "Public" },
            { nombre: "sku", tipo: "string", vis: "Public" },
            { nombre: "precio_especifico", tipo: "decimal", vis: "Public" }
        ],
        [
            { nombre: "findByProducto", retorno: "List<t_producto_talla_color>", parametros: [{ nombre: "id", tipo: "int" }] }
        ],
        1110, 380, 230, 150
    );

    var eImagen = agregarClaseTablaUML(pkg, diag, "t_producto_imagen", "entity",
        [
            { nombre: "id_imagen [PK]", tipo: "int", vis: "Public" },
            { nombre: "id_producto [FK]", tipo: "int", vis: "Public" },
            { nombre: "url", tipo: "string", vis: "Public" },
            { nombre: "orden", tipo: "int", vis: "Public" }
        ],
        [
            { nombre: "findByProductoOrderByOrden", retorno: "List<t_producto_imagen>", parametros: [{ nombre: "id", tipo: "int" }] }
        ],
        1370, 100, 220, 140
    );

    var eCacheLocal = agregarClaseTablaUML(pkg, diag, "cache_local (IndexedDB / SQLite)", "entity",
        [
            { nombre: "id [PK]", tipo: "int", vis: "Public" },
            { nombre: "payload_json", tipo: "text", vis: "Public" }
        ],
        [
            { nombre: "getProductDetail", retorno: "dict", parametros: [{ nombre: "id", tipo: "int" }] }
        ],
        1370, 270, 220, 120
    );

    // Conexiones
    conectarElementos(actor, b1, "Association", "", "");
    conectarElementos(b1, b2, "Dependency", "abre", "«use»");

    conectarElementos(b1, cRoutes, "Dependency", "consume_online", "«use»");
    conectarElementos(b1, cOffline, "Dependency", "fallback_offline", "«use»");
    conectarElementos(cRoutes, b3, "Dependency", "notifica_agotado", "«use»");

    conectarElementos(cRoutes, cServices, "Dependency", "delega", "«use»");

    conectarElementos(cServices, eProducto, "Dependency", "consulta", "«use»");
    conectarElementos(cServices, eCategoria, "Dependency", "consulta", "«use»");
    conectarElementos(cServices, eVariante, "Dependency", "consulta", "«use»");
    conectarElementos(cServices, eImagen, "Dependency", "consulta", "«use»");
    conectarElementos(cOffline, eCacheLocal, "Dependency", "lee_detalle", "«use»");

    conectarElementos(eCategoria, eProducto, "Association", "clasifica", "", "1", "0..*");
    conectarElementos(eProducto, eVariante, "Association", "contiene", "", "1", "1..*");
    conectarElementos(eProducto, eImagen, "Association", "ilustra", "", "1", "0..*");

    diag.Update();
    Repository.ReloadDiagram(diag.DiagramID);
}

// =================================================================================================
// 3. CU13W / CU04M: Consultar disponibilidad por sucursal (Web y Móvil)
// =================================================================================================
function generarCU13W(pkg) {
    Session.Output(" -> Construyendo: cd CU13W - Consultar disponibilidad por sucursal");
    var diag = pkg.Diagrams.AddNew("cd CU13W - Consultar disponibilidad por sucursal", "Logical");
    configurarDiagramaTablasUML(diag);

    var actor = agregarActor(pkg, diag, "Usuario / Cliente", 40, 240, 90, 100);

    var b1 = agregarClaseTablaUML(pkg, diag, "DisponibilidadSucursalesView", "boundary",
        [
            { nombre: "id_variante", tipo: "int", vis: "Private" },
            { nombre: "sucursales_stock", tipo: "List<StockSucursalDTO>", vis: "Private" },
            { nombre: "cargando", tipo: "boolean", vis: "Private" }
        ],
        [
            { nombre: "ngOnInit", retorno: "void" },
            { nombre: "consultarStock", retorno: "void", parametros: [{ nombre: "id_var", tipo: "int" }] },
            { nombre: "abrirMapa", retorno: "void", parametros: [{ nombre: "id_suc", tipo: "int" }] }
        ],
        180, 40, 240, 150
    );

    var b2 = agregarClaseTablaUML(pkg, diag, "MapaUbicacionSucursalModal", "boundary",
        [
            { nombre: "visible", tipo: "boolean", vis: "Private" },
            { nombre: "sucursal_sel", tipo: "SucursalDTO", vis: "Private" }
        ],
        [
            { nombre: "abrir", retorno: "void", parametros: [{ nombre: "id", tipo: "int" }] },
            { nombre: "cerrar", retorno: "void" }
        ],
        180, 220, 240, 120
    );

    var b3 = agregarClaseTablaUML(pkg, diag, "SinStockGlobalDialog", "boundary",
        [
            { nombre: "visible", tipo: "boolean", vis: "Private" },
            { nombre: "mensaje", tipo: "string", vis: "Private" }
        ],
        [
            { nombre: "mostrar", retorno: "void" },
            { nombre: "cerrar", retorno: "void" }
        ],
        180, 370, 240, 110
    );

    // Col 3: Route Controller
    var cRoutes = agregarClaseTablaUML(pkg, diag, "inventario_routes (RouteController)", "control",
        [
            { nombre: "router", tipo: "APIRouter", vis: "Private" },
            { nombre: "prefix", tipo: "string = '/api/inventario'", vis: "Private" }
        ],
        [
            { nombre: "consultar_disponibilidad_sucursales", retorno: "Response", parametros: [{ nombre: "id_variante", tipo: "int" }] },
            { nombre: "obtener_sucursales_cercanas", retorno: "Response", parametros: [{ nombre: "id_empresa", tipo: "int" }] }
        ],
        470, 180, 280, 160
    );

    // Col 4: Domain Service & Offline Storage
    var cServices = agregarClaseTablaUML(pkg, diag, "inventario_services (DomainService)", "control",
        [
            { nombre: "db", tipo: "PostgreSQL", vis: "Private" }
        ],
        [
            { nombre: "consultar_stock_por_sucursal", retorno: "List<StockSucursalDTO>", parametros: [{ nombre: "id_variante", tipo: "int" }] },
            { nombre: "verificar_disponibilidad_reserva", retorno: "boolean", parametros: [{ nombre: "id_variante", tipo: "int" }, { nombre: "id_sucursal", tipo: "int" }] }
        ],
        790, 100, 280, 160
    );

    var cOffline = agregarClaseTablaUML(pkg, diag, "offline_cache_manager (ClientStorage)", "control",
        [
            { nombre: "db_local", tipo: "IndexedDB / SQLite", vis: "Private" }
        ],
        [
            { nombre: "getSucursalesOffline", retorno: "List<SucursalDTO>", parametros: [{ nombre: "id_empresa", tipo: "int" }] },
            { nombre: "consultarStockLocal", retorno: "dict", parametros: [{ nombre: "id_variante", tipo: "int" }] }
        ],
        790, 290, 280, 140
    );

    // Col 5 & 6: Entities
    var eSucursal = agregarClaseTablaUML(pkg, diag, "t_sucursal", "entity",
        [
            { nombre: "id_sucursal [PK]", tipo: "int", vis: "Public" },
            { nombre: "id_ciudad [FK]", tipo: "int", vis: "Public" },
            { nombre: "nombre", tipo: "string", vis: "Public" },
            { nombre: "direccion", tipo: "string", vis: "Public" },
            { nombre: "activo", tipo: "boolean", vis: "Public" }
        ],
        [
            { nombre: "findAllActivas", retorno: "List<t_sucursal>" }
        ],
        1110, 40, 230, 150
    );

    var eVariante = agregarClaseTablaUML(pkg, diag, "t_producto_talla_color", "entity",
        [
            { nombre: "id_producto_talla_color [PK]", tipo: "int", vis: "Public" },
            { nombre: "sku", tipo: "string", vis: "Public" }
        ],
        [
            { nombre: "findById", retorno: "t_producto_talla_color", parametros: [{ nombre: "id", tipo: "int" }] }
        ],
        1110, 220, 230, 120
    );

    var eInventario = agregarClaseTablaUML(pkg, diag, "t_inventario", "entity",
        [
            { nombre: "id_inventario [PK]", tipo: "int", vis: "Public" },
            { nombre: "id_producto_talla_color [FK]", tipo: "int", vis: "Public" },
            { nombre: "id_sucursal [FK]", tipo: "int", vis: "Public" },
            { nombre: "stock_actual", tipo: "int", vis: "Public" }
        ],
        [
            { nombre: "findByVarianteGroupBySucursal", retorno: "List<t_inventario>", parametros: [{ nombre: "id_var", tipo: "int" }] }
        ],
        1110, 370, 230, 150
    );

    var eCiudad = agregarClaseTablaUML(pkg, diag, "t_ciudad", "entity",
        [
            { nombre: "id_ciudad [PK]", tipo: "int", vis: "Public" },
            { nombre: "nombre", tipo: "string", vis: "Public" }
        ],
        [
            { nombre: "findById", retorno: "t_ciudad", parametros: [{ nombre: "id", tipo: "int" }] }
        ],
        1370, 100, 220, 110
    );

    var eCacheLocal = agregarClaseTablaUML(pkg, diag, "cache_local (IndexedDB / SQLite)", "entity",
        [
            { nombre: "id [PK]", tipo: "int", vis: "Public" },
            { nombre: "payload_json", tipo: "text", vis: "Public" }
        ],
        [
            { nombre: "getSucursales", retorno: "List<dict>" }
        ],
        1370, 240, 220, 120
    );

    // Conexiones
    conectarElementos(actor, b1, "Association", "", "");
    conectarElementos(b1, b2, "Dependency", "abre", "«use»");

    conectarElementos(b1, cRoutes, "Dependency", "consume_online", "«use»");
    conectarElementos(b1, cOffline, "Dependency", "fallback_offline", "«use»");
    conectarElementos(cRoutes, b3, "Dependency", "notifica_sin_stock", "«use»");

    conectarElementos(cRoutes, cServices, "Dependency", "delega", "«use»");

    conectarElementos(cServices, eSucursal, "Dependency", "consulta", "«use»");
    conectarElementos(cServices, eVariante, "Dependency", "consulta", "«use»");
    conectarElementos(cServices, eInventario, "Dependency", "consulta", "«use»");
    conectarElementos(cOffline, eCacheLocal, "Dependency", "lee_sucursales", "«use»");

    conectarElementos(eCiudad, eSucursal, "Association", "ubica", "", "1", "0..*");
    conectarElementos(eSucursal, eInventario, "Association", "almacena", "", "1", "0..*");
    conectarElementos(eVariante, eInventario, "Association", "stock_en", "", "1", "0..*");

    diag.Update();
    Repository.ReloadDiagram(diag.DiagramID);
}

// =================================================================================================
// 4. CU14W / CU05M: Gestionar reservas (Web y Móvil)
// =================================================================================================
function generarCU14W(pkg) {
    Session.Output(" -> Construyendo: cd CU14W - Gestionar reservas");
    var diag = pkg.Diagrams.AddNew("cd CU14W - Gestionar reservas", "Logical");
    configurarDiagramaTablasUML(diag);

    var actor = agregarActor(pkg, diag, "Cliente / Usuario", 40, 240, 90, 100);

    var b1 = agregarClaseTablaUML(pkg, diag, "MisReservasView", "boundary",
        [
            { nombre: "id_cliente", tipo: "int", vis: "Private" },
            { nombre: "reservas_lista", tipo: "List<ReservaDTO>", vis: "Private" },
            { nombre: "cargando", tipo: "boolean", vis: "Private" }
        ],
        [
            { nombre: "ngOnInit", retorno: "void" },
            { nombre: "cargarReservas", retorno: "void" },
            { nombre: "abrirModalNuevaReserva", retorno: "void" },
            { nombre: "abrirModalCancelar", retorno: "void", parametros: [{ nombre: "id", tipo: "int" }] }
        ],
        180, 40, 240, 160
    );

    var b2 = agregarClaseTablaUML(pkg, diag, "CrearReservaModal", "boundary",
        [
            { nombre: "visible", tipo: "boolean", vis: "Private" },
            { nombre: "id_sucursal", tipo: "int", vis: "Private" },
            { nombre: "fecha_reserva", tipo: "datetime", vis: "Private" },
            { nombre: "items_reserva", tipo: "List<DetalleReservaDTO>", vis: "Private" }
        ],
        [
            { nombre: "abrir", retorno: "void" },
            { nombre: "onSubmit", retorno: "void" },
            { nombre: "cerrar", retorno: "void" }
        ],
        180, 230, 240, 150
    );

    var b3 = agregarClaseTablaUML(pkg, diag, "CancelarReservaModal", "boundary",
        [
            { nombre: "visible", tipo: "boolean", vis: "Private" },
            { nombre: "id_reserva", tipo: "int", vis: "Private" },
            { nombre: "motivo", tipo: "string", vis: "Private" }
        ],
        [
            { nombre: "abrir", retorno: "void", parametros: [{ nombre: "id", tipo: "int" }] },
            { nombre: "confirmarCancelacion", retorno: "void" }
        ],
        180, 410, 240, 120
    );

    var b4 = agregarClaseTablaUML(pkg, diag, "ErrorDialog", "boundary",
        [
            { nombre: "visible", tipo: "boolean", vis: "Private" },
            { nombre: "mensaje", tipo: "string", vis: "Private" }
        ],
        [
            { nombre: "mostrar", retorno: "void", parametros: [{ nombre: "err", tipo: "string" }] },
            { nombre: "cerrar", retorno: "void" }
        ],
        180, 560, 240, 100
    );

    // Col 3: Route Controller
    var cRoutes = agregarClaseTablaUML(pkg, diag, "reserva_routes (RouteController)", "control",
        [
            { nombre: "router", tipo: "APIRouter", vis: "Private" },
            { nombre: "prefix", tipo: "string = '/api/reservas'", vis: "Private" }
        ],
        [
            { nombre: "listar_mis_reservas", retorno: "Response", parametros: [{ nombre: "id_cliente", tipo: "int" }] },
            { nombre: "crear_reserva", retorno: "Response", parametros: [{ nombre: "dto", tipo: "CrearReservaDTO" }] },
            { nombre: "cancelar_reserva", retorno: "Response", parametros: [{ nombre: "id_reserva", tipo: "int" }] }
        ],
        470, 200, 280, 180
    );

    // Col 4: Domain Service & Offline Storage
    var cServices = agregarClaseTablaUML(pkg, diag, "reserva_services (DomainService)", "control",
        [
            { nombre: "db", tipo: "PostgreSQL", vis: "Private" },
            { nombre: "audit", tipo: "BitacoraService", vis: "Private" }
        ],
        [
            { nombre: "registrar_reserva_temporal", retorno: "dict", parametros: [{ nombre: "dto", tipo: "CrearReservaDTO" }] },
            { nombre: "bloquear_stock_reserva", retorno: "void", parametros: [{ nombre: "id_var", tipo: "int" }, { nombre: "id_suc", tipo: "int" }] },
            { nombre: "liberar_stock_reserva", retorno: "void", parametros: [{ nombre: "id_reserva", tipo: "int" }] },
            { nombre: "expirar_reservas_automaticas", retorno: "int" }
        ],
        790, 100, 280, 180
    );

    var cOffline = agregarClaseTablaUML(pkg, diag, "offline_cache_manager (ClientStorage)", "control",
        [
            { nombre: "db_local", tipo: "IndexedDB / SQLite", vis: "Private" },
            { nombre: "sync_coordinator", tipo: "SyncCoordinator", vis: "Private" }
        ],
        [
            { nombre: "guardarReservaDraft", retorno: "void", parametros: [{ nombre: "draft", tipo: "dict" }] },
            { nombre: "encolarSyncReserva", retorno: "void", parametros: [{ nombre: "op", tipo: "dict" }] }
        ],
        790, 310, 280, 150
    );

    // Col 5 & 6: Entities
    var eCliente = agregarClaseTablaUML(pkg, diag, "t_cliente", "entity",
        [
            { nombre: "id_cliente [PK]", tipo: "int", vis: "Public" },
            { nombre: "nombre", tipo: "string", vis: "Public" },
            { nombre: "telefono", tipo: "string", vis: "Public" }
        ],
        [
            { nombre: "findById", retorno: "t_cliente", parametros: [{ nombre: "id", tipo: "int" }] }
        ],
        1110, 40, 230, 130
    );

    var eReserva = agregarClaseTablaUML(pkg, diag, "t_reserva", "entity",
        [
            { nombre: "id_reserva [PK]", tipo: "int", vis: "Public" },
            { nombre: "id_cliente [FK]", tipo: "int", vis: "Public" },
            { nombre: "id_sucursal [FK]", tipo: "int", vis: "Public" },
            { nombre: "fecha_reserva", tipo: "datetime", vis: "Public" },
            { nombre: "estado", tipo: "string", vis: "Public" }
        ],
        [
            { nombre: "insert", retorno: "int", parametros: [{ nombre: "r", tipo: "dict" }] },
            { nombre: "updateEstado", retorno: "void", parametros: [{ nombre: "id", tipo: "int" }, { nombre: "est", tipo: "string" }] }
        ],
        1110, 200, 230, 160
    );

    var eDetalle = agregarClaseTablaUML(pkg, diag, "t_detalle_reserva", "entity",
        [
            { nombre: "id_detalle_reserva [PK]", tipo: "int", vis: "Public" },
            { nombre: "id_reserva [FK]", tipo: "int", vis: "Public" },
            { nombre: "id_producto_talla_color [FK]", tipo: "int", vis: "Public" },
            { nombre: "cantidad", tipo: "int", vis: "Public" }
        ],
        [
            { nombre: "bulkInsert", retorno: "void", parametros: [{ nombre: "items", tipo: "List<dict>" }] }
        ],
        1110, 390, 230, 150
    );

    var eInventario = agregarClaseTablaUML(pkg, diag, "t_inventario", "entity",
        [
            { nombre: "id_inventario [PK]", tipo: "int", vis: "Public" },
            { nombre: "id_producto_talla_color [FK]", tipo: "int", vis: "Public" },
            { nombre: "stock_actual", tipo: "int", vis: "Public" },
            { nombre: "stock_reservado", tipo: "int", vis: "Public" }
        ],
        [
            { nombre: "reservarStock", retorno: "void", parametros: [{ nombre: "id_var", tipo: "int" }, { nombre: "cant", tipo: "int" }] },
            { nombre: "liberarStock", retorno: "void", parametros: [{ nombre: "id_var", tipo: "int" }, { nombre: "cant", tipo: "int" }] }
        ],
        1370, 100, 220, 160
    );

    var eBitacora = agregarClaseTablaUML(pkg, diag, "t_bitacora", "entity",
        [
            { nombre: "id_bitacora [PK]", tipo: "int", vis: "Public" },
            { nombre: "modulo", tipo: "string", vis: "Public" },
            { nombre: "accion", tipo: "string", vis: "Public" }
        ],
        [
            { nombre: "registrar", retorno: "void", parametros: [{ nombre: "ev", tipo: "dict" }] }
        ],
        1370, 290, 220, 110
    );

    var eCacheLocal = agregarClaseTablaUML(pkg, diag, "cache_local (IndexedDB / SQLite)", "entity",
        [
            { nombre: "id [PK]", tipo: "int", vis: "Public" },
            { nombre: "payload_json", tipo: "text", vis: "Public" }
        ],
        [
            { nombre: "saveReservaDraft", retorno: "void", parametros: [{ nombre: "d", tipo: "dict" }] }
        ],
        1370, 430, 220, 120
    );

    // Conexiones
    conectarElementos(actor, b1, "Association", "", "");
    conectarElementos(actor, b2, "Association", "", "");
    conectarElementos(actor, b3, "Association", "", "");

    conectarElementos(b1, cRoutes, "Dependency", "consume_online", "«use»");
    conectarElementos(b2, cRoutes, "Dependency", "consume_online", "«use»");
    conectarElementos(b2, cOffline, "Dependency", "guardar_offline", "«use»");
    conectarElementos(cRoutes, b4, "Dependency", "notifica", "«use»");

    conectarElementos(cRoutes, cServices, "Dependency", "delega", "«use»");

    conectarElementos(cServices, eCliente, "Dependency", "consulta", "«use»");
    conectarElementos(cServices, eReserva, "Dependency", "persiste", "«use»");
    conectarElementos(cServices, eDetalle, "Dependency", "persiste_items", "«use»");
    conectarElementos(cServices, eInventario, "Dependency", "bloquea_stock", "«use»");
    conectarElementos(cServices, eBitacora, "Dependency", "audita", "«use»");
    conectarElementos(cOffline, eCacheLocal, "Dependency", "persiste_local", "«use»");

    conectarElementos(eCliente, eReserva, "Association", "solicita", "", "1", "0..*");
    conectarElementos(eReserva, eDetalle, "Association", "compone", "", "1", "1..*");
    conectarElementos(eDetalle, eInventario, "Association", "afecta", "", "1", "0..*");

    diag.Update();
    Repository.ReloadDiagram(diag.DiagramID);
}

// =================================================================================================
// 5. CU15W: Gestionar inventario (Movimientos y Lotes)
// =================================================================================================
function generarCU15W(pkg) {
    Session.Output(" -> Construyendo: cd CU15W - Gestionar inventario");
    var diag = pkg.Diagrams.AddNew("cd CU15W - Gestionar inventario", "Logical");
    configurarDiagramaTablasUML(diag);

    var actor = agregarActor(pkg, diag, "AdminTienda / Encargado", 40, 240, 90, 100);

    var b1 = agregarClaseTablaUML(pkg, diag, "InventarioSucursalesView", "boundary",
        [
            { nombre: "id_sucursal", tipo: "int", vis: "Private" },
            { nombre: "inventario_lista", tipo: "List<InventarioItemDTO>", vis: "Private" },
            { nombre: "cargando", tipo: "boolean", vis: "Private" }
        ],
        [
            { nombre: "ngOnInit", retorno: "void" },
            { nombre: "cargarStockSucursal", retorno: "void", parametros: [{ nombre: "id", tipo: "int" }] },
            { nombre: "abrirModalAjuste", retorno: "void", parametros: [{ nombre: "id_item", tipo: "int" }] },
            { nombre: "abrirModalRecepcionLote", retorno: "void" }
        ],
        180, 40, 240, 160
    );

    var b2 = agregarClaseTablaUML(pkg, diag, "AjusteInventarioModal", "boundary",
        [
            { nombre: "visible", tipo: "boolean", vis: "Private" },
            { nombre: "id_inventario", tipo: "int", vis: "Private" },
            { nombre: "cantidad_ajuste", tipo: "int", vis: "Private" },
            { nombre: "tipo_movimiento", tipo: "string", vis: "Private" },
            { nombre: "motivo", tipo: "string", vis: "Private" }
        ],
        [
            { nombre: "abrir", retorno: "void", parametros: [{ nombre: "id", tipo: "int" }] },
            { nombre: "onSubmit", retorno: "void" },
            { nombre: "cerrar", retorno: "void" }
        ],
        180, 230, 240, 160
    );

    var b3 = agregarClaseTablaUML(pkg, diag, "RecepcionLoteModal", "boundary",
        [
            { nombre: "visible", tipo: "boolean", vis: "Private" },
            { nombre: "numero_orden", tipo: "string", vis: "Private" },
            { nombre: "lote_items", tipo: "List<LoteItemDTO>", vis: "Private" }
        ],
        [
            { nombre: "abrir", retorno: "void" },
            { nombre: "confirmarRecepcion", retorno: "void" }
        ],
        180, 420, 240, 130
    );

    var b4 = agregarClaseTablaUML(pkg, diag, "ErrorDialog", "boundary",
        [
            { nombre: "visible", tipo: "boolean", vis: "Private" },
            { nombre: "mensaje", tipo: "string", vis: "Private" }
        ],
        [
            { nombre: "mostrar", retorno: "void", parametros: [{ nombre: "err", tipo: "string" }] },
            { nombre: "cerrar", retorno: "void" }
        ],
        180, 580, 240, 100
    );

    // Col 3: Route Controllers
    var cRoutes = agregarClaseTablaUML(pkg, diag, "inventario_routes (RouteController)", "control",
        [
            { nombre: "router", tipo: "APIRouter", vis: "Private" },
            { nombre: "prefix", tipo: "string = '/api/inventario'", vis: "Private" }
        ],
        [
            { nombre: "consultar_inventario_sucursal", retorno: "Response", parametros: [{ nombre: "id_sucursal", tipo: "int" }] },
            { nombre: "registrar_ajuste", retorno: "Response", parametros: [{ nombre: "dto", tipo: "AjusteInventarioDTO" }] }
        ],
        470, 150, 280, 160
    );

    var cCompras = agregarClaseTablaUML(pkg, diag, "compras_lotes_routes (RouteController)", "control",
        [
            { nombre: "router", tipo: "APIRouter", vis: "Private" },
            { nombre: "prefix", tipo: "string = '/api/compras'", vis: "Private" }
        ],
        [
            { nombre: "ingresar_lote_compras", retorno: "Response", parametros: [{ nombre: "dto", tipo: "RecepcionLoteDTO" }] }
        ],
        470, 340, 280, 140
    );

    // Col 4: Domain Service
    var cServices = agregarClaseTablaUML(pkg, diag, "inventario_services (DomainService)", "control",
        [
            { nombre: "db", tipo: "PostgreSQL", vis: "Private" },
            { nombre: "audit", tipo: "BitacoraService", vis: "Private" }
        ],
        [
            { nombre: "actualizar_stock_fisico", retorno: "dict", parametros: [{ nombre: "id_var", tipo: "int" }, { nombre: "id_suc", tipo: "int" }, { nombre: "delta", tipo: "int" }] },
            { nombre: "procesar_ingreso_lote", retorno: "dict", parametros: [{ nombre: "dto", tipo: "RecepcionLoteDTO" }] },
            { nombre: "generar_kardex_movimiento", retorno: "void", parametros: [{ nombre: "mov", tipo: "dict" }] }
        ],
        790, 200, 280, 190
    );

    // Col 5 & 6: Entities
    var eInventario = agregarClaseTablaUML(pkg, diag, "t_inventario", "entity",
        [
            { nombre: "id_inventario [PK]", tipo: "int", vis: "Public" },
            { nombre: "id_producto_talla_color [FK]", tipo: "int", vis: "Public" },
            { nombre: "id_sucursal [FK]", tipo: "int", vis: "Public" },
            { nombre: "stock_actual", tipo: "int", vis: "Public" }
        ],
        [
            { nombre: "updateStock", retorno: "void", parametros: [{ nombre: "id", tipo: "int" }, { nombre: "nuevo", tipo: "int" }] },
            { nombre: "findBySucursal", retorno: "List<t_inventario>", parametros: [{ nombre: "id_suc", tipo: "int" }] }
        ],
        1110, 40, 230, 160
    );

    var eMovimiento = agregarClaseTablaUML(pkg, diag, "t_movimiento_inventario", "entity",
        [
            { nombre: "id_movimiento [PK]", tipo: "int", vis: "Public" },
            { nombre: "id_inventario [FK]", tipo: "int", vis: "Public" },
            { nombre: "tipo_movimiento", tipo: "string", vis: "Public" },
            { nombre: "cantidad", tipo: "int", vis: "Public" },
            { nombre: "fecha", tipo: "datetime", vis: "Public" }
        ],
        [
            { nombre: "insert", retorno: "int", parametros: [{ nombre: "m", tipo: "dict" }] }
        ],
        1110, 230, 230, 160
    );

    var eOrden = agregarClaseTablaUML(pkg, diag, "t_orden_compra", "entity",
        [
            { nombre: "id_orden [PK]", tipo: "int", vis: "Public" },
            { nombre: "codigo_orden", tipo: "string", vis: "Public" },
            { nombre: "estado", tipo: "string", vis: "Public" }
        ],
        [
            { nombre: "findByCodigo", retorno: "t_orden_compra", parametros: [{ nombre: "cod", tipo: "string" }] }
        ],
        1110, 420, 230, 130
    );

    var eSucursal = agregarClaseTablaUML(pkg, diag, "t_sucursal", "entity",
        [
            { nombre: "id_sucursal [PK]", tipo: "int", vis: "Public" },
            { nombre: "nombre", tipo: "string", vis: "Public" }
        ],
        [
            { nombre: "findById", retorno: "t_sucursal", parametros: [{ nombre: "id", tipo: "int" }] }
        ],
        1370, 100, 220, 110
    );

    var eVariante = agregarClaseTablaUML(pkg, diag, "t_producto_talla_color", "entity",
        [
            { nombre: "id_producto_talla_color [PK]", tipo: "int", vis: "Public" },
            { nombre: "sku", tipo: "string", vis: "Public" }
        ],
        [
            { nombre: "findById", retorno: "t_producto_talla_color", parametros: [{ nombre: "id", tipo: "int" }] }
        ],
        1370, 240, 220, 110
    );

    var eBitacora = agregarClaseTablaUML(pkg, diag, "t_bitacora", "entity",
        [
            { nombre: "id_bitacora [PK]", tipo: "int", vis: "Public" },
            { nombre: "modulo", tipo: "string", vis: "Public" },
            { nombre: "accion", tipo: "string", vis: "Public" }
        ],
        [
            { nombre: "registrar", retorno: "void", parametros: [{ nombre: "ev", tipo: "dict" }] }
        ],
        1370, 380, 220, 110
    );

    // Conexiones
    conectarElementos(actor, b1, "Association", "", "");
    conectarElementos(actor, b2, "Association", "", "");
    conectarElementos(actor, b3, "Association", "", "");

    conectarElementos(b1, cRoutes, "Dependency", "consume", "«use»");
    conectarElementos(b2, cRoutes, "Dependency", "consume", "«use»");
    conectarElementos(b3, cCompras, "Dependency", "consume", "«use»");
    conectarElementos(cRoutes, b4, "Dependency", "notifica", "«use»");

    conectarElementos(cRoutes, cServices, "Dependency", "delega", "«use»");
    conectarElementos(cCompras, cServices, "Dependency", "delega", "«use»");

    conectarElementos(cServices, eInventario, "Dependency", "actualiza_stock", "«use»");
    conectarElementos(cServices, eMovimiento, "Dependency", "registra_kardex", "«use»");
    conectarElementos(cServices, eOrden, "Dependency", "valida_orden", "«use»");
    conectarElementos(cServices, eBitacora, "Dependency", "audita", "«use»");

    conectarElementos(eSucursal, eInventario, "Association", "almacena_en", "", "1", "0..*");
    conectarElementos(eVariante, eInventario, "Association", "detalla_stock", "", "1", "0..*");
    conectarElementos(eInventario, eMovimiento, "Association", "origina", "", "1", "0..*");
    conectarElementos(eOrden, eMovimiento, "Association", "recepciona", "", "1", "0..*");

    diag.Update();
    Repository.ReloadDiagram(diag.DiagramID);
}

// =================================================================================================
// FUNCIÓN PRINCIPAL DE EJECUCIÓN
// =================================================================================================
function main() {
    Session.Output("======================================================================");
    Session.Output("INICIANDO GENERACIÓN DE DIAGRAMAS DE ANÁLISIS DE CLASES (CU11W - CU15W)");
    Session.Output("Formato: Tablas UML Rectangulares (Boundary -> Controllers -> Entity)");
    Session.Output("======================================================================");

    var pkg = Repository.GetTreeSelectedPackage();
    if (!pkg) {
        Session.Prompt("Por favor, seleccione un Paquete en el Project Browser antes de ejecutar.", 0);
        return;
    }

    Session.Output("Paquete Destino: " + pkg.Name);

    try {
        generarCU11W(pkg);
        generarCU12W(pkg);
        generarCU13W(pkg);
        generarCU14W(pkg);
        generarCU15W(pkg);

        Session.Output("======================================================================");
        Session.Output("PROCESO COMPLETADO EXITOSAMENTE");
        Session.Output("Diagramas creados: 5");
        Session.Output("======================================================================");
        Session.Prompt("Diagramas de clases (CU11W a CU15W) generados como tablas UML con éxito.", 0);
    } catch (e) {
        Session.Output("[ERROR FATAL] " + e.message);
        Session.Prompt("Error al generar diagramas: " + e.message, 0);
    }
}

main();
