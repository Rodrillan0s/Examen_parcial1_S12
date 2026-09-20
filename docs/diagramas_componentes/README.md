# Diagramas de Componentes y Subsistemas - Sistema Web de Comercio Aura (SI2)

Este directorio contiene los **Diagramas de Componentes y Subsistemas** bajo el estándar **UML 2.5**, diseñados respetando estrictamente la plantilla y simbología solicitada por la cátedra de **Sistemas de Información II (UAGRM)**.

---

## 1. Estructura de Simbología y Convenciones de Diseño

Siguiendo la plantilla oficial:
1. **Subsistemas (Icono Carpeta/Paquete UML)**: Representan los límites funcionales de alto nivel del sistema.
2. **Cuadro Delimitador de Implementación**: 
   - **Dentro del Cuadro**: Subsistemas **implementados y activos** en la arquitectura del sistema.
   - **Fuera del Cuadro**: Subsistemas **no implementados o proyectados** para iteraciones futuras.
3. **Componente Ejecutable Central**: `<<source>> run.py` (entrypoint del backend que conecta las rutas y orquesta las dependencias).
4. **Librerías y APIs**:
   - `<<library>>`: Librerías internas y paquetes de terceros (FastAPI, psycopg2, PyJWT, Angular, TailwindCSS, etc.).
   - `<<API>>`: Servicios e interfaces externas (Cloudinary, PayPal API).
5. **Base de Datos**: Contenedor `BASE DE DATOS` con el `SGBD`, el servicio de hosting (`<<cloud service>> Oracle Cloud / VPS`) y la base de datos relacional (`<<database PostgreSQL>> comercio`).
6. **Componentes Internos de Subsistemas**:
   - **Capa Presentación**: `<<UI Component>>` (componentes Angular TS/HTML).
   - **Controlador / Rutas**: `<<router>>` (endpoints FastAPI).
   - **Lógica de Negocio**: `<<service>>` (servicios de aplicación y reglas de negocio).
   - **Acceso a Datos**: `<<repository>>` (repositorios con queries SQL parametrizadas a PostgreSQL).
   - **Persistencia**: `<<database table>>` (tablas del esquema `comercio`).
   - **Dependencias**: `<<library>>` y `<<API>>` específicas del subsistema.

---

## 2. Catálogo de Diagramas Generados

| Identificador | Archivo SVG | Archivo PNG | Descripción |
| :--- | :--- | :--- | :--- |
| **DC00** | [DC00 SVG](./DC00_Diagrama_General_Componentes_Subsistemas.svg) | [DC00 PNG](./DC00_Diagrama_General_Componentes_Subsistemas.png) | **Diagrama General Macro**: Muestra subsistemas implementados vs. futuros, `run.py`, librerías, APIs y Base de Datos. |
| **DC01** | [DC01 SVG](./DC01_Subsistema_Autenticacion_Usuarios.svg) | [DC01 PNG](./DC01_Subsistema_Autenticacion_Usuarios.png) | **Subsistema Autenticación y Gestión de Usuarios**: Login, RBAC, Perfil, Tokens JWT y tablas de seguridad. |
| **DC02** | [DC02 SVG](./DC02_Subsistema_Gestion_Catalogo.svg) | [DC02 PNG](./DC02_Subsistema_Gestion_Catalogo.png) | **Subsistema de Gestión de Catálogo**: Productos, Categorías, Marcas, Cloudinary y búsqueda. |
| **DC03** | [DC03 SVG](./DC03_Subsistema_Sucursales_Inventario_Proveedores.svg) | [DC03 PNG](./DC03_Subsistema_Sucursales_Inventario_Proveedores.png) | **Subsistema Sucursales, Inventario y Proveedores**: Stock multialmacén, compras, movimientos y geolocalización. |
| **DC04** | [DC04 SVG](./DC04_Subsistema_Gestion_Ecommerce.svg) | [DC04 PNG](./DC04_Subsistema_Gestion_Ecommerce.png) | **Subsistema de Gestión de E-Commerce**: Catálogo público, carrito, checkout, pagos con PayPal. |
| **DC05** | [DC05 SVG](./DC05_Subsistema_Reservas.svg) | [DC05 PNG](./DC05_Subsistema_Reservas.png) | **Subsistema de Reservas**: Solicitud de apartado en sucursal, confirmación y control de vencimiento. |
| **DC06** | [DC06 SVG](./DC06_Subsistema_Punto_De_Venta_POS.svg) | [DC06 PNG](./DC06_Subsistema_Punto_De_Venta_POS.png) | **Subsistema de Punto de Venta (POS)**: Facturación física, emisión de recibos PDF (ReportLab), pagos locales. |

---

## 3. Detalle de Subsistemas y Componentes

### DC00: Diagrama General Macro
- **Subsistemas Dentro del Cuadro (Implementados)**:
  1. `AUTENTICACIÓN Y GESTIÓN DE USUARIOS`
  2. `GESTIÓN DE CATÁLOGO`
  3. `GESTIÓN SUCURSALES, INVENTARIO Y PROVEEDORES`
  4. `GESTIÓN DE E-COMMERCE`
  5. `RESERVAS`
  6. `GESTIÓN DE PUNTO DE VENTA (POS)`
