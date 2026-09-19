# Catálogo de Diagramas de Navegación Web (SI2 - UAGRM)
## Sistema E-Commerce Multi-Tenant para Venta de Ropa Aura

Este directorio contiene los **Diagramas de Navegación Web** que modelan la arquitectura de pantallas, enrutamiento, transiciones y vinculación con los **Casos de Uso** del sistema Aura.

Siguiendo el estándar de cátedra UAGRM (`2.1.3.4. Diagramas de Navegación`), **se evitó un único diagrama monolítico ilegible** dividiendo la navegación en **4 diagramas modulares y cohesivos** que parten de la misma raíz común:

$$\text{Raíz Común: } \langle\text{SISTEMA E-COMMERCE AURA}\rangle \longrightarrow \text{Portal Web / Inicio de Sesión}$$

---

### Principio de Modularidad y Cohesión de Flujos

Las pantallas que poseen una relación operativa directa se mantienen juntas dentro de su propio diagrama para garantizar un análisis claro sin cortes artificiales:

1. **Flujo E-Commerce Cliente (DN-01)**:
   - Catálogo $\rightarrow$ Ficha de Prenda / Variantes $\rightarrow$ Disponibilidad en Sucursal $\rightarrow$ Carrito $\rightarrow$ Checkout $\rightarrow$ Pasarela de Pago $\rightarrow$ Confirmación de Pedido $\rightarrow$ Mis Pedidos y Mis Reservas.
2. **Flujo Operativo de Mostrador y Sucursal (DN-02)**:
   - Terminal POS $\rightarrow$ Procesamiento de Pago en Caja (Efectivo/QR) $\rightarrow$ Emisión Fiscal (Factura/Recibo) $\rightarrow$ Despacho de Reservas $\rightarrow$ Afectación de Kardex.
3. **Flujo Administrativo, Catálogo Central y Auditoría (DN-03)**:
   - Dashboard KPIs $\rightarrow$ Gestión de Productos/Colecciones $\rightarrow$ Proveedores y Sucursales $\rightarrow$ Roles RBAC $\rightarrow$ Bitácora de Auditoría del Sistema.

---

### Índice de Diagramas de Navegación

| Código | Título del Diagrama | Ámbito / Módulos Cubiertos | Casos de Uso Vinculados | SVG | PNG (2x) |
|---|---|---|---|---|---|
| **DN-00** | **Diagrama de Navegación Maestro (Hub General)** | Macro-enrutador del sistema que distribuye el acceso según el rol hacia los 3 subsistemas | Visión Global de los 25 CUs | [`DN00_Mapa_General_Navegacion_Sistema_Aura.svg`](./DN00_Mapa_General_Navegacion_Sistema_Aura.svg) | [`DN00_Mapa_General_Navegacion_Sistema_Aura.png`](./DN00_Mapa_General_Navegacion_Sistema_Aura.png) |
| **DN-01** | **Navegación Tienda E-Commerce, Catálogo y Checkout** | Catálogo Retail, Ficha de Prenda, Carrito, Checkout, Pasarela de Pago, Mis Reservas y Mis Pedidos | CU05, CU06, CU07, CU08, CU09, CU10, CU11, CU26/M15, CU_W27 | [`DN01_Navegacion_Cliente_Ecommerce_Checkout.svg`](./DN01_Navegacion_Cliente_Ecommerce_Checkout.svg) | [`DN01_Navegacion_Cliente_Ecommerce_Checkout.png`](./DN01_Navegacion_Cliente_Ecommerce_Checkout.png) |
| **DN-02** | **Navegación Operativa de Sucursal, POS y Facturación** | Punto de Venta (POS), Cobro en Caja, Emisión de Comprobante Fiscal, Entrega de Reservas y Kardex | CU_W22, CU_W24, CU_W25, CU_W28, CU_W29 | [`DN02_Navegacion_Operativa_Sucursal_POS_Caja.svg`](./DN02_Navegacion_Operativa_Sucursal_POS_Caja.svg) | [`DN02_Navegacion_Operativa_Sucursal_POS_Caja.png`](./DN02_Navegacion_Operativa_Sucursal_POS_Caja.png) |
| **DN-03** | **Navegación Panel Administrativo, Catálogo y Auditoría** | Dashboard KPIs, Productos y Variantes, Temporadas, Proveedores, Empresas/Sucursales, Roles y Bitácora | CU01, CU02, CU36, CU_W20, CU_W21, CU_W23, Bitácora | [`DN03_Navegacion_Administracion_Catalogo_Auditoria.svg`](./DN03_Navegacion_Administracion_Catalogo_Auditoria.svg) | [`DN03_Navegacion_Administracion_Catalogo_Auditoria.png`](./DN03_Navegacion_Administracion_Catalogo_Auditoria.png) |

---

### Notación Gráfica Utilizada (Estándar UAGRM)

* **Nodo Raíz (`<SISTEMA ...>`)**: Cápsula verde con borde verde (`#16a34a`).
* **Pantallas de Entrada / Hubs**: Rectángulos blancos con esquinas redondeadas y subtítulo descriptivo.
* **Módulos Funcionales**: Rombos de color distintivo con texto blanco en negrita:
  - Azul (`#0284c7`): Catálogo y Exploración Retail.
  - Verde (`#16a34a`): Transacciones de Compra / Cobros / Seguridad.
  - Naranja (`#ea580c`): Área Personal / Reservas / Proveedores.
  - Rojo (`#dc2626`): Terminal POS y Venta Presencial.
  - Púrpura (`#7c3aed`): Auditoría, BI, Kardex e Inventario.
* **Páginas de Interfaz**: Cajas blancas con borde gris (`Página: [Nombre]`).
* **Modales / Drawers**: Cajas amarillas con borde discontinuo (`Modal/Drawer: [Nombre]`).
* **Cajas de Caso de Uso**: Cajas celestes con etiqueta `«CU» [Código]: [Título]`.
* **Transiciones entre Pantallas**: Flechas con etiquetas de evento desencadenante (`[Click en Prenda]`, `[Venta Asentada]`, `[Pago Aprobado]`, etc.).
