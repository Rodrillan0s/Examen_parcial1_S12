/*
 * =================================================================================================
 * SCRIPT MAESTRO DE AUTOMATIZACIÓN DE DIAGRAMAS DE SECUENCIA UML 2.5 PARA SPARX ENTERPRISE ARCHITECT
 * =================================================================================================
 * Proyecto: AuroraStore SaaS
 * Lote 1: CU01W a CU05W (Actualizado con UIs Reales: Vistas y Modales, y Tablas de BD Completas)
 *   - sd CU01W - Gestionar usuarios y roles
 *   - sd CU02W - Gestionar cadena de tiendas (Empresas SaaS)
 *   - sd CU03W - Gestionar sucursales
 *   - sd CU04W - Gestionar productos
 *   - sd CU05W - Gestionar categorías
 * 
 * Reglas de Modelado UML 2.5 en Enterprise Architect:
 *   1. Líneas de Vida Rectangulares Estándar UML:
 *      - Sin estereotipos «boundary», «control» o «entity» en las lifelines para evitar círculos de robustez.
 *      - Representan cabeceras estándar rectangulares [ Object1 ] con líneas verticales discontinuas.
 *   2. Desglose Real de Interfaces de Usuario:
 *      - Vista Principal (Listado/Navegación) y Modal/Formulario Operativo (Captura de datos).
 *      - Exclusión expresa de errorDialog triviales y toasts.
 *   3. Controladores limpios de Backend:
 *      - Routers FastAPI y Services de dominio; sin servicios genéricos de RBAC ni auth middleware.
 *   4. Tablas reales de persistencia PostgreSQL (mapeadas a los modelos de análisis).
 *   5. Fragmentos combinados (alt, opt, loop) calculados con coordenadas negativas en 4to cuadrante (top > bottom).
 * =================================================================================================
 */

// -------------------------------------------------------------------------------------------------
// UTILIDADES Y HELPERS DE ENTERPRISE ARCHITECT AUTOMATION
// -------------------------------------------------------------------------------------------------

function agregarLifeline(pkg, diag, nombre, eaType, posX, ancho, altoTotal) {
    var tipoFinal = (eaType === "Actor") ? "Actor" : "Sequence";
    var el = pkg.Elements.AddNew(nombre, tipoFinal);
    el.Update();

    var left = posX;
    var right = posX + ancho;
    var top = -30;
    var bottom = -(30 + altoTotal);

    var diagObj = diag.DiagramObjects.AddNew("l=" + left + ";r=" + right + ";t=" + top + ";b=" + bottom + ";", "");
    diagObj.ElementID = el.ElementID;
    diagObj.Update();

    return el;
}

function agregarMensaje(sourceEl, targetEl, textoMensaje, seqNum, esRetorno, esError) {
    if (!sourceEl || !targetEl) return null;

    var conn = sourceEl.Connectors.AddNew(textoMensaje, "Sequence");
    conn.SupplierID = targetEl.ElementID;

    if (esError) {
        conn.Stereotype = "error";
    }
    conn.Update();
    sourceEl.Connectors.Refresh();

    try {
        if (esRetorno) {
            Repository.Execute("UPDATE t_connector SET PDATA4 = '1' WHERE Connector_ID = " + conn.ConnectorID);
        }
        if (seqNum > 0) {
            Repository.Execute("UPDATE t_connector SET SeqNo = " + seqNum + " WHERE Connector_ID = " + conn.ConnectorID);
        }
    } catch (ex) {
        // Fallback transparente
    }

    return conn;
}

function agregarFragmentoCombinado(pkg, diag, nombre, operador, guarda, left, right, topY, bottomY) {
    var frag = pkg.Elements.AddNew(nombre, "InteractionFragment");
    frag.Stereotype = operador; // "alt", "opt", "loop"
    frag.Notes = guarda;
    frag.Update();

    var top = -topY;
    var bottom = -bottomY;

    var fragObj = diag.DiagramObjects.AddNew("l=" + left + ";r=" + right + ";t=" + top + ";b=" + bottom + ";", "");
    fragObj.ElementID = frag.ElementID;
    fragObj.Update();

    return frag;
}


