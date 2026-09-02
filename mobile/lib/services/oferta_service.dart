import 'package:dio/dio.dart';
import 'api_client.dart';

class OfertaService {
  static const String _basePath = '/api/ofertas';

  Future<List<Map<String, dynamic>>> listarOfertasPorEmergencia({
    required int nroEmergencia,
  }) async {
    try {
      final response = await ApiClient.dio.get(
        '$_basePath/emergencia/$nroEmergencia',
      );

      final data = response.data;

      if (data is! Map) {
        throw Exception('Respuesta inválida del servidor.');
      }

      if (data['success'] != true) {
        throw Exception(data['message'] ?? 'No se pudieron cargar las ofertas.');
      }

      final lista = data['data'] as List? ?? [];

      return lista
          .map((item) => Map<String, dynamic>.from(item as Map))
          .toList();
    } on DioException catch (e) {
      throw Exception(_parsearErrorDio(e));
    }
  }

  Future<Map<String, dynamic>> responderOferta({
    required int idOferta,
    required String estadoOferta,
  }) async {
    try {
      final response = await ApiClient.dio.put(
        '$_basePath/$idOferta/responder',
        data: {
          'estado_oferta': estadoOferta,
        },
      );

      final data = response.data;

      if (data is! Map) {
        throw Exception('Respuesta inválida del servidor.');
      }

      if (data['success'] != true) {
        throw Exception(data['message'] ?? 'No se pudo responder la oferta.');
      }

      return Map<String, dynamic>.from(data);
    } on DioException catch (e) {
      throw Exception(_parsearErrorDio(e));
    }
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
        return 'No tienes permiso para esta acción.';
      case 404:
        return 'Servicio no encontrado.';
      case 500:
        return 'Error interno del servidor.';
      default:
        return 'Ocurrió un error inesperado.';
    }
  }
}