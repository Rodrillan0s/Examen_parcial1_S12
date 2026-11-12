import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:sqflite_common_ffi/sqflite_ffi.dart';
import 'package:aurora_store_mobile/services/catalogo_service.dart';
import 'package:aurora_store_mobile/services/pedido_service.dart';
import 'package:aurora_store_mobile/services/carrito_service.dart';
import 'package:aurora_store_mobile/services/reserva_service.dart';
import 'package:aurora_store_mobile/services/devoluciones_service.dart';
import 'package:aurora_store_mobile/core/sync/sync_coordinator.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  const channel = MethodChannel('plugins.it_nomads.com/flutter_secure_storage');
  final Map<String, String> mockStorage = {};

  setUpAll(() {
    sqfliteFfiInit();
    databaseFactory = databaseFactoryFfi;

    TestDefaultBinaryMessengerBinding.instance.defaultBinaryMessenger
        .setMockMethodCallHandler(channel, (MethodCall methodCall) async {
      switch (methodCall.method) {
        case 'write':
          final key = methodCall.arguments['key'] as String;
          final value = methodCall.arguments['value'] as String;
          mockStorage[key] = value;
          return null;
        case 'read':
          final key = methodCall.arguments['key'] as String;
          return mockStorage[key];
        case 'delete':
          final key = methodCall.arguments['key'] as String;
          mockStorage.remove(key);
          return null;
        case 'deleteAll':
          mockStorage.clear();
          return null;
        default:
          return null;
      }
    });
  });

  group('Flujo Offline Móvil & SQLite Resilience Tests', () {
    test('1. Sintetiza DetallePrendaModel completo desde PrendaModel de SQLite cuando está offline', () {
      final dummyPrenda = PrendaModel(
        idProducto: 42,
        idEmpresa: 1,
        idCategoria: 3,
        categoriaNombre: 'Vestidos de Gala',
        codigoProducto: 'VEST-042',
        nombre: 'Vestido Aurora Imperial',
        descripcion: 'Vestido largo con pedrería fina',
        marca: 'Aurora Collection',
        genero: 'FEMENINO',
        precio: 550.0,
        estadoStock: 'DISPONIBLE',
        stockDisponibleCatalogo: 15,
        imagenPrincipal: 'https://images.unsplash.com/photo-1515372039744-b8f02a3ae446',
        totalImagenes: 1,
        totalVariantes: 4,
        tallasDisponibles: [
          {'id_talla': 1, 'nombre': 'S'},
          {'id_talla': 2, 'nombre': 'M'},
        ],
        coloresDisponibles: [
          {'id_color': 10, 'nombre': 'Dorado', 'codigo_hex': '#D4AF37'},
          {'id_color': 20, 'nombre': 'Negro', 'codigo_hex': '#000000'},
        ],
        tieneRa: true,
      );

      final catalogoService = CatalogoService();
      final detalle = catalogoService.sintetizarDetalleDesdePrenda(dummyPrenda);

      expect(detalle.idProducto, equals(42));
      expect(detalle.idEmpresa, equals(1));
      expect(detalle.nombre, equals('Vestido Aurora Imperial'));
      expect(detalle.precio, equals(550.0));
      expect(detalle.tieneRa, isTrue);
      // Debe haber generado 2 tallas * 2 colores = 4 variantes
      expect(detalle.variantes.length, equals(4));
      expect(detalle.variantes.first.tallaNombre, equals('S'));
      expect(detalle.variantes.first.colorNombre, equals('Dorado'));
      expect(detalle.variantes.first.codigoHex, equals('#D4AF37'));
      expect(detalle.permiteReserva, isTrue);
      expect(detalle.permiteCompra, isTrue);
      expect(detalle.imagenes, contains('https://images.unsplash.com/photo-1515372039744-b8f02a3ae446'));
    });

    test('2. FiltrosCatalogoModel serializa y deserializa bidireccionalmente para almacenamiento SQLite', () {
      final filtros = FiltrosCatalogoModel(
        categorias: [
          CategoriaFiltroModel(idCategoria: 1, nombre: 'Casual', totalPrendas: 12),
          CategoriaFiltroModel(idCategoria: 2, nombre: 'Formal', totalPrendas: 8),
        ],
        tallas: [
          TallaFiltroModel(idTalla: 1, nombre: 'S'),
          TallaFiltroModel(idTalla: 2, nombre: 'M'),
        ],
        colores: [
          ColorFiltroModel(idColor: 1, nombre: 'Azul', codigoHex: '#0000FF'),
        ],
        temporadas: ['Primavera', 'Verano'],
        colecciones: ['Colección 2026'],
        precioMin: 50.0,
        precioMax: 890.0,
      );

      final jsonMap = filtros.toJson();
      final restored = FiltrosCatalogoModel.fromJson(jsonMap);

      expect(restored.categorias.length, equals(2));
      expect(restored.categorias.first.nombre, equals('Casual'));
      expect(restored.categorias.first.totalPrendas, equals(12));
      expect(restored.tallas.length, equals(2));
      expect(restored.colores.first.codigoHex, equals('#0000FF'));
      expect(restored.temporadas, contains('Primavera'));
      expect(restored.precioMin, equals(50.0));
      expect(restored.precioMax, equals(890.0));
    });

    test('3. SucursalContextModel serializa y deserializa con campos completos de ubicación para SQLite', () {
      const sucursal = SucursalContextModel(
        idSucursal: 10,
        idEmpresa: 1,
        nombre: 'Sucursal Calacoto Central',
        direccion: 'Calle 21 de Calacoto #100',
        telefono: '22789456',
        ciudad: 'La Paz',
      );

      final jsonMap = sucursal.toJson();
      final restored = SucursalContextModel.fromJson(jsonMap);

      expect(restored.idSucursal, equals(10));
      expect(restored.idEmpresa, equals(1));
      expect(restored.nombre, equals('Sucursal Calacoto Central'));
      expect(restored.direccion, equals('Calle 21 de Calacoto #100'));
      expect(restored.telefono, equals('22789456'));
      expect(restored.ciudad, equals('La Paz'));
    });

    test('4. PedidoModel y PedidoItemModel serializan y deserializan para historial offline en SQLite', () {
      final pedido = PedidoModel(
        idPedido: 99,
        idEmpresa: 1,
        idSucursal: 10,
        codigoPedido: 'PED-2026-0099',
        fechaPedido: '2026-11-10T02:00:00Z',
        estado: 'CONFIRMADO',
        estadoPago: 'PAGADO',
        modalidadCompra: 'RETIRO_SUCURSAL',
        nombreContacto: 'Carlos Mamani',
        telefonoContacto: '77234567',
        correoContacto: 'carlos@example.com',
        sucursalNombre: 'Sucursal Central',
        nombreEmpresa: 'Shopping Bolivia',
        subtotal: 450.0,
        costoEnvio: 0.0,
        descuento: 20.0,
        total: 430.0,
        totalItems: 1,
        items: [
          PedidoItemModel(
            idDetallePedido: 1,
            idVariante: 101,
            productoNombre: 'Camisa Lino Premium',
            tallaNombre: 'M',
            colorNombre: 'Blanco',
            codigoHex: '#FFFFFF',
            cantidad: 1,
            precioUnitario: 450.0,
            subtotal: 450.0,
            imagenUrl: 'https://images.unsplash.com/photo-test',
          ),
        ],
      );

      final jsonMap = pedido.toJson();
      final restored = PedidoModel.fromJson(jsonMap);

      expect(restored.idPedido, equals(99));
      expect(restored.codigoPedido, equals('PED-2026-0099'));
      expect(restored.total, equals(430.0));
      expect(restored.items.length, equals(1));
      expect(restored.items.first.productoNombre, equals('Camisa Lino Premium'));
      expect(restored.items.first.tallaNombre, equals('M'));
      expect(restored.items.first.codigoHex, equals('#FFFFFF'));
    });

    test('5. SyncResultSummary procesa resultados y conflictos de sincronización por lotes', () {
      final summary = SyncResultSummary(
        total: 5,
        synced: 3,
        conflicts: 1,
        retrying: 1,
        errorMessages: ['Stock no disponible en la sucursal seleccionada.'],
      );

      expect(summary.total, equals(5));
      expect(summary.synced, equals(3));
      expect(summary.conflicts, equals(1));
      expect(summary.retrying, equals(1));
      expect(summary.errorMessages.first, contains('Stock no disponible'));
    });

    test('6. ItemCarritoModel mantiene cálculos y avisos de stock en borrador offline', () {
      final item = ItemCarritoModel(
        idDetalleCarrito: 0,
        idVariante: 50,
        idProducto: 12,
        productoNombre: 'Pantalón Chino Clásico',
        tallaNombre: '40',
        colorNombre: 'Beige',
        codigoHex: '#F5F5DC',
        cantidad: 2,
        precioUnitario: 180.0,
        subtotal: 360.0,
        stockDisponible: 99,
        disponible: true,
        advertenciaStock: 'Precio y stock sujetos a confirmación con la tienda.',
      );

      expect(item.idVariante, equals(50));
      expect(item.subtotal, equals(360.0));
      expect(item.advertenciaStock, contains('confirmación'));
    });

    test('7. ReservaModel parsea citas presenciales gratuitas para sincronización offline', () {
      final reserva = ReservaModel(
        idReserva: 1001,
        codigoReserva: 'OFFLINE-SOLICITUD-01',
        fechaReserva: '2026-11-10T10:00:00Z',
        fechaHoraVisita: '2026-11-12 16:30',
        estado: 'PENDIENTE_SYNC',
        totalPrendas: 2,
        conPago: false,
        estadoPago: 'SIN_PAGO',
        montoPagado: 0.0,
      );

      expect(reserva.codigoReserva, equals('OFFLINE-SOLICITUD-01'));
      expect(reserva.estado, equals('PENDIENTE_SYNC'));
      expect(reserva.conPago, isFalse);
      expect(reserva.montoPagado, equals(0.0));
    });

    test('8. SolicitudDevolucionModel serializa y deserializa bidireccionalmente para SQLite y sincronización offline', () {
      final dev = SolicitudDevolucionModel(
        idDevolucion: 9901,
        codigoDevolucion: 'DEV-OFFLINE-9901',
        idVenta: 120,
        numeroVenta: 'VENTA-120',
        fechaSolicitud: '2026-11-10T09:30:00Z',
        estado: 'PENDIENTE_SYNC',
        tipoResolucion: 'CAMBIO_PRENDA',
        motivo: 'TALLA_INCORRECTA',
        descripcion: 'Requiere cambio a talla L en sucursal Calacoto',
        montoTotal: 450.0,
        items: [
          ItemDevolucionSolicitadaModel(
            idDetalleDevolucion: 1,
            idDetalleVenta: 34,
            idVariante: 78,
            productoNombre: 'Blazer Ejecutivo Lana',
            tallaNombre: 'M',
            colorNombre: 'Azul Marino',
            cantidad: 1,
            precioUnitario: 450.0,
            subtotalDevuelto: 450.0,
            condicion: 'REVENDIBLE',
            tallaCambio: 'L',
          ),
        ],
      );

      final jsonMap = dev.toJson();
      expect(jsonMap['codigo_devolucion'], equals('DEV-OFFLINE-9901'));
      expect(jsonMap['tipo_resolucion'], equals('CAMBIO_PRENDA'));
      expect(jsonMap['estado'], equals('PENDIENTE_SYNC'));
      expect(jsonMap['items'], isA<List>());

      final restored = SolicitudDevolucionModel.fromJson(jsonMap);
      expect(restored.idDevolucion, equals(9901));
      expect(restored.tipoResolucion, equals('CAMBIO_PRENDA'));
      expect(restored.items.length, equals(1));
      expect(restored.items.first.tallaCambio, equals('L'));
    });

    test('9. SucursalCheckoutModel genera estados offline con stock garantizado para pedidos y reservas presenciales', () {
      final suc = SucursalCheckoutModel(
        idSucursal: 2,
        idEmpresa: 1,
        nombre: 'Sucursal Calacoto',
        direccion: 'Calle 21 #8200',
        ciudad: 'La Paz',
        tieneStockCompleto: true,
        stockEstado: 'OFFLINE_DISPONIBLE',
        stockLabel: '✓ Disponible (Offline)',
      );

      expect(suc.idSucursal, equals(2));
      expect(suc.tieneStockCompleto, isTrue);
      expect(suc.stockEstado, equals('OFFLINE_DISPONIBLE'));
      expect(suc.stockLabel, contains('Offline'));
    });

    test('10. PedidoModel admite órdenes diferidas en modo PENDIENTE_SYNC para compras sin conexión', () {
      final pedidoOffline = PedidoModel(
        idPedido: 8801,
        idEmpresa: 1,
        idSucursal: 1,
        codigoPedido: 'PED-OFFLINE-8801',
        fechaPedido: '2026-11-10T10:00:00Z',
        estado: 'PENDIENTE_SYNC',
        estadoPago: 'PENDIENTE',
        modalidadCompra: 'RETIRO_SUCURSAL',
        nombreContacto: 'Eddy Toledo',
        telefonoContacto: '70012345',
        subtotal: 350.0,
        costoEnvio: 0.0,
        descuento: 0.0,
        total: 350.0,
        totalItems: 1,
        items: [
          PedidoItemModel(
            idDetallePedido: 1,
            idVariante: 12,
            productoNombre: 'Pantalón Lino',
            tallaNombre: 'M',
            colorNombre: 'Blanco',
            codigoHex: '#FFFFFF',
            cantidad: 1,
            precioUnitario: 350.0,
            subtotal: 350.0,
          ),
        ],
      );

      expect(pedidoOffline.codigoPedido, equals('PED-OFFLINE-8801'));
      expect(pedidoOffline.estado, equals('PENDIENTE_SYNC'));
      expect(pedidoOffline.modalidadCompra, equals('RETIRO_SUCURSAL'));
      expect(pedidoOffline.items.length, equals(1));
    });

    test('11. CatalogoService.obtenerDetalleProducto genera detalle sintético resiliente sin lanzar excepción', () async {
      final catalogo = CatalogoService();
      final detalle = await catalogo.obtenerDetalleProducto(999);
      expect(detalle, isNotNull);
      expect(detalle.idProducto, equals(999));
      expect(detalle.variantes.isNotEmpty, isTrue);
      expect(detalle.permiteCompra, isTrue);
      expect(detalle.permiteReserva, isTrue);
    });

    test('12. PedidoService.obtenerSucursalesCheckout devuelve sucursales canónicas offline garantizadas', () async {
      final pedidoService = PedidoService();
      final sucursales = await pedidoService.obtenerSucursalesCheckout(idEmpresa: 1);
      expect(sucursales, isNotEmpty);
      expect(sucursales.first.nombre, isNotEmpty);
      expect(sucursales.first.tieneStockCompleto, isTrue);
    });
  });
}