// =================================================================================================
// 1. CU01W: Gestionar usuarios y roles (Con Vistas, Modales y Tablas Completas)
// =================================================================================================
function generarCU01W(pkg) {
    Session.Output(" -> Construyendo: sd CU01W - Gestionar usuarios y roles (Enriquecido)");
    var diag = pkg.Diagrams.AddNew("sd CU01W - Gestionar usuarios y roles", "Sequence");
    diag.Update();

    var totalH = 1200;
    var w = 125;
    var pitch = 145;
    var x = 40;

    var act  = agregarLifeline(pkg, diag, "admin : Administrador", "Actor", x, 110, totalH); x += pitch;
    var vUsr = agregarLifeline(pkg, diag, "view : GestionUsuariosView", "Sequence", x, w, totalH); x += pitch;
    var mUsr = agregarLifeline(pkg, diag, "modal : ModalCrearUsuario", "Sequence", x, w, totalH); x += pitch;
    var mSuc = agregarLifeline(pkg, diag, "modal_suc : AsignarSucursalesModal", "Sequence", x, w, totalH); x += pitch;
    var rtr  = agregarLifeline(pkg, diag, "router : users_routes", "Sequence", x, w, totalH); x += pitch;
    var srv  = agregarLifeline(pkg, diag, "service : users_services", "Sequence", x, w, totalH); x += pitch;
    var emp  = agregarLifeline(pkg, diag, "empresa", "Sequence", x, w, totalH); x += pitch;
    var tUsr = agregarLifeline(pkg, diag, "t_usuario", "Sequence", x, w, totalH); x += pitch;
    var tRol = agregarLifeline(pkg, diag, "t_rol", "Sequence", x, w, totalH); x += pitch;
    var tUP  = agregarLifeline(pkg, diag, "t_usuario_permiso", "Sequence", x, w, totalH); x += pitch;
    var tUS  = agregarLifeline(pkg, diag, "t_usuario_sucursal", "Sequence", x, w, totalH); x += pitch;
    var tBit = agregarLifeline(pkg, diag, "t_bitacora", "Sequence", x, w, totalH);

    var seq = 1;

    // Escenario 1: Listar usuarios
    agregarMensaje(act, vUsr, seq++ + ": solicitar_usuarios()", seq, false, false);
    agregarMensaje(vUsr, rtr, seq++ + ": GET /api/v1/auth/usuarios", seq, false, false);
    agregarMensaje(rtr, srv, seq++ + ": listar_usuarios_service(id_empresa)", seq, false, false);
    agregarMensaje(srv, emp, seq++ + ": SELECT id_empresa, estado FROM empresa WHERE id_empresa=:id", seq, false, false);
    agregarMensaje(emp, srv, seq++ + ": return datos_empresa", seq, true, false);
    agregarMensaje(srv, tUsr, seq++ + ": SELECT id_usuario, username, correo, estado FROM t_usuario WHERE id_empresa=:id", seq, false, false);
    agregarMensaje(tUsr, srv, seq++ + ": return lista_usuarios", seq, true, false);
    agregarMensaje(srv, tRol, seq++ + ": SELECT id_rol, nombre_rol FROM t_rol", seq, false, false);
    agregarMensaje(tRol, srv, seq++ + ": return roles_activos", seq, true, false);
    agregarMensaje(srv, rtr, seq++ + ": return usuarios_response", seq, true, false);
    agregarMensaje(rtr, vUsr, seq++ + ": 200 OK (datos_usuarios)", seq, true, false);
    agregarMensaje(vUsr, act, seq++ + ": renderizar_tabla_usuarios()", seq, true, false);

    // Escenario 2: Crear / Modificar Usuario en Modal
    agregarMensaje(act, vUsr, seq++ + ": click_nuevo_usuario()", seq, false, false);
    agregarMensaje(vUsr, mUsr, seq++ + ": abrir_modal(roles_disponibles)", seq, false, false);
    agregarMensaje(act, mUsr, seq++ + ": enviar_formulario(datos, roles, permisos)", seq, false, false);
    agregarMensaje(mUsr, rtr, seq++ + ": POST /api/v1/auth/usuarios", seq, false, false);
    agregarMensaje(rtr, srv, seq++ + ": registrar_usuario(datos_usuario)", seq, false, false);
    agregarMensaje(srv, tUsr, seq++ + ": SELECT 1 FROM t_usuario WHERE username=:u AND id_empresa=:id", seq, false, false);
    agregarMensaje(tUsr, srv, seq++ + ": return existe_duplicado", seq, true, false);

    // Fragmento alt: Validación
    agregarFragmentoCombinado(pkg, diag, "alt_registro_usuario", "alt", "[username duplicado || datos invalidos] vs [else: datos validos]", 40, 1680, 410, 750);

    // Rama Error
    agregarMensaje(srv, rtr, seq++ + ": HTTPException(400, \"Username ya registrado o campos vacios\")", seq, true, true);
    agregarMensaje(rtr, mUsr, seq++ + ": 400 Bad Request", seq, true, true);
    agregarMensaje(mUsr, act, seq++ + ": mostrar_error_en_formulario()", seq, true, true);

    // Rama Normal (else)
    agregarMensaje(srv, srv, seq++ + ": hashear_password(password)", seq, false, false);
    agregarMensaje(srv, tUsr, seq++ + ": INSERT INTO t_usuario(...) RETURNING id_usuario", seq, false, false);
    agregarMensaje(tUsr, srv, seq++ + ": return id_usuario", seq, true, false);
    agregarMensaje(srv, tRol, seq++ + ": INSERT INTO t_usuario_rol(id_usuario, id_rol)", seq, false, false);

    // Loop permisos
    agregarFragmentoCombinado(pkg, diag, "loop_permisos", "loop", "[para cada id_permiso]", 620, 1390, 570, 625);
    agregarMensaje(srv, tUP, seq++ + ": INSERT INTO t_usuario_permiso(id_usuario, id_permiso, activo=true)", seq, false, false);

    agregarMensaje(srv, tBit, seq++ + ": registrar_bitacora(\"USUARIOS\", \"REGISTRO\")", seq, false, false);
    agregarMensaje(srv, rtr, seq++ + ": return usuario_creado", seq, true, false);
    agregarMensaje(rtr, mUsr, seq++ + ": 201 Created", seq, true, false);
    agregarMensaje(mUsr, vUsr, seq++ + ": cerrar_modal_y_notificar()", seq, true, false);
    agregarMensaje(vUsr, act, seq++ + ": actualizar_listado()", seq, true, false);

    // Escenario 3: Asignación de Sucursales a través del Modal Específico
    agregarMensaje(act, vUsr, seq++ + ": click_asignar_sucursales(id_usuario)", seq, false, false);
    agregarMensaje(vUsr, mSuc, seq++ + ": abrir_modal_sucursales(id_usuario)", seq, false, false);
    agregarMensaje(act, mSuc, seq++ + ": guardar_asignacion(ids_sucursales)", seq, false, false);
    agregarMensaje(mSuc, rtr, seq++ + ": POST /api/v1/auth/usuarios/{id}/sucursales", seq, false, false);
    agregarMensaje(rtr, srv, seq++ + ": asignar_sucursales_service(id, ids_sucursales)", seq, false, false);
    agregarMensaje(srv, tUS, seq++ + ": DELETE FROM t_usuario_sucursal WHERE id_usuario=:id", seq, false, false);
    agregarMensaje(srv, tUS, seq++ + ": INSERT INTO t_usuario_sucursal(id_usuario, id_sucursal) VALUES (...)", seq, false, false);
    agregarMensaje(srv, tBit, seq++ + ": registrar_bitacora(\"USUARIOS\", \"ASIGNAR_SUCURSAL\")", seq, false, false);
    agregarMensaje(srv, rtr, seq++ + ": return 200 OK", seq, true, false);
    agregarMensaje(rtr, mSuc, seq++ + ": 200 OK", seq, true, false);
    agregarMensaje(mSuc, vUsr, seq++ + ": cerrar_modal()", seq, true, false);
    agregarMensaje(vUsr, act, seq++ + ": mostrar_asignacion_confirmada()", seq, true, false);

    // Escenario 4: Desactivación Lógica
    agregarMensaje(act, vUsr, seq++ + ": solicitar_desactivacion(id_usuario)", seq, false, false);
    agregarMensaje(vUsr, rtr, seq++ + ": DELETE /api/v1/auth/usuarios/{id}", seq, false, false);
    agregarMensaje(rtr, srv, seq++ + ": desactivar_usuario(id_usuario)", seq, false, false);

    agregarFragmentoCombinado(pkg, diag, "alt_eliminar", "alt", "[usuario con dependencias || SuperAdmin] vs [else: permitido]", 40, 1680, 1020, 1180);
    agregarMensaje(srv, rtr, seq++ + ": HTTPException(400, \"Usuario con dependencias o protegido\")", seq, true, true);
    agregarMensaje(rtr, vUsr, seq++ + ": 400 Bad Request", seq, true, true);
    agregarMensaje(vUsr, act, seq++ + ": mostrar_bloqueo()", seq, true, true);

    agregarMensaje(srv, tUsr, seq++ + ": UPDATE t_usuario SET estado='INACTIVO' WHERE id_usuario=:id", seq, false, false);
    agregarMensaje(srv, tBit, seq++ + ": registrar_bitacora(\"USUARIOS\", \"DESACTIVAR\")", seq, false, false);
    agregarMensaje(srv, rtr, seq++ + ": return confirmacion", seq, true, false);
    agregarMensaje(rtr, vUsr, seq++ + ": 200 OK", seq, true, false);
    agregarMensaje(vUsr, act, seq++ + ": refrescar_tabla_inactivo()", seq, true, false);

    diag.Update();
    Repository.ReloadDiagram(diag.DiagramID);
}


