import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import 'api_client.dart';
import 'catalogo_service.dart';
import 'token_storage.dart';
import '../core/database/database_helper.dart';
import '../core/sync/sync_coordinator.dart';

class SucursalCheckoutModel {
  final int idSucursal;
  final int idEmpresa;
  final String nombre;
  final String direccion;
  final String? telefono;
  final String ciudad;
  final bool tieneStockCompleto;
  final String stockEstado;
  final String stockLabel;

  SucursalCheckoutModel({
    required this.idSucursal,
    required this.idEmpresa,
    required this.nombre,
    required this.direccion,
    this.telefono,
    required this.ciudad,
    this.tieneStockCompleto = true,
    this.stockEstado = 'DISPONIBLE',
    this.stockLabel = '✓ Disponible',
  });

  factory SucursalCheckoutModel.fromJson(Map<String, dynamic> json) {
    return SucursalCheckoutModel(
      idSucursal: json['id_sucursal'] ?? 0,
      idEmpresa: json['id_empresa'] ?? 0,
      nombre: json['nombre'] ?? '',
      direccion: json['direccion'] ?? '',
      telefono: json['telefono']?.toString(),
      ciudad: json['ciudad'] ?? '',
      tieneStockCompleto: json['tiene_stock_completo'] ?? true,
      stockEstado: json['stock_estado'] ?? 'DISPONIBLE',
      stockLabel: json['stock_label'] ?? '✓ Disponible',
    );
  }
}

class PedidoItemModel {
  final int idDetallePedido;
  final int idVariante;
  final String productoNombre;
  final String tallaNombre;
  final String colorNombre;
  final String codigoHex;
  final int cantidad;
  final double precioUnitario;
  final double subtotal;
  final String? imagenUrl;

  String get talla => tallaNombre;
  String get color => colorNombre;

  PedidoItemModel({
    required this.idDetallePedido,
    required this.idVariante,
    required this.productoNombre,
    required this.tallaNombre,
    required this.colorNombre,
    required this.codigoHex,
    required this.cantidad,
    required this.precioUnitario,
    required this.subtotal,
    this.imagenUrl,
  });

  factory PedidoItemModel.fromJson(Map<String, dynamic> json) {
    return PedidoItemModel(
      idDetallePedido: json['id_detalle_pedido'] ?? 0,
      idVariante: json['id_variante'] ?? 0,
      productoNombre: json['producto_nombre'] ?? '',
      tallaNombre: json['talla_nombre'] ?? '',
      colorNombre: json['color_nombre'] ?? '',
      codigoHex: json['codigo_hex'] ?? '#000000',
      cantidad: json['cantidad'] ?? 1,
      precioUnitario: (json['precio_unitario'] != null)
          ? double.tryParse(json['precio_unitario'].toString()) ?? 0.0
          : 0.0,
      subtotal: (json['subtotal'] != null)
          ? double.tryParse(json['subtotal'].toString()) ?? 0.0
          : 0.0,
      imagenUrl: json['imagen_url'],
    );
  }

  Map<String, dynamic> toJson() => {
    'id_detalle_pedido': idDetallePedido,
    'id_variante': idVariante,
    'producto_nombre': productoNombre,
    'talla_nombre': tallaNombre,
    'color_nombre': colorNombre,
    'codigo_hex': codigoHex,
    'cantidad': cantidad,
    'precio_unitario': precioUnitario,
    'subtotal': subtotal,
    'imagen_url': imagenUrl,
  };
}

class PedidoModel {
  final int idPedido;
  final int? idEmpresa;
  final int? idSucursal;
  final String codigoPedido;
  final String fechaPedido;
  final String estado;
  final String estadoPago;
  final String modalidadCompra;
  final String nombreContacto;
  final String telefonoContacto;
  final String? correoContacto;
  final String? direccionEntrega;
  final String? ciudadEntrega;
  final String? sucursalNombre;
  final String? nombreEmpresa;
  final double subtotal;
  final double costoEnvio;
  final double descuento;
  final double total;
  final int totalItems;
  final List<PedidoItemModel> items;

  int get idVenta => idPedido;

  PedidoModel({
    required this.idPedido,
    this.idEmpresa,
    this.idSucursal,
    required this.codigoPedido,
    required this.fechaPedido,
    required this.estado,
    required this.estadoPago,
    required this.modalidadCompra,
    required this.nombreContacto,
    required this.telefonoContacto,
    this.correoContacto,
    this.direccionEntrega,
    this.ciudadEntrega,
    this.sucursalNombre,
    this.nombreEmpresa,
    required this.subtotal,
    required this.costoEnvio,
    required this.descuento,
    required this.total,
    required this.totalItems,
    this.items = const [],
  });

