# AuroraStore — Iteración 1 SaaS

Leer este archivo antes de cada tarea. Preservar datos, diseño y funcionalidades P1.

- Trabajar en la rama actual por instrucción del usuario. No crear ramas ni publicar cambios sin solicitud.
- Codex: backend, migraciones, seguridad, contratos API y pruebas. Antigravity: Angular, UX, guards, menús e integración visual; no modificar seguridad o esquemas desde frontend.
- No modificar `mobile/`. Su migración se hará más adelante usando `docs/ITER1_CONTEXT.md` y los contratos guardados.
- Respaldos/restauraciones (CU41W) quedan expresamente fuera de alcance, incluidos sus archivos, APIs y UI.
- Reutilizar `empresa`, `t_usuario`, `t_sucursal`, `t_empleado`, `t_usuario_sucursal` y RBAC. No duplicar entidades P1.
- Básico: hasta 2 sucursales activas; Profesional: hasta 10 y motor de reportes existente. Suscripciones administrativas/simuladas; sin cobros recurrentes.
- No iniciar offline/sincronización, nueva IA ni fidelización.
- Aislamiento y permisos siempre en servidor. Un `id_empresa` del cliente selecciona contexto, no autoriza.
- Migraciones explícitas y reversibles; no ejecutar cambios de esquema, respaldos o restauraciones en la base real sin autorización específica. Nunca importar/arrancar la aplicación para probar contra la base real.
- Registrar cambios significativos en `docs/AGENT_CHANGES.md`: fecha | agente | archivos/módulos | cambio | motivo | migración/API afectada | pruebas ejecutadas | pendientes.
- Documentar contratos, migraciones y permisos antes de entregar a Antigravity. No rediseñar Angular ni cambiar contratos P1 silenciosamente.
- Ante incompatibilidad arquitectónica o riesgo de pérdida de datos: detener ese cambio, documentar y solicitar validación. No asignar planes/vigencias a empresas existentes automáticamente.
- No inventar pruebas. Distinguir pruebas unitarias, integración aislada y verificaciones pendientes.
