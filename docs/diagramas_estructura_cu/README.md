# Diagramas de Estructura de Casos de Uso (Arquitectura de Navegación del Sistema)
### Sistema Multi-Tenant de Moda y Alta Costura — AURA Atelier
**Materia:** Sistemas de Información II (SI2) - UAGRM  

---

## 1. Introducción y Fundamento Metodológico

El **Diagrama de Estructura de Casos de Uso (Control de Navegación)** modela la jerarquía navegacional y funcional completa del software desde el punto de entrada del usuario hasta la invocación de cada Caso de Uso específico.

Siguiendo la metodología formal y el estándar docente establecido para SI2 (ejemplos de referencia *Agroenlace* y *Emergencias Vehiculares*), cada flujo responde a la siguiente taxonomía de 5 niveles:

1. **Nivel 0 (Raíz del Sistema):** Nodo elíptico/píldora con el estereotipo `<SISTEMA NOMBRE_SISTEMA>`.
2. **Nivel 1 (Puntos de Entrada / Autenticación):** Acceso al sistema (`Pantalla de Inicio de Sesión` y `Portal Web / Catálogo Público`).
3. **Nivel 2 (Centro de Control):** Nodo de navegación orquestador (`Panel de Control General (Seleccione un módulo)`).
4. **Nivel 3 (Módulos / Subsistemas):** Nodos romboidales (`Módulo: [Nombre del Módulo]`) diferenciados por paleta cromática según el subsistema.
5. **Nivel 4 (Vistas de Interfaz / Páginas):** Vistas físicas de interfaz (`Página: [Nombre de la Vista]`).
6. **Nivel 5 (Casos de Uso Concretos):** Nodos finales con estereotipo `«CU» CUxx: [Nombre del Caso de Uso]`.

---

## 2. Mapa Completo de los 29 Casos de Uso del Sistema AURA

A continuación se detalla la asignación de la totalidad de los Casos de Uso (Iteración 1 e Iteración 2) dentro de la arquitectura de navegación:

### Subsistema 1: Gestión de Usuarios y Autenticación
- **Página de Autenticación / Registro:**
  - `«CU» CU01: Registrarse en el Sistema` (Autogestión de clientes)
  - `«CU» CU02: Iniciar Sesión` (Acceso seguro JWT y RBAC)
  - `«CU» CU03: Cerrar Sesión` (Invalidación de sesión)
- **Página de Administración de Cuentas y Seguridad:**
  - `«CU» CU14: Administrar Usuarios y Roles` (CRUD de personal y permisos)
  - `«CU» Bitácora: Consultar Auditoría y Trazabilidad` (Registro de eventos)

### Subsistema 2: Catálogo y Colecciones de Moda
- **Página de Exploración Pública de Prendas:**
  - `«CU» CU04/CU05: Buscar y Filtrar Catálogo` (Filtros por talla, color, precio, categoría)
  - `«CU» CU06: Consultar Detalle de Prenda` (Ficha técnica, telas, variantes)
- **Página de Administración de Catálogo y Confección:**
  - `«CU» CU17: Gestionar Prendas` (Alta, baja, edición de prendas)
  - `«CU» CU18: Gestionar Variantes (Talla/Color)` (Atributos físicos de prendas)
  - `«CU» CU19: Gestionar Categorías` (Clasificación taxonómica)
  - `«CU» CU20: Gestionar Colecciones de Temporada` (Lanzamientos de moda)

### Subsistema 3: Sucursales, Almacén e Inventario Físico
- **Página de Stock y Almacén:**
  - `«CU» CU07: Consultar Disponibilidad por Sucursal` (Inventario multitienda)
  - `«CU» CU15: Administrar Sucursales` (Gestión de sedes físicas)
  - `«CU» CU16: Administrar Inventario y Almacén` (Control de stock general)
  - `«CU» CU21: Registrar Ingreso de Mercadería / Ajuste` (Entradas de lote)
- **Página de Operaciones Logísticas:**
  - `«CU» CU22: Transferir Stock entre Sucursales` (Movimiento inter-sucursales)
  - `«CU» CU23: Notificar Alerta de Stock Mínimo` (Monitoreo de desabastecimiento)
  - `«CU» CU26: Consultar Kárdex y Movimientos` (Historial de transacciones de stock)

