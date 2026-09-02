import 'package:dio/dio.dart';
import 'api_client.dart';

class EmergenciaService {
  static const String _basePath = '/api/emergencias';

  Future<Map<String, dynamic>> crearEmergencia({
    required String tipoEmergencia,
    required double latitud,
    required double longitud,
    required int nroVehiculo,
    required List<Map<String, dynamic>> evidencias,
    String prioridad = 'MEDIA',
    String descripcion = '',
    String referencia = '',
  }) async {
    return crearEmergenciaDesdePayload({
      'tipo_emergencia': tipoEmergencia,
      'latitud': latitud,
      'longitud': longitud,
      'prioridad': prioridad,
      'nro_vehiculo': nroVehiculo,
      'evidencias': evidencias,
      'descripcion': descripcion,
      'referencia': referencia,
    });
  }

  Future<Map<String, dynamic>> crearEmergenciaDesdePayload(
    Map<String, dynamic> payload,
  ) async {
    try {
      final response = await ApiClient.dio.post(
        '$_basePath/',
        data: payload,
      );

      final data = response.data;

      if (data is! Map) {
        throw Exception('Respuesta inválida del servidor.');
      }

      if (data['success'] != true) {
        throw Exception(data['message'] ?? 'No se pudo registrar la emergencia.');
      }

      return Map<String, dynamic>.from(data);
    } on DioException catch (e) {
      throw Exception(_parsearErrorDio(e));
    }
  }

  Future<List<Map<String, dynamic>>> listarMisEmergencias() async 
  {
    try {
      final response = await ApiClient.dio.get('$_basePath/mis-emergencias');

      final data = response.data;

      if (data is! Map) {
        throw Exception('Respuesta inválida del servidor.');
      }

      if (data['success'] != true) {
        throw Exception(data['message'] ?? 'No se pudo obtener tus emergencias.');
      }

      final lista = data['data'] as List? ?? [];

      return lista
          .map((item) => Map<String, dynamic>.from(item as Map))
          .toList();
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
          if (err is Map && err['msg'] != null) return err['msg'].toString();
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
        return 'Tiempo de espera agotado. Verificá tu conexión a internet.';
      case DioExceptionType.connectionError:
        return 'No se pudo conectar al servidor. Verificá tu conexión.';
      default:
        break;
    }

    switch (e.response?.statusCode) {
      case 400:
        return 'Datos inválidos. Revisá la solicitud.';
      case 401:
        return 'Tu sesión expiró. Iniciá sesión nuevamente.';
      case 403:
        return 'No tienes permiso para realizar esta acción.';
      case 404:
        return 'Servicio no encontrado.';
      case 500:
        return 'Error interno del servidor. Intentá más tarde.';
      default:
        return 'Ocurrió un error inesperado. Intentá de nuevo.';
    }
  }

  Future<Map<String, dynamic>> cancelarEmergencia({
    required int nroEmergencia,
  }) async {
    try {
      final response = await ApiClient.dio.put(
        '$_basePath/$nroEmergencia',
        data: {
          'estado': 'CANCELADA',
        },
      );

      final data = response.data;

      if (data is! Map) {
        throw Exception('Respuesta inválida del servidor.');
      }

      if (data['success'] != true) {
        throw Exception(data['message'] ?? 'No se pudo cancelar la emergencia.');
      }

      return Map<String, dynamic>.from(data);
    } on DioException catch (e) {
      throw Exception(_parsearErrorDio(e));
    }
  }

  Future<Map<String, dynamic>> agregarEvidencia({
    required int nroEmergencia,
    required String urlEvidencia,
  }) async {
    try {
      final response = await ApiClient.dio.put(
        '$_basePath/$nroEmergencia',
        data: {
          'añadir_evidencias': [urlEvidencia],
          'eliminar_evidencias': [],
        },
      );

      final data = response.data;

      if (data is! Map) {
        throw Exception('Respuesta inválida del servidor.');
      }

      if (data['success'] != true) {
        throw Exception(data['message'] ?? 'No se pudo agregar la evidencia.');
      }

      return Map<String, dynamic>.from(data);
    } on DioException catch (e) {
      throw Exception(_parsearErrorDio(e));
    }
  }

  Future<List<Map<String, dynamic>>> listarEvidenciasEmergencia({
    required int nroEmergencia,
  }) async {
    try {
      final response = await ApiClient.dio.get(
        '$_basePath/$nroEmergencia/evidencias',
      );

      final data = response.data;

      if (data is! Map) {
        throw Exception('Respuesta inválida del servidor.');
      }

      if (data['success'] != true) {
        throw Exception(data['message'] ?? 'No se pudieron obtener las evidencias.');
      }

      final lista = data['data'] as List? ?? [];

      return lista
          .map((item) => Map<String, dynamic>.from(item as Map))
          .toList();
    } on DioException catch (e) {
      throw Exception(_parsearErrorDio(e));
    }
  }

  Future<Map<String, dynamic>> agregarEvidencias({
    required int nroEmergencia,
    required List<Map<String, dynamic>> evidencias,
  }) async {
    try {
      final response = await ApiClient.dio.put(
        '$_basePath/$nroEmergencia',
        data: {
          'añadir_evidencias': evidencias,
          'eliminar_evidencias': [],
        },
      );

      final data = response.data;

      if (data is! Map) {
        throw Exception('Respuesta inválida del servidor.');
      }

      if (data['success'] != true) {
        throw Exception(data['message'] ?? 'No se pudieron agregar las evidencias.');
      }

      return Map<String, dynamic>.from(data);
    } on DioException catch (e) {
      throw Exception(_parsearErrorDio(e));
    }
  }

  

}