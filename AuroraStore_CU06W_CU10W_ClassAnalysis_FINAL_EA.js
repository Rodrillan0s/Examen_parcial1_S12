/*
 * =================================================================================================
 * SCRIPT MAESTRO DE AUTOMATIZACIÓN DE DIAGRAMAS DE ANÁLISIS DE CLASES UML 2.5 (ICONIX VOPC) PARA SPARX EA
 * =================================================================================================
 * Proyecto: AuroraStore SaaS
 * Lote 2: CU06W a CU10W
 *   - cd CU06W - Gestionar suscripciones empresariales
 *   - cd CU07W - Consultar plan y límites de suscripción
 *   - cd CU08W - Gestionar respaldos y restauraciones
 *   - cd CU09W - Gestionar asignaciones de empleados a sucursales
 *   - cd CU10W - Consultar catálogo (Web y Móvil)
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
// 1. CU06W: Gestionar suscripciones empresariales
// =================================================================================================
function generarCU06W(pkg) {
    Session.Output(" -> Construyendo: cd CU06W - Gestionar suscripciones empresariales");
    var diag = pkg.Diagrams.AddNew("cd CU06W - Gestionar suscripciones empresariales", "Logical");
    configurarDiagramaTablasUML(diag);

    var actor = agregarActor(pkg, diag, "Administrador", 40, 240, 80, 100);

    var b1 = agregarClaseTablaUML(pkg, diag, "ListaSuscripcionesView", "boundary",
        [
            { nombre: "id_empresa_activa", tipo: "int", vis: "Private" },
            { nombre: "historial_suscripciones", tipo: "List<SuscripcionDTO>", vis: "Private" },
            { nombre: "suscripcion_vigente", tipo: "SuscripcionDTO", vis: "Private" },
            { nombre: "cargando", tipo: "boolean", vis: "Private" }
        ],
        [
            { nombre: "ngOnInit", retorno: "void" },
            { nombre: "cargarHistorial", retorno: "void" },
            { nombre: "abrirModalAsignar", retorno: "void" },
            { nombre: "abrirModalCancelar", retorno: "void", parametros: [{ nombre: "id_sub", tipo: "int" }] }
        ],
        180, 40, 240, 150
    );

    var b2 = agregarClaseTablaUML(pkg, diag, "AsignacionSuscripcionModal", "boundary",
        [
            { nombre: "visible", tipo: "boolean", vis: "Private" },
            { nombre: "planes_disponibles", tipo: "List<PlanDTO>", vis: "Private" },
            { nombre: "suscripcionForm", tipo: "FormGroup", vis: "Private" },
            { nombre: "codigo_plan_sel", tipo: "string", vis: "Private" }
        ],
        [
            { nombre: "abrir", retorno: "void" },
            { nombre: "cerrar", retorno: "void" },
            { nombre: "calcularFechasVigencia", retorno: "void" },
            { nombre: "onSubmit", retorno: "void" }
        ],
        180, 220, 240, 160
    );

    var b3 = agregarClaseTablaUML(pkg, diag, "CancelarSuscripcionModal", "boundary",
        [
            { nombre: "visible", tipo: "boolean", vis: "Private" },
            { nombre: "id_suscripcion", tipo: "int", vis: "Private" },
            { nombre: "motivo_cancelacion", tipo: "string", vis: "Private" }
        ],
        [
            { nombre: "abrir", retorno: "void", parametros: [{ nombre: "id", tipo: "int" }] },
            { nombre: "confirmarCancelacion", retorno: "void" },
            { nombre: "cancelar", retorno: "void" }
        ],
        180, 410, 240, 140
    );

    var b4 = agregarClaseTablaUML(pkg, diag, "ErrorDialog", "boundary",
        [
            { nombre: "visible", tipo: "boolean", vis: "Private" },
            { nombre: "mensaje_error", tipo: "string", vis: "Private" }
        ],
        [
            { nombre: "mostrar", retorno: "void", parametros: [{ nombre: "err", tipo: "string" }] },
            { nombre: "cerrar", retorno: "void" }
        ],
        180, 580, 240, 110
    );

    // Col 3: Route Controller
    var cRoutes = agregarClaseTablaUML(pkg, diag, "saas_routes (RouteController)", "control",
        [
            { nombre: "router", tipo: "APIRouter", vis: "Private" },
            { nombre: "prefix", tipo: "string = '/api/v1/saas'", vis: "Private" }
        ],
        [
            { nombre: "listar_suscripciones", retorno: "Response", parametros: [{ nombre: "id_empresa", tipo: "int" }] },
            { nombre: "asignar_suscripcion", retorno: "Response", parametros: [{ nombre: "id_empresa", tipo: "int" }, { nombre: "dto", tipo: "AsignarSuscripcionDTO" }] },
            { nombre: "cancelar_suscripcion", retorno: "Response", parametros: [{ nombre: "id_empresa", tipo: "int" }, { nombre: "id_sub", tipo: "int" }] }
        ],
        470, 200, 280, 180
    );

    // Col 4: Domain Service
    var cServices = agregarClaseTablaUML(pkg, diag, "saas_services (DomainService)", "control",
        [
            { nombre: "db", tipo: "PostgreSQL", vis: "Private" },
            { nombre: "audit", tipo: "BitacoraService", vis: "Private" }
        ],
        [
            { nombre: "consultar_suscripciones", retorno: "List<SuscripcionDTO>", parametros: [{ nombre: "id_empresa", tipo: "int" }] },
            { nombre: "asignar_suscripcion", retorno: "dict", parametros: [{ nombre: "id_empresa", tipo: "int" }, { nombre: "datos", tipo: "dict" }] },
            { nombre: "cancelar_suscripcion", retorno: "dict", parametros: [{ nombre: "id_empresa", tipo: "int" }, { nombre: "id_sub", tipo: "int" }] },
            { nombre: "validar_empresa_activa", retorno: "boolean", parametros: [{ nombre: "id_empresa", tipo: "int" }] }
        ],
        790, 200, 280, 190
    );

    // Col 5 & 6: Entities
    var eEmpresa = agregarClaseTablaUML(pkg, diag, "empresa", "entity",
        [
            { nombre: "id_empresa [PK]", tipo: "int", vis: "Public" },
            { nombre: "nombre", tipo: "string", vis: "Public" },
            { nombre: "nit", tipo: "string", vis: "Public" },
            { nombre: "estado", tipo: "string", vis: "Public" }
        ],
        [
            { nombre: "findById", retorno: "empresa", parametros: [{ nombre: "id", tipo: "int" }] }
        ],
        1110, 40, 220, 130
    );

    var ePlan = agregarClaseTablaUML(pkg, diag, "t_plan", "entity",
        [
            { nombre: "codigo [PK]", tipo: "string", vis: "Public" },
            { nombre: "nombre", tipo: "string", vis: "Public" },
            { nombre: "max_sucursales", tipo: "int", vis: "Public" },
            { nombre: "precio_mensual", tipo: "decimal", vis: "Public" }
        ],
        [
            { nombre: "findByCodigo", retorno: "t_plan", parametros: [{ nombre: "codigo", tipo: "string" }] }
        ],
        1110, 200, 220, 140
    );

    var eSuscripcion = agregarClaseTablaUML(pkg, diag, "t_suscripcion", "entity",
        [
            { nombre: "id_suscripcion [PK]", tipo: "int", vis: "Public" },
            { nombre: "id_empresa [FK]", tipo: "int", vis: "Public" },
            { nombre: "codigo_plan [FK]", tipo: "string", vis: "Public" },
            { nombre: "fecha_inicio", tipo: "date", vis: "Public" },
            { nombre: "fecha_fin", tipo: "date", vis: "Public" },
            { nombre: "estado", tipo: "string", vis: "Public" }
        ],
        [
            { nombre: "insert", retorno: "int", parametros: [{ nombre: "datos", tipo: "dict" }] },
            { nombre: "updateEstado", retorno: "void", parametros: [{ nombre: "id", tipo: "int" }, { nombre: "estado", tipo: "string" }] }
        ],
        1110, 370, 220, 160
    );

    var eBitacora = agregarClaseTablaUML(pkg, diag, "t_bitacora", "entity",
        [
            { nombre: "id_bitacora [PK]", tipo: "int", vis: "Public" },
            { nombre: "modulo", tipo: "string", vis: "Public" },
            { nombre: "accion", tipo: "string", vis: "Public" },
            { nombre: "fecha", tipo: "datetime", vis: "Public" }
        ],
        [
            { nombre: "registrar", retorno: "void", parametros: [{ nombre: "evento", tipo: "dict" }] }
        ],
        1370, 250, 220, 130
    );

    // Conexiones
    conectarElementos(actor, b1, "Association", "", "");
    conectarElementos(actor, b2, "Association", "", "");
    conectarElementos(actor, b3, "Association", "", "");

    conectarElementos(b1, cRoutes, "Dependency", "consume", "«use»");
    conectarElementos(b2, cRoutes, "Dependency", "consume", "«use»");
    conectarElementos(b3, cRoutes, "Dependency", "consume", "«use»");
    conectarElementos(cRoutes, b4, "Dependency", "notifica", "«use»");

    conectarElementos(cRoutes, cServices, "Dependency", "delega", "«use»");

    conectarElementos(cServices, eEmpresa, "Dependency", "consulta", "«use»");
    conectarElementos(cServices, ePlan, "Dependency", "consulta", "«use»");
    conectarElementos(cServices, eSuscripcion, "Dependency", "persiste", "«use»");
    conectarElementos(cServices, eBitacora, "Dependency", "audita", "«use»");

    conectarElementos(eEmpresa, eSuscripcion, "Association", "posee", "", "1", "0..*");
    conectarElementos(ePlan, eSuscripcion, "Association", "tipifica", "", "1", "0..*");

    diag.Update();
    Repository.ReloadDiagram(diag.DiagramID);
}

// =================================================================================================
// 2. CU07W: Consultar plan y límites de suscripción
// =================================================================================================
function generarCU07W(pkg) {
    Session.Output(" -> Construyendo: cd CU07W - Consultar plan y límites de suscripción");
    var diag = pkg.Diagrams.AddNew("cd CU07W - Consultar plan y límites de suscripción", "Logical");
    configurarDiagramaTablasUML(diag);

    var actor = agregarActor(pkg, diag, "AdminTienda", 40, 220, 80, 100);

    var b1 = agregarClaseTablaUML(pkg, diag, "AjustesPlanView", "boundary",
        [
            { nombre: "id_empresa", tipo: "int", vis: "Private" },
            { nombre: "plan_actual", tipo: "PlanDTO", vis: "Private" },
            { nombre: "suscripcion_activa", tipo: "SuscripcionDTO", vis: "Private" },
            { nombre: "dias_restantes", tipo: "int", vis: "Private" }
        ],
        [
            { nombre: "ngOnInit", retorno: "void" },
            { nombre: "consultarPlanYConsumo", retorno: "void" },
            { nombre: "abrirModalDetalleLimites", retorno: "void" }
        ],
        180, 60, 240, 160
    );

    var b2 = agregarClaseTablaUML(pkg, diag, "DetalleLimitesModal", "boundary",
        [
            { nombre: "visible", tipo: "boolean", vis: "Private" },
            { nombre: "max_sucursales", tipo: "int", vis: "Private" },
            { nombre: "sucursales_activas", tipo: "int", vis: "Private" }
        ],
        [
            { nombre: "abrir", retorno: "void" },
            { nombre: "cerrar", retorno: "void" }
        ],
        180, 260, 240, 130
    );

    var b3 = agregarClaseTablaUML(pkg, diag, "ErrorDialog", "boundary",
        [
            { nombre: "visible", tipo: "boolean", vis: "Private" },
            { nombre: "mensaje", tipo: "string", vis: "Private" }
        ],
        [
            { nombre: "mostrarAlertaSinPlan", retorno: "void" },
            { nombre: "cerrar", retorno: "void" }
        ],
        180, 420, 240, 100
    );

    // Col 3: Route Controller
    var cRoutes = agregarClaseTablaUML(pkg, diag, "saas_routes (RouteController)", "control",
        [
            { nombre: "router", tipo: "APIRouter", vis: "Private" },
            { nombre: "prefix", tipo: "string = '/api/v1/saas'", vis: "Private" }
        ],
        [
            { nombre: "consultar_mi_plan", retorno: "Response", parametros: [{ nombre: "id_empresa", tipo: "int" }] },
            { nombre: "verificar_limite_sucursales", retorno: "Response", parametros: [{ nombre: "id_empresa", tipo: "int" }] }
        ],
        470, 200, 280, 160
    );

    // Col 4: Domain Service
    var cServices = agregarClaseTablaUML(pkg, diag, "saas_services (DomainService)", "control",
        [
            { nombre: "db", tipo: "PostgreSQL", vis: "Private" }
        ],
        [
            { nombre: "consultar_plan_y_limites", retorno: "ResumenPlanDTO", parametros: [{ nombre: "id_empresa", tipo: "int" }] },
            { nombre: "calcular_consumo_recursos", retorno: "dict", parametros: [{ nombre: "id_empresa", tipo: "int" }] },
            { nombre: "calcular_dias_restantes", retorno: "int", parametros: [{ nombre: "fecha_fin", tipo: "date" }] }
        ],
        790, 200, 280, 160
    );

    // Col 5 & 6: Entities
    var eEmpresa = agregarClaseTablaUML(pkg, diag, "empresa", "entity",
        [
            { nombre: "id_empresa [PK]", tipo: "int", vis: "Public" },
            { nombre: "nombre", tipo: "string", vis: "Public" }
        ],
        [
            { nombre: "findById", retorno: "empresa", parametros: [{ nombre: "id", tipo: "int" }] }
        ],
        1110, 40, 220, 110
    );

    var eSuscripcion = agregarClaseTablaUML(pkg, diag, "t_suscripcion", "entity",
        [
            { nombre: "id_suscripcion [PK]", tipo: "int", vis: "Public" },
            { nombre: "codigo_plan [FK]", tipo: "string", vis: "Public" },
            { nombre: "fecha_fin", tipo: "date", vis: "Public" },
            { nombre: "estado", tipo: "string", vis: "Public" }
        ],
        [
            { nombre: "findActivaByEmpresa", retorno: "t_suscripcion", parametros: [{ nombre: "id_empresa", tipo: "int" }] }
        ],
        1110, 180, 220, 140
    );

    var ePlan = agregarClaseTablaUML(pkg, diag, "t_plan", "entity",
        [
            { nombre: "codigo [PK]", tipo: "string", vis: "Public" },
            { nombre: "nombre", tipo: "string", vis: "Public" },
            { nombre: "max_sucursales", tipo: "int", vis: "Public" }
        ],
        [
            { nombre: "findByCodigo", retorno: "t_plan", parametros: [{ nombre: "codigo", tipo: "string" }] }
        ],
        1110, 350, 220, 130
    );

    var eSucursal = agregarClaseTablaUML(pkg, diag, "t_sucursal", "entity",
        [
            { nombre: "id_sucursal [PK]", tipo: "int", vis: "Public" },
            { nombre: "id_empresa [FK]", tipo: "int", vis: "Public" },
            { nombre: "nombre", tipo: "string", vis: "Public" },
            { nombre: "activo", tipo: "boolean", vis: "Public" }
        ],
        [
            { nombre: "countActivasByEmpresa", retorno: "int", parametros: [{ nombre: "id_empresa", tipo: "int" }] }
        ],
        1370, 200, 220, 130
    );

    // Conexiones
    conectarElementos(actor, b1, "Association", "", "");
    conectarElementos(b1, b2, "Dependency", "abre", "«use»");
    conectarElementos(b1, cRoutes, "Dependency", "consume", "«use»");
    conectarElementos(cRoutes, b3, "Dependency", "notifica", "«use»");

    conectarElementos(cRoutes, cServices, "Dependency", "delega", "«use»");

    conectarElementos(cServices, eEmpresa, "Dependency", "consulta", "«use»");
    conectarElementos(cServices, eSuscripcion, "Dependency", "consulta", "«use»");
    conectarElementos(cServices, ePlan, "Dependency", "consulta", "«use»");
    conectarElementos(cServices, eSucursal, "Dependency", "cuenta", "«use»");

    conectarElementos(eEmpresa, eSuscripcion, "Association", "tiene", "", "1", "0..*");
    conectarElementos(ePlan, eSuscripcion, "Association", "aplica_a", "", "1", "0..*");
    conectarElementos(eEmpresa, eSucursal, "Association", "opera", "", "1", "0..*");

    diag.Update();
    Repository.ReloadDiagram(diag.DiagramID);
}

// =================================================================================================
// 3. CU08W: Gestionar respaldos y restauraciones
// =================================================================================================
function generarCU08W(pkg) {
    Session.Output(" -> Construyendo: cd CU08W - Gestionar respaldos y restauraciones");
    var diag = pkg.Diagrams.AddNew("cd CU08W - Gestionar respaldos y restauraciones", "Logical");
    configurarDiagramaTablasUML(diag);

    var actor = agregarActor(pkg, diag, "Administrador", 40, 230, 80, 100);

    var b1 = agregarClaseTablaUML(pkg, diag, "RespaldosView", "boundary",
        [
            { nombre: "lista_respaldos", tipo: "List<RespaldoDTO>", vis: "Private" },
            { nombre: "cargando", tipo: "boolean", vis: "Private" }
        ],
        [
            { nombre: "ngOnInit", retorno: "void" },
            { nombre: "cargarHistorial", retorno: "void" },
            { nombre: "abrirModalNuevoRespaldo", retorno: "void" },
            { nombre: "abrirModalRestaurar", retorno: "void", parametros: [{ nombre: "id", tipo: "int" }] }
        ],
        180, 40, 240, 150
    );

    var b2 = agregarClaseTablaUML(pkg, diag, "GenerarRespaldoModal", "boundary",
        [
            { nombre: "visible", tipo: "boolean", vis: "Private" },
            { nombre: "incluir_bitacora", tipo: "boolean", vis: "Private" },
            { nombre: "generando", tipo: "boolean", vis: "Private" }
        ],
        [
            { nombre: "abrir", retorno: "void" },
            { nombre: "confirmarGeneracion", retorno: "void" },
            { nombre: "cancelar", retorno: "void" }
        ],
        180, 220, 240, 130
    );

    var b3 = agregarClaseTablaUML(pkg, diag, "RestaurarModal", "boundary",
        [
            { nombre: "visible", tipo: "boolean", vis: "Private" },
            { nombre: "id_respaldo", tipo: "int", vis: "Private" },
            { nombre: "password_confirmacion", tipo: "string", vis: "Private" }
        ],
        [
            { nombre: "abrir", retorno: "void", parametros: [{ nombre: "id", tipo: "int" }] },
            { nombre: "confirmarRestauracion", retorno: "void" },
            { nombre: "cancelar", retorno: "void" }
        ],
        180, 380, 240, 130
    );

    var b4 = agregarClaseTablaUML(pkg, diag, "ErrorDialog", "boundary",
        [
            { nombre: "visible", tipo: "boolean", vis: "Private" },
            { nombre: "mensaje", tipo: "string", vis: "Private" }
        ],
        [
            { nombre: "mostrar", retorno: "void", parametros: [{ nombre: "msg", tipo: "string" }] },
            { nombre: "cerrar", retorno: "void" }
        ],
        180, 540, 240, 100
    );

    // Col 3: Route Controller
    var cRoutes = agregarClaseTablaUML(pkg, diag, "backup_routes (RouteController)", "control",
        [
            { nombre: "router", tipo: "APIRouter", vis: "Private" },
            { nombre: "prefix", tipo: "string = '/api/v1/admin/respaldos'", vis: "Private" }
        ],
        [
            { nombre: "listar_respaldos", retorno: "Response" },
            { nombre: "generar_respaldo", retorno: "Response" },
            { nombre: "restaurar_respaldo", retorno: "Response", parametros: [{ nombre: "id", tipo: "int" }] }
        ],
        470, 200, 280, 170
    );

    // Col 4: Domain Service
    var cServices = agregarClaseTablaUML(pkg, diag, "backup_services (DomainService)", "control",
        [
            { nombre: "db", tipo: "PostgreSQL", vis: "Private" },
            { nombre: "storage_path", tipo: "string", vis: "Private" },
            { nombre: "audit", tipo: "BitacoraService", vis: "Private" }
        ],
        [
            { nombre: "listar_respaldos_service", retorno: "List<RespaldoDTO>" },
            { nombre: "ejecutar_respaldo", retorno: "RespaldoInfo" },
            { nombre: "ejecutar_restauracion", retorno: "boolean", parametros: [{ nombre: "id_respaldo", tipo: "int" }] },
            { nombre: "verificar_espacio_y_permisos", retorno: "boolean" }
        ],
        790, 200, 280, 180
    );

    // Col 5 & 6: Entities
    var eRespaldo = agregarClaseTablaUML(pkg, diag, "t_respaldo", "entity",
        [
            { nombre: "id_respaldo [PK]", tipo: "int", vis: "Public" },
            { nombre: "nombre_archivo", tipo: "string", vis: "Public" },
            { nombre: "tamanio_bytes", tipo: "bigint", vis: "Public" },
            { nombre: "checksum", tipo: "string", vis: "Public" }
        ],
        [
            { nombre: "insert", retorno: "int", parametros: [{ nombre: "datos", tipo: "dict" }] },
            { nombre: "findAllOrderByFechaDesc", retorno: "List<t_respaldo>" }
        ],
        1110, 80, 230, 150
    );

    var eUsuario = agregarClaseTablaUML(pkg, diag, "t_usuario", "entity",
        [
            { nombre: "id_usuario [PK]", tipo: "int", vis: "Public" },
            { nombre: "username", tipo: "string", vis: "Public" },
            { nombre: "password_hash", tipo: "string", vis: "Public" }
        ],
        [
            { nombre: "validarPassword", retorno: "boolean", parametros: [{ nombre: "id", tipo: "int" }, { nombre: "pass", tipo: "string" }] }
        ],
        1110, 260, 230, 130
    );

    var eBitacora = agregarClaseTablaUML(pkg, diag, "t_bitacora", "entity",
        [
            { nombre: "id_bitacora [PK]", tipo: "int", vis: "Public" },
            { nombre: "modulo", tipo: "string", vis: "Public" },
            { nombre: "accion", tipo: "string", vis: "Public" }
        ],
        [
            { nombre: "registrar", retorno: "void", parametros: [{ nombre: "evento", tipo: "dict" }] }
        ],
        1370, 200, 230, 120
    );

    // Conexiones
    conectarElementos(actor, b1, "Association", "", "");
    conectarElementos(actor, b2, "Association", "", "");
    conectarElementos(actor, b3, "Association", "", "");

    conectarElementos(b1, cRoutes, "Dependency", "consume", "«use»");
    conectarElementos(b2, cRoutes, "Dependency", "consume", "«use»");
    conectarElementos(b3, cRoutes, "Dependency", "consume", "«use»");
    conectarElementos(cRoutes, b4, "Dependency", "notifica", "«use»");

    conectarElementos(cRoutes, cServices, "Dependency", "delega", "«use»");

    conectarElementos(cServices, eRespaldo, "Dependency", "persiste", "«use»");
    conectarElementos(cServices, eUsuario, "Dependency", "autentica", "«use»");
    conectarElementos(cServices, eBitacora, "Dependency", "audita", "«use»");

    conectarElementos(eUsuario, eBitacora, "Association", "origina", "", "1", "0..*");

    diag.Update();
    Repository.ReloadDiagram(diag.DiagramID);
}

// =================================================================================================
// 4. CU09W: Gestionar asignaciones de empleados a sucursales
// =================================================================================================
function generarCU09W(pkg) {
    Session.Output(" -> Construyendo: cd CU09W - Gestionar asignaciones de empleados a sucursales");
    var diag = pkg.Diagrams.AddNew("cd CU09W - Gestionar asignaciones de empleados a sucursales", "Logical");
    configurarDiagramaTablasUML(diag);

    var actor = agregarActor(pkg, diag, "AdminTienda", 40, 240, 80, 100);

    var b1 = agregarClaseTablaUML(pkg, diag, "ListaAsignacionesView", "boundary",
        [
            { nombre: "id_empresa", tipo: "int", vis: "Private" },
            { nombre: "empleados_lista", tipo: "List<EmpleadoAsignacionDTO>", vis: "Private" },
            { nombre: "filtro_sucursal", tipo: "int", vis: "Private" }
        ],
        [
            { nombre: "ngOnInit", retorno: "void" },
            { nombre: "cargarEmpleados", retorno: "void" },
            { nombre: "abrirModalReasignar", retorno: "void", parametros: [{ nombre: "id", tipo: "int" }] }
        ],
        180, 40, 240, 150
    );

    var b2 = agregarClaseTablaUML(pkg, diag, "AsignarSucursalesModal", "boundary",
        [
            { nombre: "visible", tipo: "boolean", vis: "Private" },
            { nombre: "id_usuario", tipo: "int", vis: "Private" },
            { nombre: "sucursales_seleccionadas", tipo: "List<int>", vis: "Private" }
        ],
        [
            { nombre: "abrir", retorno: "void", parametros: [{ nombre: "id", tipo: "int" }] },
            { nombre: "toggleSucursal", retorno: "void", parametros: [{ nombre: "id_suc", tipo: "int" }] },
            { nombre: "onSubmit", retorno: "void" }
        ],
        180, 220, 240, 150
    );

    var b3 = agregarClaseTablaUML(pkg, diag, "SucursalPrincipalModal", "boundary",
        [
            { nombre: "visible", tipo: "boolean", vis: "Private" },
            { nombre: "id_usuario", tipo: "int", vis: "Private" },
            { nombre: "id_sucursal_seleccionada", tipo: "int", vis: "Private" }
        ],
        [
            { nombre: "abrir", retorno: "void", parametros: [{ nombre: "id", tipo: "int" }] },
            { nombre: "guardarPrincipal", retorno: "void" }
        ],
        180, 400, 240, 120
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
        180, 550, 240, 100
    );

    // Col 3: Route Controller
    var cRoutes = agregarClaseTablaUML(pkg, diag, "users_routes (RouteController)", "control",
        [
            { nombre: "router", tipo: "APIRouter", vis: "Private" },
            { nombre: "prefix", tipo: "string = '/api/v1/auth/usuarios'", vis: "Private" }
        ],
        [
            { nombre: "obtener_asignaciones", retorno: "Response", parametros: [{ nombre: "id_usuario", tipo: "int" }] },
            { nombre: "reasignar_sucursales", retorno: "Response", parametros: [{ nombre: "id_usuario", tipo: "int" }, { nombre: "dto", tipo: "ReasignarDTO" }] }
        ],
        470, 200, 280, 170
    );

    // Col 4: Domain Service
    var cServices = agregarClaseTablaUML(pkg, diag, "asignaciones_services (DomainService)", "control",
        [
            { nombre: "db", tipo: "PostgreSQL", vis: "Private" },
            { nombre: "audit", tipo: "BitacoraService", vis: "Private" }
        ],
        [
            { nombre: "consultar", retorno: "List<SucursalDTO>", parametros: [{ nombre: "id_usuario", tipo: "int" }] },
            { nombre: "asignar", retorno: "void", parametros: [{ nombre: "id_usuario", tipo: "int" }, { nombre: "ids", tipo: "List<int>" }] },
            { nombre: "validar_pertenencia_sucursales", retorno: "boolean", parametros: [{ nombre: "id_empresa", tipo: "int" }, { nombre: "ids", tipo: "List<int>" }] }
        ],
        790, 200, 280, 170
    );

    // Col 5 & 6: Entities
    var eEmpresa = agregarClaseTablaUML(pkg, diag, "empresa", "entity",
        [
            { nombre: "id_empresa [PK]", tipo: "int", vis: "Public" },
            { nombre: "nombre", tipo: "string", vis: "Public" }
        ],
        [
            { nombre: "findById", retorno: "empresa", parametros: [{ nombre: "id", tipo: "int" }] }
        ],
        1110, 40, 220, 110
    );

    var eSucursal = agregarClaseTablaUML(pkg, diag, "t_sucursal", "entity",
        [
            { nombre: "id_sucursal [PK]", tipo: "int", vis: "Public" },
            { nombre: "id_empresa [FK]", tipo: "int", vis: "Public" },
            { nombre: "nombre", tipo: "string", vis: "Public" }
        ],
        [
            { nombre: "filterByEmpresa", retorno: "List<t_sucursal>", parametros: [{ nombre: "id_empresa", tipo: "int" }] }
        ],
        1110, 180, 220, 130
    );

    var eUsuario = agregarClaseTablaUML(pkg, diag, "t_usuario", "entity",
        [
            { nombre: "id_usuario [PK]", tipo: "int", vis: "Public" },
            { nombre: "id_empresa [FK]", tipo: "int", vis: "Public" },
            { nombre: "nombre_completo", tipo: "string", vis: "Public" }
        ],
        [
            { nombre: "findById", retorno: "t_usuario", parametros: [{ nombre: "id", tipo: "int" }] }
        ],
        1110, 340, 220, 130
    );

    var eEmpleado = agregarClaseTablaUML(pkg, diag, "t_empleado", "entity",
        [
            { nombre: "id_empleado [PK]", tipo: "int", vis: "Public" },
            { nombre: "id_usuario [FK]", tipo: "int", vis: "Public" },
            { nombre: "id_sucursal_principal [FK]", tipo: "int", vis: "Public" }
        ],
        [
            { nombre: "updatePrincipal", retorno: "void", parametros: [{ nombre: "id_usuario", tipo: "int" }, { nombre: "id_suc", tipo: "int" }] }
        ],
        1370, 140, 220, 130
    );

    var eUsuarioSuc = agregarClaseTablaUML(pkg, diag, "t_usuario_sucursal", "entity",
        [
            { nombre: "id_usuario_sucursal [PK]", tipo: "int", vis: "Public" },
            { nombre: "id_usuario [FK]", tipo: "int", vis: "Public" },
            { nombre: "id_sucursal [FK]", tipo: "int", vis: "Public" }
        ],
        [
            { nombre: "bulkInsert", retorno: "void", parametros: [{ nombre: "id_usuario", tipo: "int" }, { nombre: "ids", tipo: "List<int>" }] }
        ],
        1370, 300, 220, 130
    );

    var eBitacora = agregarClaseTablaUML(pkg, diag, "t_bitacora", "entity",
        [
            { nombre: "id_bitacora [PK]", tipo: "int", vis: "Public" },
            { nombre: "modulo", tipo: "string", vis: "Public" },
            { nombre: "accion", tipo: "string", vis: "Public" }
        ],
        [
            { nombre: "registrar", retorno: "void", parametros: [{ nombre: "evento", tipo: "dict" }] }
        ],
        1370, 460, 220, 110
    );

    // Conexiones
    conectarElementos(actor, b1, "Association", "", "");
    conectarElementos(actor, b2, "Association", "", "");
    conectarElementos(actor, b3, "Association", "", "");

    conectarElementos(b1, cRoutes, "Dependency", "consume", "«use»");
    conectarElementos(b2, cRoutes, "Dependency", "consume", "«use»");
    conectarElementos(b3, cRoutes, "Dependency", "consume", "«use»");
    conectarElementos(cRoutes, b4, "Dependency", "notifica", "«use»");

    conectarElementos(cRoutes, cServices, "Dependency", "delega", "«use»");

    conectarElementos(cServices, eEmpresa, "Dependency", "valida", "«use»");
    conectarElementos(cServices, eSucursal, "Dependency", "consulta", "«use»");
    conectarElementos(cServices, eUsuario, "Dependency", "consulta", "«use»");
    conectarElementos(cServices, eEmpleado, "Dependency", "actualiza", "«use»");
    conectarElementos(cServices, eUsuarioSuc, "Dependency", "persiste", "«use»");
    conectarElementos(cServices, eBitacora, "Dependency", "audita", "«use»");

    conectarElementos(eEmpresa, eSucursal, "Association", "posee", "", "1", "0..*");
    conectarElementos(eEmpresa, eUsuario, "Association", "emplea", "", "1", "0..*");
    conectarElementos(eUsuario, eEmpleado, "Association", "perfil", "", "1", "0..1");
    conectarElementos(eUsuario, eUsuarioSuc, "Association", "asignado_a", "", "1", "0..*");
    conectarElementos(eSucursal, eUsuarioSuc, "Association", "incluye", "", "1", "0..*");

    diag.Update();
    Repository.ReloadDiagram(diag.DiagramID);
}

// =================================================================================================
// 5. CU10W: Consultar catálogo (Web y Móvil con Soporte Offline)
// =================================================================================================
function generarCU10W(pkg) {
    Session.Output(" -> Construyendo: cd CU10W - Consultar catálogo");
    var diag = pkg.Diagrams.AddNew("cd CU10W - Consultar catálogo", "Logical");
    configurarDiagramaTablasUML(diag);

    var actor = agregarActor(pkg, diag, "Usuario / Cliente", 40, 240, 90, 100);

    var b1 = agregarClaseTablaUML(pkg, diag, "CatalogoPublicoView", "boundary",
        [
            { nombre: "id_empresa", tipo: "int", vis: "Private" },
            { nombre: "productos_lista", tipo: "List<ProductoCardDTO>", vis: "Private" },
            { nombre: "modo_offline_activo", tipo: "boolean", vis: "Private" }
        ],
        [
            { nombre: "ngOnInit", retorno: "void" },
            { nombre: "cargarCatalogo", retorno: "void" },
            { nombre: "onFiltrosCambiados", retorno: "void", parametros: [{ nombre: "f", tipo: "FiltroDTO" }] },
            { nombre: "seleccionarProducto", retorno: "void", parametros: [{ nombre: "id", tipo: "int" }] }
        ],
        180, 40, 240, 160
    );

    var b2 = agregarClaseTablaUML(pkg, diag, "FiltroCatalogoSidebar", "boundary",
        [
            { nombre: "categorias_disponibles", tipo: "List<CategoriaDTO>", vis: "Private" },
            { nombre: "tallas_disponibles", tipo: "List<TallaDTO>", vis: "Private" }
        ],
        [
            { nombre: "aplicarFiltros", retorno: "void" },
            { nombre: "limpiarFiltros", retorno: "void" }
        ],
        180, 230, 240, 130
    );

    var b3 = agregarClaseTablaUML(pkg, diag, "FichaDetalleProductoModal", "boundary",
        [
            { nombre: "visible", tipo: "boolean", vis: "Private" },
            { nombre: "producto_detalle", tipo: "ProductoDetalleDTO", vis: "Private" },
            { nombre: "talla_seleccionada", tipo: "int", vis: "Private" }
        ],
        [
            { nombre: "abrir", retorno: "void", parametros: [{ nombre: "id", tipo: "int" }] },
            { nombre: "seleccionarVariante", retorno: "void", parametros: [{ nombre: "talla", tipo: "int" }] },
            { nombre: "cerrar", retorno: "void" }
        ],
        180, 390, 240, 150
    );

    var b4 = agregarClaseTablaUML(pkg, diag, "OfflineStatusBar", "boundary",
        [
            { nombre: "is_online", tipo: "boolean", vis: "Private" },
            { nombre: "elementos_en_cache", tipo: "int", vis: "Private" }
        ],
        [
            { nombre: "mostrarEstadoConexion", retorno: "void" },
            { nombre: "dispararDescargaCache", retorno: "void" }
        ],
        180, 560, 240, 110
    );

    // Col 3: Route Controller
    var cRoutes = agregarClaseTablaUML(pkg, diag, "catalogo_routes (RouteController)", "control",
        [
            { nombre: "router", tipo: "APIRouter", vis: "Private" },
            { nombre: "prefix", tipo: "string = '/api/catalogo'", vis: "Private" }
        ],
        [
            { nombre: "listar_catalogo", retorno: "Response", parametros: [{ nombre: "id_empresa", tipo: "int" }] },
            { nombre: "obtener_detalle", retorno: "Response", parametros: [{ nombre: "id_producto", tipo: "int" }] },
            { nombre: "consultar_filtros", retorno: "Response", parametros: [{ nombre: "id_empresa", tipo: "int" }] }
        ],
        470, 200, 280, 160
    );

    // Col 4: Domain Service & Offline Storage
    var cServices = agregarClaseTablaUML(pkg, diag, "catalogo_services (DomainService)", "control",
        [
            { nombre: "db", tipo: "PostgreSQL", vis: "Private" },
            { nombre: "cache", tipo: "CacheService", vis: "Private" }
        ],
        [
            { nombre: "filtrar_catalogo", retorno: "CatalogoPageDTO", parametros: [{ nombre: "id_empresa", tipo: "int" }, { nombre: "filtros", tipo: "dict" }] },
            { nombre: "obtener_ficha_tecnica", retorno: "ProductoDetalleDTO", parametros: [{ nombre: "id_producto", tipo: "int" }] }
        ],
        790, 100, 280, 160
    );

    var cOffline = agregarClaseTablaUML(pkg, diag, "offline_cache_manager (ClientStorage)", "control",
        [
            { nombre: "db_local", tipo: "IndexedDB / SQLite", vis: "Private" },
            { nombre: "sync_coordinator", tipo: "SyncCoordinator", vis: "Private" }
        ],
        [
            { nombre: "consultarCatalogoLocal", retorno: "List<ProductoDTO>", parametros: [{ nombre: "filtros", tipo: "dict" }] },
            { nombre: "guardarCatalogoEnCache", retorno: "void", parametros: [{ nombre: "items", tipo: "List<dict>" }] }
        ],
        790, 300, 280, 150
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
            { nombre: "findById", retorno: "t_producto", parametros: [{ nombre: "id", tipo: "int" }] }
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
            { nombre: "sku", tipo: "string", vis: "Public" }
        ],
        [
            { nombre: "findByProducto", retorno: "List<t_producto_talla_color>", parametros: [{ nombre: "id", tipo: "int" }] }
        ],
        1110, 370, 230, 140
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
        1370, 220, 220, 100
    );

    var eCacheLocal = agregarClaseTablaUML(pkg, diag, "cache_local (IndexedDB / SQLite)", "entity",
        [
            { nombre: "id [PK]", tipo: "int", vis: "Public" },
            { nombre: "tenant_id", tipo: "int", vis: "Public" },
            { nombre: "payload_json", tipo: "text", vis: "Public" }
        ],
        [
            { nombre: "getProductsOffline", retorno: "List<dict>" },
            { nombre: "saveProductsBatch", retorno: "void", parametros: [{ nombre: "items", tipo: "List<dict>" }] }
        ],
        1370, 350, 220, 130
    );

    // Conexiones
    conectarElementos(actor, b1, "Association", "", "");
    conectarElementos(b1, b2, "Dependency", "integra", "«use»");
    conectarElementos(b1, b3, "Dependency", "despliega", "«use»");
    conectarElementos(b1, b4, "Dependency", "monitorea", "«use»");

    conectarElementos(b1, cRoutes, "Dependency", "consume_online", "«use»");
    conectarElementos(b1, cOffline, "Dependency", "fallback_offline", "«use»");

    conectarElementos(cRoutes, cServices, "Dependency", "delega", "«use»");

    conectarElementos(cServices, eProducto, "Dependency", "consulta", "«use»");
    conectarElementos(cServices, eCategoria, "Dependency", "consulta", "«use»");
    conectarElementos(cServices, eVariante, "Dependency", "consulta", "«use»");

    conectarElementos(cOffline, eCacheLocal, "Dependency", "lee_y_escribe", "«use»");

    conectarElementos(eCategoria, eProducto, "Association", "clasifica", "", "1", "0..*");
    conectarElementos(eProducto, eVariante, "Association", "contiene", "", "1", "1..*");
    conectarElementos(eTalla, eVariante, "Association", "dimensiona", "", "1", "0..*");
    conectarElementos(eColor, eVariante, "Association", "matiza", "", "1", "0..*");

    diag.Update();
    Repository.ReloadDiagram(diag.DiagramID);
}

// =================================================================================================
// FUNCIÓN PRINCIPAL DE EJECUCIÓN
// =================================================================================================
function main() {
    Session.Output("======================================================================");
    Session.Output("INICIANDO GENERACIÓN DE DIAGRAMAS DE ANÁLISIS DE CLASES (CU06W - CU10W)");
    Session.Output("Formato: Tablas UML Rectangulares (Boundary -> Controllers -> Entity)");
    Session.Output("======================================================================");

    var pkg = Repository.GetTreeSelectedPackage();
    if (!pkg) {
        Session.Prompt("Por favor, seleccione un Paquete en el Project Browser antes de ejecutar.", 0);
        return;
    }

    Session.Output("Paquete Destino: " + pkg.Name);

    try {
        generarCU06W(pkg);
        generarCU07W(pkg);
        generarCU08W(pkg);
        generarCU09W(pkg);
        generarCU10W(pkg);

        Session.Output("======================================================================");
        Session.Output("PROCESO COMPLETADO EXITOSAMENTE");
        Session.Output("Diagramas de análisis de clases creados: 5");
        Session.Output("======================================================================");
        Session.Prompt("Diagramas de clases (CU06W a CU10W) generados como tablas UML con éxito.", 0);
    } catch (e) {
        Session.Output("[ERROR FATAL] " + e.message);
        Session.Prompt("Error al generar diagramas: " + e.message, 0);
    }
}

main();