// =================================================================================================
// 2. CU02W: Gestionar cadena de tiendas (Empresas SaaS con Vistas, Modales y Tablas)
// =================================================================================================
function generarCU02W(pkg) {
    Session.Output(" -> Construyendo: sd CU02W - Gestionar cadena de tiendas (Enriquecido)");
    var diag = pkg.Diagrams.AddNew("sd CU02W - Gestionar cadena de tiendas", "Sequence");
    diag.Update();

    var totalH = 980;
    var w = 125;
    var pitch = 150;
    var x = 40;

    var act  = agregarLifeline(pkg, diag, "admin : Administrador", "Actor", x, 110, totalH); x += pitch;
    var vEmp = agregarLifeline(pkg, diag, "view : GestionEmpresasView", "Sequence", x, w, totalH); x += pitch;
    var mEmp = agregarLifeline(pkg, diag, "modal : ModalCrearEmpresa", "Sequence", x, w, totalH); x += pitch;
    var rtr  = agregarLifeline(pkg, diag, "router : tenant_routes", "Sequence", x, w, totalH); x += pitch;
    var srv  = agregarLifeline(pkg, diag, "service : tenant_services", "Sequence", x, w, totalH); x += pitch;
    var emp  = agregarLifeline(pkg, diag, "empresa", "Sequence", x, w, totalH); x += pitch;
    var tSus = agregarLifeline(pkg, diag, "t_suscripcion", "Sequence", x, w, totalH); x += pitch;
    var tSuc = agregarLifeline(pkg, diag, "t_sucursal", "Sequence", x, w, totalH); x += pitch;
    var tBit = agregarLifeline(pkg, diag, "t_bitacora", "Sequence", x, w, totalH);

    var seq = 1;

    // Escenario 1: Listar empresas con métricas de plan y sucursales
    agregarMensaje(act, vEmp, seq++ + ": solicitar_listado_empresas()", seq, false, false);
    agregarMensaje(vEmp, rtr, seq++ + ": GET /api/v1/saas/tenants", seq, false, false);
    agregarMensaje(rtr, srv, seq++ + ": listar_empresas_service()", seq, false, false);
    agregarMensaje(srv, emp, seq++ + ": SELECT id_empresa, nombre_empresa, nit, correo, estado FROM empresa", seq, false, false);
    agregarMensaje(emp, srv, seq++ + ": return lista_empresas", seq, true, false);
    agregarMensaje(srv, tSus, seq++ + ": SELECT id_empresa, codigo_plan, estado FROM t_suscripcion WHERE estado='ACTIVA'", seq, false, false);
    agregarMensaje(tSus, srv, seq++ + ": return planes_activos", seq, true, false);
    agregarMensaje(srv, tSuc, seq++ + ": SELECT id_empresa, COUNT(*) AS sucursales FROM t_sucursal GROUP BY id_empresa", seq, false, false);
    agregarMensaje(tSuc, srv, seq++ + ": return total_sucursales", seq, true, false);
    agregarMensaje(srv, rtr, seq++ + ": return tenants_resumen", seq, true, false);
    agregarMensaje(rtr, vEmp, seq++ + ": 200 OK (tenants_resumen)", seq, true, false);
    agregarMensaje(vEmp, act, seq++ + ": desplegar_tabla_empresas()", seq, true, false);

    // Escenario 2: Crear Empresa desde Modal
    agregarMensaje(act, vEmp, seq++ + ": click_nueva_empresa()", seq, false, false);
    agregarMensaje(vEmp, mEmp, seq++ + ": abrir_modal_registro()", seq, false, false);
    agregarMensaje(act, mEmp, seq++ + ": enviar_formulario(nombre, nit, correo, representante)", seq, false, false);
    agregarMensaje(mEmp, rtr, seq++ + ": POST /api/v1/saas/tenants", seq, false, false);
    agregarMensaje(rtr, srv, seq++ + ": registrar_empresa(datos_empresa)", seq, false, false);
    agregarMensaje(srv, emp, seq++ + ": SELECT 1 FROM empresa WHERE LOWER(nit)=LOWER(:nit)", seq, false, false);
    agregarMensaje(emp, srv, seq++ + ": return existe_nit", seq, true, false);

    // Fragmento alt: Validación NIT y datos
    agregarFragmentoCombinado(pkg, diag, "alt_validar_nit", "alt", "[campos invalidos || NIT duplicado] vs [else: NIT unico y valido]", 40, 1350, 460, 730);

    // Rama Error
    agregarMensaje(srv, rtr, seq++ + ": HTTPException(400, \"NIT fiscal ya registrado o datos invalidos\")", seq, true, true);
    agregarMensaje(rtr, mEmp, seq++ + ": 400 Bad Request", seq, true, true);
    agregarMensaje(mEmp, act, seq++ + ": mostrar_error_en_formulario()", seq, true, true);

    // Rama Normal (else)
    agregarMensaje(srv, emp, seq++ + ": INSERT INTO empresa(nombre_empresa, nit, correo, estado='ACTIVO')", seq, false, false);
    agregarMensaje(emp, srv, seq++ + ": return id_empresa", seq, true, false);
    agregarMensaje(srv, tBit, seq++ + ": registrar_bitacora(\"EMPRESAS\", \"REGISTRO\")", seq, false, false);
    agregarMensaje(srv, rtr, seq++ + ": return tenant_creado", seq, true, false);
    agregarMensaje(rtr, mEmp, seq++ + ": 201 Created", seq, true, false);
    agregarMensaje(mEmp, vEmp, seq++ + ": cerrar_modal_y_notificar()", seq, true, false);
    agregarMensaje(vEmp, act, seq++ + ": actualizar_listado_empresas()", seq, true, false);

    // Escenario 3: Desactivación Lógica
    agregarMensaje(act, vEmp, seq++ + ": solicitar_baja_empresa(id_empresa)", seq, false, false);
    agregarMensaje(vEmp, rtr, seq++ + ": DELETE /api/v1/saas/tenants/{id}", seq, false, false);
    agregarMensaje(rtr, srv, seq++ + ": desactivar_empresa(id_empresa)", seq, false, false);
    agregarMensaje(srv, tSuc, seq++ + ": SELECT COUNT(*) FROM t_sucursal WHERE id_empresa=:id AND activo=true", seq, false, false);
    agregarMensaje(tSuc, srv, seq++ + ": return sucursales_activas", seq, true, false);

    agregarFragmentoCombinado(pkg, diag, "alt_baja_empresa", "alt", "[sucursales_activas > 0] vs [else: sin dependencias]", 40, 1350, 800, 960);
    agregarMensaje(srv, rtr, seq++ + ": HTTPException(409, \"Empresa posee sucursales activas\")", seq, true, true);
    agregarMensaje(rtr, vEmp, seq++ + ": 409 Conflict", seq, true, true);
    agregarMensaje(vEmp, act, seq++ + ": mostrar_alerta_baja_denegada()", seq, true, true);

    agregarMensaje(srv, emp, seq++ + ": UPDATE empresa SET estado='INACTIVO' WHERE id_empresa=:id", seq, false, false);
    agregarMensaje(srv, tBit, seq++ + ": registrar_bitacora(\"EMPRESAS\", \"DESACTIVAR_TENANT\")", seq, false, false);
    agregarMensaje(srv, rtr, seq++ + ": return confirmacion_baja", seq, true, false);
    agregarMensaje(rtr, vEmp, seq++ + ": 200 OK", seq, true, false);
    agregarMensaje(vEmp, act, seq++ + ": actualizar_fila_inactiva()", seq, true, false);

    diag.Update();
    Repository.ReloadDiagram(diag.DiagramID);
}


