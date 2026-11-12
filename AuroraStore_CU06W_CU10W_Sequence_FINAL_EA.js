/*
 * =================================================================================================
 * SCRIPT MAESTRO DE AUTOMATIZACIÓN DE DIAGRAMAS DE SECUENCIA UML 2.5 PARA SPARX ENTERPRISE ARCHITECT
 * =================================================================================================
 * Proyecto: AuroraStore SaaS
 * Lote 2: CU06W a CU10W (Actualizado con UIs Reales: Vistas, Modales/Drawers y Tablas de BD Completas)
 *   - sd CU06W - Gestionar suscripciones empresariales
 *   - sd CU07W - Consultar plan y límites de suscripción
 *   - sd CU08W - Gestionar respaldos y restauraciones
 *   - sd CU09W - Gestionar asignaciones de empleados a sucursales
 *   - sd CU10W - Consultar catálogo (Web y Móvil con Soporte Offline)
 * 
 * Reglas de Modelado UML 2.5 en Enterprise Architect:
 *   1. Líneas de Vida Rectangulares Estándar UML:
 *      - Sin estereotipos «boundary», «control» o «entity» en las lifelines para evitar círculos de robustez.
 *      - Representan cabeceras estándar rectangulares [ Object1 ] con líneas verticales discontinuas.
 *   2. Desglose Real de Interfaces de Usuario:
 *      - Vista Principal (Listado/Navegación) y Modal/Drawer Operativo (Captura de datos/Filtros).
 *      - Exclusión expresa de errorDialog triviales y toasts.
 *   3. Controladores limpios de Backend:
 *      - Routers FastAPI y Services de dominio; sin servicios genéricos de RBAC ni auth middleware.
 *   4. Tablas reales de persistencia PostgreSQL y cache_local (IndexedDB/SQLite).
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
// 1. CU06W: Gestionar suscripciones empresariales (Con Vistas, Modales y Tablas)
// =================================================================================================
function generarCU06W(pkg) {
    Session.Output(" -> Construyendo: sd CU06W - Gestionar suscripciones empresariales (Enriquecido)");
    var diag = pkg.Diagrams.AddNew("sd CU06W - Gestionar suscripciones empresariales", "Sequence");
    diag.Update();

    var totalH = 1040;
    var w = 125;
    var pitch = 150;
    var x = 40;

    var act  = agregarLifeline(pkg, diag, "admin : Administrador", "Actor", x, 110, totalH); x += pitch;
    var vSub = agregarLifeline(pkg, diag, "view : HistorialSuscripcionesView", "Sequence", x, w, totalH); x += pitch;
    var mSub = agregarLifeline(pkg, diag, "modal : ModalAsignarSuscripcion", "Sequence", x, w, totalH); x += pitch;
    var rtr  = agregarLifeline(pkg, diag, "router : saas_routes", "Sequence", x, w, totalH); x += pitch;
    var srv  = agregarLifeline(pkg, diag, "service : saas_services", "Sequence", x, w, totalH); x += pitch;
    var emp  = agregarLifeline(pkg, diag, "empresa", "Sequence", x, w, totalH); x += pitch;
    var tPln = agregarLifeline(pkg, diag, "t_plan", "Sequence", x, w, totalH); x += pitch;
    var tSus = agregarLifeline(pkg, diag, "t_suscripcion", "Sequence", x, w, totalH); x += pitch;
    var tBit = agregarLifeline(pkg, diag, "t_bitacora", "Sequence", x, w, totalH);

    var seq = 1;

    // Escenario 1: Listar suscripciones
    agregarMensaje(act, vSub, seq++ + ": solicitar_suscripciones(id_empresa)", seq, false, false);
    agregarMensaje(vSub, rtr, seq++ + ": GET /api/v1/saas/empresas/{id}/suscripciones", seq, false, false);
    agregarMensaje(rtr, srv, seq++ + ": consultar_suscripciones(id_empresa)", seq, false, false);
    agregarMensaje(srv, tSus, seq++ + ": SELECT s.*, p.nombre, p.max_sucursales FROM t_suscripcion s JOIN t_plan p ON p.codigo=s.codigo_plan WHERE s.id_empresa=:id", seq, false, false);
    agregarMensaje(tSus, srv, seq++ + ": return lista_suscripciones", seq, true, false);
    agregarMensaje(srv, rtr, seq++ + ": return suscripciones_response", seq, true, false);
    agregarMensaje(rtr, vSub, seq++ + ": 200 OK", seq, true, false);
    agregarMensaje(vSub, act, seq++ + ": mostrar_historial_suscripciones()", seq, true, false);

    // Escenario 2: Asignar / Renovar Suscripción desde Modal
    agregarMensaje(act, vSub, seq++ + ": click_asignar_o_renovar()", seq, false, false);
    agregarMensaje(vSub, mSub, seq++ + ": abrir_modal_asignacion(planes_disponibles)", seq, false, false);
    agregarMensaje(act, mSub, seq++ + ": enviar_asignacion(codigo_plan, fecha_inicio, fecha_fin)", seq, false, false);
    agregarMensaje(mSub, rtr, seq++ + ": POST /api/v1/saas/empresas/{id}/suscripciones", seq, false, false);
    agregarMensaje(rtr, srv, seq++ + ": asignar_suscripcion(id_empresa, datos_suscripcion)", seq, false, false);

    agregarMensaje(srv, emp, seq++ + ": SELECT estado FROM empresa WHERE id_empresa=:id", seq, false, false);
    agregarMensaje(emp, srv, seq++ + ": return estado_empresa", seq, true, false);
    agregarMensaje(srv, tPln, seq++ + ": SELECT codigo, max_sucursales FROM t_plan WHERE codigo=:codigo_plan", seq, false, false);
    agregarMensaje(tPln, srv, seq++ + ": return plan_valido", seq, true, false);

    // Fragmento alt: Validación
    agregarFragmentoCombinado(pkg, diag, "alt_validar_suscripcion", "alt", "[empresa inactiva || fecha_fin <= fecha_inicio] vs [else: datos validos]", 40, 1390, 470, 770);

    // Rama Error
    agregarMensaje(srv, rtr, seq++ + ": HTTPException(400, \"Empresa inactiva o rango de fechas invalido\")", seq, true, true);
    agregarMensaje(rtr, mSub, seq++ + ": 400 Bad Request", seq, true, true);
    agregarMensaje(mSub, act, seq++ + ": mostrar_error_en_formulario()", seq, true, true);

    // Rama Normal (else)
    agregarMensaje(srv, tSus, seq++ + ": INSERT INTO t_suscripcion(id_empresa, codigo_plan, estado='ACTIVA', fecha_inicio, fecha_fin)", seq, false, false);
    agregarMensaje(tSus, srv, seq++ + ": return id_suscripcion", seq, true, false);
    agregarMensaje(srv, tBit, seq++ + ": registrar_bitacora(\"SAAS\", \"ASIGNAR_SUSCRIPCION\")", seq, false, false);
    agregarMensaje(srv, rtr, seq++ + ": return suscripcion_creada", seq, true, false);
    agregarMensaje(rtr, mSub, seq++ + ": 201 Created", seq, true, false);
    agregarMensaje(mSub, vSub, seq++ + ": cerrar_modal_y_notificar()", seq, true, false);
    agregarMensaje(vSub, act, seq++ + ": actualizar_listado_suscripciones()", seq, true, false);

    // Escenario 3: Cancelar Suscripción Activa
    agregarMensaje(act, vSub, seq++ + ": solicitar_cancelacion(id_suscripcion, motivo)", seq, false, false);
    agregarMensaje(vSub, rtr, seq++ + ": POST /api/v1/saas/empresas/{id}/suscripciones/{id_sub}/cancelar", seq, false, false);
    agregarMensaje(rtr, srv, seq++ + ": cancelar_suscripcion(id_empresa, id_suscripcion, motivo)", seq, false, false);
    agregarMensaje(srv, tSus, seq++ + ": UPDATE t_suscripcion SET estado='CANCELADA' WHERE id_suscripcion=:id", seq, false, false);
    agregarMensaje(srv, tBit, seq++ + ": registrar_bitacora(\"SAAS\", \"CANCELAR_SUSCRIPCION\")", seq, false, false);
    agregarMensaje(srv, rtr, seq++ + ": return confirmacion_cancelacion", seq, true, false);
    agregarMensaje(rtr, vSub, seq++ + ": 200 OK", seq, true, false);
    agregarMensaje(vSub, act, seq++ + ": mostrar_suscripcion_cancelada()", seq, true, false);

    diag.Update();
    Repository.ReloadDiagram(diag.DiagramID);
}


// =================================================================================================
// 2. CU07W: Consultar plan y límites de suscripción (Con Vistas y Modal de Upgrade)
// =================================================================================================
function generarCU07W(pkg) {
    Session.Output(" -> Construyendo: sd CU07W - Consultar plan y límites de suscripción (Enriquecido)");
    var diag = pkg.Diagrams.AddNew("sd CU07W - Consultar plan y límites de suscripción", "Sequence");
    diag.Update();

    var totalH = 920;
    var w = 125;
    var pitch = 150;
    var x = 40;

    var act  = agregarLifeline(pkg, diag, "admin : AdminTienda", "Actor", x, 110, totalH); x += pitch;
    var vPln = agregarLifeline(pkg, diag, "view : MiPlanView", "Sequence", x, w, totalH); x += pitch;
    var mUpg = agregarLifeline(pkg, diag, "modal : ModalUpgradePlan", "Sequence", x, w, totalH); x += pitch;
    var rtr  = agregarLifeline(pkg, diag, "router : saas_routes", "Sequence", x, w, totalH); x += pitch;
    var srv  = agregarLifeline(pkg, diag, "service : saas_services", "Sequence", x, w, totalH); x += pitch;
    var emp  = agregarLifeline(pkg, diag, "empresa", "Sequence", x, w, totalH); x += pitch;
    var tSus = agregarLifeline(pkg, diag, "t_suscripcion", "Sequence", x, w, totalH); x += pitch;
    var tPln = agregarLifeline(pkg, diag, "t_plan", "Sequence", x, w, totalH); x += pitch;
    var tSuc = agregarLifeline(pkg, diag, "t_sucursal", "Sequence", x, w, totalH); x += pitch;
    var tBit = agregarLifeline(pkg, diag, "t_bitacora", "Sequence", x, w, totalH);

    var seq = 1;

    // Escenario 1: Consultar estado y límites
    agregarMensaje(act, vPln, seq++ + ": solicitar_ajustes_plan()", seq, false, false);
    agregarMensaje(vPln, rtr, seq++ + ": GET /api/v1/saas/mi-empresa/plan", seq, false, false);
    agregarMensaje(rtr, srv, seq++ + ": consultar_plan_y_limites(id_empresa)", seq, false, false);

    agregarMensaje(srv, emp, seq++ + ": SELECT id_empresa, nombre_empresa FROM empresa WHERE id_empresa=:id", seq, false, false);
    agregarMensaje(emp, srv, seq++ + ": return datos_empresa", seq, true, false);

    agregarMensaje(srv, tSus, seq++ + ": SELECT codigo_plan, fecha_inicio, fecha_fin FROM t_suscripcion WHERE id_empresa=:id AND estado='ACTIVA'", seq, false, false);
    agregarMensaje(tSus, srv, seq++ + ": return suscripcion_activa", seq, true, false);

    // Fragmento alt: Verificación de suscripción activa
    agregarFragmentoCombinado(pkg, diag, "alt_suscripcion_activa", "alt", "[sin suscripcion activa] vs [else: suscripcion vigente]", 40, 1540, 300, 680);

    // Rama Error / Sin suscripción
    agregarMensaje(srv, rtr, seq++ + ": HTTPException(404, \"Empresa sin plan activo\")", seq, true, true);
    agregarMensaje(rtr, vPln, seq++ + ": 404 Not Found", seq, true, true);
    agregarMensaje(vPln, act, seq++ + ": mostrar_alerta_sin_suscripcion()", seq, true, true);

    // Rama Normal (else)
    agregarMensaje(srv, tPln, seq++ + ": SELECT nombre, max_sucursales, precio_mensual FROM t_plan WHERE codigo=:codigo", seq, false, false);
    agregarMensaje(tPln, srv, seq++ + ": return datos_plan", seq, true, false);
    agregarMensaje(srv, tSuc, seq++ + ": SELECT COUNT(*) FROM t_sucursal WHERE id_empresa=:id AND activo=true", seq, false, false);
    agregarMensaje(tSuc, srv, seq++ + ": return conteo_sucursales_activas", seq, true, false);

    agregarMensaje(srv, srv, seq++ + ": calcular_consumo_y_dias_restantes()", seq, false, false);
    agregarMensaje(srv, rtr, seq++ + ": return plan_resumen(plan, max_sucursales, usadas, vigencia)", seq, true, false);
    agregarMensaje(rtr, vPln, seq++ + ": 200 OK (plan_resumen)", seq, true, false);
    agregarMensaje(vPln, act, seq++ + ": mostrar_estado_y_limites()", seq, true, false);

    // Escenario 2: Solicitar Upgrade / Cambio de Plan desde Modal
    agregarMensaje(act, vPln, seq++ + ": click_upgrade_plan()", seq, false, false);
    agregarMensaje(vPln, mUpg, seq++ + ": abrir_modal_upgrade()", seq, false, false);
    agregarMensaje(act, mUpg, seq++ + ": seleccionar_nuevo_plan(codigo_plan_profesional)", seq, false, false);
    agregarMensaje(mUpg, rtr, seq++ + ": POST /api/v1/saas/mi-empresa/solicitar-upgrade", seq, false, false);
    agregarMensaje(rtr, srv, seq++ + ": solicitar_upgrade_plan(id_empresa, nuevo_codigo)", seq, false, false);
    agregarMensaje(srv, tBit, seq++ + ": registrar_bitacora(\"SAAS\", \"SOLICITUD_UPGRADE\")", seq, false, false);
    agregarMensaje(srv, rtr, seq++ + ": return solicitud_recibida", seq, true, false);
    agregarMensaje(rtr, mUpg, seq++ + ": 200 OK", seq, true, false);
    agregarMensaje(mUpg, vPln, seq++ + ": cerrar_modal_y_notificar()", seq, true, false);
    agregarMensaje(vPln, act, seq++ + ": mostrar_confirmacion_upgrade()", seq, true, false);

    diag.Update();
    Repository.ReloadDiagram(diag.DiagramID);
}


// =================================================================================================
// 3. CU08W: Gestionar respaldos y restauraciones (Con Vistas y Modal de Confirmación)
// =================================================================================================
function generarCU08W(pkg) {
    Session.Output(" -> Construyendo: sd CU08W - Gestionar respaldos y restauraciones (Enriquecido)");
    var diag = pkg.Diagrams.AddNew("sd CU08W - Gestionar respaldos y restauraciones", "Sequence");
    diag.Update();

    var totalH = 1000;
    var w = 125;
    var pitch = 150;
    var x = 40;

    var act  = agregarLifeline(pkg, diag, "admin : Administrador", "Actor", x, 110, totalH); x += pitch;
    var vRes = agregarLifeline(pkg, diag, "view : RespaldosView", "Sequence", x, w, totalH); x += pitch;
    var mRes = agregarLifeline(pkg, diag, "modal : ModalConfirmarRestauracion", "Sequence", x, w, totalH); x += pitch;
    var rtr  = agregarLifeline(pkg, diag, "router : backup_routes", "Sequence", x, w, totalH); x += pitch;
    var srv  = agregarLifeline(pkg, diag, "service : backup_services", "Sequence", x, w, totalH); x += pitch;
    var tRes = agregarLifeline(pkg, diag, "t_respaldo", "Sequence", x, w, totalH); x += pitch;
    var tBit = agregarLifeline(pkg, diag, "t_bitacora", "Sequence", x, w, totalH);

    var seq = 1;

    // Escenario 1: Listar respaldos existentes
    agregarMensaje(act, vRes, seq++ + ": solicitar_historial_respaldos()", seq, false, false);
    agregarMensaje(vRes, rtr, seq++ + ": GET /api/v1/admin/respaldos", seq, false, false);
    agregarMensaje(rtr, srv, seq++ + ": listar_respaldos_service()", seq, false, false);
    agregarMensaje(srv, tRes, seq++ + ": SELECT id_respaldo, nombre_archivo, tamanio_bytes, checksum, creado_en FROM t_respaldo ORDER BY creado_en DESC", seq, false, false);
    agregarMensaje(tRes, srv, seq++ + ": return lista_respaldos", seq, true, false);
    agregarMensaje(srv, rtr, seq++ + ": return respaldos_response", seq, true, false);
    agregarMensaje(rtr, vRes, seq++ + ": 200 OK", seq, true, false);
    agregarMensaje(vRes, act, seq++ + ": desplegar_tabla_respaldos()", seq, true, false);

    // Escenario 2: Ejecutar Respaldo de Base de Datos
    agregarMensaje(act, vRes, seq++ + ": solicitar_generacion_respaldo()", seq, false, false);
    agregarMensaje(vRes, rtr, seq++ + ": POST /api/v1/admin/respaldos/generar", seq, false, false);
    agregarMensaje(rtr, srv, seq++ + ": ejecutar_respaldo()", seq, false, false);

    agregarMensaje(srv, srv, seq++ + ": verificar_espacio_y_permisos()", seq, false, false);

    // Fragmento alt: Ejecución de Respaldo
    agregarFragmentoCombinado(pkg, diag, "alt_ejecutar_respaldo", "alt", "[espacio insuficiente || fallo IO] vs [else: ejecucion exitosa]", 40, 1080, 420, 680);

    // Rama Error
    agregarMensaje(srv, rtr, seq++ + ": HTTPException(500, \"Fallo al generar archivo de volcado\")", seq, true, true);
    agregarMensaje(rtr, vRes, seq++ + ": 500 Internal Error", seq, true, true);
    agregarMensaje(vRes, act, seq++ + ": mostrar_error_respaldo()", seq, true, true);

    // Rama Normal (else)
    agregarMensaje(srv, srv, seq++ + ": pg_dump(comercio_db) -> archivo.dump", seq, false, false);
    agregarMensaje(srv, tRes, seq++ + ": INSERT INTO t_respaldo(nombre_archivo, tamanio_bytes, checksum)", seq, false, false);
    agregarMensaje(tRes, srv, seq++ + ": return id_respaldo", seq, true, false);
    agregarMensaje(srv, tBit, seq++ + ": registrar_bitacora(\"SISTEMA\", \"RESPALDO_GENERADO\")", seq, false, false);
    agregarMensaje(srv, rtr, seq++ + ": return respaldo_completado", seq, true, false);
    agregarMensaje(rtr, vRes, seq++ + ": 201 Created", seq, true, false);
    agregarMensaje(vRes, act, seq++ + ": notificar_respaldo_exitoso()", seq, true, false);

    // Escenario 3: Ejecutar Restauración con Modal de Confirmación Crítica
    agregarMensaje(act, vRes, seq++ + ": click_restaurar_backup(id_respaldo)", seq, false, false);
    agregarMensaje(vRes, mRes, seq++ + ": abrir_modal_confirmacion(id_respaldo)", seq, false, false);
    agregarMensaje(act, mRes, seq++ + ": confirmar_restauracion_con_clave(clave_seguridad)", seq, false, false);
    agregarMensaje(mRes, rtr, seq++ + ": POST /api/v1/admin/respaldos/{id}/restaurar", seq, false, false);
    agregarMensaje(rtr, srv, seq++ + ": ejecutar_restauracion(id_respaldo)", seq, false, false);
    agregarMensaje(srv, srv, seq++ + ": pg_restore(archivo.dump)", seq, false, false);
    agregarMensaje(srv, tBit, seq++ + ": registrar_bitacora(\"SISTEMA\", \"RESTAURACION_EJECUTADA\")", seq, false, false);
    agregarMensaje(srv, rtr, seq++ + ": return confirmacion_restauracion", seq, true, false);
    agregarMensaje(rtr, mRes, seq++ + ": 200 OK", seq, true, false);
    agregarMensaje(mRes, vRes, seq++ + ": cerrar_modal_y_recargar()", seq, true, false);
    agregarMensaje(vRes, act, seq++ + ": notificar_restauracion_exitosa()", seq, true, false);

    diag.Update();
    Repository.ReloadDiagram(diag.DiagramID);
}


// =================================================================================================
// 4. CU09W: Gestionar asignaciones de empleados a sucursales (Con Vistas y Modal de Reasignación)
// =================================================================================================
function generarCU09W(pkg) {
    Session.Output(" -> Construyendo: sd CU09W - Gestionar asignaciones de empleados (Enriquecido)");
    var diag = pkg.Diagrams.AddNew("sd CU09W - Gestionar asignaciones de empleados a sucursales", "Sequence");
    diag.Update();

    var totalH = 1040;
    var w = 125;
    var pitch = 145;
    var x = 40;

    var act  = agregarLifeline(pkg, diag, "admin : AdminTienda", "Actor", x, 110, totalH); x += pitch;
    var vEmp = agregarLifeline(pkg, diag, "view : ListaEmpleadosView", "Sequence", x, w, totalH); x += pitch;
    var mAsg = agregarLifeline(pkg, diag, "modal : ModalReasignarSucursales", "Sequence", x, w, totalH); x += pitch;
    var rtr  = agregarLifeline(pkg, diag, "router : users_routes", "Sequence", x, w, totalH); x += pitch;
    var srv  = agregarLifeline(pkg, diag, "service : asignaciones_services", "Sequence", x, w, totalH); x += pitch;
    var emp  = agregarLifeline(pkg, diag, "empresa", "Sequence", x, w, totalH); x += pitch;
    var tSuc = agregarLifeline(pkg, diag, "t_sucursal", "Sequence", x, w, totalH); x += pitch;
    var tEmp = agregarLifeline(pkg, diag, "t_empleado", "Sequence", x, w, totalH); x += pitch;
    var tUS  = agregarLifeline(pkg, diag, "t_usuario_sucursal", "Sequence", x, w, totalH); x += pitch;
    var tBit = agregarLifeline(pkg, diag, "t_bitacora", "Sequence", x, w, totalH);

    var seq = 1;

    // Escenario 1: Listar empleados y sucursales asignadas
    agregarMensaje(act, vEmp, seq++ + ": solicitar_empleados_asignaciones()", seq, false, false);
    agregarMensaje(vEmp, rtr, seq++ + ": GET /api/v1/auth/usuarios/{id}/sucursales", seq, false, false);
    agregarMensaje(rtr, srv, seq++ + ": consultar(id_usuario, actor)", seq, false, false);
    agregarMensaje(srv, tUS, seq++ + ": SELECT us.*, s.nombre AS sucursal FROM t_usuario_sucursal us JOIN t_sucursal s ON s.id_sucursal=us.id_sucursal WHERE us.id_usuario=:id", seq, false, false);
    agregarMensaje(tUS, srv, seq++ + ": return lista_asignaciones", seq, true, false);
    agregarMensaje(srv, rtr, seq++ + ": return asignaciones_response", seq, true, false);
    agregarMensaje(rtr, vEmp, seq++ + ": 200 OK", seq, true, false);
    agregarMensaje(vEmp, act, seq++ + ": desplegar_empleados_y_sucursales()", seq, true, false);

    // Escenario 2: Reasignar Empleado desde Modal de Selección
    agregarMensaje(act, vEmp, seq++ + ": click_reasignar_sucursal(id_empleado)", seq, false, false);
    agregarMensaje(vEmp, mAsg, seq++ + ": abrir_modal_reasignacion(sucursales_empresa)", seq, false, false);
    agregarMensaje(act, mAsg, seq++ + ": enviar_reasignacion(id_empleado, ids_sucursales)", seq, false, false);
    agregarMensaje(mAsg, rtr, seq++ + ": POST /api/v1/auth/usuarios/{id}/sucursales", seq, false, false);
    agregarMensaje(rtr, srv, seq++ + ": asignar(usuario, ids_sucursales, actor)", seq, false, false);

    agregarMensaje(srv, emp, seq++ + ": SELECT id_empresa FROM empresa WHERE id_empresa=:emp", seq, false, false);
    agregarMensaje(emp, srv, seq++ + ": return empresa_valida", seq, true, false);

    agregarMensaje(srv, tSuc, seq++ + ": SELECT id_sucursal FROM t_sucursal WHERE id_empresa=:emp AND id_sucursal=ANY(:ids)", seq, false, false);
    agregarMensaje(tSuc, srv, seq++ + ": return sucursales_validas", seq, true, false);

    // Fragmento alt: Validación de Pertenencia y Jerarquía
    agregarFragmentoCombinado(pkg, diag, "alt_validar_asignacion", "alt", "[sucursales no pertenecen a la empresa || empleado inactivo] vs [else: asignacion valida]", 40, 1540, 480, 800);

    // Rama Error
    agregarMensaje(srv, rtr, seq++ + ": HTTPException(403, \"Rechazo de cambio: sucursales no pertenecen a la empresa\")", seq, true, true);
    agregarMensaje(rtr, mAsg, seq++ + ": 403 Forbidden", seq, true, true);
    agregarMensaje(mAsg, act, seq++ + ": mostrar_error_rechazo_cambio()", seq, true, true);

    // Rama Normal (else)
    agregarMensaje(srv, tUS, seq++ + ": DELETE FROM t_usuario_sucursal WHERE id_usuario=:id", seq, false, false);
    agregarMensaje(srv, tUS, seq++ + ": INSERT INTO t_usuario_sucursal(id_usuario, id_sucursal) VALUES (...)", seq, false, false);
    agregarMensaje(srv, tEmp, seq++ + ": UPDATE t_empleado SET id_sucursal_principal=:id_suc WHERE id_usuario=:id", seq, false, false);
    agregarMensaje(srv, tBit, seq++ + ": registrar_bitacora(\"USUARIOS\", \"REASIGNAR_SUCURSALES\")", seq, false, false);
    agregarMensaje(srv, rtr, seq++ + ": return asignacion_completada", seq, true, false);
    agregarMensaje(rtr, mAsg, seq++ + ": 200 OK", seq, true, false);
    agregarMensaje(mAsg, vEmp, seq++ + ": cerrar_modal_y_notificar()", seq, true, false);
    agregarMensaje(vEmp, act, seq++ + ": actualizar_tabla_asignaciones()", seq, true, false);

    diag.Update();
    Repository.ReloadDiagram(diag.DiagramID);
}


// =================================================================================================
// 5. CU10W / CU01M: Consultar catálogo (Con Vistas, Drawer de Filtros y Modal de Detalle)
// =================================================================================================
function generarCU10W(pkg) {
    Session.Output(" -> Construyendo: sd CU10W - Consultar catálogo (Enriquecido)");
    var diag = pkg.Diagrams.AddNew("sd CU10W - Consultar catálogo", "Sequence");
    diag.Update();

    var totalH = 1040;
    var w = 125;
    var pitch = 145;
    var x = 40;

    var act  = agregarLifeline(pkg, diag, "user : Usuario", "Actor", x, 110, totalH); x += pitch;
    var vCat = agregarLifeline(pkg, diag, "view : CatalogoView", "Sequence", x, w, totalH); x += pitch;
    var dFlt = agregarLifeline(pkg, diag, "drawer : FiltrosDrawer", "Sequence", x, w, totalH); x += pitch;
    var mDet = agregarLifeline(pkg, diag, "modal : DetalleProductoModal", "Sequence", x, w, totalH); x += pitch;
    var rtr  = agregarLifeline(pkg, diag, "router : catalogo_routes", "Sequence", x, w, totalH); x += pitch;
    var srv  = agregarLifeline(pkg, diag, "service : catalogo_services", "Sequence", x, w, totalH); x += pitch;
    var tCat = agregarLifeline(pkg, diag, "t_categoria", "Sequence", x, w, totalH); x += pitch;
    var tPrd = agregarLifeline(pkg, diag, "t_producto", "Sequence", x, w, totalH); x += pitch;
    var tVar = agregarLifeline(pkg, diag, "t_producto_talla_color", "Sequence", x, w, totalH); x += pitch;
    var cLoc = agregarLifeline(pkg, diag, "cache_local", "Sequence", x, w, totalH);

    var seq = 1;

    // Escenario 1: Filtrar y Listar Catálogo mediante Drawer de Filtros
    agregarMensaje(act, vCat, seq++ + ": abrir_drawer_filtros()", seq, false, false);
    agregarMensaje(vCat, dFlt, seq++ + ": desplegar_filtros()", seq, false, false);
    agregarMensaje(act, dFlt, seq++ + ": aplicar_filtros(categoria, talla, color, busqueda)", seq, false, false);

    // Fragmento alt: Detección de Conectividad
    agregarFragmentoCombinado(pkg, diag, "alt_conectividad_catalogo", "alt", "[sin conexion de red: MODO OFFLINE] vs [else: conexion activa: ONLINE]", 40, 1540, 210, 560);

    // Rama Offline (Nodo Rojo)
    agregarMensaje(dFlt, cLoc, seq++ + ": obtener_catalogo_cache(filtros)", seq, false, true);
    agregarMensaje(cLoc, dFlt, seq++ + ": return productos_cache", seq, true, true);
    agregarMensaje(dFlt, vCat, seq++ + ": notificar_productos_filtrados(productos_cache)", seq, true, true);
    agregarMensaje(vCat, act, seq++ + ": renderizar_catalogo_offline(\"(Modo Sin Conexión)\")", seq, true, true);

    // Rama Online
    agregarMensaje(dFlt, rtr, seq++ + ": GET /api/v1/catalogo/productos?cat=&tal=&col=", seq, false, false);
    agregarMensaje(rtr, srv, seq++ + ": listar_productos_catalogo(filtros)", seq, false, false);
    agregarMensaje(srv, tCat, seq++ + ": SELECT id_categoria, nombre FROM t_categoria WHERE activo=true", seq, false, false);
    agregarMensaje(tCat, srv, seq++ + ": return categorias", seq, true, false);
    agregarMensaje(srv, tPrd, seq++ + ": SELECT p.*, c.nombre FROM t_producto p JOIN t_categoria c ON c.id_categoria=p.id_categoria WHERE p.activo=true", seq, false, false);
    agregarMensaje(tPrd, srv, seq++ + ": return catalogo_productos", seq, true, false);
    agregarMensaje(srv, rtr, seq++ + ": return catalogo_response", seq, true, false);
    agregarMensaje(rtr, dFlt, seq++ + ": 200 OK (catalogo_productos)", seq, true, false);
    agregarMensaje(dFlt, cLoc, seq++ + ": actualizar_cache_local(catalogo_productos)", seq, false, false);
    agregarMensaje(dFlt, vCat, seq++ + ": notificar_productos_actualizados(catalogo_productos)", seq, true, false);
    agregarMensaje(vCat, act, seq++ + ": renderizar_catalogo_online()", seq, true, false);

    // Escenario 2: Seleccionar Producto y Consultar Detalle en Modal
    agregarMensaje(act, vCat, seq++ + ": seleccionar_producto(id_producto)", seq, false, false);
    agregarMensaje(vCat, mDet, seq++ + ": abrir_modal_detalle(id_producto)", seq, false, false);

    agregarFragmentoCombinado(pkg, diag, "alt_detalle_conectividad", "alt", "[sin conexion] vs [else: online]", 40, 1540, 640, 990);

    // Rama Detalle Offline
    agregarMensaje(mDet, cLoc, seq++ + ": obtener_detalle_producto_cache(id_producto)", seq, false, true);
    agregarMensaje(cLoc, mDet, seq++ + ": return detalle_cache", seq, true, true);
    agregarMensaje(mDet, act, seq++ + ": mostrar_detalle_producto_offline()", seq, true, true);

    // Rama Detalle Online
    agregarMensaje(mDet, rtr, seq++ + ": GET /api/v1/catalogo/productos/{id}", seq, false, false);
    agregarMensaje(rtr, srv, seq++ + ": obtener_detalle_producto_catalogo(id_producto)", seq, false, false);
    agregarMensaje(srv, tVar, seq++ + ": SELECT ptc.*, col.nombre, tal.talla FROM t_producto_talla_color ptc JOIN t_color col ON col.id_color=ptc.id_color JOIN t_talla tal ON tal.id_talla=ptc.id_talla WHERE ptc.id_producto=:id", seq, false, false);
    agregarMensaje(tVar, srv, seq++ + ": return variantes_completas", seq, true, false);
    agregarMensaje(srv, rtr, seq++ + ": return detalle_response", seq, true, false);
    agregarMensaje(rtr, mDet, seq++ + ": 200 OK", seq, true, false);
    agregarMensaje(mDet, act, seq++ + ": desplegar_modal_con_variantes()", seq, true, false);

    diag.Update();
    Repository.ReloadDiagram(diag.DiagramID);
}


// =================================================================================================
// FUNCIÓN PRINCIPAL DE EJECUCIÓN EN ENTERPRISE ARCHITECT
// =================================================================================================
function Main() {
    Repository.EnsureOutputVisible("Script");
    Session.Output("================================================================================");
    Session.Output("Iniciando generación de Diagramas de Secuencia UML 2.5 (CU06W a CU10W Enriquecidos) en EA...");
    Session.Output("================================================================================");

    var pkg = Repository.GetTreeSelectedPackage();
    if (pkg == null) {
        Session.Prompt("ERROR: Por favor seleccione un paquete en el Project Browser antes de ejecutar.", 0);
        return;
    }

    var pkgName = "Diagramas de Secuencia (UML 2.5) - Lote 2 (CU06W-CU10W Enriquecido)";
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

    generarCU06W(subPkg);
    generarCU07W(subPkg);
    generarCU08W(subPkg);
    generarCU09W(subPkg);
    generarCU10W(subPkg);

    Repository.RefreshModelView(subPkg.PackageID);
    Session.Output("================================================================================");
    Session.Output(" [OK] Se generaron exitosamente los 5 diagramas de secuencia enriquecidos (CU06W a CU10W).");
    Session.Output(" Paquete: " + subPkg.Name);
    Session.Output("================================================================================");
}

Main();