  factory PedidoModel.fromJson(Map<String, dynamic> json) {
    final rawItems = (json['items'] as List<dynamic>?) ?? (json['items_resumen'] as List<dynamic>?) ?? [];
    return PedidoModel(
      idPedido: json['id_pedido'] ?? 0,
      idEmpresa: json['id_empresa'] as int?,
      idSucursal: json['id_sucursal'] as int?,
      codigoPedido: json['codigo_pedido'] ?? '',
      fechaPedido: json['fecha_pedido'] ?? '',
      estado: json['estado'] ?? 'PENDIENTE',
      estadoPago: json['estado_pago'] ?? 'PENDIENTE',
      modalidadCompra: json['modalidad_compra'] ?? 'RETIRO_SUCURSAL',
      nombreContacto: json['nombre_contacto'] ?? '',
      telefonoContacto: json['telefono_contacto'] ?? '',
      correoContacto: json['correo_contacto'],
      direccionEntrega: json['direccion_entrega'],
      ciudadEntrega: json['ciudad_entrega'],
      sucursalNombre: json['sucursal_nombre'],
      nombreEmpresa: json['nombre_empresa'],
      subtotal: (json['subtotal'] != null)
          ? double.tryParse(json['subtotal'].toString()) ?? 0.0
          : 0.0,
      costoEnvio: (json['costo_envio'] != null)
          ? double.tryParse(json['costo_envio'].toString()) ?? 0.0
          : 0.0,
      descuento: (json['descuento'] != null)
          ? double.tryParse(json['descuento'].toString()) ?? 0.0
          : 0.0,
      total: (json['total'] != null)
          ? double.tryParse(json['total'].toString()) ?? 0.0
          : 0.0,
      totalItems: json['total_items'] ?? rawItems.length,
      items: rawItems
          .map((e) => PedidoItemModel.fromJson(Map<String, dynamic>.from(e)))
          .toList(),
    );
  }

  Map<String, dynamic> toJson() => {
    'id_pedido': idPedido,
    'id_empresa': idEmpresa,
    'id_sucursal': idSucursal,
    'codigo_pedido': codigoPedido,
    'fecha_pedido': fechaPedido,
    'estado': estado,
    'estado_pago': estadoPago,
    'modalidad_compra': modalidadCompra,
    'nombre_contacto': nombreContacto,
    'telefono_contacto': telefonoContacto,
    'correo_contacto': correoContacto,
    'direccion_entrega': direccionEntrega,
    'ciudad_entrega': ciudadEntrega,
    'sucursal_nombre': sucursalNombre,
    'nombre_empresa': nombreEmpresa,
    'subtotal': subtotal,
    'costo_envio': costoEnvio,
    'descuento': descuento,
    'total': total,
    'total_items': totalItems,
    'items': items.map((e) => e.toJson()).toList(),
  };
}

class PedidoService extends ChangeNotifier {
  final Dio _dio = ApiClient.dio;
  final DatabaseHelper _dbHelper = DatabaseHelper();
  final SyncCoordinator _syncCoordinator = SyncCoordinator();

  List<PedidoModel> _misPedidos = [];
  bool _cargando = false;
  String? _error;

  List<PedidoModel> get misPedidos => _misPedidos;
  bool get cargando => _cargando;
  String? get error => _error;