// =================================================================================================
// 3. CU03W: Gestionar sucursales (Con Vistas, Modales y Validación de Plan SaaS)
// =================================================================================================
function generarCU03W(pkg) {
    Session.Output(" -> Construyendo: sd CU03W - Gestionar sucursales (Enriquecido)");
    var diag = pkg.Diagrams.AddNew("sd CU03W - Gestionar sucursales", "Sequence");
    diag.Update();

    var totalH = 920;
    var w = 125;
    var pitch = 145;
    var x = 40;

    var act  = agregarLifeline(pkg, diag, "admin : AdminTienda", "Actor", x, 110, totalH); x += pitch;
    var vSuc = agregarLifeline(pkg, diag, "view : GestionSucursalesView", "Sequence", x, w, totalH); x += pitch;
    var mSuc = agregarLifeline(pkg, diag, "modal : ModalCrearSucursal", "Sequence", x, w, totalH); x += pitch;
    var rtr  = agregarLifeline(pkg, diag, "router : sucursales_routes", "Sequence", x, w, totalH); x += pitch;
    var srv  = agregarLifeline(pkg, diag, "service : sucursales_services", "Sequence", x, w, totalH); x += pitch;
    var emp  = agregarLifeline(pkg, diag, "empresa", "Sequence", x, w, totalH); x += pitch;
    var tSus = agregarLifeline(pkg, diag, "t_suscripcion", "Sequence", x, w, totalH); x += pitch;
    var tPln = agregarLifeline(pkg, diag, "t_plan", "Sequence", x, w, totalH); x += pitch;
    var tSuc = agregarLifeline(pkg, diag, "t_sucursal", "Sequence", x, w, totalH); x += pitch;
    var tCiu = agregarLifeline(pkg, diag, "t_ciudad", "Sequence", x, w, totalH); x += pitch;
    var tBit = agregarLifeline(pkg, diag, "t_bitacora", "Sequence", x, w, totalH);

    var seq = 1;

    // Escenario 1: Listar sucursales
    agregarMensaje(act, vSuc, seq++ + ": solicitar_sucursales()", seq, false, false);
    agregarMensaje(vSuc, rtr, seq++ + ": GET /api/v1/inventario/sucursales", seq, false, false);
    agregarMensaje(rtr, srv, seq++ + ": listar_sucursales(id_empresa)", seq, false, false);
    agregarMensaje(srv, tSuc, seq++ + ": SELECT s.*, c.nombre AS ciudad FROM t_sucursal s JOIN t_ciudad c ON c.id_ciudad=s.id_ciudad WHERE s.id_empresa=:id", seq, false, false);
    agregarMensaje(tSuc, srv, seq++ + ": return lista_sucursales", seq, true, false);
    agregarMensaje(srv, rtr, seq++ + ": return sucursales_response", seq, true, false);
    agregarMensaje(rtr, vSuc, seq++ + ": 200 OK", seq, true, false);
    agregarMensaje(vSuc, act, seq++ + ": desplegar_sucursales()", seq, true, false);

    // Escenario 2: Crear Sucursal desde Modal con validación de límite de plan
    agregarMensaje(act, vSuc, seq++ + ": click_nueva_sucursal()", seq, false, false);
    agregarMensaje(vSuc, mSuc, seq++ + ": abrir_modal_sucursal(ciudades_disponibles)", seq, false, false);
    agregarMensaje(act, mSuc, seq++ + ": enviar_datos_sucursal(nombre, direccion, telefono, id_ciudad)", seq, false, false);
    agregarMensaje(mSuc, rtr, seq++ + ": POST /api/v1/inventario/sucursales", seq, false, false);
    agregarMensaje(rtr, srv, seq++ + ": registrar_sucursal(id_empresa, datos_sucursal)", seq, false, false);

    agregarMensaje(srv, tSus, seq++ + ": SELECT codigo_plan FROM t_suscripcion WHERE id_empresa=:id AND estado='ACTIVA'", seq, false, false);
    agregarMensaje(tSus, srv, seq++ + ": return codigo_plan", seq, true, false);
    agregarMensaje(srv, tPln, seq++ + ": SELECT max_sucursales FROM t_plan WHERE codigo=:codigo_plan", seq, false, false);
    agregarMensaje(tPln, srv, seq++ + ": return max_sucursales", seq, true, false);
    agregarMensaje(srv, tSuc, seq++ + ": SELECT COUNT(*) FROM t_sucursal WHERE id_empresa=:id AND activo=true", seq, false, false);
    agregarMensaje(tSuc, srv, seq++ + ": return conteo_sucursales_activas", seq, true, false);

    // Fragmento alt: Límite de plan
    agregarFragmentoCombinado(pkg, diag, "alt_limite_sucursales", "alt", "[conteo >= max_sucursales] vs [else: cuota disponible]", 40, 1580, 500, 880);

    // Rama Error
    agregarMensaje(srv, rtr, seq++ + ": HTTPException(400, \"Limite de sucursales alcanzado para el plan contratado\")", seq, true, true);
    agregarMensaje(rtr, mSuc, seq++ + ": 400 Bad Request", seq, true, true);
    agregarMensaje(mSuc, act, seq++ + ": mostrar_error_limite_plan()", seq, true, true);

    // Rama Normal (else)
    agregarFragmentoCombinado(pkg, diag, "opt_nueva_ciudad", "opt", "[ciudad no registrada previamente]", 620, 1440, 630, 690);
    agregarMensaje(srv, tCiu, seq++ + ": INSERT INTO t_ciudad(nombre) RETURNING id_ciudad", seq, false, false);
    agregarMensaje(tCiu, srv, seq++ + ": return id_ciudad", seq, true, false);

    agregarMensaje(srv, tSuc, seq++ + ": INSERT INTO t_sucursal(nombre, direccion, telefono, id_ciudad, id_empresa, activo=true)", seq, false, false);
    agregarMensaje(tSuc, srv, seq++ + ": return id_sucursal", seq, true, false);
    agregarMensaje(srv, tBit, seq++ + ": registrar_bitacora(\"SUCURSALES\", \"GUARDAR_SUCURSAL\")", seq, false, false);
    agregarMensaje(srv, rtr, seq++ + ": return sucursal_creada", seq, true, false);
    agregarMensaje(rtr, mSuc, seq++ + ": 201 Created", seq, true, false);
    agregarMensaje(mSuc, vSuc, seq++ + ": cerrar_modal_y_notificar()", seq, true, false);
    agregarMensaje(vSuc, act, seq++ + ": actualizar_listado_sucursales()", seq, true, false);

    diag.Update();
    Repository.ReloadDiagram(diag.DiagramID);
}


