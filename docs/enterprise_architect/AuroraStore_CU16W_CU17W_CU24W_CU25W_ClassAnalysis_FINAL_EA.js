/*
 * =================================================================================================
 * SCRIPT MAESTRO DE AUTOMATIZACIÓN DE DIAGRAMAS DE ANÁLISIS DE CLASES UML 2.5 (ICONIX VOPC) PARA SPARX EA
 * =================================================================================================
 * Proyecto: AuroraStore SaaS
 * Lote 4: CU16W, CU17W, CU24W, CU25W
 *   - cd CU16W - Registrar venta presencial (POS / Caja)
 *   - cd CU17W - Registrar venta online (E-commerce / Checkout)
 *   - cd CU24W - Solicitar devolución (Cliente)
 *   - cd CU25W - Gestionar devoluciones (Administración)
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
// 1. CU16W: Registrar venta presencial (POS / Caja)
// =================================================================================================
function generarCU16W(pkg) {
    Session.Output(" -> Construyendo: cd CU16W - Registrar venta presencial");
    var diag = pkg.Diagrams.AddNew("cd CU16W - Registrar venta presencial", "Logical");
    configurarDiagramaTablasUML(diag);

    // Col 1: Actor
    var actor = agregarActor(pkg, diag, "Cajero", 40, 240, 80, 100);

    // Col 2: Boundaries (Vistas y Modales)
    var b1 = agregarClaseTablaUML(pkg, diag, "CajaPosView", "boundary",
        [
            { nombre: "id_sucursal", tipo: "int", vis: "Private" },
            { nombre: "items_ticket", tipo: "List<ItemVentaDTO>", vis: "Private" },
            { nombre: "codigo_barras_input", tipo: "string", vis: "Private" },
            { nombre: "total_venta", tipo: "decimal", vis: "Private" },
            { nombre: "sesion_activa", tipo: "boolean", vis: "Private" }
        ],
        [
            { nombre: "ngOnInit", retorno: "void" },
            { nombre: "escanearCodigo", retorno: "void", parametros: [{ nombre: "sku", tipo: "string" }] },
            { nombre: "modificarCantidad", retorno: "void", parametros: [{ nombre: "idx", tipo: "int" }, { nombre: "cant", tipo: "int" }] },
            { nombre: "abrirModalCobro", retorno: "void" }
        ],
        180, 40, 240, 160
    );

    var b2 = agregarClaseTablaUML(pkg, diag, "CobroModal", "boundary",
        [
            { nombre: "visible", tipo: "boolean", vis: "Private" },
            { nombre: "metodo_pago", tipo: "string", vis: "Private" },
            { nombre: "monto_recibido", tipo: "decimal", vis: "Private" },
            { nombre: "cambio_calculado", tipo: "decimal", vis: "Private" }
        ],
        [
            { nombre: "abrir", retorno: "void", parametros: [{ nombre: "total", tipo: "decimal" }] },
            { nombre: "confirmarPago", retorno: "void" },
            { nombre: "cerrar", retorno: "void" }
        ],
        180, 230, 240, 140
    );

    var b3 = agregarClaseTablaUML(pkg, diag, "ComprobanteVentaModal", "boundary",
        [
            { nombre: "visible", tipo: "boolean", vis: "Private" },
            { nombre: "id_venta", tipo: "int", vis: "Private" },
            { nombre: "ticket_formateado", tipo: "string", vis: "Private" }
        ],
        [
            { nombre: "imprimirTicket", retorno: "void" },
            { nombre: "cerrar", retorno: "void" }
        ],
        180, 400, 240, 120
    );

    var b4 = agregarClaseTablaUML(pkg, diag, "CajaCerradaDialog", "boundary",
        [
            { nombre: "visible", tipo: "boolean", vis: "Private" },
            { nombre: "mensaje", tipo: "string", vis: "Private" }
        ],
        [
            { nombre: "mostrarAlerta", retorno: "void" }
        ],
        180, 550, 240, 90
    );

    var b5 = agregarClaseTablaUML(pkg, diag, "ErrorDialog", "boundary",
        [
            { nombre: "visible", tipo: "boolean", vis: "Private" },
            { nombre: "mensaje", tipo: "string", vis: "Private" }
        ],
        [
            { nombre: "mostrar", retorno: "void", parametros: [{ nombre: "err", tipo: "string" }] },
            { nombre: "cerrar", retorno: "void" }
        ],
        180, 670, 240, 100
    );

    // Col 3: Main Route Controller
    var cRoutes = agregarClaseTablaUML(pkg, diag, "pos_routes (RouteController)", "control",
        [
            { nombre: "router", tipo: "APIRouter", vis: "Private" },
            { nombre: "prefix", tipo: "string = '/api/pos'", vis: "Private" }
        ],
        [
            { nombre: "registrar_venta_pos", retorno: "Response", parametros: [{ nombre: "dto", tipo: "VentaPosDTO" }] },
            { nombre: "verificar_estado_caja", retorno: "Response", parametros: [{ nombre: "id_usuario", tipo: "int" }] }
        ],
        470, 200, 280, 170
    );

    // Col 4: Domain Services
    var cPosSrv = agregarClaseTablaUML(pkg, diag, "pos_services (DomainService)", "control",
        [
            { nombre: "db", tipo: "PostgreSQL", vis: "Private" },
            { nombre: "audit", tipo: "BitacoraService", vis: "Private" }
        ],
        [
            { nombre: "procesar_venta_caja", retorno: "dict", parametros: [{ nombre: "dto", tipo: "VentaPosDTO" }, { nombre: "id_cajero", tipo: "int" }] },
            { nombre: "descontar_stock_venta", retorno: "void", parametros: [{ nombre: "items", tipo: "List<dict>" }, { nombre: "id_suc", tipo: "int" }] },
            { nombre: "generar_comprobante", retorno: "ComprobanteDTO", parametros: [{ nombre: "id_venta", tipo: "int" }] }
        ],
        790, 110, 280, 170
    );

    var cCajaSrv = agregarClaseTablaUML(pkg, diag, "caja_services (DomainService)", "control",
        [
            { nombre: "db", tipo: "PostgreSQL", vis: "Private" }
        ],
        [
            { nombre: "obtener_sesion_vigente", retorno: "SesionCajaDTO", parametros: [{ nombre: "id_usuario", tipo: "int" }] },
            { nombre: "acumular_saldo_caja", retorno: "void", parametros: [{ nombre: "id_sesion", tipo: "int" }, { nombre: "monto", tipo: "decimal" }] }
        ],
        790, 310, 280, 150
    );

    // Col 5 & 6: Entities
    var eCajaSes = agregarClaseTablaUML(pkg, diag, "t_caja_sesion", "entity",
        [
            { nombre: "id_sesion [PK]", tipo: "int", vis: "Public" },
            { nombre: "id_usuario [FK]", tipo: "int", vis: "Public" },
            { nombre: "id_sucursal [FK]", tipo: "int", vis: "Public" },
            { nombre: "monto_apertura", tipo: "decimal", vis: "Public" },
            { nombre: "estado", tipo: "string", vis: "Public" }
        ],
        [
            { nombre: "findAbiertaByUsuario", retorno: "t_caja_sesion", parametros: [{ nombre: "id", tipo: "int" }] }
        ],
        1110, 40, 230, 150
    );

    var eVenta = agregarClaseTablaUML(pkg, diag, "t_venta", "entity",
        [
            { nombre: "id_venta [PK]", tipo: "int", vis: "Public" },
            { nombre: "id_sucursal [FK]", tipo: "int", vis: "Public" },
            { nombre: "id_cajero [FK]", tipo: "int", vis: "Public" },
            { nombre: "total", tipo: "decimal", vis: "Public" },
            { nombre: "tipo_venta", tipo: "string", vis: "Public" }
        ],
        [
            { nombre: "insert", retorno: "int", parametros: [{ nombre: "v", tipo: "dict" }] }
        ],
        1110, 220, 230, 150
    );

    var eDetalle = agregarClaseTablaUML(pkg, diag, "t_detalle_venta", "entity",
        [
            { nombre: "id_detalle [PK]", tipo: "int", vis: "Public" },
            { nombre: "id_venta [FK]", tipo: "int", vis: "Public" },
            { nombre: "id_producto_talla_color [FK]", tipo: "int", vis: "Public" },
            { nombre: "cantidad", tipo: "int", vis: "Public" },
            { nombre: "subtotal", tipo: "decimal", vis: "Public" }
        ],
        [
            { nombre: "bulkInsert", retorno: "void", parametros: [{ nombre: "items", tipo: "List<dict>" }] }
        ],
        1110, 400, 230, 150
    );

    var ePago = agregarClaseTablaUML(pkg, diag, "t_pago", "entity",
        [
            { nombre: "id_pago [PK]", tipo: "int", vis: "Public" },
            { nombre: "id_venta [FK]", tipo: "int", vis: "Public" },
            { nombre: "metodo_pago", tipo: "string", vis: "Public" },
            { nombre: "monto", tipo: "decimal", vis: "Public" }
        ],
        [
            { nombre: "insert", retorno: "int", parametros: [{ nombre: "p", tipo: "dict" }] }
        ],
        1370, 80, 220, 140
    );

    var eInventario = agregarClaseTablaUML(pkg, diag, "t_inventario", "entity",
        [
            { nombre: "id_inventario [PK]", tipo: "int", vis: "Public" },
            { nombre: "id_producto_talla_color [FK]", tipo: "int", vis: "Public" },
            { nombre: "id_sucursal [FK]", tipo: "int", vis: "Public" },
            { nombre: "stock_actual", tipo: "int", vis: "Public" }
        ],
        [
            { nombre: "descontarStock", retorno: "void", parametros: [{ nombre: "id_var", tipo: "int" }, { nombre: "id_suc", tipo: "int" }, { nombre: "cant", tipo: "int" }] }
        ],
        1370, 250, 220, 140
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
        1370, 420, 220, 110
    );

    // Conexiones
    conectarElementos(actor, b1, "Association", "", "");
    conectarElementos(b1, b2, "Dependency", "abre", "«use»");
    conectarElementos(b1, b3, "Dependency", "despliega", "«use»");

    conectarElementos(b1, cRoutes, "Dependency", "consume", "«use»");
    conectarElementos(b2, cRoutes, "Dependency", "consume", "«use»");
    conectarElementos(cRoutes, b4, "Dependency", "notifica_caja_cerrada", "«use»");
    conectarElementos(cRoutes, b5, "Dependency", "notifica_error", "«use»");

    conectarElementos(cRoutes, cPosSrv, "Dependency", "delega", "«use»");
    conectarElementos(cRoutes, cCajaSrv, "Dependency", "valida_caja", "«use»");

    conectarElementos(cCajaSrv, eCajaSes, "Dependency", "consulta_y_acumula", "«use»");
    conectarElementos(cPosSrv, eVenta, "Dependency", "persiste", "«use»");
    conectarElementos(cPosSrv, eDetalle, "Dependency", "persiste_items", "«use»");
    conectarElementos(cPosSrv, ePago, "Dependency", "registra_pago", "«use»");
    conectarElementos(cPosSrv, eInventario, "Dependency", "descuenta_stock", "«use»");
    conectarElementos(cPosSrv, eBitacora, "Dependency", "audita", "«use»");

    conectarElementos(eVenta, eDetalle, "Association", "compone", "", "1", "1..*");
    conectarElementos(eVenta, ePago, "Association", "liquida", "", "1", "1..*");
    conectarElementos(eCajaSes, eVenta, "Association", "registra", "", "1", "0..*");

    diag.Update();
    Repository.ReloadDiagram(diag.DiagramID);
}

// =================================================================================================
// 2. CU17W / CU06M: Registrar venta online (E-commerce / Checkout)
// =================================================================================================
function generarCU17W(pkg) {
    Session.Output(" -> Construyendo: cd CU17W - Registrar venta online");
    var diag = pkg.Diagrams.AddNew("cd CU17W - Registrar venta online", "Logical");
    configurarDiagramaTablasUML(diag);

    var actor = agregarActor(pkg, diag, "Cliente / Usuario", 40, 240, 90, 100);

    var b1 = agregarClaseTablaUML(pkg, diag, "CheckoutView", "boundary",
        [
            { nombre: "id_carrito", tipo: "int", vis: "Private" },
            { nombre: "tipo_entrega", tipo: "string", vis: "Private" },
            { nombre: "id_sucursal_retiro", tipo: "int", vis: "Private" },
            { nombre: "total_pedido", tipo: "decimal", vis: "Private" }
        ],
        [
            { nombre: "ngOnInit", retorno: "void" },
            { nombre: "seleccionarSucursalRetiro", retorno: "void", parametros: [{ nombre: "id", tipo: "int" }] },
            { nombre: "abrirModalPasarela", retorno: "void" }
        ],
        180, 40, 240, 150
    );

    var b2 = agregarClaseTablaUML(pkg, diag, "PasarelaPagoModal", "boundary",
        [
            { nombre: "visible", tipo: "boolean", vis: "Private" },
            { nombre: "metodo_seleccionado", tipo: "string", vis: "Private" },
            { nombre: "datos_tarjeta", tipo: "TarjetaDTO", vis: "Private" },
            { nombre: "procesando", tipo: "boolean", vis: "Private" }
        ],
        [
            { nombre: "abrir", retorno: "void" },
            { nombre: "procesarPago", retorno: "void" },
            { nombre: "cerrar", retorno: "void" }
        ],
        180, 220, 240, 150
    );

    var b3 = agregarClaseTablaUML(pkg, diag, "ConfirmacionOrdenModal", "boundary",
        [
            { nombre: "visible", tipo: "boolean", vis: "Private" },
            { nombre: "codigo_pedido", tipo: "string", vis: "Private" },
            { nombre: "comprobante_url", tipo: "string", vis: "Private" }
        ],
        [
            { nombre: "descargarComprobante", retorno: "void" },
            { nombre: "finalizar", retorno: "void" }
        ],
        180, 400, 240, 130
    );

    var b4 = agregarClaseTablaUML(pkg, diag, "ErrorPagoDialog", "boundary",
        [
            { nombre: "visible", tipo: "boolean", vis: "Private" },
            { nombre: "motivo_rechazo", tipo: "string", vis: "Private" }
        ],
        [
            { nombre: "mostrar", retorno: "void", parametros: [{ nombre: "err", tipo: "string" }] },
            { nombre: "reintentar", retorno: "void" }
        ],
        180, 560, 240, 110
    );

    // Col 3: Route Controller
    var cRoutes = agregarClaseTablaUML(pkg, diag, "pago_routes (RouteController)", "control",
        [
            { nombre: "router", tipo: "APIRouter", vis: "Private" },
            { nombre: "prefix", tipo: "string = '/api/pagos'", vis: "Private" }
        ],
        [
            { nombre: "iniciar_checkout", retorno: "Response", parametros: [{ nombre: "dto", tipo: "CheckoutRequestDTO" }] },
            { nombre: "procesar_transaccion_online", retorno: "Response", parametros: [{ nombre: "dto", tipo: "PagoOnlineDTO" }] }
        ],
        470, 200, 280, 160
    );

    // Col 4: Domain Service & Offline Storage
    var cServices = agregarClaseTablaUML(pkg, diag, "pago_services (DomainService)", "control",
        [
            { nombre: "db", tipo: "PostgreSQL", vis: "Private" },
            { nombre: "audit", tipo: "BitacoraService", vis: "Private" }
        ],
        [
            { nombre: "procesar_pedido_ecommerce", retorno: "dict", parametros: [{ nombre: "dto", tipo: "CheckoutRequestDTO" }, { nombre: "id_cli", tipo: "int" }] },
            { nombre: "validar_stock_y_bloquear", retorno: "boolean", parametros: [{ nombre: "items", tipo: "List<dict>" }, { nombre: "id_suc", tipo: "int" }] },
            { nombre: "confirmar_pago_exitoso", retorno: "void", parametros: [{ nombre: "id_pago", tipo: "int" }] }
        ],
        790, 110, 280, 170
    );

    var cOffline = agregarClaseTablaUML(pkg, diag, "offline_cache_manager (ClientStorage)", "control",
        [
            { nombre: "db_local", tipo: "IndexedDB / SQLite", vis: "Private" }
        ],
        [
            { nombre: "guardarOrdenDraft", retorno: "void", parametros: [{ nombre: "draft", tipo: "dict" }] },
            { nombre: "limpiarCarritoLocal", retorno: "void" }
        ],
        790, 310, 280, 130
    );

    // Col 5 & 6: Entities
    var eCarrito = agregarClaseTablaUML(pkg, diag, "t_carrito", "entity",
        [
            { nombre: "id_carrito [PK]", tipo: "int", vis: "Public" },
            { nombre: "id_cliente [FK]", tipo: "int", vis: "Public" },
            { nombre: "id_empresa", tipo: "int", vis: "Public" }
        ],
        [
            { nombre: "findItemsByCliente", retorno: "List<dict>", parametros: [{ nombre: "id_cli", tipo: "int" }] },
            { nombre: "clearByCliente", retorno: "void", parametros: [{ nombre: "id_cli", tipo: "int" }] }
        ],
        1110, 40, 230, 140
    );

    var eVenta = agregarClaseTablaUML(pkg, diag, "t_venta", "entity",
        [
            { nombre: "id_venta [PK]", tipo: "int", vis: "Public" },
            { nombre: "id_cliente [FK]", tipo: "int", vis: "Public" },
            { nombre: "id_sucursal [FK]", tipo: "int", vis: "Public" },
            { nombre: "total", tipo: "decimal", vis: "Public" },
            { nombre: "tipo_venta", tipo: "string", vis: "Public" }
        ],
        [
            { nombre: "insert", retorno: "int", parametros: [{ nombre: "v", tipo: "dict" }] }
        ],
        1110, 210, 230, 150
    );

    var eDetalle = agregarClaseTablaUML(pkg, diag, "t_detalle_venta", "entity",
        [
            { nombre: "id_detalle [PK]", tipo: "int", vis: "Public" },
            { nombre: "id_venta [FK]", tipo: "int", vis: "Public" },
            { nombre: "id_producto_talla_color [FK]", tipo: "int", vis: "Public" },
            { nombre: "cantidad", tipo: "int", vis: "Public" }
        ],
        [
            { nombre: "bulkInsert", retorno: "void", parametros: [{ nombre: "items", tipo: "List<dict>" }] }
        ],
        1110, 390, 230, 140
    );

    var ePago = agregarClaseTablaUML(pkg, diag, "t_pago", "entity",
        [
            { nombre: "id_pago [PK]", tipo: "int", vis: "Public" },
            { nombre: "id_venta [FK]", tipo: "int", vis: "Public" },
            { nombre: "referencia_transaccion", tipo: "string", vis: "Public" },
            { nombre: "estado", tipo: "string", vis: "Public" }
        ],
        [
            { nombre: "insert", retorno: "int", parametros: [{ nombre: "p", tipo: "dict" }] },
            { nombre: "updateEstado", retorno: "void", parametros: [{ nombre: "id", tipo: "int" }, { nombre: "est", tipo: "string" }] }
        ],
        1370, 80, 220, 150
    );

    var eInventario = agregarClaseTablaUML(pkg, diag, "t_inventario", "entity",
        [
            { nombre: "id_inventario [PK]", tipo: "int", vis: "Public" },
            { nombre: "stock_actual", tipo: "int", vis: "Public" }
        ],
        [
            { nombre: "descontarStock", retorno: "void", parametros: [{ nombre: "id_var", tipo: "int" }, { nombre: "id_suc", tipo: "int" }, { nombre: "cant", tipo: "int" }] }
        ],
        1370, 260, 220, 120
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
        1370, 410, 220, 110
    );

    // Conexiones
    conectarElementos(actor, b1, "Association", "", "");
    conectarElementos(b1, b2, "Dependency", "abre", "«use»");
    conectarElementos(b2, b3, "Dependency", "muestra_confirmacion", "«use»");

    conectarElementos(b1, cRoutes, "Dependency", "inicia", "«use»");
    conectarElementos(b2, cRoutes, "Dependency", "procesa", "«use»");
    conectarElementos(b2, cOffline, "Dependency", "guarda_draft", "«use»");
    conectarElementos(cRoutes, b4, "Dependency", "notifica_error", "«use»");

    conectarElementos(cRoutes, cServices, "Dependency", "delega", "«use»");

    conectarElementos(cServices, eCarrito, "Dependency", "lee_y_vacia", "«use»");
    conectarElementos(cServices, eVenta, "Dependency", "persiste", "«use»");
    conectarElementos(cServices, eDetalle, "Dependency", "persiste_items", "«use»");
    conectarElementos(cServices, ePago, "Dependency", "registra_transaccion", "«use»");
    conectarElementos(cServices, eInventario, "Dependency", "descuenta_stock", "«use»");
    conectarElementos(cServices, eBitacora, "Dependency", "audita", "«use»");

    conectarElementos(eVenta, eDetalle, "Association", "compone", "", "1", "1..*");
    conectarElementos(eVenta, ePago, "Association", "liquida", "", "1", "1..*");

    diag.Update();
    Repository.ReloadDiagram(diag.DiagramID);
}

// =================================================================================================
// 3. CU24W / CU12M: Solicitar devolución (Cliente bajo Ley 453)
// =================================================================================================
function generarCU24W(pkg) {
    Session.Output(" -> Construyendo: cd CU24W - Solicitar devolución");
    var diag = pkg.Diagrams.AddNew("cd CU24W - Solicitar devolución", "Logical");
    configurarDiagramaTablasUML(diag);

    var actor = agregarActor(pkg, diag, "Cliente / Usuario", 40, 240, 90, 100);

    var b1 = agregarClaseTablaUML(pkg, diag, "MisDevolucionesView", "boundary",
        [
            { nombre: "id_cliente", tipo: "int", vis: "Private" },
            { nombre: "solicitudes_lista", tipo: "List<DevolucionDTO>", vis: "Private" },
            { nombre: "cargando", tipo: "boolean", vis: "Private" }
        ],
        [
            { nombre: "ngOnInit", retorno: "void" },
            { nombre: "cargarDevoluciones", retorno: "void" },
            { nombre: "abrirModalNuevaSolicitud", retorno: "void" }
        ],
        180, 40, 240, 150
    );

    var b2 = agregarClaseTablaUML(pkg, diag, "SolicitudDevolucionModal", "boundary",
        [
            { nombre: "visible", tipo: "boolean", vis: "Private" },
            { nombre: "id_venta_sel", tipo: "int", vis: "Private" },
            { nombre: "motivo_devolucion", tipo: "string", vis: "Private" },
            { nombre: "items_devolver", tipo: "List<int>", vis: "Private" }
        ],
        [
            { nombre: "abrir", retorno: "void" },
            { nombre: "onSubmit", retorno: "void" },
            { nombre: "cerrar", retorno: "void" }
        ],
        180, 220, 240, 150
    );

    var b3 = agregarClaseTablaUML(pkg, diag, "VentanaVencidaDialog", "boundary",
        [
            { nombre: "visible", tipo: "boolean", vis: "Private" },
            { nombre: "mensaje_ley453", tipo: "string", vis: "Private" }
        ],
        [
            { nombre: "mostrarAvisoPlazoVencido", retorno: "void" },
            { nombre: "cerrar", retorno: "void" }
        ],
        180, 400, 240, 120
    );

    var b4 = agregarClaseTablaUML(pkg, diag, "ErrorDialog", "boundary",
        [
            { nombre: "visible", tipo: "boolean", vis: "Private" },
            { nombre: "mensaje", tipo: "string", vis: "Private" }
        ],
        [
            { nombre: "mostrar", retorno: "void", parametros: [{ nombre: "err", tipo: "string" }] }
        ],
        180, 550, 240, 100
    );

    // Col 3: Route Controller
    var cRoutes = agregarClaseTablaUML(pkg, diag, "devoluciones_routes (RouteController)", "control",
        [
            { nombre: "router", tipo: "APIRouter", vis: "Private" },
            { nombre: "prefix", tipo: "string = '/api/devoluciones'", vis: "Private" }
        ],
        [
            { nombre: "obtener_mis_devoluciones", retorno: "Response", parametros: [{ nombre: "id_cliente", tipo: "int" }] },
            { nombre: "crear_solicitud_devolucion", retorno: "Response", parametros: [{ nombre: "dto", tipo: "SolicitudDevolucionDTO" }] }
        ],
        470, 200, 280, 160
    );

    // Col 4: Domain Service
    var cServices = agregarClaseTablaUML(pkg, diag, "devoluciones_services (DomainService)", "control",
        [
            { nombre: "db", tipo: "PostgreSQL", vis: "Private" },
            { nombre: "audit", tipo: "BitacoraService", vis: "Private" }
        ],
        [
            { nombre: "registrar_solicitud_cliente", retorno: "dict", parametros: [{ nombre: "dto", tipo: "SolicitudDevolucionDTO" }, { nombre: "id_cli", tipo: "int" }] },
            { nombre: "validar_elegibilidad_ley453", retorno: "boolean", parametros: [{ nombre: "id_venta", tipo: "int" }] },
            { nombre: "generar_cupon_saldo_favor", retorno: "dict", parametros: [{ nombre: "id_devolucion", tipo: "int" }] }
        ],
        790, 200, 280, 180
    );

    // Col 5 & 6: Entities
    var eCliente = agregarClaseTablaUML(pkg, diag, "t_cliente", "entity",
        [
            { nombre: "id_cliente [PK]", tipo: "int", vis: "Public" },
            { nombre: "nombre", tipo: "string", vis: "Public" },
            { nombre: "email", tipo: "string", vis: "Public" }
        ],
        [
            { nombre: "findById", retorno: "t_cliente", parametros: [{ nombre: "id", tipo: "int" }] }
        ],
        1110, 40, 230, 130
    );

    var eVenta = agregarClaseTablaUML(pkg, diag, "t_venta", "entity",
        [
            { nombre: "id_venta [PK]", tipo: "int", vis: "Public" },
            { nombre: "id_cliente [FK]", tipo: "int", vis: "Public" },
            { nombre: "fecha_venta", tipo: "datetime", vis: "Public" },
            { nombre: "total", tipo: "decimal", vis: "Public" }
        ],
        [
            { nombre: "findById", retorno: "t_venta", parametros: [{ nombre: "id", tipo: "int" }] }
        ],
        1110, 200, 230, 150
    );

    var eDetalle = agregarClaseTablaUML(pkg, diag, "t_detalle_venta", "entity",
        [
            { nombre: "id_detalle [PK]", tipo: "int", vis: "Public" },
            { nombre: "id_venta [FK]", tipo: "int", vis: "Public" },
            { nombre: "id_producto_talla_color [FK]", tipo: "int", vis: "Public" },
            { nombre: "cantidad", tipo: "int", vis: "Public" }
        ],
        [
            { nombre: "findByVenta", retorno: "List<t_detalle_venta>", parametros: [{ nombre: "id_venta", tipo: "int" }] }
        ],
        1110, 380, 230, 140
    );

    var eDevolucion = agregarClaseTablaUML(pkg, diag, "t_devolucion", "entity",
        [
            { nombre: "id_devolucion [PK]", tipo: "int", vis: "Public" },
            { nombre: "id_venta [FK]", tipo: "int", vis: "Public" },
            { nombre: "id_cliente [FK]", tipo: "int", vis: "Public" },
            { nombre: "motivo", tipo: "string", vis: "Public" },
            { nombre: "estado", tipo: "string", vis: "Public" },
            { nombre: "creado_en", tipo: "datetime", vis: "Public" }
        ],
        [
            { nombre: "insert", retorno: "int", parametros: [{ nombre: "d", tipo: "dict" }] },
            { nombre: "findByCliente", retorno: "List<t_devolucion>", parametros: [{ nombre: "id_cli", tipo: "int" }] }
        ],
        1370, 140, 220, 170
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
        1370, 340, 220, 110
    );

    // Conexiones
    conectarElementos(actor, b1, "Association", "", "");
    conectarElementos(b1, b2, "Dependency", "abre", "«use»");

    conectarElementos(b1, cRoutes, "Dependency", "consume", "«use»");
    conectarElementos(b2, cRoutes, "Dependency", "consume", "«use»");
    conectarElementos(cRoutes, b3, "Dependency", "notifica_vencimiento", "«use»");
    conectarElementos(cRoutes, b4, "Dependency", "notifica_error", "«use»");

    conectarElementos(cRoutes, cServices, "Dependency", "delega", "«use»");

    conectarElementos(cServices, eCliente, "Dependency", "consulta", "«use»");
    conectarElementos(cServices, eVenta, "Dependency", "valida_compra", "«use»");
    conectarElementos(cServices, eDetalle, "Dependency", "consulta_items", "«use»");
    conectarElementos(cServices, eDevolucion, "Dependency", "persiste", "«use»");
    conectarElementos(cServices, eBitacora, "Dependency", "audita", "«use»");

    conectarElementos(eVenta, eDevolucion, "Association", "origina", "", "1", "0..*");
    conectarElementos(eCliente, eDevolucion, "Association", "solicita", "", "1", "0..*");

    diag.Update();
    Repository.ReloadDiagram(diag.DiagramID);
}

// =================================================================================================
// 4. CU25W: Gestionar devoluciones (Bandeja Administrativa)
// =================================================================================================
function generarCU25W(pkg) {
    Session.Output(" -> Construyendo: cd CU25W - Gestionar devoluciones");
    var diag = pkg.Diagrams.AddNew("cd CU25W - Gestionar devoluciones", "Logical");
    configurarDiagramaTablasUML(diag);

    var actor = agregarActor(pkg, diag, "AdminTienda", 40, 240, 80, 100);

    var b1 = agregarClaseTablaUML(pkg, diag, "BandejaDevolucionesView", "boundary",
        [
            { nombre: "id_empresa", tipo: "int", vis: "Private" },
            { nombre: "solicitudes_pendientes", tipo: "List<DevolucionItemDTO>", vis: "Private" },
            { nombre: "filtro_estado", tipo: "string", vis: "Private" },
            { nombre: "cargando", tipo: "boolean", vis: "Private" }
        ],
        [
            { nombre: "ngOnInit", retorno: "void" },
            { nombre: "cargarSolicitudes", retorno: "void" },
            { nombre: "abrirModalRevision", retorno: "void", parametros: [{ nombre: "id_dev", tipo: "int" }] }
        ],
        180, 40, 240, 160
    );

    var b2 = agregarClaseTablaUML(pkg, diag, "RevisionDevolucionModal", "boundary",
        [
            { nombre: "visible", tipo: "boolean", vis: "Private" },
            { nombre: "id_devolucion", tipo: "int", vis: "Private" },
            { nombre: "dictamen_aprobado", tipo: "boolean", vis: "Private" },
            { nombre: "reingresar_a_stock", tipo: "boolean", vis: "Private" },
            { nombre: "observaciones", tipo: "string", vis: "Private" }
        ],
        [
            { nombre: "abrir", retorno: "void", parametros: [{ nombre: "id", tipo: "int" }] },
            { nombre: "confirmarDictamen", retorno: "void" },
            { nombre: "cerrar", retorno: "void" }
        ],
        180, 230, 240, 170
    );

    var b3 = agregarClaseTablaUML(pkg, diag, "ComprobanteCreditoModal", "boundary",
        [
            { nombre: "visible", tipo: "boolean", vis: "Private" },
            { nombre: "codigo_credito", tipo: "string", vis: "Private" },
            { nombre: "saldo_acreditado", tipo: "decimal", vis: "Private" }
        ],
        [
            { nombre: "imprimirNotaCredito", retorno: "void" },
            { nombre: "cerrar", retorno: "void" }
        ],
        180, 430, 240, 130
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
        180, 590, 240, 100
    );

    // Col 3: Route Controller
    var cRoutes = agregarClaseTablaUML(pkg, diag, "devoluciones_routes (RouteController)", "control",
        [
            { nombre: "router", tipo: "APIRouter", vis: "Private" },
            { nombre: "prefix", tipo: "string = '/api/admin/devoluciones'", vis: "Private" }
        ],
        [
            { nombre: "listar_devoluciones_pendientes", retorno: "Response", parametros: [{ nombre: "id_empresa", tipo: "int" }] },
            { nombre: "emitir_dictamen", retorno: "Response", parametros: [{ nombre: "id_dev", tipo: "int" }, { nombre: "dto", tipo: "DictamenDTO" }] }
        ],
        470, 200, 280, 160
    );

    // Col 4: Domain Service
    var cServices = agregarClaseTablaUML(pkg, diag, "devoluciones_services (DomainService)", "control",
        [
            { nombre: "db", tipo: "PostgreSQL", vis: "Private" },
            { nombre: "audit", tipo: "BitacoraService", vis: "Private" }
        ],
        [
            { nombre: "procesar_dictamen_administrativo", retorno: "dict", parametros: [{ nombre: "id_dev", tipo: "int" }, { nombre: "aprobado", tipo: "boolean" }, { nombre: "reingreso", tipo: "boolean" }] },
            { nombre: "reingresar_stock_inventario", retorno: "void", parametros: [{ nombre: "id_var", tipo: "int" }, { nombre: "id_suc", tipo: "int" }, { nombre: "cant", tipo: "int" }] },
            { nombre: "registrar_kardex_reingreso", retorno: "void", parametros: [{ nombre: "mov", tipo: "dict" }] }
        ],
        790, 200, 280, 180
    );

    // Col 5 & 6: Entities
    var eDevolucion = agregarClaseTablaUML(pkg, diag, "t_devolucion", "entity",
        [
            { nombre: "id_devolucion [PK]", tipo: "int", vis: "Public" },
            { nombre: "id_venta [FK]", tipo: "int", vis: "Public" },
            { nombre: "estado", tipo: "string", vis: "Public" },
            { nombre: "dictamen_motivo", tipo: "string", vis: "Public" },
            { nombre: "procesado_en", tipo: "datetime", vis: "Public" }
        ],
        [
            { nombre: "updateDictamen", retorno: "void", parametros: [{ nombre: "id", tipo: "int" }, { nombre: "est", tipo: "string" }, { nombre: "mot", tipo: "string" }] },
            { nombre: "findPendientesByEmpresa", retorno: "List<t_devolucion>", parametros: [{ nombre: "id_empresa", tipo: "int" }] }
        ],
        1110, 40, 230, 170
    );

    var eInventario = agregarClaseTablaUML(pkg, diag, "t_inventario", "entity",
        [
            { nombre: "id_inventario [PK]", tipo: "int", vis: "Public" },
            { nombre: "id_producto_talla_color [FK]", tipo: "int", vis: "Public" },
            { nombre: "id_sucursal [FK]", tipo: "int", vis: "Public" },
            { nombre: "stock_actual", tipo: "int", vis: "Public" }
        ],
        [
            { nombre: "reingresarStock", retorno: "void", parametros: [{ nombre: "id_var", tipo: "int" }, { nombre: "id_suc", tipo: "int" }, { nombre: "cant", tipo: "int" }] }
        ],
        1110, 240, 230, 150
    );

    var eMovimiento = agregarClaseTablaUML(pkg, diag, "t_movimiento_inventario", "entity",
        [
            { nombre: "id_movimiento [PK]", tipo: "int", vis: "Public" },
            { nombre: "id_inventario [FK]", tipo: "int", vis: "Public" },
            { nombre: "tipo_movimiento", tipo: "string", vis: "Public" },
            { nombre: "cantidad", tipo: "int", vis: "Public" }
        ],
        [
            { nombre: "insert", retorno: "int", parametros: [{ nombre: "m", tipo: "dict" }] }
        ],
        1110, 420, 230, 140
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
        1370, 200, 220, 110
    );

    // Conexiones
    conectarElementos(actor, b1, "Association", "", "");
    conectarElementos(b1, b2, "Dependency", "abre", "«use»");
    conectarElementos(b2, b3, "Dependency", "emite_credito", "«use»");

    conectarElementos(b1, cRoutes, "Dependency", "consume", "«use»");
    conectarElementos(b2, cRoutes, "Dependency", "consume", "«use»");
    conectarElementos(cRoutes, b4, "Dependency", "notifica", "«use»");

    conectarElementos(cRoutes, cServices, "Dependency", "delega", "«use»");

    conectarElementos(cServices, eDevolucion, "Dependency", "actualiza_dictamen", "«use»");
    conectarElementos(cServices, eInventario, "Dependency", "reingresa_stock", "«use»");
    conectarElementos(cServices, eMovimiento, "Dependency", "registra_kardex", "«use»");
    conectarElementos(cServices, eBitacora, "Dependency", "audita", "«use»");

    conectarElementos(eDevolucion, eInventario, "Association", "restituye", "", "1", "0..*");
    conectarElementos(eInventario, eMovimiento, "Association", "origina", "", "1", "0..*");

    diag.Update();
    Repository.ReloadDiagram(diag.DiagramID);
}

// =================================================================================================
// FUNCIÓN PRINCIPAL DE EJECUCIÓN
// =================================================================================================
function main() {
    Session.Output("======================================================================");
    Session.Output("INICIANDO GENERACIÓN DE DIAGRAMAS DE ANÁLISIS DE CLASES (CU16W, CU17W, CU24W, CU25W)");
    Session.Output("Formato: Tablas UML Rectangulares (Boundary -> Controllers -> Entity)");
    Session.Output("======================================================================");

    var pkg = Repository.GetTreeSelectedPackage();
    if (!pkg) {
        Session.Prompt("Por favor, seleccione un Paquete en el Project Browser antes de ejecutar.", 0);
        return;
    }

    Session.Output("Paquete Destino: " + pkg.Name);

    try {
        generarCU16W(pkg);
        generarCU17W(pkg);
        generarCU24W(pkg);
        generarCU25W(pkg);

        Session.Output("======================================================================");
        Session.Output("PROCESO COMPLETADO EXITOSAMENTE");
        Session.Output("Diagramas creados: 4");
        Session.Output("======================================================================");
        Session.Prompt("Diagramas de clases (CU16W, CU17W, CU24W, CU25W) generados como tablas UML con éxito.", 0);
    } catch (e) {
        Session.Output("[ERROR FATAL] " + e.message);
        Session.Prompt("Error al generar diagramas: " + e.message, 0);
    }
}

main();