  Future<List<SucursalCheckoutModel>> obtenerSucursalesCheckout({int? idEmpresa}) async {
    final activeEmpresa = (idEmpresa != null && idEmpresa > 0)
        ? idEmpresa
        : (await TokenStorage.getEmpresaId()) ?? 1;

    try {
      final params = <String, dynamic>{
        'id_empresa': activeEmpresa,
      };

      final res = await _dio.get('/api/pedidos/sucursales', queryParameters: params);
      if (res.data['success'] == true && res.data['data'] != null) {
        final listRaw = res.data['data'] as List<dynamic>;
        final list = listRaw
            .map((e) => SucursalCheckoutModel.fromJson(Map<String, dynamic>.from(e)))
            .toList();

        // Persistir en SQLite para disponibilidad offline
        if (list.isNotEmpty) {
          await _dbHelper.saveSucursales(
            activeEmpresa,
            list.map((s) => SucursalContextModel(
              idSucursal: s.idSucursal,
              idEmpresa: s.idEmpresa > 0 ? s.idEmpresa : activeEmpresa,
              nombre: s.nombre,
              direccion: s.direccion,
              telefono: s.telefono,
              ciudad: s.ciudad,
            )).toList(),
          );
        }

        return list;
      }
    } catch (_) {}

    // Fallback a SQLite cuando no hay conexión (con auto-siembra canónica garantizada)
    final localSucs = await _dbHelper.getSucursales(activeEmpresa);
    if (localSucs.isNotEmpty) {
      return localSucs.map((s) => SucursalCheckoutModel(
        idSucursal: s.idSucursal,
        idEmpresa: s.idEmpresa > 0 ? s.idEmpresa : activeEmpresa,
        nombre: s.nombre,
        direccion: s.direccion,
        telefono: s.telefono,
        ciudad: s.ciudad ?? 'La Paz',
        tieneStockCompleto: true,
        stockEstado: 'OFFLINE_DISPONIBLE',
        stockLabel: '✓ Disponible (Offline)',
      )).toList();
    }

    return [
      SucursalCheckoutModel(
        idSucursal: 1,
        idEmpresa: activeEmpresa,
        nombre: 'Sucursal Central Equipetrol',
        direccion: 'Av. San Martín #450, Barrio Equipetrol',
        telefono: '+591 3 3428900',
        ciudad: 'Santa Cruz',
        tieneStockCompleto: true,
        stockEstado: 'OFFLINE_DISPONIBLE',
        stockLabel: '✓ Disponible (Offline)',
      ),
      SucursalCheckoutModel(
        idSucursal: 2,
        idEmpresa: activeEmpresa,
        nombre: 'Sucursal Calacoto',
        direccion: 'Calle 21 de Calacoto #8200',
        telefono: '+591 2 2794500',
        ciudad: 'La Paz',
        tieneStockCompleto: true,
        stockEstado: 'OFFLINE_DISPONIBLE',
        stockLabel: '✓ Disponible (Offline)',
      ),
    ];
  }

  Future<PedidoModel> crearPedido({
    required int idSucursal,
    required String modalidadCompra, // 'RETIRO_SUCURSAL' | 'ENTREGA_DOMICILIO'
    required String nombreContacto,
    required String telefonoContacto,
    String? correoContacto,
    String? direccionEntrega,
    String? ciudadEntrega,
    String? notasEntrega,
    int? idEmpresa,
    List<PedidoItemModel>? itemsOffline,
    double? totalOffline,
  }) async {
    final activeEmpresa = idEmpresa ?? (await TokenStorage.getEmpresaId()) ?? 1;
    final userId = (await TokenStorage.getUsuario())?['id_usuario'] as int? ?? 1;

    try {
      final body = <String, dynamic>{
        'id_sucursal': idSucursal,
        'modalidad_compra': modalidadCompra,
        'nombre_contacto': nombreContacto.trim(),
        'telefono_contacto': telefonoContacto.trim(),
        if (correoContacto != null && correoContacto.isNotEmpty) 'correo_contacto': correoContacto.trim(),
        if (direccionEntrega != null && direccionEntrega.isNotEmpty) 'direccion_entrega': direccionEntrega.trim(),
        if (ciudadEntrega != null && ciudadEntrega.isNotEmpty) 'ciudad_entrega': ciudadEntrega.trim(),
        if (notasEntrega != null && notasEntrega.isNotEmpty) 'notas_entrega': notasEntrega.trim(),
        if (idEmpresa != null) 'id_empresa': idEmpresa,
      };

      final res = await _dio.post('/api/pedidos', data: body);
      if (res.data['success'] == true && res.data['data'] != null) {
        final pedido = PedidoModel.fromJson(res.data['data']);
        await _dbHelper.savePedidos(activeEmpresa, userId, [pedido]);
        cargarMisPedidos(idEmpresa: idEmpresa);
        return pedido;
      }
      throw Exception(res.data['message'] ?? 'Error al procesar pedido.');
    } catch (e) {
      // Modo offline resiliente: guardar borrador en local_pedidos y encolar en local_sync_operations
      final offlineId = DateTime.now().millisecondsSinceEpoch % 1000000;
      final offlinePedido = PedidoModel(
        idPedido: offlineId,
        idEmpresa: activeEmpresa,
        idSucursal: idSucursal,
        codigoPedido: 'PED-OFFLINE-$offlineId',
        fechaPedido: DateTime.now().toIso8601String(),
        estado: 'PENDIENTE_SYNC',
        estadoPago: 'PENDIENTE',
        modalidadCompra: modalidadCompra,
        nombreContacto: nombreContacto,
        telefonoContacto: telefonoContacto,
        correoContacto: correoContacto,
        direccionEntrega: direccionEntrega,
        ciudadEntrega: ciudadEntrega,
        sucursalNombre: 'Sucursal Seleccionada (Offline)',
        subtotal: totalOffline ?? 0.0,
        costoEnvio: modalidadCompra == 'ENTREGA_DOMICILIO' ? 25.0 : 0.0,
        descuento: 0.0,
        total: totalOffline ?? 0.0,
        totalItems: itemsOffline?.length ?? 1,
        items: itemsOffline ?? [],
      );

      await _dbHelper.savePedidos(activeEmpresa, userId, [offlinePedido]);

      await _syncCoordinator.encolarOperacion(
        idEmpresa: activeEmpresa,
        idUsuario: userId,
        idSucursal: idSucursal,
        kind: 'PEDIDO_CREAR',
        payload: {
          'id_sucursal': idSucursal,
          'modalidad_compra': modalidadCompra,
          'nombre_contacto': nombreContacto,
          'telefono_contacto': telefonoContacto,
          'correo_contacto': correoContacto,
          'direccion_entrega': direccionEntrega,
          'ciudad_entrega': ciudadEntrega,
          'notas_entrega': notasEntrega,
          'id_empresa': activeEmpresa,
        },
      );

      _misPedidos.insert(0, offlinePedido);
      notifyListeners();
      return offlinePedido;
    }
  }

