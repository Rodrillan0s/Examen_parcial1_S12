#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generador de Diagrama de Secuencia UML 2.5+ para CU01W: Gestionar usuarios y roles.
Arquitectura y Criterios:
- ACTOR -> «boundary» -> «control» -> «entity» (todas las tablas reales de BD)
- Entidades completas: t_rol, t_usuario, t_usuario_rol, t_usuario_permiso, t_usuario_sucursal, t_bitacora.
- Controles agrupados funcionalmente en UsuarioControl.
- Métodos fieles a PostgreSQL y código FastAPI/Service.
"""

import os
import resvg_py

def build_svg_cu01w():
    width = 1960
    height = 1140
    
    # Coordenadas X de las líneas de vida
    x_actor = 110
    x_iu = 290
    x_ctrl = 500
    x_t_rol = 730
    x_t_usr = 960
    x_t_usr_rol = 1190
    x_t_usr_perm = 1430
    x_t_usr_suc = 1680
    x_t_bita = 1880
    
    y_top_box = 135
    h_box = 56
    y_lifeline_start = y_top_box + h_box
    y_lifeline_end = 1085
    
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" style="background-color: #ffffff; font-family: 'Segoe UI', Arial, Helvetica, sans-serif;">
  <defs>
    <!-- Marcador de flecha síncrona (rellena) -->
    <marker id="arrow-sync" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#000000" />
    </marker>
    <!-- Marcador de flecha de retorno (abierta) -->
    <marker id="arrow-return" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <polyline points="0,1 10,5 0,9" fill="none" stroke="#000000" stroke-width="1.6" />
    </marker>
    <!-- Marcador de flecha de error (roja abierta) -->
    <marker id="arrow-error" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <polyline points="0,1 10,5 0,9" fill="none" stroke="#b91c1c" stroke-width="1.6" />
    </marker>
    <!-- Sombra suave para cajas -->
    <filter id="shadow" x="-5%" y="-5%" width="110%" height="115%" filterUnits="userSpaceOnUse">
      <feDropShadow dx="1" dy="1.5" stdDeviation="1.5" flood-color="#000000" flood-opacity="0.10"/>
    </filter>
  </defs>

  <!-- ==================== MARCO PRINCIPAL UML 2.5 ==================== -->
  <rect x="20" y="20" width="{width - 40}" height="{height - 40}" fill="#ffffff" stroke="#1e293b" stroke-width="1.6" />
  
  <!-- Pestaña superior izquierda (Pentágono de Título UML) -->
  <path d="M 20 20 L 460 20 L 478 38 L 478 56 L 20 56 Z" fill="#ffffff" stroke="#1e293b" stroke-width="1.6" />
  <text x="35" y="42" font-size="13.5" font-weight="bold" fill="#0f172a">sd CU01W — Gestionar usuarios y roles (UML 2.5+ / BCE)</text>

  <!-- ==================== LÍNEAS DE VIDA (LIFELINES) ==================== -->
  
  <!-- 1. ACTOR -->
  <g transform="translate({x_actor}, 65)">
    <circle cx="0" cy="14" r="12" fill="#ffffff" stroke="#000000" stroke-width="1.8" />
    <line x1="0" y1="26" x2="0" y2="52" stroke="#000000" stroke-width="1.8" />
    <line x1="-22" y1="36" x2="22" y2="36" stroke="#000000" stroke-width="1.8" />
    <line x1="0" y1="52" x2="-18" y2="78" stroke="#000000" stroke-width="1.8" />
    <line x1="0" y1="52" x2="18" y2="78" stroke="#000000" stroke-width="1.8" />
    <text x="0" y="98" text-anchor="middle" font-size="12" font-weight="bold" fill="#0f172a">Administrador /</text>
    <text x="0" y="114" text-anchor="middle" font-size="12" font-weight="bold" fill="#0f172a">Administrador de Tienda</text>
  </g>
  <line x1="{x_actor}" y1="195" x2="{x_actor}" y2="{y_lifeline_end}" stroke="#000000" stroke-width="1.2" stroke-dasharray="6,4" />
  <polygon points="{x_actor - 4},{y_lifeline_end - 2} {x_actor},{y_lifeline_end + 8} {x_actor + 4},{y_lifeline_end - 2}" fill="#000000" />

  <!-- 2. BOUNDARY: IU_Usuario -->
  <g filter="url(#shadow)">
    <rect x="{x_iu - 65}" y="{y_top_box}" width="130" height="{h_box}" rx="2" fill="#ffffff" stroke="#000000" stroke-width="1.5" />
    <text x="{x_iu}" y="{y_top_box + 22}" text-anchor="middle" font-size="11" fill="#475569">&#171;boundary&#187;</text>
    <text x="{x_iu}" y="{y_top_box + 41}" text-anchor="middle" font-size="13" font-weight="bold" fill="#0f172a">IU_Usuario</text>
  </g>
  <line x1="{x_iu}" y1="{y_lifeline_start}" x2="{x_iu}" y2="{y_lifeline_end}" stroke="#000000" stroke-width="1.2" stroke-dasharray="6,4" />
  <polygon points="{x_iu - 4},{y_lifeline_end - 2} {x_iu},{y_lifeline_end + 8} {x_iu + 4},{y_lifeline_end - 2}" fill="#000000" />

  <!-- 3. CONTROL: UsuarioControl -->
  <g filter="url(#shadow)">
    <rect x="{x_ctrl - 75}" y="{y_top_box}" width="150" height="{h_box}" rx="2" fill="#ffffff" stroke="#000000" stroke-width="1.5" />
    <text x="{x_ctrl}" y="{y_top_box + 22}" text-anchor="middle" font-size="11" fill="#475569">&#171;control&#187;</text>
    <text x="{x_ctrl}" y="{y_top_box + 41}" text-anchor="middle" font-size="13" font-weight="bold" fill="#0f172a">UsuarioControl</text>
  </g>
  <line x1="{x_ctrl}" y1="{y_lifeline_start}" x2="{x_ctrl}" y2="{y_lifeline_end}" stroke="#000000" stroke-width="1.2" stroke-dasharray="6,4" />
  <polygon points="{x_ctrl - 4},{y_lifeline_end - 2} {x_ctrl},{y_lifeline_end + 8} {x_ctrl + 4},{y_lifeline_end - 2}" fill="#000000" />

  <!-- 4. ENTITY: t_rol -->
  <g filter="url(#shadow)">
    <rect x="{x_t_rol - 60}" y="{y_top_box}" width="120" height="{h_box}" rx="2" fill="#ffffff" stroke="#000000" stroke-width="1.5" />
    <text x="{x_t_rol}" y="{y_top_box + 22}" text-anchor="middle" font-size="11" fill="#475569">&#171;entity&#187;</text>
    <text x="{x_t_rol}" y="{y_top_box + 41}" text-anchor="middle" font-size="13" font-weight="bold" fill="#0f172a">:t_rol</text>
  </g>
  <line x1="{x_t_rol}" y1="{y_lifeline_start}" x2="{x_t_rol}" y2="{y_lifeline_end}" stroke="#000000" stroke-width="1.2" stroke-dasharray="6,4" />
  <polygon points="{x_t_rol - 4},{y_lifeline_end - 2} {x_t_rol},{y_lifeline_end + 8} {x_t_rol + 4},{y_lifeline_end - 2}" fill="#000000" />

  <!-- 5. ENTITY: t_usuario -->
  <g filter="url(#shadow)">
    <rect x="{x_t_usr - 60}" y="{y_top_box}" width="120" height="{h_box}" rx="2" fill="#ffffff" stroke="#000000" stroke-width="1.5" />
    <text x="{x_t_usr}" y="{y_top_box + 22}" text-anchor="middle" font-size="11" fill="#475569">&#171;entity&#187;</text>
    <text x="{x_t_usr}" y="{y_top_box + 41}" text-anchor="middle" font-size="13" font-weight="bold" fill="#0f172a">:t_usuario</text>
  </g>
  <line x1="{x_t_usr}" y1="{y_lifeline_start}" x2="{x_t_usr}" y2="{y_lifeline_end}" stroke="#000000" stroke-width="1.2" stroke-dasharray="6,4" />
  <polygon points="{x_t_usr - 4},{y_lifeline_end - 2} {x_t_usr},{y_lifeline_end + 8} {x_t_usr + 4},{y_lifeline_end - 2}" fill="#000000" />

  <!-- 6. ENTITY: t_usuario_rol -->
  <g filter="url(#shadow)">
    <rect x="{x_t_usr_rol - 65}" y="{y_top_box}" width="130" height="{h_box}" rx="2" fill="#ffffff" stroke="#000000" stroke-width="1.5" />
    <text x="{x_t_usr_rol}" y="{y_top_box + 22}" text-anchor="middle" font-size="11" fill="#475569">&#171;entity&#187;</text>
    <text x="{x_t_usr_rol}" y="{y_top_box + 41}" text-anchor="middle" font-size="13" font-weight="bold" fill="#0f172a">:t_usuario_rol</text>
  </g>
  <line x1="{x_t_usr_rol}" y1="{y_lifeline_start}" x2="{x_t_usr_rol}" y2="{y_lifeline_end}" stroke="#000000" stroke-width="1.2" stroke-dasharray="6,4" />
  <polygon points="{x_t_usr_rol - 4},{y_lifeline_end - 2} {x_t_usr_rol},{y_lifeline_end + 8} {x_t_usr_rol + 4},{y_lifeline_end - 2}" fill="#000000" />

  <!-- 7. ENTITY: t_usuario_permiso -->
  <g filter="url(#shadow)">
    <rect x="{x_t_usr_perm - 75}" y="{y_top_box}" width="150" height="{h_box}" rx="2" fill="#ffffff" stroke="#000000" stroke-width="1.5" />
    <text x="{x_t_usr_perm}" y="{y_top_box + 22}" text-anchor="middle" font-size="11" fill="#475569">&#171;entity&#187;</text>
    <text x="{x_t_usr_perm}" y="{y_top_box + 41}" text-anchor="middle" font-size="13" font-weight="bold" fill="#0f172a">:t_usuario_permiso</text>
  </g>
  <line x1="{x_t_usr_perm}" y1="{y_lifeline_start}" x2="{x_t_usr_perm}" y2="{y_lifeline_end}" stroke="#000000" stroke-width="1.2" stroke-dasharray="6,4" />
  <polygon points="{x_t_usr_perm - 4},{y_lifeline_end - 2} {x_t_usr_perm},{y_lifeline_end + 8} {x_t_usr_perm + 4},{y_lifeline_end - 2}" fill="#000000" />

  <!-- 8. ENTITY: t_usuario_sucursal -->
  <g filter="url(#shadow)">
    <rect x="{x_t_usr_suc - 75}" y="{y_top_box}" width="150" height="{h_box}" rx="2" fill="#ffffff" stroke="#000000" stroke-width="1.5" />
    <text x="{x_t_usr_suc}" y="{y_top_box + 22}" text-anchor="middle" font-size="11" fill="#475569">&#171;entity&#187;</text>
    <text x="{x_t_usr_suc}" y="{y_top_box + 41}" text-anchor="middle" font-size="13" font-weight="bold" fill="#0f172a">:t_usuario_sucursal</text>
  </g>
  <line x1="{x_t_usr_suc}" y1="{y_lifeline_start}" x2="{x_t_usr_suc}" y2="{y_lifeline_end}" stroke="#000000" stroke-width="1.2" stroke-dasharray="6,4" />
  <polygon points="{x_t_usr_suc - 4},{y_lifeline_end - 2} {x_t_usr_suc},{y_lifeline_end + 8} {x_t_usr_suc + 4},{y_lifeline_end - 2}" fill="#000000" />

  <!-- 9. ENTITY: t_bitacora -->
  <g filter="url(#shadow)">
    <rect x="{x_t_bita - 60}" y="{y_top_box}" width="120" height="{h_box}" rx="2" fill="#ffffff" stroke="#000000" stroke-width="1.5" />
    <text x="{x_t_bita}" y="{y_top_box + 22}" text-anchor="middle" font-size="11" fill="#475569">&#171;entity&#187;</text>
    <text x="{x_t_bita}" y="{y_top_box + 41}" text-anchor="middle" font-size="13" font-weight="bold" fill="#0f172a">:t_bitacora</text>
  </g>
  <line x1="{x_t_bita}" y1="{y_lifeline_start}" x2="{x_t_bita}" y2="{y_lifeline_end}" stroke="#000000" stroke-width="1.2" stroke-dasharray="6,4" />
  <polygon points="{x_t_bita - 4},{y_lifeline_end - 2} {x_t_bita},{y_lifeline_end + 8} {x_t_bita + 4},{y_lifeline_end - 2}" fill="#000000" />

  <!-- ==================== BARRAS DE ACTIVACIÓN ==================== -->
  <!-- IU_Usuario -->
  <rect x="{x_iu - 6}" y="222" width="12" height="825" fill="#f8fafc" stroke="#334155" stroke-width="1.2" />

  <!-- UsuarioControl -->
  <rect x="{x_ctrl - 6}" y="254" width="12" height="735" fill="#f8fafc" stroke="#334155" stroke-width="1.2" />

  <!-- :t_rol -->
  <rect x="{x_t_rol - 6}" y="318" width="12" height="38" fill="#f8fafc" stroke="#334155" stroke-width="1.2" />

  <!-- :t_usuario (Verificación y luego Insert) -->
  <rect x="{x_t_usr - 6}" y="378" width="12" height="38" fill="#f8fafc" stroke="#334155" stroke-width="1.2" />
  <rect x="{x_t_usr - 6}" y="608" width="12" height="38" fill="#f8fafc" stroke="#334155" stroke-width="1.2" />

  <!-- :t_usuario_rol -->
  <rect x="{x_t_usr_rol - 6}" y="668" width="12" height="38" fill="#f8fafc" stroke="#334155" stroke-width="1.2" />

  <!-- :t_usuario_permiso -->
  <rect x="{x_t_usr_perm - 6}" y="750" width="12" height="32" fill="#f8fafc" stroke="#334155" stroke-width="1.2" />

  <!-- :t_usuario_sucursal -->
  <rect x="{x_t_usr_suc - 6}" y="834" width="12" height="32" fill="#f8fafc" stroke="#334155" stroke-width="1.2" />

  <!-- :t_bitacora -->
  <rect x="{x_t_bita - 6}" y="892" width="12" height="38" fill="#f8fafc" stroke="#334155" stroke-width="1.2" />

  <!-- ==================== MENSAJES INICIALES ==================== -->
  <!-- 1. Actor -> IU -->
  <line x1="{x_actor}" y1="228" x2="{x_iu - 6}" y2="228" stroke="#000000" stroke-width="1.5" marker-end="url(#arrow-sync)" />
  <text x="{(x_actor + x_iu) / 2}" y="220" text-anchor="middle" font-size="11" font-weight="600" fill="#0f172a">1: solicitar_registro(datos_usuario)</text>

  <!-- 2. IU -> Ctrl -->
  <line x1="{x_iu + 6}" y1="260" x2="{x_ctrl - 6}" y2="260" stroke="#000000" stroke-width="1.5" marker-end="url(#arrow-sync)" />
  <text x="{(x_iu + x_ctrl) / 2}" y="252" text-anchor="middle" font-size="11" font-weight="600" fill="#0f172a">2: POST /api/usuarios/ (datos_usuario)</text>

  <!-- 3. Ctrl self-call: validar_campos_requeridos -->
  <path d="M {x_ctrl + 6} 276 L {x_ctrl + 32} 276 L {x_ctrl + 32} 296 L {x_ctrl + 6} 296" fill="none" stroke="#000000" stroke-width="1.4" marker-end="url(#arrow-sync)" />
  <text x="{x_ctrl + 38}" y="290" font-size="10.5" font-weight="600" fill="#0f172a">3: validar_campos_requeridos(datos)</text>

  <!-- 4. Ctrl -> :t_rol (SELECT) -->
  <line x1="{x_ctrl + 6}" y1="322" x2="{x_t_rol - 6}" y2="322" stroke="#000000" stroke-width="1.5" marker-end="url(#arrow-sync)" />
  <text x="{(x_ctrl + x_t_rol) / 2}" y="314" text-anchor="middle" font-size="10.5" font-weight="600" fill="#0f172a">4: SELECT nivel, permisos FROM t_rol WHERE id_rol = :id_rol</text>

  <!-- 5. :t_rol -> Ctrl (return) -->
  <line x1="{x_t_rol - 6}" y1="352" x2="{x_ctrl + 6}" y2="352" stroke="#000000" stroke-width="1.4" stroke-dasharray="6,4" marker-end="url(#arrow-return)" />
  <text x="{(x_ctrl + x_t_rol) / 2}" y="345" text-anchor="middle" font-size="10" font-style="italic" fill="#334155">5: return datos_rol (nivel, permisos)</text>

  <!-- 6. Ctrl -> :t_usuario (SELECT) -->
  <line x1="{x_ctrl + 6}" y1="382" x2="{x_t_usr - 6}" y2="382" stroke="#000000" stroke-width="1.5" marker-end="url(#arrow-sync)" />
  <text x="{(x_ctrl + x_t_usr) / 2}" y="374" text-anchor="middle" font-size="10.5" font-weight="600" fill="#0f172a">6: SELECT id_usuario FROM t_usuario WHERE username = :username</text>

  <!-- 7. :t_usuario -> Ctrl (return) -->
  <line x1="{x_t_usr - 6}" y1="412" x2="{x_ctrl + 6}" y2="412" stroke="#000000" stroke-width="1.4" stroke-dasharray="6,4" marker-end="url(#arrow-return)" />
  <text x="{(x_ctrl + x_t_usr) / 2}" y="405" text-anchor="middle" font-size="10" font-style="italic" fill="#334155">7: return usuario_existente</text>

  <!-- ==================== FRAGMENTO COMBINADO (alt) ==================== -->
  <rect x="35" y="432" width="{width - 70}" height="625" fill="none" stroke="#334155" stroke-width="1.3" />
  
  <!-- Pestaña alt -->
  <path d="M 35 432 L 115 432 L 128 445 L 128 456 L 35 456 Z" fill="#f8fafc" stroke="#334155" stroke-width="1.3" />
  <text x="46" y="449" font-size="11" font-weight="bold" fill="#1e293b">alt</text>
  <text x="138" y="449" font-size="11" font-weight="bold" fill="#b91c1c">[usuario_existente != null || jerarquia_invalida] (Curso Alterno: Rechazo 400 / 403)</text>

  <!-- MENSAJES CASO ERROR (8.1 y 8.2) -->
  <line x1="{x_ctrl - 6}" y1="476" x2="{x_iu + 6}" y2="476" stroke="#b91c1c" stroke-width="1.4" stroke-dasharray="5,4" marker-end="url(#arrow-error)" />
  <text x="{(x_iu + x_ctrl) / 2}" y="468" text-anchor="middle" font-size="10.5" font-weight="600" fill="#b91c1c">8.1: 400 Bad Request ("El nombre de usuario elegido ya está en uso")</text>

  <line x1="{x_iu - 6}" y1="506" x2="{x_actor}" y2="506" stroke="#b91c1c" stroke-width="1.4" stroke-dasharray="5,4" marker-end="url(#arrow-error)" />
  <text x="{(x_actor + x_iu) / 2}" y="498" text-anchor="middle" font-size="10.5" font-weight="600" fill="#b91c1c">8.2: mostrar_error("Usuario existente o rol no autorizado")</text>

  <!-- LÍNEA SEPARADORA DEL ALT -->
  <line x1="35" y1="535" x2="{width - 35}" y2="535" stroke="#64748b" stroke-width="1.2" stroke-dasharray="6,4" />
  <text x="45" y="552" font-size="11" font-weight="bold" fill="#15803d">[else: usuario_existente == null &amp;&amp; jerarquia_valida] (Curso Básico: Creación y Persistencia)</text>

  <!-- 9. Ctrl self-call: hashear_password -->
  <path d="M {x_ctrl + 6} 568 L {x_ctrl + 32} 568 L {x_ctrl + 32} 588 L {x_ctrl + 6} 588" fill="none" stroke="#000000" stroke-width="1.4" marker-end="url(#arrow-sync)" />
  <text x="{x_ctrl + 38}" y="582" font-size="10.5" font-weight="600" fill="#0f172a">9: hashear_password(password)</text>

  <!-- 10. Ctrl -> :t_usuario (INSERT) -->
  <line x1="{x_ctrl + 6}" y1="612" x2="{x_t_usr - 6}" y2="612" stroke="#000000" stroke-width="1.5" marker-end="url(#arrow-sync)" />
  <text x="{(x_ctrl + x_t_usr) / 2}" y="604" text-anchor="middle" font-size="10.5" font-weight="600" fill="#0f172a">10: INSERT INTO t_usuario(username, correo, password_hash, id_empresa, estado)</text>

  <!-- 11. :t_usuario -> Ctrl (return) -->
  <line x1="{x_t_usr - 6}" y1="642" x2="{x_ctrl + 6}" y2="642" stroke="#000000" stroke-width="1.4" stroke-dasharray="6,4" marker-end="url(#arrow-return)" />
  <text x="{(x_ctrl + x_t_usr) / 2}" y="635" text-anchor="middle" font-size="10" font-style="italic" fill="#334155">11: return id_usuario</text>

  <!-- 12. Ctrl -> :t_usuario_rol (INSERT) -->
  <line x1="{x_ctrl + 6}" y1="672" x2="{x_t_usr_rol - 6}" y2="672" stroke="#000000" stroke-width="1.5" marker-end="url(#arrow-sync)" />
  <text x="{(x_ctrl + x_t_usr_rol) / 2}" y="664" text-anchor="middle" font-size="10.5" font-weight="600" fill="#0f172a">12: INSERT INTO t_usuario_rol(id_usuario, id_rol)</text>

  <!-- 13. :t_usuario_rol -> Ctrl (return) -->
  <line x1="{x_t_usr_rol - 6}" y1="702" x2="{x_ctrl + 6}" y2="702" stroke="#000000" stroke-width="1.4" stroke-dasharray="6,4" marker-end="url(#arrow-return)" />
  <text x="{(x_ctrl + x_t_usr_rol) / 2}" y="695" text-anchor="middle" font-size="10" font-style="italic" fill="#334155">13: return confirmacion_rol</text>

  <!-- ==================== OPT: PERMISOS DIRECTOS ==================== -->
  <rect x="470" y="722" width="{x_t_usr_perm - 450}" height="70" fill="none" stroke="#64748b" stroke-width="1.1" />
  <path d="M 470 722 L 530 722 L 540 732 L 540 740 L 470 740 Z" fill="#f8fafc" stroke="#64748b" stroke-width="1.1" />
  <text x="478" y="734" font-size="9.5" font-weight="bold" fill="#334155">opt</text>
  <text x="548" y="734" font-size="9.5" font-weight="bold" fill="#334155">[ids_permisos directos != null]</text>

  <!-- loop permisos -->
  <rect x="485" y="742" width="{x_t_usr_perm - 470}" height="44" fill="none" stroke="#94a3b8" stroke-width="1" stroke-dasharray="4,3" />
  <text x="492" y="753" font-size="9" font-style="italic" fill="#475569">loop [para cada id_permiso]</text>

  <line x1="{x_ctrl + 6}" y1="762" x2="{x_t_usr_perm - 6}" y2="762" stroke="#000000" stroke-width="1.3" marker-end="url(#arrow-sync)" />
  <text x="{(x_ctrl + x_t_usr_perm) / 2}" y="756" text-anchor="middle" font-size="9.5" font-weight="500" fill="#0f172a">14: INSERT INTO t_usuario_permiso(id_usuario, id_permiso, activo)</text>

  <line x1="{x_t_usr_perm - 6}" y1="778" x2="{x_ctrl + 6}" y2="778" stroke="#000000" stroke-width="1.2" stroke-dasharray="5,3" marker-end="url(#arrow-return)" />
  <text x="{(x_ctrl + x_t_usr_perm) / 2}" y="773" text-anchor="middle" font-size="9" font-style="italic" fill="#334155">15: return confirmacion_permiso</text>

  <!-- ==================== OPT: SUCURSALES ASIGNADAS ==================== -->
  <rect x="470" y="804" width="{x_t_usr_suc - 450}" height="70" fill="none" stroke="#64748b" stroke-width="1.1" />
  <path d="M 470 804 L 530 804 L 540 814 L 540 822 L 470 822 Z" fill="#f8fafc" stroke="#64748b" stroke-width="1.1" />
  <text x="478" y="816" font-size="9.5" font-weight="bold" fill="#334155">opt</text>
  <text x="548" y="816" font-size="9.5" font-weight="bold" fill="#334155">[ids_sucursales asignadas != null]</text>

  <!-- loop sucursales -->
  <rect x="485" y="824" width="{x_t_usr_suc - 470}" height="44" fill="none" stroke="#94a3b8" stroke-width="1" stroke-dasharray="4,3" />
  <text x="492" y="835" font-size="9" font-style="italic" fill="#475569">loop [para cada id_sucursal]</text>

  <line x1="{x_ctrl + 6}" y1="844" x2="{x_t_usr_suc - 6}" y2="844" stroke="#000000" stroke-width="1.3" marker-end="url(#arrow-sync)" />
  <text x="{(x_ctrl + x_t_usr_suc) / 2}" y="838" text-anchor="middle" font-size="9.5" font-weight="500" fill="#0f172a">16: INSERT INTO t_usuario_sucursal(id_usuario, id_sucursal)</text>

  <line x1="{x_t_usr_suc - 6}" y1="860" x2="{x_ctrl + 6}" y2="860" stroke="#000000" stroke-width="1.2" stroke-dasharray="5,3" marker-end="url(#arrow-return)" />
  <text x="{(x_ctrl + x_t_usr_suc) / 2}" y="855" text-anchor="middle" font-size="9" font-style="italic" fill="#334155">17: return confirmacion_sucursal</text>

  <!-- ==================== AUDITORÍA / BITÁCORA ==================== -->
  <line x1="{x_ctrl + 6}" y1="896" x2="{x_t_bita - 6}" y2="896" stroke="#000000" stroke-width="1.5" marker-end="url(#arrow-sync)" />
  <text x="{(x_ctrl + x_t_bita) / 2}" y="888" text-anchor="middle" font-size="10.5" font-weight="600" fill="#0f172a">18: INSERT INTO t_bitacora(id_usuario, id_empresa, modulo='USUARIOS', accion='USUARIO_CREADO', ...)</text>

  <line x1="{x_t_bita - 6}" y1="924" x2="{x_ctrl + 6}" y2="924" stroke="#000000" stroke-width="1.4" stroke-dasharray="6,4" marker-end="url(#arrow-return)" />
  <text x="{(x_ctrl + x_t_bita) / 2}" y="917" text-anchor="middle" font-size="10" font-style="italic" fill="#334155">19: return confirmacion_log</text>

  <!-- ==================== RETORNOS FINALES ==================== -->
  <!-- 20. Ctrl -> IU (201 Created) -->
  <line x1="{x_ctrl - 6}" y1="970" x2="{x_iu + 6}" y2="970" stroke="#000000" stroke-width="1.4" stroke-dasharray="6,4" marker-end="url(#arrow-return)" />
  <text x="{(x_iu + x_ctrl) / 2}" y="962" text-anchor="middle" font-size="10.5" font-weight="600" fill="#15803d">20: 201 Created (id_usuario, "Usuario registrado exitosamente")</text>

  <!-- 21. IU -> Actor (Renderizar / Notificar) -->
  <line x1="{x_iu - 6}" y1="1010" x2="{x_actor}" y2="1010" stroke="#000000" stroke-width="1.4" stroke-dasharray="6,4" marker-end="url(#arrow-return)" />
  <text x="{(x_actor + x_iu) / 2}" y="1002" text-anchor="middle" font-size="10.5" font-weight="600" fill="#0f172a">21: mostrar_confirmacion_y_actualizar()</text>

</svg>"""
    return svg

def main():
    output_dir = os.path.join("docs", "diagramas_secuencia_uml")
    os.makedirs(output_dir, exist_ok=True)
    
    svg_content = build_svg_cu01w()
    svg_path = os.path.join(output_dir, "CU01W_Gestionar_Usuarios_Roles_Secuencia.svg")
    png_path = os.path.join(output_dir, "CU01W_Gestionar_Usuarios_Roles_Secuencia.png")
    
    with open(svg_path, "w", encoding="utf-8") as f:
        f.write(svg_content)
    print(f"[OK] SVG generado en: {svg_path}")
    
    png_bytes = resvg_py.svg_to_bytes(svg_string=svg_content, zoom=2.0)
    with open(png_path, "wb") as f:
        f.write(png_bytes)
    print(f"[OK] PNG de alta resolución (zoom 2x) generado en: {png_path} ({len(png_bytes)} bytes)")

if __name__ == "__main__":
    main()
