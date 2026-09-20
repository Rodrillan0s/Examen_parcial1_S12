import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import 'api_client.dart';

class ItemCarritoModel {
  final int idDetalleCarrito;
  final int idVariante;
  final int idProducto;
  final String productoNombre;
  final String? codigoProducto;
  final String tallaNombre;
  final String colorNombre;
  final String codigoHex;
  final String? sku;
  final String? imagenUrl;
  int cantidad;
  final double precioUnitario;
  double subtotal;
  final int stockDisponible;
  final bool disponible;
  final String? advertenciaStock;

  ItemCarritoModel({
    required this.idDetalleCarrito,
    required this.idVariante,
    required this.idProducto,
    required this.productoNombre,
    this.codigoProducto,
    required this.tallaNombre,
    required this.colorNombre,
    required this.codigoHex,
    this.sku,
    this.imagenUrl,
    required this.cantidad,
    required this.precioUnitario,
    required this.subtotal,
    required this.stockDisponible,
    required this.disponible,
    this.advertenciaStock,
  });

  factory ItemCarritoModel.fromJson(Map<String, dynamic> json) {
    return ItemCarritoModel(
      idDetalleCarrito: json['id_detalle_carrito'] ?? 0,
      idVariante: json['id_variante'] ?? 0,
      idProducto: json['id_producto'] ?? 0,
      productoNombre: json['producto_nombre'] ?? '',
      codigoProducto: json['codigo_producto'],
      tallaNombre: json['talla_nombre'] ?? '',
      colorNombre: json['color_nombre'] ?? '',
      codigoHex: json['codigo_hex'] ?? '#000000',
      sku: json['sku'],
      imagenUrl: json['imagen_url'],
      cantidad: json['cantidad'] ?? 1,
      precioUnitario: (json['precio_unitario'] != null)
          ? double.tryParse(json['precio_unitario'].toString()) ?? 0.0
          : 0.0,
      subtotal: (json['subtotal'] != null)
          ? double.tryParse(json['subtotal'].toString()) ?? 0.0
          : 0.0,
      stockDisponible: json['stock_disponible'] ?? 0,
      disponible: json['disponible'] ?? true,
      advertenciaStock: json['advertencia_stock'],
    );
  }
}

class CarritoModel {
  final int idCarrito;
  final int idEmpresa;
  final String nombreEmpresa;
  final List<ItemCarritoModel> items;
  final int totalItems;
  final double subtotal;
  final double descuento;
  final double total;
  final bool puedeContinuarCompra;

  CarritoModel({
    required this.idCarrito,
    required this.idEmpresa,
    required this.nombreEmpresa,
    required this.items,
    required this.totalItems,
    required this.subtotal,
    required this.descuento,
    required this.total,
    required this.puedeContinuarCompra,
  });

  factory CarritoModel.fromJson(Map<String, dynamic> json) {
    final itemsRaw = json['items'] as List<dynamic>? ?? [];
    return CarritoModel(
      idCarrito: json['id_carrito'] ?? 0,
      idEmpresa: json['id_empresa'] ?? 0,
      nombreEmpresa: json['nombre_empresa'] ?? '',
      items: itemsRaw
          .map((e) => ItemCarritoModel.fromJson(Map<String, dynamic>.from(e)))
          .toList(),
      totalItems: json['total_items'] ?? 0,
      subtotal: (json['subtotal'] != null)
          ? double.tryParse(json['subtotal'].toString()) ?? 0.0
          : 0.0,
      descuento: (json['descuento'] != null)
          ? double.tryParse(json['descuento'].toString()) ?? 0.0
          : 0.0,
      total: (json['total'] != null)
          ? double.tryParse(json['total'].toString()) ?? 0.0
          : 0.0,
      puedeContinuarCompra: json['puede_continuar_compra'] ?? true,
    );
  }
}

class CarritoService extends ChangeNotifier {
  final Dio _dio = ApiClient.dio;

  CarritoModel? _carrito;
  bool _cargando = false;
  String? _error;

