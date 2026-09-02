import 'package:dio/dio.dart';
import 'api_client.dart';

class ProfileService {
  static const String _basePath = '/api/perfil';

  Future<Map<String, dynamic>> obtenerPerfil() async {
    try {
      final response = await ApiClient.dio.get('$_basePath/');
      final data = response.data;

      if (data is! Map) {
        throw Exception('Respuesta inválida del servidor.');
      }

      if (data['success'] != true) {
        throw Exception(data['message'] ?? 'No se pudo obtener el perfil.');
      }

      final perfil = data['data'];

      if (perfil is! Map) {
        throw Exception('Datos de perfil inválidos.');
      }

      return Map<String, dynamic>.from(perfil);
    } on DioException catch (e) {
      throw Exception(_parsearErrorDio(e));
    }
  }

  Future<Map<String, dynamic>> actualizarPerfil({
    required String ci,
    required String telefono,
    required String correo,
    required String direccion,
    String? password,
  }) async {
    try {
      final body = {
        'ci': ci,
        'telefono': telefono,
        'correo': correo,
        'direccion': direccion,
      };

      if (password != null && password.trim().isNotEmpty) {
        body['password'] = password.trim();
      }

      final response = await ApiClient.dio.put(
        '$_basePath/',
        data: body,
      );

      final data = response.data;

      if (data is! Map) {
        throw Exception('Respuesta inválida del servidor.');
      }

      if (data['success'] != true) {
        throw Exception(data['message'] ?? 'No se pudo actualizar el perfil.');
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