// =================================================================================================
// 4. CU04W: Gestionar productos (Con Vistas, Modales y Gestión de Variantes Talla/Color)
// =================================================================================================
function generarCU04W(pkg) {
    Session.Output(" -> Construyendo: sd CU04W - Gestionar productos (Enriquecido)");
    var diag = pkg.Diagrams.AddNew("sd CU04W - Gestionar productos", "Sequence");
    diag.Update();

    var totalH = 1100;
    var w = 125;
    var pitch = 145;
    var x = 40;

    var act  = agregarLifeline(pkg, diag, "admin : AdminTienda", "Actor", x, 110, totalH); x += pitch;
    var vPrd = agregarLifeline(pkg, diag, "view : GestionProductosView", "Sequence", x, w, totalH); x += pitch;
    var mPrd = agregarLifeline(pkg, diag, "modal_prod : ModalCrearProducto", "Sequence", x, w, totalH); x += pitch;
    var mVar = agregarLifeline(pkg, diag, "modal_var : DetalleVariantesModal", "Sequence", x, w, totalH); x += pitch;
    var rtr  = agregarLifeline(pkg, diag, "router : productos_routes", "Sequence", x, w, totalH); x += pitch;
    var srv  = agregarLifeline(pkg, diag, "service : productos_services", "Sequence", x, w, totalH); x += pitch;
    var tCat = agregarLifeline(pkg, diag, "t_categoria", "Sequence", x, w, totalH); x += pitch;
    var tPrd = agregarLifeline(pkg, diag, "t_producto", "Sequence", x, w, totalH); x += pitch;
    var tVar = agregarLifeline(pkg, diag, "t_producto_talla_color", "Sequence", x, w, totalH); x += pitch;
    var tImg = agregarLifeline(pkg, diag, "t_producto_imagen", "Sequence", x, w, totalH); x += pitch;
    var tBit = agregarLifeline(pkg, diag, "t_bitacora", "Sequence", x, w, totalH);

    var seq = 1;

    // Escenario 1: Listar catálogo
    agregarMensaje(act, vPrd, seq++ + ": solicitar_catalogo()", seq, false, false);
    agregarMensaje(vPrd, rtr, seq++ + ": GET /api/v1/catalogo/productos", seq, false, false);
    agregarMensaje(rtr, srv, seq++ + ": listar_productos(id_empresa)", seq, false, false);
    agregarMensaje(srv, tPrd, seq++ + ": SELECT p.*, c.nombre FROM t_producto p JOIN t_categoria c ON c.id_categoria=p.id_categoria WHERE p.id_empresa=:id", seq, false, false);
    agregarMensaje(tPrd, srv, seq++ + ": return lista_productos", seq, true, false);
    agregarMensaje(srv, rtr, seq++ + ": return catalogo_response", seq, true, false);
    agregarMensaje(rtr, vPrd, seq++ + ": 200 OK", seq, true, false);
    agregarMensaje(vPrd, act, seq++ + ": desplegar_grilla_productos()", seq, true, false);

    // Escenario 2: Crear Producto Base desde Modal
    agregarMensaje(act, vPrd, seq++ + ": click_nuevo_producto()", seq, false, false);
    agregarMensaje(vPrd, mPrd, seq++ + ": abrir_modal_producto(categorias)", seq, false, false);
    agregarMensaje(act, mPrd, seq++ + ": enviar_datos_producto(nombre, descripcion, precio_base, id_categoria)", seq, false, false);
    agregarMensaje(mPrd, rtr, seq++ + ": POST /api/v1/catalogo/productos", seq, false, false);
    agregarMensaje(rtr, srv, seq++ + ": registrar_producto(id_empresa, datos_producto)", seq, false, false);
    agregarMensaje(srv, tCat, seq++ + ": SELECT id_categoria FROM t_categoria WHERE id_categoria=:id_cat AND id_empresa=:id", seq, false, false);
    agregarMensaje(tCat, srv, seq++ + ": return categoria_valida", seq, true, false);
    agregarMensaje(srv, tPrd, seq++ + ": INSERT INTO t_producto(nombre, descripcion, precio_base, id_categoria, id_empresa, activo=true)", seq, false, false);
    agregarMensaje(tPrd, srv, seq++ + ": return id_producto", seq, true, false);
    agregarMensaje(srv, tImg, seq++ + ": INSERT INTO t_producto_imagen(id_producto, url_imagen, es_portada=true)", seq, false, false);
    agregarMensaje(srv, tBit, seq++ + ": registrar_bitacora(\"CATALOGO\", \"CREAR_PRODUCTO\")", seq, false, false);
    agregarMensaje(srv, rtr, seq++ + ": return producto_creado(id_producto)", seq, true, false);
    agregarMensaje(rtr, mPrd, seq++ + ": 201 Created", seq, true, false);
    agregarMensaje(mPrd, vPrd, seq++ + ": cerrar_modal_y_notificar()", seq, true, false);
    agregarMensaje(vPrd, act, seq++ + ": mostrar_producto_registrado()", seq, true, false);

    // Escenario 3: Gestionar Variantes y Precios Diferenciados desde Modal de Variantes
    agregarMensaje(act, vPrd, seq++ + ": click_gestionar_variantes(id_producto)", seq, false, false);
    agregarMensaje(vPrd, mVar, seq++ + ": abrir_modal_variantes(id_producto)", seq, false, false);
    agregarMensaje(act, mVar, seq++ + ": guardar_variantes(tallas_colores_precios_skus)", seq, false, false);
    agregarMensaje(mVar, rtr, seq++ + ": PUT /api/v1/catalogo/productos/{id}/variantes", seq, false, false);
    agregarMensaje(rtr, srv, seq++ + ": sincronizar_variantes_producto(id_producto, variantes)", seq, false, false);

    agregarFragmentoCombinado(pkg, diag, "loop_variantes", "loop", "[para cada variante talla/color]", 620, 1390, 830, 910);
    agregarMensaje(srv, tVar, seq++ + ": INSERT INTO t_producto_talla_color(id_producto, id_talla, id_color, precio, sku)", seq, false, false);

    agregarMensaje(srv, tBit, seq++ + ": registrar_bitacora(\"CATALOGO\", \"ACTUALIZAR_VARIANTES\")", seq, false, false);
    agregarMensaje(srv, rtr, seq++ + ": return variantes_guardadas", seq, true, false);
    agregarMensaje(rtr, mVar, seq++ + ": 200 OK", seq, true, false);
    agregarMensaje(mVar, vPrd, seq++ + ": cerrar_modal_variantes()", seq, true, false);
    agregarMensaje(vPrd, act, seq++ + ": actualizar_tarjeta_producto()", seq, true, false);

    diag.Update();
    Repository.ReloadDiagram(diag.DiagramID);
}