  CarritoModel? get carrito => _carrito;
  bool get cargando => _cargando;
  String? get error => _error;
  int get totalItems => _carrito?.totalItems ?? 0;
  double get total => _carrito?.total ?? 0.0;

  Future<void> cargarCarrito({int? idEmpresa}) async {
    _cargando = true;
    _error = null;
    notifyListeners();

    try {
      final params = <String, dynamic>{};
      if (idEmpresa != null) params['id_empresa'] = idEmpresa;

      final res = await _dio.get('/api/carrito', queryParameters: params);
      if (res.data['success'] == true && res.data['data'] != null) {
        _carrito = CarritoModel.fromJson(res.data['data']);
      } else {
        _carrito = null;
      }
    } on DioException catch (e) {
      if (e.response?.statusCode == 401) {
        _carrito = null;
        _error = null; // No mostrar error en banner para no autenticado
      } else {
        _error = e.response?.data?['detail'] ?? 'Error al consultar la bolsa.';
      }
    } catch (e) {
      _error = 'Error de conexión con el carrito.';
    } finally {
      _cargando = false;
      notifyListeners();
    }
  }

  Future<bool> agregarItem({
    required int idVariante,
    int cantidad = 1,
    int? idEmpresa,
  }) async {
    _cargando = true;
    _error = null;
    notifyListeners();

    try {
      final body = <String, dynamic>{
        'id_variante': idVariante,
        'cantidad': cantidad,
        if (idEmpresa != null) 'id_empresa': idEmpresa,
      };

      final res = await _dio.post('/api/carrito/items', data: body);
      if (res.data['success'] == true && res.data['data'] != null) {
        _carrito = CarritoModel.fromJson(res.data['data']);
        notifyListeners();
        return true;
      }
      return false;
    } on DioException catch (e) {
      if (e.response?.statusCode == 401) {
        _error = 'Debes iniciar sesión para agregar prendas a la bolsa.';
      } else {
        _error = e.response?.data?['detail'] ?? 'Stock insuficiente o error al agregar.';
      }
      notifyListeners();
      return false;
    } catch (_) {
      _error = 'No se pudo agregar a la bolsa.';
      notifyListeners();
      return false;
    } finally {
      _cargando = false;
      notifyListeners();
    }
  }

  Future<void> actualizarCantidad({
    required int idDetalleCarrito,
    required int nuevaCantidad,
    int? idEmpresa,
  }) async {
    try {
      final body = <String, dynamic>{
        'cantidad': nuevaCantidad,
        if (idEmpresa != null) 'id_empresa': idEmpresa,
      };

      final res = await _dio.put(
        '/api/carrito/items/$idDetalleCarrito',
        data: body,
      );

      if (res.data['success'] == true && res.data['data'] != null) {
        _carrito = CarritoModel.fromJson(res.data['data']);
        notifyListeners();
      }
    } on DioException catch (e) {
      _error = e.response?.data?['detail'] ?? 'Error al actualizar cantidad.';
      notifyListeners();
    }
  }

  Future<void> eliminarItem({
    required int idDetalleCarrito,
    int? idEmpresa,
  }) async {
    try {
      final params = <String, dynamic>{};
      if (idEmpresa != null) params['id_empresa'] = idEmpresa;

      final res = await _dio.delete(
        '/api/carrito/items/$idDetalleCarrito',
        queryParameters: params,
      );

      if (res.data['success'] == true && res.data['data'] != null) {
        _carrito = CarritoModel.fromJson(res.data['data']);
        notifyListeners();
      }
    } catch (_) {}
  }

  Future<void> vaciarCarrito({int? idEmpresa}) async {
    try {
      final params = <String, dynamic>{};
      if (idEmpresa != null) params['id_empresa'] = idEmpresa;

      final res = await _dio.delete(
        '/api/carrito/vaciar',
        queryParameters: params,
      );

      if (res.data['success'] == true && res.data['data'] != null) {
        _carrito = CarritoModel.fromJson(res.data['data']);
        notifyListeners();
      }
    } catch (_) {}
  }
}
