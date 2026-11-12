/*
 * =================================================================================================
 * SCRIPT MAESTRO DE AUTOMATIZACIÓN DE DIAGRAMAS DE ANÁLISIS DE CLASES UML 2.5 (ICONIX VOPC) PARA SPARX EA
 * =================================================================================================
 * Proyecto: AuroraStore SaaS
 * Lote 5: CU18W a CU22W
 *   - cd CU18W - Sincronizar operaciones pendientes
 *   - cd CU19W - Resolver conflictos de sincronización
 *   - cd CU20W - Consultar ventas, reservas e inventario
 *   - cd CU21W - Visualizar indicadores empresariales
 *   - cd CU22W - Generar reportes bajo demanda
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
// 1. CU18W: Sincronizar operaciones pendientes (Sincronización Offline & Lotes)
// =================================================================================================
function generarClasesCU18W(pkg) {
    Session.Output(" -> Construyendo: cd CU18W - Sincronizar operaciones pendientes");
    var diag = pkg.Diagrams.AddNew("cd CU18W - Sincronizar operaciones pendientes", "Logical");
    diag.Update();
    configurarDiagramaTablasUML(diag);

    // --- Columna 1: Actor ---
    var act = agregarActor(pkg, diag, "Administrador / Cajero", 40, 240, 90, 110);

    // --- Columna 2: Boundary (Vistas, Modales y Componentes Angular) ---
    var b1 = agregarClaseTablaUML(pkg, diag, "CentroSyncView", "boundary",
        [
            { nombre: "queueStatus", tipo: "string" },
            { nombre: "pendingBatchCount", tipo: "number" },
            { nombre: "networkStatus", tipo: "boolean" },
            { nombre: "isSyncing", tipo: "boolean" },
            { nombre: "lastSyncDate", tipo: "Date" }
        ],
        [
            { nombre: "iniciarSincronizacion", retorno: "void", parametros: [] },
            { nombre: "reintentarLoteFallido", retorno: "void", parametros: [{ nombre: "batchId", tipo: "UUID" }] },
            { nombre: "mostrarAlertaConflictos", retorno: "void", parametros: [{ nombre: "conflictos", tipo: "SyncConflict[]" }] },
            { nombre: "mostrarExitoSincronizacion", retorno: "void", parametros: [{ nombre: "recibo", tipo: "SyncReceipt" }] }
        ],
        180, 50, 240, 150
    );

    var b2 = agregarClaseTablaUML(pkg, diag, "ColaOfflineModal", "boundary",
        [
            { nombre: "operacionesLocales", tipo: "LocalOperation[]" },
            { nombre: "selectedFilter", tipo: "string" },
            { nombre: "isPurging", tipo: "boolean" }
        ],
        [
            { nombre: "inspeccionarPayload", retorno: "void", parametros: [{ nombre: "opId", tipo: "UUID" }] },
            { nombre: "purgarOperacionesConfirmadas", retorno: "void", parametros: [] },
            { nombre: "exportarLogOffline", retorno: "Blob", parametros: [] }
        ],
        180, 230, 240, 130
    );

    var b3 = agregarClaseTablaUML(pkg, diag, "IndicadorConexionWidget", "boundary",
        [
            { nombre: "serverOnline", tipo: "boolean" },
            { nombre: "pingLatencyMs", tipo: "number" },
            { nombre: "autoSyncEnabled", tipo: "boolean" }
        ],
        [
            { nombre: "testConnection", retorno: "Promise<boolean>", parametros: [] },
            { nombre: "triggerAutoSyncOnReconnect", retorno: "void", parametros: [] }
        ],
        180, 390, 240, 120
    );

    // --- Columna 3: Controller Principal (FastAPI Router) ---
    var cRoute = agregarClaseTablaUML(pkg, diag, "SyncRouteController", "control",
        [
            { nombre: "prefix", tipo: "string = '/api/v1/sync'" },
            { nombre: "dbSession", tipo: "AsyncSession" },
            { nombre: "tokenValidator", tipo: "JWTBearer" }
        ],
        [
            { nombre: "postLoteSync", retorno: "JSONResponse", parametros: [{ nombre: "lote", tipo: "SyncBatchDTO" }, { nombre: "token", tipo: "TokenPayload" }] },
            { nombre: "getPendientesConciliacion", retorno: "JSONResponse", parametros: [{ nombre: "idSucursal", tipo: "int" }] },
            { nombre: "getEstadoColaSync", retorno: "JSONResponse", parametros: [] },
            { nombre: "postHeartbeatSync", retorno: "JSONResponse", parametros: [] }
        ],
        470, 170, 280, 210
    );

    // --- Columna 4: Domain Services (Lógica de Negocio y Cache Local) ---
    var cDomain = agregarClaseTablaUML(pkg, diag, "SyncDomainService", "control",
        [
            { nombre: "maxBatchSize", tipo: "int = 500" },
            { nombre: "logger", tipo: "StructuredLogger" },
            { nombre: "conflictDetector", tipo: "ConflictPolicy" }
        ],
        [
            { nombre: "_ejecutar_lote_sync", retorno: "BatchResult", parametros: [{ nombre: "lote", tipo: "SyncBatchDTO" }, { nombre: "user", tipo: "UserContext" }] },
            { nombre: "validarFingerprint", retorno: "boolean", parametros: [{ nombre: "opId", tipo: "UUID" }, { nombre: "hash", tipo: "string" }] },
            { nombre: "procesarOperacionOffline", retorno: "OpStatus", parametros: [{ nombre: "op", tipo: "SyncOpPayload" }, { nombre: "session", tipo: "Session" }] },
            { nombre: "descontarStockAtomic", retorno: "boolean", parametros: [{ nombre: "idSucursal", tipo: "int" }, { nombre: "items", tipo: "ItemDTO[]" }] },
            { nombre: "retenerConflictos", retorno: "void", parametros: [{ nombre: "conflictos", tipo: "ConflictDTO[]" }] },
            { nombre: "purgarConfirmadas", retorno: "void", parametros: [{ nombre: "recibos", tipo: "UUID[]" }] }
        ],
        790, 70, 280, 210
    );

    var cLocal = agregarClaseTablaUML(pkg, diag, "CacheLocalStorageService", "control",
        [
            { nombre: "dbName", tipo: "string = 'AuroraOfflineDB'" },
            { nombre: "storageEngine", tipo: "IndexedDB_Adapter" }
        ],
        [
            { nombre: "obtenerColaPendientes", retorno: "Promise<LocalOperation[]>", parametros: [] },
            { nombre: "marcarEnTransito", retorno: "Promise<void>", parametros: [{ nombre: "ids", tipo: "UUID[]" }] },
            { nombre: "purgarConfirmadasLocal", retorno: "Promise<void>", parametros: [{ nombre: "ids", tipo: "UUID[]" }] },
            { nombre: "registrarConflictoLocal", retorno: "Promise<void>", parametros: [{ nombre: "opId", tipo: "UUID" }, { nombre: "reason", tipo: "string" }] }
        ],
        790, 310, 280, 160
    );

    // --- Columna 5 & 6: Entities (PostgreSQL DAO & Cache Local) ---
    var e1 = agregarClaseTablaUML(pkg, diag, "t_sync_operacion", "entity",
        [
            { nombre: "operation_id", tipo: "UUID [PK]" },
            { nombre: "id_sucursal", tipo: "integer [FK]" },
            { nombre: "id_usuario", tipo: "integer [FK]" },
            { nombre: "tipo_operacion", tipo: "varchar(50)" },
            { nombre: "payload_json", tipo: "jsonb" },
            { nombre: "client_timestamp", tipo: "timestamptz" },
            { nombre: "server_timestamp", tipo: "timestamptz" },
            { nombre: "status", tipo: "varchar(20)" },
            { nombre: "conflict_code", tipo: "varchar(50)" },
            { nombre: "fingerprint", tipo: "varchar(64)" }
        ],
        [
            { nombre: "findById", retorno: "SyncOp", parametros: [{ nombre: "id", tipo: "UUID" }] },
            { nombre: "findByStatus", retorno: "SyncOp[]", parametros: [{ nombre: "status", tipo: "string" }] },
            { nombre: "updateStatus", retorno: "void", parametros: [{ nombre: "id", tipo: "UUID" }, { nombre: "status", tipo: "string" }, { nombre: "conflict", tipo: "string" }] },
            { nombre: "insertBatch", retorno: "void", parametros: [{ nombre: "ops", tipo: "SyncOp[]" }] }
        ],
        1110, 30, 230, 220
    );

    var e2 = agregarClaseTablaUML(pkg, diag, "t_inventario", "entity",
        [
            { nombre: "id_inventario", tipo: "serial [PK]" },
            { nombre: "id_sucursal", tipo: "integer [FK]" },
            { nombre: "id_producto", tipo: "integer [FK]" },
            { nombre: "stock_actual", tipo: "integer" },
            { nombre: "stock_minimo", tipo: "integer" },
            { nombre: "fecha_actualizacion", tipo: "timestamp" }
        ],
        [
            { nombre: "findBySucursalProducto", retorno: "Inventario", parametros: [{ nombre: "sucId", tipo: "int" }, { nombre: "prodId", tipo: "int" }] },
            { nombre: "atomicDescontar", retorno: "boolean", parametros: [{ nombre: "id", tipo: "int" }, { nombre: "cant", tipo: "int" }] }
        ],
        1110, 280, 230, 160
    );

    var e3 = agregarClaseTablaUML(pkg, diag, "t_venta", "entity",
        [
            { nombre: "id_venta", tipo: "serial [PK]" },
            { nombre: "id_empresa", tipo: "integer [FK]" },
            { nombre: "id_sucursal", tipo: "integer [FK]" },
            { nombre: "id_cliente", tipo: "integer [FK]" },
            { nombre: "total", tipo: "numeric(12,2)" },
            { nombre: "estado", tipo: "varchar(20)" },
            { nombre: "es_offline", tipo: "boolean" },
            { nombre: "uuid_offline", tipo: "UUID" }
        ],
        [
            { nombre: "insertVentaSync", retorno: "int", parametros: [{ nombre: "venta", tipo: "VentaData" }] },
            { nombre: "findByUuidOffline", retorno: "Venta", parametros: [{ nombre: "uuid", tipo: "UUID" }] }
        ],
        1370, 30, 220, 190
    );

    var e4 = agregarClaseTablaUML(pkg, diag, "t_pago", "entity",
        [
            { nombre: "id_pago", tipo: "serial [PK]" },
            { nombre: "id_venta", tipo: "integer [FK]" },
            { nombre: "monto", tipo: "numeric(12,2)" },
            { nombre: "metodo_pago", tipo: "varchar(30)" },
            { nombre: "estado", tipo: "varchar(20)" }
        ],
        [
            { nombre: "insertPago", retorno: "int", parametros: [{ nombre: "pago", tipo: "PagoData" }] }
        ],
        1370, 250, 220, 130
    );

    var e5 = agregarClaseTablaUML(pkg, diag, "t_bitacora", "entity",
        [
            { nombre: "id_bitacora", tipo: "serial [PK]" },
            { nombre: "id_usuario", tipo: "integer [FK]" },
            { nombre: "accion", tipo: "varchar(100)" },
            { nombre: "modulo", tipo: "varchar(50)" },
            { nombre: "detalle", tipo: "text" },
            { nombre: "ip_origen", tipo: "varchar(45)" },
            { nombre: "fecha", tipo: "timestamp" }
        ],
        [
            { nombre: "registrar", retorno: "void", parametros: [{ nombre: "modulo", tipo: "string" }, { nombre: "accion", tipo: "string" }, { nombre: "detalle", tipo: "string" }] }
        ],
        1370, 410, 220, 150
    );

    // --- Conexiones Ortogonales ---
    conectarElementos(act, b1, "Association", "interactua", null, "1", "1");
    conectarElementos(act, b2, "Association", "abre modal", null, "1", "1");
    conectarElementos(act, b3, "Association", "monitorea", null, "1", "1");

    conectarElementos(b1, cRoute, "Dependency", "envía HTTP", "use", null, null);
    conectarElementos(b1, cLocal, "Dependency", "consulta cola", "use", null, null);
    conectarElementos(b2, cLocal, "Dependency", "gestiona items", "use", null, null);
    conectarElementos(b3, cRoute, "Dependency", "ping heartbeat", "use", null, null);

    conectarElementos(cRoute, cDomain, "Association", "delega ejecución", null, "1", "1");
    conectarElementos(cDomain, e1, "Dependency", "registra/valida", "use", null, null);
    conectarElementos(cDomain, e2, "Dependency", "descuenta stock", "use", null, null);
    conectarElementos(cDomain, e3, "Dependency", "inserta venta", "use", null, null);
    conectarElementos(cDomain, e4, "Dependency", "registra cobro", "use", null, null);
    conectarElementos(cDomain, e5, "Dependency", "audita evento", "use", null, null);

    diag.Update();
    Repository.ReloadDiagram(diag.DiagramID);
}


// =================================================================================================
// 2. CU19W: Resolver conflictos de sincronización (Conciliación & Bandeja)
// =================================================================================================
function generarClasesCU19W(pkg) {
    Session.Output(" -> Construyendo: cd CU19W - Resolver conflictos de sincronización");
    var diag = pkg.Diagrams.AddNew("cd CU19W - Resolver conflictos de sincronización", "Logical");
    diag.Update();
    configurarDiagramaTablasUML(diag);

    // --- Columna 1: Actor ---
    var act = agregarActor(pkg, diag, "Administrador", 40, 220, 90, 110);

    // --- Columna 2: Boundary ---
    var b1 = agregarClaseTablaUML(pkg, diag, "BandejaConflictosView", "boundary",
        [
            { nombre: "conflictosPendientes", tipo: "SyncConflict[]" },
            { nombre: "selectedConflict", tipo: "SyncConflict" },
            { nombre: "isLoading", tipo: "boolean" },
            { nombre: "filterType", tipo: "string" }
        ],
        [
            { nombre: "cargarBandejaConflictos", retorno: "void", parametros: [] },
            { nombre: "seleccionarConflicto", retorno: "void", parametros: [{ nombre: "id", tipo: "UUID" }] },
            { nombre: "filtrarPorTipo", retorno: "void", parametros: [{ nombre: "tipo", tipo: "string" }] },
            { nombre: "mostrarAlertaResolucion", retorno: "void", parametros: [{ nombre: "msg", tipo: "string" }] }
        ],
        180, 50, 240, 150
    );

    var b2 = agregarClaseTablaUML(pkg, diag, "ModalResolucionConflicto", "boundary",
        [
            { nombre: "operationId", tipo: "UUID" },
            { nombre: "serverPayload", tipo: "Object" },
            { nombre: "localPayload", tipo: "Object" },
            { nombre: "resolutionStrategy", tipo: "string" }
        ],
        [
            { nombre: "seleccionarEstrategia", retorno: "void", parametros: [{ nombre: "est", tipo: "string" }] },
            { nombre: "aplicarResolucionForzar", retorno: "void", parametros: [] },
            { nombre: "aplicarResolucionDescartar", retorno: "void", parametros: [] },
            { nombre: "aplicarAjusteManual", retorno: "void", parametros: [{ nombre: "datos", tipo: "Object" }] }
        ],
        180, 230, 240, 150
    );

    var b3 = agregarClaseTablaUML(pkg, diag, "AuditoriaResolucionDialog", "boundary",
        [
            { nombre: "justificacion", tipo: "string" },
            { nombre: "supervisorPin", tipo: "string" }
        ],
        [
            { nombre: "confirmarAccion", retorno: "void", parametros: [] },
            { nombre: "cancelar", retorno: "void", parametros: [] }
        ],
        180, 410, 240, 110
    );

    // --- Columna 3: Controller Principal ---
    var cRoute = agregarClaseTablaUML(pkg, diag, "SyncConflictRouteController", "control",
        [
            { nombre: "prefix", tipo: "string = '/api/v1/sync'" },
            { nombre: "dbSession", tipo: "AsyncSession" },
            { nombre: "authGuard", tipo: "SupervisorGuard" }
        ],
        [
            { nombre: "getPendientesConciliacion", retorno: "JSONResponse", parametros: [{ nombre: "filters", tipo: "ConflictFilterDTO" }] },
            { nombre: "postConciliarConflicto", retorno: "JSONResponse", parametros: [{ nombre: "id", tipo: "UUID" }, { nombre: "body", tipo: "ConciliacionDTO" }] },
            { nombre: "getDetalleOperacionConflicto", retorno: "JSONResponse", parametros: [{ nombre: "id", tipo: "UUID" }] }
        ],
        470, 180, 280, 180
    );

    // --- Columna 4: Domain Service ---
    var cDomain = agregarClaseTablaUML(pkg, diag, "SyncConflictDomainService", "control",
        [
            { nombre: "syncLogger", tipo: "StructuredLogger" },
            { nombre: "inventoryService", tipo: "InventoryService" }
        ],
        [
            { nombre: "listarConflictosSync", retorno: "ConflictListDTO", parametros: [{ nombre: "filter", tipo: "FilterContext" }] },
            { nombre: "procesarConciliacion", retorno: "ResolutionReceipt", parametros: [{ nombre: "opId", tipo: "UUID" }, { nombre: "resolucion", tipo: "ResolucionData" }] },
            { nombre: "validarEstadoConflicto", retorno: "boolean", parametros: [{ nombre: "opId", tipo: "UUID" }] },
            { nombre: "aplicarReglaForzar", retorno: "void", parametros: [{ nombre: "op", tipo: "SyncOp" }] },
            { nombre: "aplicarReglaDescartar", retorno: "void", parametros: [{ nombre: "op", tipo: "SyncOp" }] },
            { nombre: "ajustarInventarioAuditado", retorno: "void", parametros: [{ nombre: "sucursalId", tipo: "int" }, { nombre: "items", tipo: "ItemQty[]" }] }
        ],
        790, 160, 280, 210
    );

    // --- Columna 5 & 6: Entities ---
    var e1 = agregarClaseTablaUML(pkg, diag, "t_sync_operacion", "entity",
        [
            { nombre: "operation_id", tipo: "UUID [PK]" },
            { nombre: "id_sucursal", tipo: "integer [FK]" },
            { nombre: "id_usuario", tipo: "integer [FK]" },
            { nombre: "payload_json", tipo: "jsonb" },
            { nombre: "status", tipo: "varchar(20)" },
            { nombre: "conflict_code", tipo: "varchar(50)" },
            { nombre: "resolution_action", tipo: "varchar(30)" },
            { nombre: "resolved_by", tipo: "integer [FK]" },
            { nombre: "resolved_at", tipo: "timestamptz" }
        ],
        [
            { nombre: "findConflictById", retorno: "SyncOp", parametros: [{ nombre: "id", tipo: "UUID" }] },
            { nombre: "listActiveConflicts", retorno: "SyncOp[]", parametros: [] },
            { nombre: "updateResolution", retorno: "void", parametros: [{ nombre: "id", tipo: "UUID" }, { nombre: "status", tipo: "string" }, { nombre: "action", tipo: "string" }, { nombre: "userId", tipo: "int" }] }
        ],
        1110, 60, 230, 210
    );

    var e2 = agregarClaseTablaUML(pkg, diag, "t_inventario", "entity",
        [
            { nombre: "id_inventario", tipo: "serial [PK]" },
            { nombre: "id_sucursal", tipo: "integer [FK]" },
            { nombre: "id_producto", tipo: "integer [FK]" },
            { nombre: "stock_actual", tipo: "integer" },
            { nombre: "stock_minimo", tipo: "integer" }
        ],
        [
            { nombre: "findById", retorno: "Inventario", parametros: [{ nombre: "id", tipo: "int" }] },
            { nombre: "updateStockAuditado", retorno: "void", parametros: [{ nombre: "id", tipo: "int" }, { nombre: "nuevoStock", tipo: "int" }] }
        ],
        1110, 300, 230, 150
    );

    var e3 = agregarClaseTablaUML(pkg, diag, "cache_local", "entity",
        [
            { nombre: "localQueueId", tipo: "string [PK]" },
            { nombre: "operationId", tipo: "UUID" },
            { nombre: "localStatus", tipo: "string" },
            { nombre: "lastSyncAttempt", tipo: "Date" }
        ],
        [
            { nombre: "updateLocalItemResuelto", retorno: "void", parametros: [{ nombre: "opId", tipo: "UUID" }] },
            { nombre: "removeIfDiscarded", retorno: "void", parametros: [{ nombre: "opId", tipo: "UUID" }] }
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
    conectarElementos(act, b1, "Association", "consulta bandeja", null, "1", "1");
    conectarElementos(act, b2, "Association", "aplica resolución", null, "1", "1");
    conectarElementos(act, b3, "Association", "ingresa justificación", null, "1", "1");

    conectarElementos(b1, cRoute, "Dependency", "GET incidencias", "use", null, null);
    conectarElementos(b2, cRoute, "Dependency", "POST resolución", "use", null, null);
    conectarElementos(b2, e3, "Dependency", "actualiza local", "use", null, null);

    conectarElementos(cRoute, cDomain, "Association", "delega conciliación", null, "1", "1");
    conectarElementos(cDomain, e1, "Dependency", "actualiza estado", "use", null, null);
    conectarElementos(cDomain, e2, "Dependency", "ajusta existencias", "use", null, null);
    conectarElementos(cDomain, e4, "Dependency", "audita resolución", "use", null, null);

    diag.Update();
    Repository.ReloadDiagram(diag.DiagramID);
}


// =================================================================================================
// 3. CU20W: Consultar ventas, reservas e inventario (Gestión Operacional de Tienda)
// =================================================================================================
function generarClasesCU20W(pkg) {
    Session.Output(" -> Construyendo: cd CU20W - Consultar ventas, reservas e inventario");
    var diag = pkg.Diagrams.AddNew("cd CU20W - Consultar ventas, reservas e inventario", "Logical");
    diag.Update();
    configurarDiagramaTablasUML(diag);

    // --- Columna 1: Actor ---
    var act = agregarActor(pkg, diag, "AdminTienda / Encargado", 40, 220, 90, 110);

    // --- Columna 2: Boundary ---
    var b1 = agregarClaseTablaUML(pkg, diag, "GestionTiendaView", "boundary",
        [
            { nombre: "currentSucursalId", tipo: "number" },
            { nombre: "operacionMetrics", tipo: "TiendaOperationalDTO" },
            { nombre: "refreshing", tipo: "boolean" }
        ],
        [
            { nombre: "accederGestionTienda", retorno: "void", parametros: [{ nombre: "idSucursal", tipo: "number" }] },
            { nombre: "refrescarDashboard", retorno: "void", parametros: [] },
            { nombre: "cambiarSucursal", retorno: "void", parametros: [{ nombre: "id", tipo: "number" }] },
            { nombre: "mostrarAlertaBajoStock", retorno: "void", parametros: [{ nombre: "alertas", tipo: "ItemStockAlert[]" }] }
        ],
        180, 50, 240, 140
    );

    var b2 = agregarClaseTablaUML(pkg, diag, "PanelCajasTurnoWidget", "boundary",
        [
            { nombre: "sesionActiva", tipo: "CajaSesionDTO" },
            { nombre: "totalVentasEfectivo", tipo: "number" },
            { nombre: "totalVentasDigital", tipo: "number" }
        ],
        [
            { nombre: "verDetalleSesion", retorno: "void", parametros: [{ nombre: "idSesion", tipo: "number" }] },
            { nombre: "solicitarCierreTurno", retorno: "void", parametros: [] }
        ],
        180, 220, 240, 120
    );

    var b3 = agregarClaseTablaUML(pkg, diag, "TablaVentasReservasComponent", "boundary",
        [
            { nombre: "ultimasVentas", tipo: "VentaItem[]" },
            { nombre: "reservasPendientes", tipo: "ReservaItem[]" }
        ],
        [
            { nombre: "verDetalleVenta", retorno: "void", parametros: [{ nombre: "idVenta", tipo: "number" }] },
            { nombre: "entregarReserva", retorno: "void", parametros: [{ nombre: "idReserva", tipo: "number" }] }
        ],
        180, 370, 240, 120
    );

    // --- Columna 3: Controller Principal ---
    var cRoute = agregarClaseTablaUML(pkg, diag, "KpisOperationalRouteController", "control",
        [
            { nombre: "prefix", tipo: "string = '/api/v1/kpis'" },
            { nombre: "session", tipo: "AsyncSession" },
            { nombre: "branchSecurity", tipo: "BranchAccessGuard" }
        ],
        [
            { nombre: "getKpisOperacionales", retorno: "JSONResponse", parametros: [{ nombre: "idSucursal", tipo: "int" }, { nombre: "fecha", tipo: "date" }] },
            { nombre: "getCajaTurnoResumen", retorno: "JSONResponse", parametros: [{ nombre: "idSucursal", tipo: "int" }] },
            { nombre: "getAlertasStockTienda", retorno: "JSONResponse", parametros: [{ nombre: "idSucursal", tipo: "int" }] }
        ],
        470, 170, 280, 180
    );

    // --- Columna 4: Domain Service ---
    var cDomain = agregarClaseTablaUML(pkg, diag, "KpisOperationalDomainService", "control",
        [
            { nombre: "cacheManager", tipo: "RedisCache" },
            { nombre: "metricAggregator", tipo: "MetricHelper" }
        ],
        [
            { nombre: "generarDashboardOperacional", retorno: "TiendaOperationalDTO", parametros: [{ nombre: "idSucursal", tipo: "int" }] },
            { nombre: "obtenerMetricasVentasDia", retorno: "VentasSummaryDTO", parametros: [{ nombre: "idSucursal", tipo: "int" }] },
            { nombre: "obtenerMetricasReservas", retorno: "ReservasSummaryDTO", parametros: [{ nombre: "idSucursal", tipo: "int" }] },
            { nombre: "calcularAlertasInventario", retorno: "StockHealthDTO", parametros: [{ nombre: "idSucursal", tipo: "int" }] },
            { nombre: "obtenerEstadoCajaTurno", retorno: "CajaTurnoDTO", parametros: [{ nombre: "idSucursal", tipo: "int" }] }
        ],
        790, 160, 280, 200
    );

    // --- Columna 5 & 6: Entities ---
    var e1 = agregarClaseTablaUML(pkg, diag, "t_sucursal", "entity",
        [
            { nombre: "id_sucursal", tipo: "serial [PK]" },
            { nombre: "id_empresa", tipo: "integer [FK]" },
            { nombre: "nombre", tipo: "varchar(100)" },
            { nombre: "direccion", tipo: "varchar(200)" },
            { nombre: "estado", tipo: "varchar(20)" }
        ],
        [
            { nombre: "findById", retorno: "Sucursal", parametros: [{ nombre: "id", tipo: "int" }] },
            { nombre: "listActivas", retorno: "Sucursal[]", parametros: [{ nombre: "empresaId", tipo: "int" }] }
        ],
        1110, 40, 230, 150
    );

    var e2 = agregarClaseTablaUML(pkg, diag, "t_caja_sesion", "entity",
        [
            { nombre: "id_sesion", tipo: "serial [PK]" },
            { nombre: "id_caja", tipo: "integer [FK]" },
            { nombre: "id_sucursal", tipo: "integer [FK]" },
            { nombre: "id_usuario", tipo: "integer [FK]" },
            { nombre: "estado", tipo: "varchar(20)" },
            { nombre: "monto_apertura", tipo: "numeric(12,2)" },
            { nombre: "monto_cierre", tipo: "numeric(12,2)" }
        ],
        [
            { nombre: "findSesionAbierta", retorno: "CajaSesion", parametros: [{ nombre: "sucursalId", tipo: "int" }] },
            { nombre: "findById", retorno: "CajaSesion", parametros: [{ nombre: "id", tipo: "int" }] }
        ],
        1110, 220, 230, 170
    );

    var e3 = agregarClaseTablaUML(pkg, diag, "t_venta", "entity",
        [
            { nombre: "id_venta", tipo: "serial [PK]" },
            { nombre: "id_sucursal", tipo: "integer [FK]" },
            { nombre: "id_cliente", tipo: "integer [FK]" },
            { nombre: "total", tipo: "numeric(12,2)" },
            { nombre: "estado", tipo: "varchar(20)" },
            { nombre: "fecha", tipo: "timestamp" }
        ],
        [
            { nombre: "sumVentasDia", retorno: "TotalVentasDTO", parametros: [{ nombre: "sucursalId", tipo: "int" }, { nombre: "fecha", tipo: "date" }] },
            { nombre: "countVentasDia", retorno: "int", parametros: [{ nombre: "sucursalId", tipo: "int" }] }
        ],
        1370, 40, 220, 160
    );

    var e4 = agregarClaseTablaUML(pkg, diag, "t_reserva", "entity",
        [
            { nombre: "id_reserva", tipo: "serial [PK]" },
            { nombre: "id_sucursal", tipo: "integer [FK]" },
            { nombre: "id_cliente", tipo: "integer [FK]" },
            { nombre: "estado", tipo: "varchar(20)" },
            { nombre: "fecha_reserva", tipo: "timestamp" },
            { nombre: "fecha_vencimiento", tipo: "timestamp" }
        ],
        [
            { nombre: "countByEstado", retorno: "int", parametros: [{ nombre: "sucursalId", tipo: "int" }, { nombre: "estado", tipo: "string" }] },
            { nombre: "listPendientes", retorno: "Reserva[]", parametros: [{ nombre: "sucursalId", tipo: "int" }] }
        ],
        1370, 220, 220, 160
    );

    var e5 = agregarClaseTablaUML(pkg, diag, "t_inventario", "entity",
        [
            { nombre: "id_inventario", tipo: "serial [PK]" },
            { nombre: "id_sucursal", tipo: "integer [FK]" },
            { nombre: "id_producto", tipo: "integer [FK]" },
            { nombre: "stock_actual", tipo: "integer" },
            { nombre: "stock_reservado", tipo: "integer" },
            { nombre: "stock_minimo", tipo: "integer" }
        ],
        [
            { nombre: "sumStockActual", retorno: "int", parametros: [{ nombre: "sucursalId", tipo: "int" }] },
            { nombre: "findBajoStock", retorno: "Inventario[]", parametros: [{ nombre: "sucursalId", tipo: "int" }] }
        ],
        1370, 400, 220, 160
    );

    // --- Conexiones Ortogonales ---
    conectarElementos(act, b1, "Association", "visualiza", null, "1", "1");
    conectarElementos(act, b2, "Association", "supervisa turno", null, "1", "1");
    conectarElementos(act, b3, "Association", "despacha reservas", null, "1", "1");

    conectarElementos(b1, cRoute, "Dependency", "GET kpis", "use", null, null);
    conectarElementos(b2, cRoute, "Dependency", "GET caja", "use", null, null);
    conectarElementos(b3, cRoute, "Dependency", "GET transacciones", "use", null, null);

    conectarElementos(cRoute, cDomain, "Association", "consolida metricas", null, "1", "1");
    conectarElementos(cDomain, e1, "Dependency", "consulta sucursal", "use", null, null);
    conectarElementos(cDomain, e2, "Dependency", "consulta turno", "use", null, null);
    conectarElementos(cDomain, e3, "Dependency", "agrega ventas", "use", null, null);
    conectarElementos(cDomain, e4, "Dependency", "agrega reservas", "use", null, null);
    conectarElementos(cDomain, e5, "Dependency", "evalua stock", "use", null, null);

    diag.Update();
    Repository.ReloadDiagram(diag.DiagramID);
}


// =================================================================================================
// 4. CU21W: Visualizar indicadores empresariales (Dashboard Estratégico Ejecutivo)
// =================================================================================================
function generarClasesCU21W(pkg) {
    Session.Output(" -> Construyendo: cd CU21W - Visualizar indicadores empresariales");
    var diag = pkg.Diagrams.AddNew("cd CU21W - Visualizar indicadores empresariales", "Logical");
    diag.Update();
    configurarDiagramaTablasUML(diag);

    // --- Columna 1: Actor ---
    var act = agregarActor(pkg, diag, "Administrador", 40, 240, 90, 110);

    // --- Columna 2: Boundary ---
    var b1 = agregarClaseTablaUML(pkg, diag, "DashboardKpisView", "boundary",
        [
            { nombre: "kpiPayload", tipo: "StrategicKpiDTO" },
            { nombre: "activePeriod", tipo: "DateRange" },
            { nombre: "selectedCurrency", tipo: "string = 'BOB'" }
        ],
        [
            { nombre: "cargarDashboardKpis", retorno: "void", parametros: [] },
            { nombre: "cambiarRangoTemporal", retorno: "void", parametros: [{ nombre: "range", tipo: "DateRange" }] },
            { nombre: "exportarVistaDashboard", retorno: "void", parametros: [] },
            { nombre: "mostrarGraficosIndicadores", retorno: "void", parametros: [] }
        ],
        180, 50, 240, 140
    );

    var b2 = agregarClaseTablaUML(pkg, diag, "GraficoVentasSucursalComponent", "boundary",
        [
            { nombre: "seriesData", tipo: "BranchSalesChart[]" },
            { nombre: "chartType", tipo: "string = 'bar'" }
        ],
        [
            { nombre: "renderChart", retorno: "void", parametros: [] },
            { nombre: "drillDownSucursal", retorno: "void", parametros: [{ nombre: "sucId", tipo: "number" }] }
        ],
        180, 220, 240, 120
    );

    var b3 = agregarClaseTablaUML(pkg, diag, "TarjetasKpiExecutiveWidget", "boundary",
        [
            { nombre: "totalIngresos", tipo: "number" },
            { nombre: "transaccionesMes", tipo: "number" },
            { nombre: "ticketPromedio", tipo: "number" },
            { nombre: "ratingSatisfaccion", tipo: "number" }
        ],
        [
            { nombre: "formatCurrency", retorno: "string", parametros: [{ nombre: "val", tipo: "number" }] },
            { nombre: "renderTrendBadge", retorno: "void", parametros: [{ nombre: "growth", tipo: "number" }] }
        ],
        180, 370, 240, 140
    );

    // --- Columna 3: Controller Principal ---
    var cRoute = agregarClaseTablaUML(pkg, diag, "KpisExecutiveRouteController", "control",
        [
            { nombre: "prefix", tipo: "string = '/api/v1/kpis'" },
            { nombre: "db", tipo: "AsyncSession" },
            { nombre: "saasTenantGuard", tipo: "TenantContextGuard" }
        ],
        [
            { nombre: "getKpisResumen", retorno: "JSONResponse", parametros: [{ nombre: "periodo", tipo: "string" }, { nombre: "token", tipo: "TokenData" }] },
            { nombre: "getVentasPorSucursal", retorno: "JSONResponse", parametros: [{ nombre: "empresaId", tipo: "int" }] },
            { nombre: "getCapitalInventario", retorno: "JSONResponse", parametros: [{ nombre: "empresaId", tipo: "int" }] },
            { nombre: "getSatisfaccionClientes", retorno: "JSONResponse", parametros: [{ nombre: "empresaId", tipo: "int" }] }
        ],
        470, 170, 280, 190
    );

    // --- Columna 4: Domain Service ---
    var cDomain = agregarClaseTablaUML(pkg, diag, "KpisExecutiveDomainService", "control",
        [
            { nombre: "tenantFilter", tipo: "TenantResolver" },
            { nombre: "analyticEngine", tipo: "AnalyticAggregator" }
        ],
        [
            { nombre: "generarKpisResumen", retorno: "StrategicKpiDTO", parametros: [{ nombre: "context", tipo: "SecurityContext" }] },
            { nombre: "calcularIngresosPeriodo", retorno: "RevenueDTO", parametros: [{ nombre: "empresaId", tipo: "int" }, { nombre: "dias", tipo: "int" }] },
            { nombre: "consolidarVentasPorSucursal", retorno: "SucursalBreakdownDTO[]", parametros: [{ nombre: "empresaId", tipo: "int" }] },
            { nombre: "calcularValuacionCapitalStock", retorno: "StockValuationDTO", parametros: [{ nombre: "empresaId", tipo: "int" }] },
            { nombre: "calcularIndiceSatisfaccion", retorno: "CSAT_DTO", parametros: [{ nombre: "empresaId", tipo: "int" }] }
        ],
        790, 160, 280, 200
    );

    // --- Columna 5 & 6: Entities ---
    var e1 = agregarClaseTablaUML(pkg, diag, "empresa", "entity",
        [
            { nombre: "id_empresa", tipo: "serial [PK]" },
            { nombre: "nombre_empresa", tipo: "varchar(150)" },
            { nombre: "nit", tipo: "varchar(30)" },
            { nombre: "estado", tipo: "varchar(20)" },
            { nombre: "plan_actual", tipo: "varchar(50)" }
        ],
        [
            { nombre: "findById", retorno: "Empresa", parametros: [{ nombre: "id", tipo: "int" }] },
            { nombre: "getPlanLimits", retorno: "PlanLimits", parametros: [{ nombre: "id", tipo: "int" }] }
        ],
        1110, 40, 230, 150
    );

    var e2 = agregarClaseTablaUML(pkg, diag, "t_sucursal", "entity",
        [
            { nombre: "id_sucursal", tipo: "serial [PK]" },
            { nombre: "id_empresa", tipo: "integer [FK]" },
            { nombre: "nombre", tipo: "varchar(100)" },
            { nombre: "ciudad", tipo: "varchar(100)" },
            { nombre: "activo", tipo: "boolean" }
        ],
        [
            { nombre: "listByEmpresa", retorno: "Sucursal[]", parametros: [{ nombre: "empId", tipo: "int" }] },
            { nombre: "countActivas", retorno: "int", parametros: [{ nombre: "empId", tipo: "int" }] }
        ],
        1110, 220, 230, 150
    );

    var e3 = agregarClaseTablaUML(pkg, diag, "t_venta", "entity",
        [
            { nombre: "id_venta", tipo: "serial [PK]" },
            { nombre: "id_empresa", tipo: "integer [FK]" },
            { nombre: "id_sucursal", tipo: "integer [FK]" },
            { nombre: "total", tipo: "numeric(12,2)" },
            { nombre: "estado", tipo: "varchar(20)" },
            { nombre: "fecha", tipo: "timestamp" }
        ],
        [
            { nombre: "sumVentasPeriodo", retorno: "MetricDTO", parametros: [{ nombre: "empId", tipo: "int" }, { nombre: "since", tipo: "timestamp" }] },
            { nombre: "sumPorSucursal", retorno: "BranchMetric[]", parametros: [{ nombre: "empId", tipo: "int" }] }
        ],
        1370, 40, 220, 160
    );

    var e4 = agregarClaseTablaUML(pkg, diag, "t_reserva", "entity",
        [
            { nombre: "id_reserva", tipo: "serial [PK]" },
            { nombre: "id_empresa", tipo: "integer [FK]" },
            { nombre: "estado", tipo: "varchar(20)" },
            { nombre: "fecha_reserva", tipo: "timestamp" }
        ],
        [
            { nombre: "countActivas", retorno: "int", parametros: [{ nombre: "empId", tipo: "int" }] }
        ],
        1370, 220, 220, 120
    );

    var e5 = agregarClaseTablaUML(pkg, diag, "t_inventario", "entity",
        [
            { nombre: "id_inventario", tipo: "serial [PK]" },
            { nombre: "id_sucursal", tipo: "integer [FK]" },
            { nombre: "id_producto", tipo: "integer [FK]" },
            { nombre: "stock_actual", tipo: "integer" },
            { nombre: "precio_unitario", tipo: "numeric(12,2)" }
        ],
        [
            { nombre: "sumValuacionCapital", retorno: "numeric", parametros: [{ nombre: "empId", tipo: "int" }] }
        ],
        1110, 390, 230, 140
    );

    var e6 = agregarClaseTablaUML(pkg, diag, "t_valoracion", "entity",
        [
            { nombre: "id_valoracion", tipo: "serial [PK]" },
            { nombre: "id_producto", tipo: "integer [FK]" },
            { nombre: "id_cliente", tipo: "integer [FK]" },
            { nombre: "calificacion", tipo: "integer" },
            { nombre: "estado", tipo: "varchar(20)" },
            { nombre: "fecha", tipo: "timestamp" }
        ],
        [
            { nombre: "avgRatingEmpresa", retorno: "numeric", parametros: [{ nombre: "empId", tipo: "int" }] },
            { nombre: "countReviews", retorno: "int", parametros: [{ nombre: "empId", tipo: "int" }] }
        ],
        1370, 370, 220, 160
    );

    // --- Conexiones Ortogonales ---
    conectarElementos(act, b1, "Association", "visualiza", null, "1", "1");
    conectarElementos(act, b2, "Association", "analiza desglose", null, "1", "1");
    conectarElementos(act, b3, "Association", "evalua KPIs", null, "1", "1");

    conectarElementos(b1, cRoute, "Dependency", "GET indicadores", "use", null, null);
    conectarElementos(b2, cRoute, "Dependency", "GET sucursales", "use", null, null);
    conectarElementos(b3, cRoute, "Dependency", "GET resumen", "use", null, null);

    conectarElementos(cRoute, cDomain, "Association", "calcula agregados", null, "1", "1");
    conectarElementos(cDomain, e1, "Dependency", "valida tenant", "use", null, null);
    conectarElementos(cDomain, e2, "Dependency", "filtra sucursales", "use", null, null);
    conectarElementos(cDomain, e3, "Dependency", "suma ingresos", "use", null, null);
    conectarElementos(cDomain, e4, "Dependency", "cuenta reservas", "use", null, null);
    conectarElementos(cDomain, e5, "Dependency", "calcula capital", "use", null, null);
    conectarElementos(cDomain, e6, "Dependency", "calcula rating", "use", null, null);

    diag.Update();
    Repository.ReloadDiagram(diag.DiagramID);
}


// =================================================================================================
// 5. CU22W: Generar reportes bajo demanda (Motor Dinámico & Vistas Analíticas)
// =================================================================================================
function generarClasesCU22W(pkg) {
    Session.Output(" -> Construyendo: cd CU22W - Generar reportes bajo demanda");
    var diag = pkg.Diagrams.AddNew("cd CU22W - Generar reportes bajo demanda", "Logical");
    diag.Update();
    configurarDiagramaTablasUML(diag);

    // --- Columna 1: Actor ---
    var act = agregarActor(pkg, diag, "Administrador", 40, 230, 90, 110);

    // --- Columna 2: Boundary ---
    var b1 = agregarClaseTablaUML(pkg, diag, "MotorReportesView", "boundary",
        [
            { nombre: "comandoTexto", tipo: "string" },
            { nombre: "parsedDefinition", tipo: "QueryDefinitionDTO" },
            { nombre: "reportData", tipo: "ReportResultDTO" },
            { nombre: "isGenerating", tipo: "boolean" }
        ],
        [
            { nombre: "ingresarComandoReporte", retorno: "void", parametros: [{ nombre: "prompt", tipo: "string" }] },
            { nombre: "ejecutarReporte", retorno: "void", parametros: [] },
            { nombre: "solicitarExportacionPDF", retorno: "void", parametros: [] },
            { nombre: "solicitarExportacionExcel", retorno: "void", parametros: [] }
        ],
        180, 50, 240, 150
    );

    var b2 = agregarClaseTablaUML(pkg, diag, "EditorConsultaDinamicaModal", "boundary",
        [
            { nombre: "dimensionesSeleccionadas", tipo: "string[]" },
            { nombre: "metricasSeleccionadas", tipo: "string[]" },
            { nombre: "filtrosAvanzados", tipo: "FilterDef[]" }
        ],
        [
            { nombre: "agregarFiltro", retorno: "void", parametros: [{ nombre: "dim", tipo: "string" }, { nombre: "op", tipo: "string" }, { nombre: "val", tipo: "any" }] },
            { nombre: "previsualizarDatos", retorno: "void", parametros: [] },
            { nombre: "guardarPlantillaReporte", retorno: "void", parametros: [] }
        ],
        180, 230, 240, 140
    );

    var b3 = agregarClaseTablaUML(pkg, diag, "VisorTablaGraficosComponent", "boundary",
        [
            { nombre: "columnas", tipo: "TableColumn[]" },
            { nombre: "filas", tipo: "any[]" },
            { nombre: "totalizadores", tipo: "Object" },
            { nombre: "graficoTipo", tipo: "string" }
        ],
        [
            { nombre: "renderDataTable", retorno: "void", parametros: [] },
            { nombre: "renderPivotChart", retorno: "void", parametros: [] },
            { nombre: "paginar", retorno: "void", parametros: [{ nombre: "pagina", tipo: "number" }] }
        ],
        180, 390, 240, 140
    );

    // --- Columna 3: Controller Principal ---
    var cRoute = agregarClaseTablaUML(pkg, diag, "MotorReportesRouteController", "control",
        [
            { nombre: "prefix", tipo: "string = '/api/v1/motor-reportes'" },
            { nombre: "db", tipo: "AsyncSession" },
            { nombre: "reportAudit", tipo: "AuditLogger" }
        ],
        [
            { nombre: "postParseCommand", retorno: "JSONResponse", parametros: [{ nombre: "body", tipo: "CommandParseDTO" }] },
            { nombre: "postEjecutarReporte", retorno: "JSONResponse", parametros: [{ nombre: "queryDef", tipo: "QueryDefinitionDTO" }] },
            { nombre: "postExportarPDF", retorno: "StreamingResponse", parametros: [{ nombre: "queryDef", tipo: "QueryDefinitionDTO" }] },
            { nombre: "postExportarExcel", retorno: "StreamingResponse", parametros: [{ nombre: "queryDef", tipo: "QueryDefinitionDTO" }] }
        ],
        470, 170, 280, 190
    );

    // --- Columna 4: Domain Service ---
    var cDomain = agregarClaseTablaUML(pkg, diag, "ReportesDomainService", "control",
        [
            { nombre: "parserNLQ", tipo: "NaturalLanguageQueryParser" },
            { nombre: "pdfGenerator", tipo: "ReportPDFBuilder" },
            { nombre: "excelGenerator", tipo: "ExcelBuilder" }
        ],
        [
            { nombre: "parsearComandoReporte", retorno: "QueryDefinitionDTO", parametros: [{ nombre: "comando", tipo: "string" }] },
            { nombre: "ejecutarReporte", retorno: "ReportResultDTO", parametros: [{ nombre: "queryDef", tipo: "QueryDefinitionDTO" }] },
            { nombre: "generarPdfReporte", retorno: "byte[]", parametros: [{ nombre: "queryDef", tipo: "QueryDefinitionDTO" }] },
            { nombre: "generarExcelReporte", retorno: "byte[]", parametros: [{ nombre: "queryDef", tipo: "QueryDefinitionDTO" }] },
            { nombre: "construirConsultaSQLSegura", retorno: "string", parametros: [{ nombre: "queryDef", tipo: "QueryDefinitionDTO" }] }
        ],
        790, 160, 280, 200
    );

    // --- Columna 5 & 6: Analytical Views & Entities ---
    var e1 = agregarClaseTablaUML(pkg, diag, "vw_ventas_reporte", "entity",
        [
            { nombre: "id_venta", tipo: "integer" },
            { nombre: "fecha_venta", tipo: "date" },
            { nombre: "id_sucursal", tipo: "integer" },
            { nombre: "sucursal_nombre", tipo: "varchar(100)" },
            { nombre: "categoria_prenda", tipo: "varchar(80)" },
            { nombre: "cantidad_prendas", tipo: "integer" },
            { nombre: "subtotal", tipo: "numeric(12,2)" },
            { nombre: "descuento", tipo: "numeric(12,2)" },
            { nombre: "total", tipo: "numeric(12,2)" },
            { nombre: "metodo_pago", tipo: "varchar(30)" }
        ],
        [
            { nombre: "executeQuery", retorno: "RowData[]", parametros: [{ nombre: "filters", tipo: "FilterClause" }, { nombre: "dims", tipo: "string[]" }, { nombre: "metrics", tipo: "string[]" }] }
        ],
        1110, 40, 230, 210
    );

    var e2 = agregarClaseTablaUML(pkg, diag, "vw_inventario_reporte", "entity",
        [
            { nombre: "id_inventario", tipo: "integer" },
            { nombre: "prenda_sku", tipo: "varchar(50)" },
            { nombre: "prenda_nombre", tipo: "varchar(150)" },
            { nombre: "categoria", tipo: "varchar(80)" },
            { nombre: "talla", tipo: "varchar(10)" },
            { nombre: "color", tipo: "varchar(50)" },
            { nombre: "stock_actual", tipo: "integer" },
            { nombre: "stock_minimo", tipo: "integer" },
            { nombre: "costo_unitario", tipo: "numeric(12,2)" },
            { nombre: "valuacion_total", tipo: "numeric(14,2)" }
        ],
        [
            { nombre: "executeQuery", retorno: "RowData[]", parametros: [{ nombre: "filters", tipo: "FilterClause" }, { nombre: "dims", tipo: "string[]" }, { nombre: "metrics", tipo: "string[]" }] }
        ],
        1110, 270, 230, 210
    );

    var e3 = agregarClaseTablaUML(pkg, diag, "vw_rentabilidad_reporte", "entity",
        [
            { nombre: "id_producto", tipo: "integer" },
            { nombre: "nombre_producto", tipo: "varchar(150)" },
            { nombre: "categoria", tipo: "varchar(80)" },
            { nombre: "ingresos_totales", tipo: "numeric(14,2)" },
            { nombre: "costo_mercaderia", tipo: "numeric(14,2)" },
            { nombre: "margen_bruto_monto", tipo: "numeric(14,2)" },
            { nombre: "margen_bruto_pct", tipo: "numeric(5,2)" }
        ],
        [
            { nombre: "executeQuery", retorno: "RowData[]", parametros: [{ nombre: "filters", tipo: "FilterClause" }, { nombre: "dims", tipo: "string[]" }, { nombre: "metrics", tipo: "string[]" }] }
        ],
        1370, 70, 220, 180
    );

    var e4 = agregarClaseTablaUML(pkg, diag, "t_bitacora", "entity",
        [
            { nombre: "id_bitacora", tipo: "serial [PK]" },
            { nombre: "id_usuario", tipo: "integer [FK]" },
            { nombre: "accion", tipo: "varchar(100)" },
            { nombre: "modulo", tipo: "varchar(50)" },
            { nombre: "detalle", tipo: "text" },
            { nombre: "ip_origen", tipo: "varchar(45)" },
            { nombre: "fecha", tipo: "timestamp" }
        ],
        [
            { nombre: "registrar", retorno: "void", parametros: [{ nombre: "modulo", tipo: "string" }, { nombre: "accion", tipo: "string" }, { nombre: "detalle", tipo: "string" }] }
        ],
        1370, 280, 220, 160
    );

    // --- Conexiones Ortogonales ---
    conectarElementos(act, b1, "Association", "ingresa consulta", null, "1", "1");
    conectarElementos(act, b2, "Association", "ajusta filtros", null, "1", "1");
    conectarElementos(act, b3, "Association", "explora resultados", null, "1", "1");

    conectarElementos(b1, cRoute, "Dependency", "POST parse/execute", "use", null, null);
    conectarElementos(b2, cRoute, "Dependency", "POST previsualizar", "use", null, null);
    conectarElementos(b3, cRoute, "Dependency", "POST exportar", "use", null, null);

    conectarElementos(cRoute, cDomain, "Association", "procesa query", null, "1", "1");
    conectarElementos(cDomain, e1, "Dependency", "consulta ventas", "use", null, null);
    conectarElementos(cDomain, e2, "Dependency", "consulta inventario", "use", null, null);
    conectarElementos(cDomain, e3, "Dependency", "consulta rentabilidad", "use", null, null);
    conectarElementos(cDomain, e4, "Dependency", "audita reporte", "use", null, null);

    diag.Update();
    Repository.ReloadDiagram(diag.DiagramID);
}


// =================================================================================================
// FUNCIÓN PRINCIPAL DE EJECUCIÓN EN ENTERPRISE ARCHITECT
// =================================================================================================
function Main() {
    Repository.EnsureOutputVisible("Script");
    Session.Output("================================================================================");
    Session.Output("Iniciando generación de Diagramas de Análisis de Clases (CU18W a CU22W) en EA...");
    Session.Output("================================================================================");

    var pkg = Repository.GetTreeSelectedPackage();
    if (pkg == null) {
        Session.Prompt("ERROR: Por favor seleccione un paquete en el Project Browser antes de ejecutar.", 0);
        return;
    }

    var pkgName = "Diagramas de Análisis de Clases (ICONIX) - Lote 5 (CU18W-CU22W)";
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

    generarClasesCU18W(subPkg);
    generarClasesCU19W(subPkg);
    generarClasesCU20W(subPkg);
    generarClasesCU21W(subPkg);
    generarClasesCU22W(subPkg);

    Repository.RefreshModelView(subPkg.PackageID);
    Session.Output("================================================================================");
    Session.Output(" [OK] Se generaron exitosamente los 5 diagramas de análisis de clases (CU18W a CU22W).");
    Session.Output(" Paquete: " + subPkg.Name);
    Session.Output("================================================================================");
}

Main();
