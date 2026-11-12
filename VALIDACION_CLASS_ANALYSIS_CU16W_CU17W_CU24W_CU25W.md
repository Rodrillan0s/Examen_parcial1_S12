# Matriz de Validación de Diagramas de Análisis de Clases (CU16W, CU17W, CU24W, CU25W)
**Proyecto:** AuroraStore SaaS  
**Herramienta:** Sparx Enterprise Architect (JavaScript Automation)  
**Estándar:** UML 2.5 / Metodología ICONIX (View of Participating Classes - VOPC)  
**Fecha:** 11 de Noviembre de 2026  

---

## 1. Cobertura Estructural de los 4 Casos de Uso

| Caso de Uso | Actor | Boundaries (Vistas/Modales) | Controllers (Rutas & Servicios) | Entities (Persistencia PostgreSQL / Cache) | Conectores / Multiplicidad | Estado |
| :--- | :--- | :--- | :--- | :--- | :--- | :---: |
| **CU16W**<br>Registrar venta presencial (POS / Caja) | Cajero | `CajaPosView`<br>`CobroModal`<br>`ComprobanteVentaModal`<br>`CajaCerradaDialog`<br>`ErrorDialog` | `pos_routes`<br>`pos_services`<br>`caja_services` | `t_caja_sesion`<br>`t_venta`<br>`t_detalle_venta`<br>`t_pago`<br>`t_inventario`<br>`t_bitacora` | • Association (Actor $\rightarrow$ Boundary)<br>• Dependency `«use»` (Boundary $\rightarrow$ Controller $\rightarrow$ Entity)<br>• DB Associations (1 a 1..*, 1 a 0..*) | **VALIDADO** |
| **CU17W**<br>Registrar venta online (Checkout) | Cliente / Usuario | `CheckoutView`<br>`PasarelaPagoModal`<br>`ConfirmacionOrdenModal`<br>`ErrorPagoDialog` | `pago_routes`<br>`pago_services`<br>`offline_cache_manager` | `t_carrito`<br>`t_venta`<br>`t_detalle_venta`<br>`t_pago`<br>`t_inventario`<br>`t_bitacora` | • Association (Actor $\rightarrow$ Boundary)<br>• Dependency `«use»`<br>• DB Associations (1 a 1..*) | **VALIDADO** |
| **CU24W**<br>Solicitar devolución (Cliente) | Cliente / Usuario | `MisDevolucionesView`<br>`SolicitudDevolucionModal`<br>`VentanaVencidaDialog`<br>`ErrorDialog` | `devoluciones_routes`<br>`devoluciones_services` | `t_cliente`<br>`t_venta`<br>`t_detalle_venta`<br>`t_devolucion`<br>`t_bitacora` | • Association (Actor $\rightarrow$ Boundary)<br>• Dependency `«use»`<br>• DB Associations (1 a 0..*) | **VALIDADO** |
| **CU25W**<br>Gestionar devoluciones (Admin) | AdminTienda | `BandejaDevolucionesView`<br>`RevisionDevolucionModal`<br>`ComprobanteCreditoModal`<br>`ErrorDialog` | `devoluciones_routes`<br>`devoluciones_services` | `t_devolucion`<br>`t_inventario`<br>`t_movimiento_inventario`<br>`t_bitacora` | • Association (Actor $\rightarrow$ Boundary)<br>• Dependency `«use»`<br>• DB Associations (1 a 0..*) | **VALIDADO** |

---

## 2. Verificación de Trazabilidad con Diagramas de Secuencia Previos

1. **Correspondencia de Actores:**
   - CU16W: `Cajero` (coincide con la lifeline `cajero : Cajero`).
   - CU17W: `Cliente / Usuario` (coincide con la lifeline `cliente : Cliente`).
   - CU24W: `Cliente / Usuario` (coincide con la lifeline `cliente : Cliente`).
   - CU25W: `AdminTienda` (coincide con la lifeline `admin : AdminTienda`).

2. **Correspondencia de Métodos y Operaciones:**
   - Los endpoints REST (`registrar_venta_pos`, `verificar_estado_caja`, `iniciar_checkout`, `procesar_transaccion_online`, `obtener_mis_devoluciones`, `crear_solicitud_devolucion`, `listar_devoluciones_pendientes`, `emitir_dictamen`) corresponden a los mensajes de entrada de los routers en la secuencia.
   - Las operaciones de servicio (`procesar_venta_caja`, `descontar_stock_venta`, `obtener_sesion_vigente`, `procesar_pedido_ecommerce`, `validar_elegibilidad_ley453`, `procesar_dictamen_administrativo`, `reingresar_stock_inventario`) implementan la lógica de negocio descrita en la secuencia.
   - Los métodos de persistencia DAO de cada entidad (`findAbiertaByUsuario`, `insert`, `bulkInsert`, `descontarStock`, `findItemsByCliente`, `clearByCliente`, `updateDictamen`, `reingresarStock`) formalizan las consultas SQL de las lifelines de base de datos.

3. **Prueba de Sintaxis Node.js:**
   - Comando ejecutado: `node --check AuroraStore_CU16W_CU17W_CU24W_CU25W_ClassAnalysis_FINAL_EA.js`
   - Resultado: **Exit Code 0 (Sin errores sintácticos)**.
   - 0 apariciones de `Repository.Execute`.
