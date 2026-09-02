//auth_service.dart
import 'package:dio/dio.dart';
import '../config/app_config.dart';
import 'token_storage.dart';

class AuthService {
  final Dio _dio = Dio(
    BaseOptions(
      baseUrl: AppConfig.apiBaseUrl,
      connectTimeout: const Duration(seconds: 20),
      receiveTimeout: const Duration(seconds: 20),
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
    ),
  );

  // ── LOGIN ──────────────────────────────────────────────────────────────
  // POST /api/auth/login
  // Body: { "ci": "...", "password": "..." }
  // Response: { "success": true, "token": "...", "usuario": { ... } }
  Future<Map<String, dynamic>> login({
    required String ci,
    required String password,
  }) async {
    try {
      final response = await _dio.post(
        '/api/auth/login',
        data: {'ci': ci, 'password': password},
      );

      final data = response.data;

      if (data == null || data['success'] != true) {
        throw Exception(data?['message'] ?? 'Error al iniciar sesión.');
      }

      final token = data['token'] as String;
      final usuario = data['usuario'] as Map<String, dynamic>;

      // Guardamos token y todos los datos del usuario en secure storage
      await TokenStorage.saveToken(token);
      await TokenStorage.saveUserData(
        nroUsuario: usuario['nro_usuario'].toString(),
        ci: usuario['ci'].toString(),
        nombreCompleto: usuario['nombre_completo'].toString(),
        correo: usuario['correo'].toString(),
        nombreRol: usuario['nombre_rol'].toString(),
        telefono: usuario['telefono'].toString(),
        idEmpresa: usuario['id_empresa']?.toString() ?? '',
      );

      return usuario;
    } on DioException catch (e) {
      throw Exception(_parsearErrorDio(e));
    }
  }

  // ── REGISTER ───────────────────────────────────────────────────────────
  // POST /api/auth/register
  // Body: {
  //   "ci": "...",
  //   "nombre_completo": "...",
  //   "nombre_usuario": "...",
  //   "password": "...",
  //   "nro_rol": 3,           ← 3 = Cliente (ajustá según tu BD)
  //   "telefono": "...",
  //   "correo": "...",
  //   "direccion": "",        ← opcional
  //   "id_empresa": null      ← null para clientes sin empresa
  // }
  // Response: { "success": true, "message": "...", "data": { ... } }
  Future<Map<String, dynamic>> register({
    required String ci,
    required String nombreCompleto,
    required String nombreUsuario,
    required String password,
    required String telefono,
    required String correo,
    required int nroRol,
    String direccion = '',
    int? idEmpresa,
  }) async {
    try {
      final response = await _dio.post(
        '/api/auth/register',
        data: {
          'ci': ci,
          'nombre_completo': nombreCompleto,
          'nombre_usuario': nombreUsuario,
          'password': password,
          'nro_rol': nroRol,
          'telefono': telefono,
          'correo': correo,
          'direccion': direccion,
          'id_empresa': idEmpresa,
        },
      );

      final data = response.data;

      if (data == null || data['success'] != true) {
        throw Exception(data?['message'] ?? 'Error al registrar usuario.');
      }

      return data;
    } on DioException catch (e) {
      throw Exception(_parsearErrorDio(e));
    }
  }

  // ── Parser de errores Dio ──────────────────────────────────────────────
  // FastAPI siempre devuelve errores en response.data['detail']
  String _parsearErrorDio(DioException e) {
    // Primero intentamos leer el 'detail' que manda FastAPI
    if (e.response?.data != null) {
      final data = e.response!.data;

      // Caso normal: { "detail": "mensaje del backend" }
      if (data is Map && data['detail'] != null) {
        return data['detail'].toString();
      }

      // Caso raro: FastAPI manda detail como lista de validaciones
      if (data is Map && data['detail'] is List) {
        final errores = data['detail'] as List;
        return errores.map((e) => e['msg'] ?? e.toString()).join('\n');
      }
    }

    // Errores de red (sin respuesta del servidor)
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

    // Fallback por código HTTP
    switch (e.response?.statusCode) {
      case 400:
        return 'Datos inválidos. Revisá el formulario.';
      case 401:
        return 'Credenciales incorrectas.';
      case 404:
        return 'Servicio no encontrado.';
      case 500:
        return 'Error interno del servidor. Intentá más tarde.';
      default:
        return 'Ocurrió un error inesperado. Intentá de nuevo.';
    }
  }
}