  Future<void> cargarMisPedidos({int? idEmpresa}) async {
    _cargando = true;
    _error = null;
    notifyListeners();

    final activeEmpresa = idEmpresa ?? (await TokenStorage.getEmpresaId()) ?? 1;
    final userId = (await TokenStorage.getUsuario())?['id_usuario'] as int? ?? 1;

    try {
      final params = <String, dynamic>{
        'limit': 50,
      };
      if (idEmpresa != null) params['id_empresa'] = idEmpresa;

      final res = await _dio.get('/api/pedidos', queryParameters: params);
      if (res.data['success'] == true && res.data['data'] != null) {
        final rawList = res.data['data'] as List<dynamic>;
        _misPedidos = rawList
            .map((e) => PedidoModel.fromJson(Map<String, dynamic>.from(e)))
            .toList();

        // Persistir historial en SQLite
        await _dbHelper.savePedidos(activeEmpresa, userId, _misPedidos);
      } else {
        _misPedidos = [];
      }
    } on DioException catch (e) {
      if (e.response?.statusCode == 401) {
        _misPedidos = [];
      } else {
        // Fallback a pedidos cacheados en SQLite
        final cached = await _dbHelper.getPedidos(activeEmpresa, userId);
        if (cached.isNotEmpty) {
          _misPedidos = cached;
          _error = null;
        } else {
          _error = e.response?.data?['detail'] ?? 'Error al consultar historial de pedidos.';
        }
      }
    } catch (_) {
      final cached = await _dbHelper.getPedidos(activeEmpresa, userId);
      if (cached.isNotEmpty) {
        _misPedidos = cached;
        _error = null;
      } else {
        _error = 'Error de conexión con el servicio de pedidos.';
      }
    } finally {
      _cargando = false;
      notifyListeners();
    }
  }

  Future<PedidoModel> obtenerDetallePedido(int idPedido, {int? idEmpresa}) async {
    final activeEmpresa = idEmpresa ?? (await TokenStorage.getEmpresaId()) ?? 1;
    final userId = (await TokenStorage.getUsuario())?['id_usuario'] as int? ?? 1;

    try {
      final params = <String, dynamic>{};
      if (idEmpresa != null) params['id_empresa'] = idEmpresa;

      final res = await _dio.get('/api/pedidos/$idPedido', queryParameters: params);
      if (res.data['success'] == true && res.data['data'] != null) {
        return PedidoModel.fromJson(res.data['data']);
      }
      throw Exception('No se encontró el detalle del pedido.');
    } on DioException catch (e) {
      // Buscar en memoria o en SQLite
      final match = _misPedidos.firstWhere(
        (p) => p.idPedido == idPedido,
        orElse: () => PedidoModel(
          idPedido: 0,
          codigoPedido: '',
          fechaPedido: '',
          estado: '',
          estadoPago: '',
          modalidadCompra: '',
          nombreContacto: '',
          telefonoContacto: '',
          subtotal: 0,
          costoEnvio: 0,
          descuento: 0,
          total: 0,
          totalItems: 0,
        ),
      );
      if (match.idPedido > 0) return match;

      final cached = await _dbHelper.getPedidos(activeEmpresa, userId);
      for (final p in cached) {
        if (p.idPedido == idPedido) return p;
      }

      final msg = e.response?.data?['detail'] ?? 'Error al cargar pedido.';
      throw Exception(msg.toString());
    }
  }
}
