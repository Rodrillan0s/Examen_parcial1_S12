import 'package:dio/dio.dart';
import 'package:latlong2/latlong.dart';

import 'api_client.dart';

class TallerService {
  static const String _basePath = '/api/talleres';

  Future<LatLng?> obtenerUbicacionTaller({
    required int nroTaller,
  }) async {
    try {
      final response = await ApiClient.dio.get('$_basePath/');
      final data = response.data;

      if (data is! Map) {
        throw Exception('Respuesta inválida del servidor.');
      }

      if (data['success'] != true) {
        throw Exception(
          data['message'] ?? 'No se pudieron cargar los talleres.',
        );
      }

      final lista = data['data'] as List? ?? [];

      for (final item in lista) {
        if (item is! Map) continue;

        final taller = Map<String, dynamic>.from(item);
        final nro = _int(taller['nro_taller']);

        if (nro == nroTaller) {
          final lat = _double(taller['latitud']);
          final lng = _double(taller['longitud']);

          if (lat == null || lng == null) {
            return null;
          }

          return LatLng(lat, lng);
        }
      }

      return null;
    } on DioException catch (e) {
      throw Exception(_parsearErrorDio(e));
    }
  }

  int? _int(dynamic value) {
    if (value == null) return null;
    return int.tryParse(value.toString());
  }

  double? _double(dynamic value) {
    if (value == null) return null;
    return double.tryParse(value.toString());
  }

  String _parsearErrorDio(DioException e) {
    if (e.response?.data != null) {
      final data = e.response!.data;

      if (data is Map && data['detail'] is List) {
        final errores = data['detail'] as List;

        return errores.map((err) {
          if (err is Map && err['msg'] != null) {
            return err['msg'].toString();
          }

          return err.toString();
        }).join('\n');
      }

      if (data is Map && data['detail'] != null) {
        return data['detail'].toString();
      }

      if (data is Map && data['message'] != null) {
        return data['message'].toString();
      }
    }

    switch (e.type) {
      case DioExceptionType.connectionTimeout:
      case DioExceptionType.receiveTimeout:
      case DioExceptionType.sendTimeout:
        return 'Tiempo de espera agotado. Verificá tu conexión.';
      case DioExceptionType.connectionError:
        return 'No se pudo conectar al servidor.';
      default:
        break;
    }

    switch (e.response?.statusCode) {
      case 400:
        return 'Datos inválidos.';
      case 401:
        return 'Tu sesión expiró. Iniciá sesión nuevamente.';
      case 403:
        return 'No tienes permiso para consultar los talleres.';
      case 404:
        return 'Servicio de talleres no encontrado.';
      case 500:
        return 'Error interno del servidor.';
      default:
        return 'Ocurrió un error inesperado.';
    }
  }
}