- **Subsistemas Fuera del Cuadro (Futuros / No Implementados)**:
  1. `GESTIÓN DE PEDIDOS Y REPORTES`
  2. `INTELIGENCIA ARTIFICIAL Y EXPERIENCIA DEL CLIENTE`
- **Componente Orquestador**: `<<source>> run.py`
- **Librerías Backend/Frontend**: FastAPI, psycopg2, python-dotenv, Gunicorn, Angular, TailwindCSS, PyJWT, ReportLab, CloudinarySDK, Requests.
- **APIs Externas**: PayPal API, Cloudinary.
- **Base de Datos**: PostgreSQL (`comercio`) sobre Oracle Cloud / VPS.

### DC01: Autenticación y Gestión de Usuarios
- **UI**: `login.component`, `lista-usuarios.component`, `perfil.component`, `roles-rbac.component`
- **Routes**: `auth_routes.py`, `users_routes.py`, `profile_routes.py`, `rbac_routes.py`
- **Services**: `auth_services.py`, `users_services.py`, `profile_services.py`, `rbac_services.py`
- **Repositories**: `auth_repos.py`, `users_repos.py`, `profile_repos.py`, `rbac_repos.py`
- **Tablas**: `t_usuario`, `t_rol`, `t_permiso`, `t_rol_permiso`, `t_sesion`, `t_empresa`
- **Dependencias**: PyJWT, werkzeug, email-validator, FastAPI

### DC02: Gestión de Catálogo
- **UI**: `productos.component`, `categorias.component`, `marcas.component`, `detalle-producto.component`
- **Routes**: `productos_routes.py`, `categorias_routes.py`, `marcas_routes.py`, `busqueda_routes.py`
- **Services**: `productos_services.py`, `categorias_services.py`, `marcas_services.py`, `busqueda_services.py`
- **Repositories**: `productos_repos.py`, `categorias_repos.py`, `marcas_repos.py`, `busqueda_repos.py`
- **Tablas**: `t_producto`, `t_categoria`, `t_marca`, `t_imagen_producto`, `t_especificacion_producto`
- **Dependencias**: CloudinarySDK, Pillow, Requests, FastAPI

### DC03: Sucursales, Inventario y Proveedores
- **UI**: `sucursales.component`, `inventario-stock.component`, `movimientos-stock.component`, `proveedores.component`
- **Routes**: `sucursales_routes.py`, `inventario_routes.py`, `movimientos_routes.py`, `proveedores_routes.py`
- **Services**: `sucursales_services.py`, `inventario_services.py`, `movimientos_services.py`, `proveedores_services.py`
- **Repositories**: `sucursales_repos.py`, `inventario_repos.py`, `movimientos_repos.py`, `proveedores_repos.py`
- **Tablas**: `t_sucursal`, `t_inventario`, `t_movimiento_inventario`, `t_proveedor`, `t_orden_compra`
- **Dependencias**: Leaflet, psycopg2, pydantic, FastAPI

### DC04: Gestión de E-Commerce
- **UI**: `catalogo.component`, `carrito-drawer.component`, `checkout.component`, `pago.component`
- **Routes**: `catalogo_routes.py`, `carrito_routes.py`, `pedido_routes.py`, `pago_routes.py`
- **Services**: `catalogo_services.py`, `carrito_services.py`, `pedido_services.py`, `pago_services.py`
- **Repositories**: `catalogo_repos.py`, `carrito_repos.py`, `pedido_repos.py`, `pago_repos.py`
- **Tablas**: `t_carrito`, `t_carrito_item`, `t_venta`, `t_detalle_venta`, `t_pago`, `t_metodo_pago`
- **Dependencias**: PayPal Sandbox, Requests, Angular SSR, TailwindCSS

### DC05: Reservas
- **UI**: `reserva-modal.component`, `mis-reservas.component`, `gestion-reservas.component`, `detalle-reserva.component`
- **Routes**: `reserva_routes.py`, `reserva_admin_routes.py`, `stock_reserva_routes.py`, `notif_reserva_routes.py`
- **Services**: `reserva_services.py`, `reserva_admin_services.py`, `stock_reserva_services.py`, `notif_reserva_services.py`
- **Repositories**: `reserva_repos.py`, `reserva_admin_repos.py`, `stock_reserva_repos.py`, `notif_reserva_repos.py`
- **Tablas**: `t_reserva`, `t_detalle_reserva`, `t_inventario`, `t_sucursal`, `t_usuario`
- **Dependencias**: datetime/cron, smtplib, psycopg2, FastAPI

### DC06: Punto de Venta (POS)
- **UI**: `pos-terminal.component`, `pos-facturacion.component`, `cierre-caja.component`, `ticket-impresion.component`
- **Routes**: `pos_routes.py`, `facturacion_routes.py`, `caja_routes.py`, `comprobante_routes.py`
- **Services**: `pos_services.py`, `facturacion_services.py`, `caja_services.py`, `comprobante_services.py`
- **Repositories**: `pos_repos.py`, `facturacion_repos.py`, `caja_repos.py`, `comprobante_repos.py`
- **Tablas**: `t_venta_pos`, `t_detalle_venta_pos`, `t_caja_sesion`, `t_movimiento_caja`, `t_comprobante`
- **Dependencias**: ReportLab, barcode, psycopg2, FastAPI