### Subsistema 4: E-Commerce, Compras y Pasarela de Pagos
- **Página de Carrito y Checkout Online:**
  - `«CU» CU08: Gestionar Carrito de Compras` (Persistencia y cálculo en vivo)
  - `«CU» CU09: Realizar Compra y Pago Online` (Integración PayPal / Pasarela)
- **Página de Seguimiento y Facturación Web:**
  - `«CU» CU11: Consultar Historial de Pedidos` (Seguimiento de compras y envíos)
  - `«CU» CU27: Emitir Comprobante Digital` (Generación de voucher/factura digital)

### Subsistema 5: Reservas y Citas de Alta Costura
- **Página de Reservas y Ateliers:**
  - `«CU» CU10: Gestionar Reserva de Prendas` (Reserva anticipada exclusiva)
  - `«CU» CU25: Agendar Cita de Prueba en Sucursal` (Prueba de vestuario en tienda)

### Subsistema 6: Punto de Venta (POS) en Sucursales Físicas
- **Página de Terminal Punto de Venta:**
  - `«CU» CU24: Registrar Venta en Mostrador (POS)` (Venta directa con escaneo de SKU)
  - `«CU» CU28: Emitir Factura / Comprobante POS` (Emisión de recibo fiscal)
  - `«CU» CU29: Gestionar Apertura y Cierre de Caja` (Arqueo y control de efectivo)

### Subsistemas Proyectados (Fases Futuras)
- **Módulo: Producción y Confección a Medida** (Patronaje, ficha técnica de telas, órdenes de taller)
- **Módulo: CRM, Marketing y Fidelización** (Programas de puntos, promociones VIP y campañas de moda)

---

## 3. Catálogo de Archivos Generados

Los diagramas han sido generados vectorialmente en alta precisión (SVG) y renderizados a imágenes PNG de alta resolución (2x DPI) para su visualización e impresión:

| ID | Diagrama | Archivo SVG | Archivo PNG |
|---|---|---|---|
| **DE-00** | **Estructura General del Sistema AURA (Master 29 CUs)** | [Ver SVG](./DE_CU00_Estructura_Casos_De_Uso_General_Sistema_Aura.svg) | [Ver PNG](./DE_CU00_Estructura_Casos_De_Uso_General_Sistema_Aura.png) |
| **DE-01** | Sub. 1: Usuarios y Autenticación | [Ver SVG](./DE_CU01_Estructura_Usuarios_Autenticacion.svg) | [Ver PNG](./DE_CU01_Estructura_Usuarios_Autenticacion.png) |
| **DE-02** | Sub. 2: Catálogo y Colecciones de Moda | [Ver SVG](./DE_CU02_Estructura_Catalogo_Colecciones.svg) | [Ver PNG](./DE_CU02_Estructura_Catalogo_Colecciones.png) |
| **DE-03** | Sub. 3: Sucursales, Almacén e Inventario | [Ver SVG](./DE_CU03_Estructura_Sucursales_Inventario.svg) | [Ver PNG](./DE_CU03_Estructura_Sucursales_Inventario.png) |
| **DE-04** | Sub. 4: E-Commerce, Compras y Pagos | [Ver SVG](./DE_CU04_Estructura_Ecommerce_Compras_Pagos.svg) | [Ver PNG](./DE_CU04_Estructura_Ecommerce_Compras_Pagos.png) |
| **DE-05** | Sub. 5: Reservas y Citas | [Ver SVG](./DE_CU05_Estructura_Reservas.svg) | [Ver PNG](./DE_CU05_Estructura_Reservas.png) |
| **DE-06** | Sub. 6: Punto de Venta (POS) Mostrador | [Ver SVG](./DE_CU06_Estructura_Punto_De_Venta_POS.svg) | [Ver PNG](./DE_CU06_Estructura_Punto_De_Venta_POS.png) |
| **UML-00**| **Diagrama UML de Paquetes de Casos de Uso** | [Ver SVG](./DE_CU_Paquetes_UML.svg) | [Ver PNG](./DE_CU_Paquetes_UML.png) |