// =================================================================================================
// 5. CU05W: Gestionar categorías (Con Vistas, Modales y Validación de Dependencias)
// =================================================================================================
function generarCU05W(pkg) {
    Session.Output(" -> Construyendo: sd CU05W - Gestionar categorías (Enriquecido)");
    var diag = pkg.Diagrams.AddNew("sd CU05W - Gestionar categorías", "Sequence");
    diag.Update();

    var totalH = 1040;
    var w = 125;
    var pitch = 150;
    var x = 40;

    var act  = agregarLifeline(pkg, diag, "admin : AdminTienda", "Actor", x, 110, totalH); x += pitch;
    var vCat = agregarLifeline(pkg, diag, "view : GestionCategoriasView", "Sequence", x, w, totalH); x += pitch;
    var mCat = agregarLifeline(pkg, diag, "modal : ModalCrearCategoria", "Sequence", x, w, totalH); x += pitch;
    var rtr  = agregarLifeline(pkg, diag, "router : categorias_routes", "Sequence", x, w, totalH); x += pitch;
    var srv  = agregarLifeline(pkg, diag, "service : categorias_services", "Sequence", x, w, totalH); x += pitch;
    var tCat = agregarLifeline(pkg, diag, "t_categoria", "Sequence", x, w, totalH); x += pitch;
    var tPrd = agregarLifeline(pkg, diag, "t_producto", "Sequence", x, w, totalH); x += pitch;
    var tBit = agregarLifeline(pkg, diag, "t_bitacora", "Sequence", x, w, totalH);

    var seq = 1;

    // Escenario 1: Listar categorías
    agregarMensaje(act, vCat, seq++ + ": solicitar_arbol_categorias()", seq, false, false);
    agregarMensaje(vCat, rtr, seq++ + ": GET /api/v1/catalogo/categorias", seq, false, false);
    agregarMensaje(rtr, srv, seq++ + ": listar_categorias_service(id_empresa)", seq, false, false);
    agregarMensaje(srv, tCat, seq++ + ": SELECT c.*, COUNT(p.id_producto) AS total_prendas FROM t_categoria c LEFT JOIN t_producto p ON p.id_categoria=c.id_categoria WHERE c.id_empresa=:id GROUP BY c.id_categoria", seq, false, false);
    agregarMensaje(tCat, srv, seq++ + ": return categorias_arbol", seq, true, false);
    agregarMensaje(srv, rtr, seq++ + ": return categorias_response", seq, true, false);
    agregarMensaje(rtr, vCat, seq++ + ": 200 OK", seq, true, false);
    agregarMensaje(vCat, act, seq++ + ": desplegar_categorias_con_miniaturas()", seq, true, false);

    // Escenario 2: Crear Categoría desde Modal
    agregarMensaje(act, vCat, seq++ + ": click_nueva_categoria()", seq, false, false);
    agregarMensaje(vCat, mCat, seq++ + ": abrir_modal_categoria()", seq, false, false);
    agregarMensaje(act, mCat, seq++ + ": enviar_datos_categoria(nombre, descripcion, id_padre, imagen_url)", seq, false, false);
    agregarMensaje(mCat, rtr, seq++ + ": POST /api/v1/catalogo/categorias", seq, false, false);
    agregarMensaje(rtr, srv, seq++ + ": registrar_categoria(id_empresa, datos_cat)", seq, false, false);
    agregarMensaje(srv, tCat, seq++ + ": SELECT 1 FROM t_categoria WHERE LOWER(nombre)=LOWER(:nom) AND id_empresa=:id", seq, false, false);
    agregarMensaje(tCat, srv, seq++ + ": return existe_nombre", seq, true, false);

    // Fragmento alt: Validación
    agregarFragmentoCombinado(pkg, diag, "alt_validar_categoria", "alt", "[nombre duplicado || vacio] vs [else: valido]", 40, 1240, 480, 750);

    // Rama Error
    agregarMensaje(srv, rtr, seq++ + ": HTTPException(400, \"Categoria ya existe en la empresa\")", seq, true, true);
    agregarMensaje(rtr, mCat, seq++ + ": 400 Bad Request", seq, true, true);
    agregarMensaje(mCat, act, seq++ + ": mostrar_error_en_formulario()", seq, true, true);

    // Rama Normal (else)
    agregarMensaje(srv, tCat, seq++ + ": INSERT INTO t_categoria(nombre, descripcion, id_padre, imagen_url, id_empresa)", seq, false, false);
    agregarMensaje(tCat, srv, seq++ + ": return id_categoria", seq, true, false);
    agregarMensaje(srv, tBit, seq++ + ": registrar_bitacora(\"CATALOGO\", \"CREAR_CATEGORIA\")", seq, false, false);
    agregarMensaje(srv, rtr, seq++ + ": return categoria_creada", seq, true, false);
    agregarMensaje(rtr, mCat, seq++ + ": 201 Created", seq, true, false);
    agregarMensaje(mCat, vCat, seq++ + ": cerrar_modal_y_notificar()", seq, true, false);
    agregarMensaje(vCat, act, seq++ + ": actualizar_arbol_categorias()", seq, true, false);

    // Escenario 3: Eliminar Categoría con Validación de Productos
    agregarMensaje(act, vCat, seq++ + ": click_eliminar_categoria(id_categoria)", seq, false, false);
    agregarMensaje(vCat, rtr, seq++ + ": DELETE /api/v1/catalogo/categorias/{id}", seq, false, false);
    agregarMensaje(rtr, srv, seq++ + ": eliminar_categoria(id_categoria)", seq, false, false);
    agregarMensaje(srv, tPrd, seq++ + ": SELECT COUNT(*) FROM t_producto WHERE id_categoria=:id AND activo=true", seq, false, false);
    agregarMensaje(tPrd, srv, seq++ + ": return total_productos_asociados", seq, true, false);

    agregarFragmentoCombinado(pkg, diag, "alt_eliminar_cat", "alt", "[total_productos > 0] vs [else: sin productos]", 40, 1240, 830, 1020);
    agregarMensaje(srv, rtr, seq++ + ": HTTPException(409, \"No se puede eliminar categoria con productos activos\")", seq, true, true);
    agregarMensaje(rtr, vCat, seq++ + ": 409 Conflict", seq, true, true);
    agregarMensaje(vCat, act, seq++ + ": mostrar_alerta_bloqueo_eliminacion()", seq, true, true);

    agregarMensaje(srv, tCat, seq++ + ": DELETE FROM t_categoria WHERE id_categoria=:id", seq, false, false);
    agregarMensaje(srv, tBit, seq++ + ": registrar_bitacora(\"CATALOGO\", \"ELIMINAR_CATEGORIA\")", seq, false, false);
    agregarMensaje(srv, rtr, seq++ + ": return 200 OK", seq, true, false);
    agregarMensaje(rtr, vCat, seq++ + ": 200 OK", seq, true, false);
    agregarMensaje(vCat, act, seq++ + ": remover_categoria_de_vista()", seq, true, false);

    diag.Update();
    Repository.ReloadDiagram(diag.DiagramID);
}


