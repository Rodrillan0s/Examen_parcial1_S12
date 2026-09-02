//api_client.dart
import 'package:dio/dio.dart';
import '../config/app_config.dart';
import 'token_storage.dart';

class ApiClient {
  static final Dio dio = Dio(
    BaseOptions(
      baseUrl: AppConfig.apiBaseUrl,
      connectTimeout: const Duration(seconds: 20),
      receiveTimeout: const Duration(seconds: 20),
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
    ),
  )..interceptors.add(
      InterceptorsWrapper(
        onRequest: (options, handler) async {
          // Inyectar el token automáticamente en CADA petición que hagas
          final token = await TokenStorage.getToken();
          if (token != null) {
            options.headers['Authorization'] = 'Bearer $token';
          }
          return handler.next(options);
        },
        onError: (DioException e, handler) async {
          // Si el token expira (401), aquí podrías forzar el cierre de sesión
          if (e.response?.statusCode == 401) {
            await TokenStorage.clearToken();
            // TODO: Redirigir al LoginScreen
          }
          return handler.next(e);
        },
      ),
    );
}