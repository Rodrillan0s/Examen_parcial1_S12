import 'package:dio/dio.dart';
import '../config/app_config.dart';
import 'token_storage.dart';

class TriajeService {
  final String _basePath = '/api/triaje';

  final Dio _dio = Dio(
    BaseOptions(
      baseUrl: AppConfig.apiBaseUrl,
      connectTimeout: const Duration(seconds: 20),
      receiveTimeout: const Duration(seconds: 30),
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
    ),
  );

  Future<void> _setAuthHeader() async {
    final token = await TokenStorage.getToken();
    if (token != null && token.isNotEmpty) {
      _dio.options.headers['Authorization'] = 'Bearer $token';
    }
  }

  Future<Map<String, dynamic>> iniciarChat() async {
    await _setAuthHeader();

    try {
      final response = await _dio.post('$_basePath/iniciar');
      return Map<String, dynamic>.from(response.data);
    } on DioException catch (e) {
      throw Exception(_parsearErrorDio(e));
    }
  }

  Future<Map<String, dynamic>> enviarMensaje({
    required int idConversacion,
    required String mensaje,
  }) async {
    await _setAuthHeader();

    try {
      final response = await _dio.post(
        '$_basePath/$idConversacion/mensaje',
        data: {'mensaje': mensaje},
      );

      final data = response.data;

      if (data == null || data['success'] != true) {
        throw Exception(data?['message'] ?? 'No se pudo enviar el mensaje.');
      }

      return Map<String, dynamic>.from(data['data'] ?? {});
    } on DioException catch (e) {
      throw Exception(_parsearErrorDio(e));
    }
  }

  String _parsearErrorDio(DioException e) {
    if (e.response?.data != null) {
      final data = e.response!.data;

      if (data is Map && data['detail'] != null) {
        return data['detail'].toString();
      }
    }

    switch (e.response?.statusCode) {
      case 400:
        return 'El mensaje no puede estar vacío.';
      case 401:
        return 'Sesión vencida. Inicia sesión otra vez.';
      case 404:
        return 'Servicio de chatbot no encontrado.';
      case 500:
        return 'Error del asistente IA. Intenta otra vez.';
      default:
        return 'No se pudo conectar con el asistente.';
    }
  }
}