/*
 * =================================================================================================
 * SCRIPT MAESTRO DE AUTOMATIZACIÓN DE DIAGRAMAS DE ANÁLISIS DE CLASES UML 2.5 (ICONIX VOPC) PARA SPARX EA
 * =================================================================================================
 * Proyecto: AuroraStore SaaS
 * Lote 1: CU01W a CU05W
 *   - cd CU01W - Gestionar usuarios y roles
 *   - cd CU02W - Gestionar empresas SaaS
 *   - cd CU03W - Gestionar sucursales y ciudades
 *   - cd CU04W - Gestionar productos
 *   - cd CU05W - Gestionar planes de suscripción
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
    // Configuración formal para forzar renderizado como TABLAS UML (rectángulos) y no círculos de análisis
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
// 1. CU01W: Gestionar usuarios y roles
// =================================================================================================
function generarCU01W(pkg) {
    Session.Output(" -> Construyendo: cd CU01W - Gestionar usuarios y roles");
    var diag = pkg.Diagrams.AddNew("cd CU01W - Gestionar usuarios y roles", "Logical");
    configurarDiagramaTablasUML(diag);

    // Col 1: Actor
    var actor = agregarActor(pkg, diag, "Administrador", 40, 240, 80, 100);

    // Col 2: Boundaries (Vistas y Modales)
    var b1 = agregarClaseTablaUML(pkg, diag, "ListaUsuariosView", "boundary",
        [
            { nombre: "id_empresa_activa", tipo: "int", vis: "Private" },
            { nombre: "filtro_busqueda", tipo: "string", vis: "Private" },
            { nombre: "filtro_rol", tipo: "string", vis: "Private" },
            { nombre: "usuarios_lista", tipo: "List<UsuarioDTO>", vis: "Private" },
            { nombre: "cargando", tipo: "boolean", vis: "Private" }
        ],
        [
            { nombre: "ngOnInit", retorno: "void" },
            { nombre: "cargarUsuarios", retorno: "void" },
            { nombre: "onBuscar", retorno: "void", parametros: [{ nombre: "criterio", tipo: "string" }] },
            { nombre: "abrirModalNuevo", retorno: "void" },
            { nombre: "abrirModalEditar", retorno: "void", parametros: [{ nombre: "id", tipo: "int" }] }
        ],
        180, 40, 240, 160
    );

    var b2 = agregarClaseTablaUML(pkg, diag, "FormularioUsuarioModal", "boundary",
        [
            { nombre: "visible", tipo: "boolean", vis: "Private" },
            { nombre: "modo_edicion", tipo: "boolean", vis: "Private" },
            { nombre: "id_usuario", tipo: "int", vis: "Private" },
            { nombre: "roles_disponibles", tipo: "List<RolDTO>", vis: "Private" },
            { nombre: "sucursales_disponibles", tipo: "List<SucursalDTO>", vis: "Private" },
            { nombre: "usuarioForm", tipo: "FormGroup", vis: "Private" }
        ],
        [
            { nombre: "abrir", retorno: "void", parametros: [{ nombre: "id", tipo: "int" }] },
            { nombre: "cerrar", retorno: "void" },
            { nombre: "validarFormulario", retorno: "boolean" },
            { nombre: "onSubmit", retorno: "void" }
        ],
        180, 230, 240, 160
    );

    var b3 = agregarClaseTablaUML(pkg, diag, "EliminarUsuarioModal", "boundary",
        [
            { nombre: "visible", tipo: "boolean", vis: "Private" },
            { nombre: "id_usuario", tipo: "int", vis: "Private" },
            { nombre: "motivo_desactivacion", tipo: "string", vis: "Private" }
        ],
        [
            { nombre: "abrir", retorno: "void", parametros: [{ nombre: "id", tipo: "int" }] },
            { nombre: "confirmarDesactivacion", retorno: "void" },
            { nombre: "cancelar", retorno: "void" }
        ],
        180, 420, 240, 130
    );

    var b4 = agregarClaseTablaUML(pkg, diag, "ErrorDialog", "boundary",
        [
            { nombre: "visible", tipo: "boolean", vis: "Private" },
            { nombre: "codigo_error", tipo: "string", vis: "Private" },
            { nombre: "mensaje", tipo: "string", vis: "Private" }
        ],
        [
            { nombre: "mostrar", retorno: "void", parametros: [{ nombre: "error", tipo: "ErrorDTO" }] },
            { nombre: "cerrar", retorno: "void" }
        ],
        180, 580, 240, 110
    );

    // Col 3: Main Route Controller (Coordinador Central)
    var cRoutes = agregarClaseTablaUML(pkg, diag, "users_routes (RouteController)", "control",
        [
            { nombre: "router", tipo: "APIRouter", vis: "Private" },
            { nombre: "prefix", tipo: "string = '/api/usuarios'", vis: "Private" }
        ],
        [
            { nombre: "listar_usuarios", retorno: "Response", parametros: [{ nombre: "id_empresa", tipo: "int" }, { nombre: "rol", tipo: "string" }] },
            { nombre: "crear_usuario", retorno: "Response", parametros: [{ nombre: "dto", tipo: "CrearUsuarioDTO" }] },
            { nombre: "actualizar_usuario", retorno: "Response", parametros: [{ nombre: "id", tipo: "int" }, { nombre: "dto", tipo: "UpdateUsuarioDTO" }] },
            { nombre: "desactivar_usuario", retorno: "Response", parametros: [{ nombre: "id", tipo: "int" }] }
        ],
        470, 200, 280, 210
    );

    // Col 4: Domain Services & Authorization
    var cServices = agregarClaseTablaUML(pkg, diag, "users_services (DomainService)", "control",
        [
            { nombre: "db", tipo: "PostgreSQL", vis: "Private" },
            { nombre: "pwd_context", tipo: "CryptContext", vis: "Private" }
        ],
        [
            { nombre: "registrar_usuario", retorno: "dict", parametros: [{ nombre: "dto", tipo: "CrearUsuarioDTO" }, { nombre: "id_empresa", tipo: "int" }] },
            { nombre: "modificar_usuario", retorno: "dict", parametros: [{ nombre: "id", tipo: "int" }, { nombre: "dto", tipo: "UpdateUsuarioDTO" }] },
            { nombre: "cambiar_estado_usuario", retorno: "dict", parametros: [{ nombre: "id", tipo: "int" }, { nombre: "activo", tipo: "boolean" }] },
            { nombre: "sincronizar_sucursales_empleado", retorno: "void", parametros: [{ nombre: "id", tipo: "int" }, { nombre: "sucursales", tipo: "List<int>" }] }
        ],
        790, 120, 280, 180
    );

    var cRbac = agregarClaseTablaUML(pkg, diag, "rbac_services (Authorization)", "control",
        [
            { nombre: "db", tipo: "PostgreSQL", vis: "Private" }
        ],
        [
            { nombre: "listar_roles_empresa", retorno: "List<RolDTO>", parametros: [{ nombre: "id_empresa", tipo: "int" }] },
            { nombre: "verificar_permiso", retorno: "boolean", parametros: [{ nombre: "id_usuario", tipo: "int" }, { nombre: "permiso", tipo: "string" }] },
            { nombre: "asignar_rol_usuario", retorno: "void", parametros: [{ nombre: "id_usuario", tipo: "int" }, { nombre: "id_rol", tipo: "int" }] }
        ],
        790, 330, 280, 160
    );

    // Col 5 & 6: Entities (Tablas PostgreSQL)
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

    var eUsuario = agregarClaseTablaUML(pkg, diag, "t_usuario", "entity",
        [
            { nombre: "id_usuario [PK]", tipo: "int", vis: "Public" },
            { nombre: "id_empresa [FK]", tipo: "int", vis: "Public" },
            { nombre: "id_rol [FK]", tipo: "int", vis: "Public" },
            { nombre: "username", tipo: "string", vis: "Public" },
            { nombre: "email", tipo: "string", vis: "Public" },
            { nombre: "activo", tipo: "boolean", vis: "Public" }
        ],
        [
            { nombre: "insert", retorno: "int", parametros: [{ nombre: "u", tipo: "dict" }] },
            { nombre: "update", retorno: "void", parametros: [{ nombre: "id", tipo: "int" }, { nombre: "u", tipo: "dict" }] },
            { nombre: "filterByEmpresa", retorno: "List<t_usuario>", parametros: [{ nombre: "id_empresa", tipo: "int" }] }
        ],
        1110, 200, 220, 180
    );

    var eRol = agregarClaseTablaUML(pkg, diag, "t_rol", "entity",
        [
            { nombre: "id_rol [PK]", tipo: "int", vis: "Public" },
            { nombre: "nombre", tipo: "string", vis: "Public" },
            { nombre: "tipo_alcance", tipo: "string", vis: "Public" }
        ],
        [
            { nombre: "findAll", retorno: "List<t_rol>" },
            { nombre: "findById", retorno: "t_rol", parametros: [{ nombre: "id", tipo: "int" }] }
        ],
        1110, 410, 220, 130
    );

    var eUsuarioSuc = agregarClaseTablaUML(pkg, diag, "t_usuario_sucursal", "entity",
        [
            { nombre: "id_usuario_sucursal [PK]", tipo: "int", vis: "Public" },
            { nombre: "id_usuario [FK]", tipo: "int", vis: "Public" },
            { nombre: "id_sucursal [FK]", tipo: "int", vis: "Public" },
            { nombre: "asignado_en", tipo: "datetime", vis: "Public" }
        ],
        [
            { nombre: "deleteByUsuario", retorno: "void", parametros: [{ nombre: "id_usuario", tipo: "int" }] },
            { nombre: "bulkInsert", retorno: "void", parametros: [{ nombre: "id_usuario", tipo: "int" }, { nombre: "ids", tipo: "List<int>" }] }
        ],
        1370, 200, 220, 140
    );

    var eBitacora = agregarClaseTablaUML(pkg, diag, "t_bitacora", "entity",
        [
            { nombre: "id_bitacora [PK]", tipo: "int", vis: "Public" },
            { nombre: "id_usuario [FK]", tipo: "int", vis: "Public" },
            { nombre: "modulo", tipo: "string", vis: "Public" },
            { nombre: "accion", tipo: "string", vis: "Public" },
            { nombre: "fecha", tipo: "datetime", vis: "Public" }
        ],
        [
            { nombre: "registrar", retorno: "void", parametros: [{ nombre: "evento", tipo: "dict" }] }
        ],
        1370, 380, 220, 130
    );

    // Conexiones Formale UML
    conectarElementos(actor, b1, "Association", "", "");
    conectarElementos(actor, b2, "Association", "", "");
    conectarElementos(actor, b3, "Association", "", "");

    conectarElementos(b1, cRoutes, "Dependency", "consume", "«use»");
    conectarElementos(b2, cRoutes, "Dependency", "consume", "«use»");
    conectarElementos(b3, cRoutes, "Dependency", "consume", "«use»");
    conectarElementos(cRoutes, b4, "Dependency", "notifica", "«use»");

    conectarElementos(cRoutes, cServices, "Dependency", "delega", "«use»");
    conectarElementos(cRoutes, cRbac, "Dependency", "autoriza", "«use»");

    conectarElementos(cServices, eEmpresa, "Dependency", "valida", "«use»");
    conectarElementos(cServices, eUsuario, "Dependency", "persiste", "«use»");
    conectarElementos(cServices, eUsuarioSuc, "Dependency", "asigna", "«use»");
    conectarElementos(cServices, eBitacora, "Dependency", "audita", "«use»");
    conectarElementos(cRbac, eRol, "Dependency", "consulta", "«use»");

    // Relaciones entre Entidades
    conectarElementos(eEmpresa, eUsuario, "Association", "posee", "", "1", "0..*");
    conectarElementos(eRol, eUsuario, "Association", "clasifica", "", "1", "0..*");
    conectarElementos(eUsuario, eUsuarioSuc, "Association", "opera_en", "", "1", "0..*");
    conectarElementos(eUsuario, eBitacora, "Association", "registra", "", "1", "0..*");

    diag.Update();
    Repository.ReloadDiagram(diag.DiagramID);
}

// =================================================================================================
// 2. CU02W: Gestionar empresas SaaS
// =================================================================================================
function generarCU02W(pkg) {
    Session.Output(" -> Construyendo: cd CU02W - Gestionar empresas SaaS");
    var diag = pkg.Diagrams.AddNew("cd CU02W - Gestionar empresas SaaS", "Logical");
    configurarDiagramaTablasUML(diag);

    var actor = agregarActor(pkg, diag, "SuperAdministrador", 40, 240, 80, 100);

    var b1 = agregarClaseTablaUML(pkg, diag, "ListaEmpresasView", "boundary",
        [
            { nombre: "empresas_lista", tipo: "List<EmpresaDTO>", vis: "Private" },
            { nombre: "filtro_estado", tipo: "string", vis: "Private" },
            { nombre: "cargando", tipo: "boolean", vis: "Private" }
        ],
        [
            { nombre: "ngOnInit", retorno: "void" },
            { nombre: "cargarEmpresas", retorno: "void" },
            { nombre: "abrirModalNuevaEmpresa", retorno: "void" },
            { nombre: "abrirModalCambiarEstado", retorno: "void", parametros: [{ nombre: "id", tipo: "int" }] }
        ],
        180, 40, 240, 160
    );

    var b2 = agregarClaseTablaUML(pkg, diag, "FormularioEmpresaModal", "boundary",
        [
            { nombre: "visible", tipo: "boolean", vis: "Private" },
            { nombre: "planes_disponibles", tipo: "List<PlanDTO>", vis: "Private" },
            { nombre: "empresaForm", tipo: "FormGroup", vis: "Private" }
        ],
        [
            { nombre: "abrir", retorno: "void" },
            { nombre: "cerrar", retorno: "void" },
            { nombre: "onSubmit", retorno: "void" }
        ],
        180, 230, 240, 160
    );

    var b3 = agregarClaseTablaUML(pkg, diag, "EstadoEmpresaModal", "boundary",
        [
            { nombre: "visible", tipo: "boolean", vis: "Private" },
            { nombre: "id_empresa", tipo: "int", vis: "Private" },
            { nombre: "nuevo_estado", tipo: "string", vis: "Private" }
        ],
        [
            { nombre: "abrir", retorno: "void", parametros: [{ nombre: "id", tipo: "int" }] },
            { nombre: "confirmarCambio", retorno: "void" },
            { nombre: "cancelar", retorno: "void" }
        ],
        180, 420, 240, 130
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
        180, 580, 240, 110
    );

    // Col 3: Route Controller
    var cRoutes = agregarClaseTablaUML(pkg, diag, "tenant_routes (RouteController)", "control",
        [
            { nombre: "router", tipo: "APIRouter", vis: "Private" },
            { nombre: "prefix", tipo: "string = '/api/tenants'", vis: "Private" }
        ],
        [
            { nombre: "listar_tenants", retorno: "Response" },
            { nombre: "crear_tenant", retorno: "Response", parametros: [{ nombre: "dto", tipo: "CrearTenantDTO" }] },
            { nombre: "cambiar_estado", retorno: "Response", parametros: [{ nombre: "id", tipo: "int" }, { nombre: "estado", tipo: "string" }] }
        ],
        470, 220, 280, 190
    );

    // Col 4: Domain Service
    var cServices = agregarClaseTablaUML(pkg, diag, "tenant_services (DomainService)", "control",
        [
            { nombre: "db", tipo: "PostgreSQL", vis: "Private" },
            { nombre: "audit", tipo: "BitacoraService", vis: "Private" }
        ],
        [
            { nombre: "registrar_tenant_y_admin", retorno: "dict", parametros: [{ nombre: "dto", tipo: "CrearTenantDTO" }] },
            { nombre: "actualizar_estado_tenant", retorno: "dict", parametros: [{ nombre: "id", tipo: "int" }, { nombre: "estado", tipo: "string" }] },
            { nombre: "asignar_plan_inicial", retorno: "void", parametros: [{ nombre: "id_empresa", tipo: "int" }, { nombre: "codigo_plan", tipo: "string" }] }
        ],
        790, 220, 280, 190
    );

    // Col 5 & 6: Entities
    var eEmpresa = agregarClaseTablaUML(pkg, diag, "empresa", "entity",
        [
            { nombre: "id_empresa [PK]", tipo: "int", vis: "Public" },
            { nombre: "nombre", tipo: "string", vis: "Public" },
            { nombre: "nit", tipo: "string", vis: "Public" },
            { nombre: "estado", tipo: "string", vis: "Public" },
            { nombre: "creado_en", tipo: "datetime", vis: "Public" }
        ],
        [
            { nombre: "insert", retorno: "int", parametros: [{ nombre: "e", tipo: "dict" }] },
            { nombre: "updateEstado", retorno: "void", parametros: [{ nombre: "id", tipo: "int" }, { nombre: "est", tipo: "string" }] },
            { nombre: "findAll", retorno: "List<empresa>" }
        ],
        1110, 60, 220, 160
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
            { nombre: "insert", retorno: "int", parametros: [{ nombre: "s", tipo: "dict" }] },
            { nombre: "findActivaByEmpresa", retorno: "t_suscripcion", parametros: [{ nombre: "id", tipo: "int" }] }
        ],
        1110, 250, 220, 160
    );

    var ePlan = agregarClaseTablaUML(pkg, diag, "t_plan", "entity",
        [
            { nombre: "codigo [PK]", tipo: "string", vis: "Public" },
            { nombre: "nombre", tipo: "string", vis: "Public" },
            { nombre: "max_sucursales", tipo: "int", vis: "Public" },
            { nombre: "precio_mensual", tipo: "decimal", vis: "Public" }
        ],
        [
            { nombre: "findByCodigo", retorno: "t_plan", parametros: [{ nombre: "cod", tipo: "string" }] }
        ],
        1110, 440, 220, 130
    );

    var eUsuario = agregarClaseTablaUML(pkg, diag, "t_usuario", "entity",
        [
            { nombre: "id_usuario [PK]", tipo: "int", vis: "Public" },
            { nombre: "id_empresa [FK]", tipo: "int", vis: "Public" },
            { nombre: "username", tipo: "string", vis: "Public" },
            { nombre: "email", tipo: "string", vis: "Public" }
        ],
        [
            { nombre: "insert", retorno: "int", parametros: [{ nombre: "u", tipo: "dict" }] }
        ],
        1370, 140, 220, 140
    );

    var eBitacora = agregarClaseTablaUML(pkg, diag, "t_bitacora", "entity",
        [
            { nombre: "id_bitacora [PK]", tipo: "int", vis: "Public" },
            { nombre: "modulo", tipo: "string", vis: "Public" },
            { nombre: "accion", tipo: "string", vis: "Public" },
            { nombre: "fecha", tipo: "datetime", vis: "Public" }
        ],
        [
            { nombre: "registrar", retorno: "void", parametros: [{ nombre: "ev", tipo: "dict" }] }
        ],
        1370, 320, 220, 120
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

    conectarElementos(cServices, eEmpresa, "Dependency", "persiste", "«use»");
    conectarElementos(cServices, eSuscripcion, "Dependency", "crea", "«use»");
    conectarElementos(cServices, ePlan, "Dependency", "consulta", "«use»");
    conectarElementos(cServices, eUsuario, "Dependency", "crea_admin", "«use»");
    conectarElementos(cServices, eBitacora, "Dependency", "audita", "«use»");

    conectarElementos(eEmpresa, eSuscripcion, "Association", "posee", "", "1", "1..*");
    conectarElementos(ePlan, eSuscripcion, "Association", "asigna", "", "1", "0..*");
    conectarElementos(eEmpresa, eUsuario, "Association", "emplea", "", "1", "0..*");

    diag.Update();
    Repository.ReloadDiagram(diag.DiagramID);
}

// =================================================================================================
// 3. CU03W: Gestionar sucursales y ciudades
// =================================================================================================
function generarCU03W(pkg) {
    Session.Output(" -> Construyendo: cd CU03W - Gestionar sucursales y ciudades");
    var diag = pkg.Diagrams.AddNew("cd CU03W - Gestionar sucursales y ciudades", "Logical");
    configurarDiagramaTablasUML(diag);

    var actor = agregarActor(pkg, diag, "Administrador", 40, 240, 80, 100);

    var b1 = agregarClaseTablaUML(pkg, diag, "ListaSucursalesView", "boundary",
        [
            { nombre: "id_empresa", tipo: "int", vis: "Private" },
            { nombre: "sucursales_lista", tipo: "List<SucursalDTO>", vis: "Private" },
            { nombre: "cargando", tipo: "boolean", vis: "Private" }
        ],
        [
            { nombre: "ngOnInit", retorno: "void" },
            { nombre: "cargarSucursales", retorno: "void" },
            { nombre: "abrirModalNuevaSucursal", retorno: "void" },
            { nombre: "abrirModalEstado", retorno: "void", parametros: [{ nombre: "id", tipo: "int" }] }
        ],
        180, 40, 240, 160
    );

    var b2 = agregarClaseTablaUML(pkg, diag, "FormularioSucursalModal", "boundary",
        [
            { nombre: "visible", tipo: "boolean", vis: "Private" },
            { nombre: "ciudades_disponibles", tipo: "List<CiudadDTO>", vis: "Private" },
            { nombre: "sucursalForm", tipo: "FormGroup", vis: "Private" }
        ],
        [
            { nombre: "abrir", retorno: "void" },
            { nombre: "cerrar", retorno: "void" },
            { nombre: "onSubmit", retorno: "void" }
        ],
        180, 230, 240, 160
    );

    var b3 = agregarClaseTablaUML(pkg, diag, "EstadoSucursalModal", "boundary",
        [
            { nombre: "visible", tipo: "boolean", vis: "Private" },
            { nombre: "id_sucursal", tipo: "int", vis: "Private" },
            { nombre: "activo", tipo: "boolean", vis: "Private" }
        ],
        [
            { nombre: "confirmarCambio", retorno: "void" },
            { nombre: "cancelar", retorno: "void" }
        ],
        180, 420, 240, 130
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
        180, 580, 240, 110
    );

    // Col 3: Route Controller
    var cRoutes = agregarClaseTablaUML(pkg, diag, "sucursales_routes (RouteController)", "control",
        [
            { nombre: "router", tipo: "APIRouter", vis: "Private" },
            { nombre: "prefix", tipo: "string = '/api/sucursales'", vis: "Private" }
        ],
        [
            { nombre: "listar_sucursales", retorno: "Response", parametros: [{ nombre: "id_empresa", tipo: "int" }] },
            { nombre: "crear_sucursal", retorno: "Response", parametros: [{ nombre: "dto", tipo: "CrearSucursalDTO" }] },
            { nombre: "cambiar_estado", retorno: "Response", parametros: [{ nombre: "id", tipo: "int" }] }
        ],
        470, 220, 280, 190
    );

    // Col 4: Domain Service
    var cServices = agregarClaseTablaUML(pkg, diag, "sucursales_services (DomainService)", "control",
        [
            { nombre: "db", tipo: "PostgreSQL", vis: "Private" },
            { nombre: "audit", tipo: "BitacoraService", vis: "Private" }
        ],
        [
            { nombre: "registrar_sucursal", retorno: "dict", parametros: [{ nombre: "dto", tipo: "CrearSucursalDTO" }, { nombre: "id_empresa", tipo: "int" }] },
            { nombre: "validar_limite_plan", retorno: "boolean", parametros: [{ nombre: "id_empresa", tipo: "int" }] },
            { nombre: "alternar_estado_sucursal", retorno: "dict", parametros: [{ nombre: "id", tipo: "int" }] }
        ],
        790, 220, 280, 190
    );

    // Col 5 & 6: Entities
    var eSucursal = agregarClaseTablaUML(pkg, diag, "t_sucursal", "entity",
        [
            { nombre: "id_sucursal [PK]", tipo: "int", vis: "Public" },
            { nombre: "id_empresa [FK]", tipo: "int", vis: "Public" },
            { nombre: "id_ciudad [FK]", tipo: "int", vis: "Public" },
            { nombre: "nombre", tipo: "string", vis: "Public" },
            { nombre: "direccion", tipo: "string", vis: "Public" },
            { nombre: "activo", tipo: "boolean", vis: "Public" }
        ],
        [
            { nombre: "insert", retorno: "int", parametros: [{ nombre: "s", tipo: "dict" }] },
            { nombre: "updateEstado", retorno: "void", parametros: [{ nombre: "id", tipo: "int" }, { nombre: "act", tipo: "boolean" }] },
            { nombre: "filterByEmpresa", retorno: "List<t_sucursal>", parametros: [{ nombre: "id_empresa", tipo: "int" }] }
        ],
        1110, 60, 220, 170
    );

    var eCiudad = agregarClaseTablaUML(pkg, diag, "t_ciudad", "entity",
        [
            { nombre: "id_ciudad [PK]", tipo: "int", vis: "Public" },
            { nombre: "nombre", tipo: "string", vis: "Public" },
            { nombre: "departamento", tipo: "string", vis: "Public" }
        ],
        [
            { nombre: "findAll", retorno: "List<t_ciudad>" }
        ],
        1110, 260, 220, 120
    );

    var eEmpresa = agregarClaseTablaUML(pkg, diag, "empresa", "entity",
        [
            { nombre: "id_empresa [PK]", tipo: "int", vis: "Public" },
            { nombre: "nombre", tipo: "string", vis: "Public" }
        ],
        [
            { nombre: "findById", retorno: "empresa", parametros: [{ nombre: "id", tipo: "int" }] }
        ],
        1110, 410, 220, 120
    );

    var eUsuarioSuc = agregarClaseTablaUML(pkg, diag, "t_usuario_sucursal", "entity",
        [
            { nombre: "id_usuario_sucursal [PK]", tipo: "int", vis: "Public" },
            { nombre: "id_usuario [FK]", tipo: "int", vis: "Public" },
            { nombre: "id_sucursal [FK]", tipo: "int", vis: "Public" }
        ],
        [
            { nombre: "countBySucursal", retorno: "int", parametros: [{ nombre: "id_sucursal", tipo: "int" }] }
        ],
        1370, 140, 220, 130
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
        1370, 310, 220, 110
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
    conectarElementos(cServices, eSucursal, "Dependency", "persiste", "«use»");
    conectarElementos(cServices, eCiudad, "Dependency", "consulta", "«use»");
    conectarElementos(cServices, eBitacora, "Dependency", "audita", "«use»");

    conectarElementos(eEmpresa, eSucursal, "Association", "posee", "", "1", "0..*");
    conectarElementos(eCiudad, eSucursal, "Association", "ubica", "", "1", "0..*");
    conectarElementos(eSucursal, eUsuarioSuc, "Association", "incluye", "", "1", "0..*");

    diag.Update();
    Repository.ReloadDiagram(diag.DiagramID);
}

// =================================================================================================
// 4. CU04W: Gestionar productos
// =================================================================================================
function generarCU04W(pkg) {
    Session.Output(" -> Construyendo: cd CU04W - Gestionar productos");
    var diag = pkg.Diagrams.AddNew("cd CU04W - Gestionar productos", "Logical");
    configurarDiagramaTablasUML(diag);

    var actor = agregarActor(pkg, diag, "Administrador / Encargado", 40, 240, 90, 100);

    var b1 = agregarClaseTablaUML(pkg, diag, "ListaProductosView", "boundary",
        [
            { nombre: "id_empresa", tipo: "int", vis: "Private" },
            { nombre: "productos_lista", tipo: "List<ProductoDTO>", vis: "Private" },
            { nombre: "filtro_categoria", tipo: "int", vis: "Private" },
            { nombre: "cargando", tipo: "boolean", vis: "Private" }
        ],
        [
            { nombre: "ngOnInit", retorno: "void" },
            { nombre: "cargarProductos", retorno: "void" },
            { nombre: "abrirModalNuevo", retorno: "void" },
            { nombre: "abrirModalEditar", retorno: "void", parametros: [{ nombre: "id", tipo: "int" }] }
        ],
        180, 40, 240, 160
    );

    var b2 = agregarClaseTablaUML(pkg, diag, "FormularioPrendaModal", "boundary",
        [
            { nombre: "visible", tipo: "boolean", vis: "Private" },
            { nombre: "categorias_disponibles", tipo: "List<CategoriaDTO>", vis: "Private" },
            { nombre: "prendaForm", tipo: "FormGroup", vis: "Private" }
        ],
        [
            { nombre: "abrir", retorno: "void", parametros: [{ nombre: "id", tipo: "int" }] },
            { nombre: "cerrar", retorno: "void" },
            { nombre: "onSubmit", retorno: "void" }
        ],
        180, 230, 240, 160
    );

    var b3 = agregarClaseTablaUML(pkg, diag, "TabVariantesTallaColor", "boundary",
        [
            { nombre: "tallas_seleccionadas", tipo: "List<int>", vis: "Private" },
            { nombre: "colores_seleccionados", tipo: "List<int>", vis: "Private" },
            { nombre: "matriz_variantes", tipo: "List<VarianteDTO>", vis: "Private" }
        ],
        [
            { nombre: "generarCombinaciones", retorno: "void" },
            { nombre: "actualizarPrecioSku", retorno: "void", parametros: [{ nombre: "idx", tipo: "int" }] }
        ],
        180, 420, 240, 140
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
        180, 590, 240, 110
    );

    // Col 3: Route Controller
    var cRoutes = agregarClaseTablaUML(pkg, diag, "productos_routes (RouteController)", "control",
        [
            { nombre: "router", tipo: "APIRouter", vis: "Private" },
            { nombre: "prefix", tipo: "string = '/api/productos'", vis: "Private" }
        ],
        [
            { nombre: "listar_productos", retorno: "Response", parametros: [{ nombre: "id_empresa", tipo: "int" }] },
            { nombre: "crear_producto_con_variantes", retorno: "Response", parametros: [{ nombre: "dto", tipo: "PrendaMatrizDTO" }] },
            { nombre: "actualizar_producto", retorno: "Response", parametros: [{ nombre: "id", tipo: "int" }, { nombre: "dto", tipo: "PrendaDTO" }] }
        ],
        470, 220, 280, 210
    );

    // Col 4: Domain Service
    var cServices = agregarClaseTablaUML(pkg, diag, "productos_services (DomainService)", "control",
        [
            { nombre: "db", tipo: "PostgreSQL", vis: "Private" },
            { nombre: "audit", tipo: "BitacoraService", vis: "Private" }
        ],
        [
            { nombre: "registrar_prenda_y_matriz", retorno: "dict", parametros: [{ nombre: "dto", tipo: "PrendaMatrizDTO" }, { nombre: "id_empresa", tipo: "int" }] },
            { nombre: "modificar_prenda", retorno: "dict", parametros: [{ nombre: "id", tipo: "int" }, { nombre: "dto", tipo: "PrendaDTO" }] },
            { nombre: "sincronizar_inventario_inicial", retorno: "void", parametros: [{ nombre: "id_variante", tipo: "int" }] }
        ],
        790, 220, 280, 210
    );

    // Col 5 & 6: Entities
    var eProducto = agregarClaseTablaUML(pkg, diag, "t_producto", "entity",
        [
            { nombre: "id_producto [PK]", tipo: "int", vis: "Public" },
            { nombre: "id_empresa [FK]", tipo: "int", vis: "Public" },
            { nombre: "id_categoria [FK]", tipo: "int", vis: "Public" },
            { nombre: "nombre", tipo: "string", vis: "Public" },
            { nombre: "descripcion", tipo: "text", vis: "Public" },
            { nombre: "precio_base", tipo: "decimal", vis: "Public" }
        ],
        [
            { nombre: "insert", retorno: "int", parametros: [{ nombre: "p", tipo: "dict" }] },
            { nombre: "update", retorno: "void", parametros: [{ nombre: "id", tipo: "int" }, { nombre: "p", tipo: "dict" }] }
        ],
        1110, 40, 220, 160
    );

    var eCategoria = agregarClaseTablaUML(pkg, diag, "t_categoria", "entity",
        [
            { nombre: "id_categoria [PK]", tipo: "int", vis: "Public" },
            { nombre: "id_empresa [FK]", tipo: "int", vis: "Public" },
            { nombre: "nombre", tipo: "string", vis: "Public" }
        ],
        [
            { nombre: "findAll", retorno: "List<t_categoria>" }
        ],
        1110, 230, 220, 120
    );

    var eVariante = agregarClaseTablaUML(pkg, diag, "t_producto_talla_color", "entity",
        [
            { nombre: "id_producto_talla_color [PK]", tipo: "int", vis: "Public" },
            { nombre: "id_producto [FK]", tipo: "int", vis: "Public" },
            { nombre: "id_talla [FK]", tipo: "int", vis: "Public" },
            { nombre: "id_color [FK]", tipo: "int", vis: "Public" },
            { nombre: "sku", tipo: "string", vis: "Public" },
            { nombre: "codigo_barras", tipo: "string", vis: "Public" }
        ],
        [
            { nombre: "bulkInsert", retorno: "void", parametros: [{ nombre: "items", tipo: "List<dict>" }] }
        ],
        1110, 380, 220, 160
    );

    var eTalla = agregarClaseTablaUML(pkg, diag, "t_talla", "entity",
        [
            { nombre: "id_talla [PK]", tipo: "int", vis: "Public" },
            { nombre: "nombre", tipo: "string", vis: "Public" }
        ],
        [
            { nombre: "findAll", retorno: "List<t_talla>" }
        ],
        1370, 80, 210, 110
    );

    var eColor = agregarClaseTablaUML(pkg, diag, "t_color", "entity",
        [
            { nombre: "id_color [PK]", tipo: "int", vis: "Public" },
            { nombre: "nombre", tipo: "string", vis: "Public" }
        ],
        [
            { nombre: "findAll", retorno: "List<t_color>" }
        ],
        1370, 220, 210, 110
    );

    var eInventario = agregarClaseTablaUML(pkg, diag, "t_inventario", "entity",
        [
            { nombre: "id_inventario [PK]", tipo: "int", vis: "Public" },
            { nombre: "id_producto_talla_color [FK]", tipo: "int", vis: "Public" },
            { nombre: "id_sucursal [FK]", tipo: "int", vis: "Public" },
            { nombre: "stock_actual", tipo: "int", vis: "Public" }
        ],
        [
            { nombre: "initStock", retorno: "void", parametros: [{ nombre: "id_var", tipo: "int" }] }
        ],
        1370, 360, 210, 140
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
        1370, 530, 210, 120
    );

    // Conexiones
    conectarElementos(actor, b1, "Association", "", "");
    conectarElementos(actor, b2, "Association", "", "");
    conectarElementos(b2, b3, "Dependency", "contiene", "«use»");

    conectarElementos(b1, cRoutes, "Dependency", "consume", "«use»");
    conectarElementos(b2, cRoutes, "Dependency", "consume", "«use»");
    conectarElementos(cRoutes, b4, "Dependency", "notifica", "«use»");

    conectarElementos(cRoutes, cServices, "Dependency", "delega", "«use»");

    conectarElementos(cServices, eProducto, "Dependency", "persiste", "«use»");
    conectarElementos(cServices, eCategoria, "Dependency", "consulta", "«use»");
    conectarElementos(cServices, eVariante, "Dependency", "persiste_matriz", "«use»");
    conectarElementos(cServices, eInventario, "Dependency", "inicializa", "«use»");
    conectarElementos(cServices, eBitacora, "Dependency", "audita", "«use»");

    conectarElementos(eCategoria, eProducto, "Association", "clasifica", "", "1", "0..*");
    conectarElementos(eProducto, eVariante, "Association", "contiene", "", "1", "1..*");
    conectarElementos(eTalla, eVariante, "Association", "dimensiona", "", "1", "0..*");
    conectarElementos(eColor, eVariante, "Association", "matiza", "", "1", "0..*");
    conectarElementos(eVariante, eInventario, "Association", "registra_stock", "", "1", "0..*");

    diag.Update();
    Repository.ReloadDiagram(diag.DiagramID);
}

// =================================================================================================
// 5. CU05W: Gestionar planes de suscripción
// =================================================================================================
function generarCU05W(pkg) {
    Session.Output(" -> Construyendo: cd CU05W - Gestionar planes de suscripción");
    var diag = pkg.Diagrams.AddNew("cd CU05W - Gestionar planes de suscripción", "Logical");
    configurarDiagramaTablasUML(diag);

    var actor = agregarActor(pkg, diag, "SuperAdministrador", 40, 220, 80, 100);

    var b1 = agregarClaseTablaUML(pkg, diag, "CatalogoPlanesView", "boundary",
        [
            { nombre: "planes_lista", tipo: "List<PlanDTO>", vis: "Private" },
            { nombre: "cargando", tipo: "boolean", vis: "Private" }
        ],
        [
            { nombre: "ngOnInit", retorno: "void" },
            { nombre: "cargarPlanes", retorno: "void" },
            { nombre: "abrirModalEditar", retorno: "void", parametros: [{ nombre: "codigo", tipo: "string" }] }
        ],
        180, 60, 240, 150
    );

    var b2 = agregarClaseTablaUML(pkg, diag, "FormularioPlanModal", "boundary",
        [
            { nombre: "visible", tipo: "boolean", vis: "Private" },
            { nombre: "planForm", tipo: "FormGroup", vis: "Private" }
        ],
        [
            { nombre: "abrir", retorno: "void", parametros: [{ nombre: "codigo", tipo: "string" }] },
            { nombre: "cerrar", retorno: "void" },
            { nombre: "onSubmit", retorno: "void" }
        ],
        180, 250, 240, 150
    );

    var b3 = agregarClaseTablaUML(pkg, diag, "ErrorDialog", "boundary",
        [
            { nombre: "visible", tipo: "boolean", vis: "Private" },
            { nombre: "mensaje", tipo: "string", vis: "Private" }
        ],
        [
            { nombre: "mostrar", retorno: "void", parametros: [{ nombre: "msg", tipo: "string" }] },
            { nombre: "cerrar", retorno: "void" }
        ],
        180, 440, 240, 110
    );

    // Col 3: Route Controller
    var cRoutes = agregarClaseTablaUML(pkg, diag, "saas_routes (RouteController)", "control",
        [
            { nombre: "router", tipo: "APIRouter", vis: "Private" },
            { nombre: "prefix", tipo: "string = '/api/saas/planes'", vis: "Private" }
        ],
        [
            { nombre: "listar_planes", retorno: "Response" },
            { nombre: "actualizar_plan", retorno: "Response", parametros: [{ nombre: "codigo", tipo: "string" }, { nombre: "dto", tipo: "PlanDTO" }] }
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
            { nombre: "obtener_catalogo_planes", retorno: "List<PlanDTO>" },
            { nombre: "modificar_tarifas_y_limites", retorno: "dict", parametros: [{ nombre: "codigo", tipo: "string" }, { nombre: "dto", tipo: "PlanDTO" }] }
        ],
        790, 200, 280, 180
    );

    // Col 5 & 6: Entities
    var ePlan = agregarClaseTablaUML(pkg, diag, "t_plan", "entity",
        [
            { nombre: "codigo [PK]", tipo: "string", vis: "Public" },
            { nombre: "nombre", tipo: "string", vis: "Public" },
            { nombre: "max_sucursales", tipo: "int", vis: "Public" },
            { nombre: "max_usuarios", tipo: "int", vis: "Public" },
            { nombre: "precio_mensual", tipo: "decimal", vis: "Public" }
        ],
        [
            { nombre: "update", retorno: "void", parametros: [{ nombre: "cod", tipo: "string" }, { nombre: "p", tipo: "dict" }] },
            { nombre: "findAll", retorno: "List<t_plan>" }
        ],
        1110, 80, 220, 150
    );

    var eSuscripcion = agregarClaseTablaUML(pkg, diag, "t_suscripcion", "entity",
        [
            { nombre: "id_suscripcion [PK]", tipo: "int", vis: "Public" },
            { nombre: "codigo_plan [FK]", tipo: "string", vis: "Public" },
            { nombre: "estado", tipo: "string", vis: "Public" }
        ],
        [
            { nombre: "countActivasByPlan", retorno: "int", parametros: [{ nombre: "cod", tipo: "string" }] }
        ],
        1110, 270, 220, 130
    );

    var eEmpresa = agregarClaseTablaUML(pkg, diag, "empresa", "entity",
        [
            { nombre: "id_empresa [PK]", tipo: "int", vis: "Public" },
            { nombre: "nombre", tipo: "string", vis: "Public" }
        ],
        [
            { nombre: "findById", retorno: "empresa", parametros: [{ nombre: "id", tipo: "int" }] }
        ],
        1370, 150, 220, 120
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
        1370, 310, 220, 120
    );

    // Conexiones
    conectarElementos(actor, b1, "Association", "", "");
    conectarElementos(actor, b2, "Association", "", "");

    conectarElementos(b1, cRoutes, "Dependency", "consume", "«use»");
    conectarElementos(b2, cRoutes, "Dependency", "consume", "«use»");
    conectarElementos(cRoutes, b3, "Dependency", "notifica", "«use»");

    conectarElementos(cRoutes, cServices, "Dependency", "delega", "«use»");

    conectarElementos(cServices, ePlan, "Dependency", "actualiza", "«use»");
    conectarElementos(cServices, eSuscripcion, "Dependency", "valida_impacto", "«use»");
    conectarElementos(cServices, eBitacora, "Dependency", "audita", "«use»");

    conectarElementos(ePlan, eSuscripcion, "Association", "tipifica", "", "1", "0..*");
    conectarElementos(eEmpresa, eSuscripcion, "Association", "suscribe", "", "1", "0..*");

    diag.Update();
    Repository.ReloadDiagram(diag.DiagramID);
}

// =================================================================================================
// FUNCIÓN PRINCIPAL DE EJECUCIÓN
// =================================================================================================
function main() {
    Session.Output("======================================================================");
    Session.Output("INICIANDO GENERACIÓN DE DIAGRAMAS DE ANÁLISIS DE CLASES (CU01W - CU05W)");
    Session.Output("Formato: Tablas UML Rectangulares (Boundary -> Controllers -> Entity)");
    Session.Output("======================================================================");

    var pkg = Repository.GetTreeSelectedPackage();
    if (!pkg) {
        Session.Prompt("Por favor, seleccione un Paquete en el Project Browser antes de ejecutar.", 0);
        return;
    }

    Session.Output("Paquete Destino: " + pkg.Name);

    try {
        generarCU01W(pkg);
        generarCU02W(pkg);
        generarCU03W(pkg);
        generarCU04W(pkg);
        generarCU05W(pkg);

        Session.Output("======================================================================");
        Session.Output("PROCESO COMPLETADO EXITOSAMENTE");
        Session.Output("Diagramas creados: 5");
        Session.Output("======================================================================");
        Session.Prompt("Diagramas de clases (CU01W a CU05W) generados como tablas UML con éxito.", 0);
    } catch (e) {
        Session.Output("[ERROR FATAL] " + e.message);
        Session.Prompt("Error al generar diagramas: " + e.message, 0);
    }
}

main();
