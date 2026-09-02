import 'package:dio/dio.dart';
import 'api_client.dart';

class VehiculoService {
  static const String _basePath = '/api/vehiculos';

  Future<List<Map<String, dynamic>>> listarMisVehiculos() async {
    try {
      final response = await ApiClient.dio.get('$_basePath/mis-vehiculos');
      final data = response.data;

      if (data is! Map) {
        throw Exception('Respuesta inválida del servidor.');
      }

      if (data['success'] != true) {
        throw Exception(data['message'] ?? 'No se pudieron cargar los vehículos.');
      }

      final lista = data['data'] as List? ?? [];

      return lista
          .map((item) => Map<String, dynamic>.from(item as Map))
          .toList();
    } on DioException catch (e) {
      throw Exception(_parsearErrorDio(e));
    }
  }

  Future<Map<String, dynamic>> registrarVehiculo({
    required String placa,
    required String marcaModelo,
    required int anio,
  }) async {
    try {
      final response = await ApiClient.dio.post(
        '$_basePath/',
        data: {
          'placa': placa.trim().toUpperCase(),
          'marca_modelo': marcaModelo.trim(),
          'anio': anio,
        },
      );

      final data = response.data;

      if (data is! Map) {
        throw Exception('Respuesta inválida del servidor.');
      }

      if (data['success'] != true) {
        throw Exception(data['message'] ?? 'No se pudo registrar el vehículo.');
      }

      return Map<String, dynamic>.from(data);
    } on DioException catch (e) {
      throw Exception(_parsearErrorDio(e));
    }
  }

  Future<Map<String, dynamic>> actualizarVehiculo({
    required int nroVehiculo,
    required String placa,
    required String marcaModelo,
    required int anio,
  }) async {
    try {
      final response = await ApiClient.dio.put(
        '$_basePath/$nroVehiculo',
        data: {
          'placa': placa.trim().toUpperCase(),
          'marca_modelo': marcaModelo.trim(),
          'anio': anio,
        },
      );

      final data = response.data;

      if (data is! Map) {
        throw Exception('Respuesta inválida del servidor.');
      }

      if (data['success'] != true) {
        throw Exception(data['message'] ?? 'No se pudo actualizar el vehículo.');
      }

      return Map<String, dynamic>.from(data);
    } on DioException catch (e) {
      throw Exception(_parsearErrorDio(e));
    }
  }

  Future<Map<String, dynamic>> eliminarVehiculo({
    required int nroVehiculo,
  }) async {
    try {
      final response = await ApiClient.dio.delete('$_basePath/$nroVehiculo');
      final data = response.data;

      if (data is! Map) {
        throw Exception('Respuesta inválida del servidor.');
      }

      if (data['success'] != true) {
        throw Exception(data['message'] ?? 'No se pudo eliminar el vehículo.');
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
        return 'Tiempo de espera agotado. Verificá tu conexión.';
      case DioExceptionType.connectionError:
        return 'No se pudo conectar al servidor.';
      default:
        break;
    }

    switch (e.response?.statusCode) {
      case 400:
        return 'Datos inválidos. Revisá el formulario.';
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