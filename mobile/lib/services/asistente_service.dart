import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import 'api_client.dart';

class ChatMessageModel {
  final String id;
  final String role; // 'user' | 'assistant'
  final String content;
  final DateTime timestamp;
  final String tipo; // 'texto' | 'productos' | 'tabla' | 'indicadores'
  final dynamic datos;

  ChatMessageModel({
    required this.id,
    required this.role,
    required this.content,
    required this.timestamp,
    this.tipo = 'texto',
    this.datos,
  });
}

class AsistenteService extends ChangeNotifier {
  final Dio _dio = ApiClient.dio;

  List<ChatMessageModel> _mensajes = [];
  bool _cargando = false;

  List<ChatMessageModel> get mensajes => _mensajes;
  bool get cargando => _cargando;

  AsistenteService() {
    _agregarMensajeBienvenida();
  }

  void _agregarMensajeBienvenida() {
    _mensajes = [
      ChatMessageModel(
        id: 'msg_welcome',
        role: 'assistant',
        content: '¡Hola! Soy el asistente inteligente de Aurora Store.\n\nPuedo ayudarte a buscar prendas exclusivas, consultar disponibilidad de tallas y colores, sucursales o resolver dudas sobre tus pedidos y reservas.\n\n¿Qué deseas consultar hoy?',
        timestamp: DateTime.now(),
      ),
    ];
  }

  void limpiarConversacion() {
    _agregarMensajeBienvenida();
    notifyListeners();
  }

  Future<void> enviarMensaje(String texto) async {
    final mensajeLimpio = texto.trim();
    if (mensajeLimpio.isEmpty) return;

    final userMsg = ChatMessageModel(
      id: 'msg_user_${DateTime.now().millisecondsSinceEpoch}',
      role: 'user',
      content: mensajeLimpio,
      timestamp: DateTime.now(),
    );

    _mensajes.add(userMsg);
    _cargando = true;
    notifyListeners();

    try {
      // Tomar últimos 6 mensajes para contexto conversacional
      final historial = _mensajes
          .sublist(_mensajes.length > 6 ? _mensajes.length - 6 : 0)
          .map((m) => {'role': m.role, 'content': m.content})
          .toList();

      final res = await _dio.post(
        '/api/asistente/chat',
        data: {
          'mensaje': mensajeLimpio,
          'historial': historial,
        },
      );

      final data = res.data;
      final respuestaBot = data['respuesta'] ?? 'He procesado tu consulta.';
      final tipo = data['tipo'] ?? 'texto';
      final datosExtra = data['datos'];

      final botMsg = ChatMessageModel(
        id: 'msg_bot_${DateTime.now().millisecondsSinceEpoch}',
        role: 'assistant',
        content: respuestaBot,
        timestamp: DateTime.now(),
        tipo: tipo,
        datos: datosExtra,
      );

      _mensajes.add(botMsg);
    } catch (e) {
      _mensajes.add(
        ChatMessageModel(
          id: 'msg_err_${DateTime.now().millisecondsSinceEpoch}',
          role: 'assistant',
          content: 'No pude procesar la consulta en este momento. Las demás funciones de Aurora Store continúan funcionando normalmente.',
          timestamp: DateTime.now(),
        ),
      );
    } finally {
      _cargando = false;
      notifyListeners();
    }
  }
}