// =================================================================================================
// FUNCIÓN PRINCIPAL DE EJECUCIÓN EN ENTERPRISE ARCHITECT
// =================================================================================================
function Main() {
    Repository.EnsureOutputVisible("Script");
    Session.Output("================================================================================");
    Session.Output("Iniciando generación de Diagramas de Secuencia UML 2.5 (CU01W a CU05W Enriquecidos) en EA...");
    Session.Output("================================================================================");

    var pkg = Repository.GetTreeSelectedPackage();
    if (pkg == null) {
        Session.Prompt("ERROR: Por favor seleccione un paquete en el Project Browser antes de ejecutar.", 0);
        return;
    }

    var pkgName = "Diagramas de Secuencia (UML 2.5) - Lote 1 (CU01W-CU05W Enriquecido)";
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

    generarCU01W(subPkg);
    generarCU02W(subPkg);
    generarCU03W(subPkg);
    generarCU04W(subPkg);
    generarCU05W(subPkg);

    Repository.RefreshModelView(subPkg.PackageID);
    Session.Output("================================================================================");
    Session.Output(" [OK] Se generaron exitosamente los 5 diagramas de secuencia enriquecidos (CU01W a CU05W).");
    Session.Output(" Paquete: " + subPkg.Name);
    Session.Output("================================================================================");
}

Main();
