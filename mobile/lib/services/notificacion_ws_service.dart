import 'dart:async';
import 'dart:convert';

import 'package:web_socket_channel/web_socket_channel.dart';

import '../config/app_config.dart';
import 'token_storage.dart';

class NotificacionWsService {
  WebSocketChannel? _channel;
  StreamSubscription? _subscription;
  Timer? _pingTimer;

  bool _activo = false;
  bool _conectando = false;

  bool get activo => _activo;

  Future<void> conectar({
    required void Function(bool activo) onEstado,
    required void Function(Map<String, dynamic> mensaje) onMensaje,
    required void Function(String error) onError,
  }) async {
    if (_activo || _conectando) return;

    _conectando = true;

    final token = await TokenStorage.getToken();

    if (token == null || token.trim().isEmpty) {
      _conectando = false;
      onError('No hay token para conectar WebSocket.');
      return;
    }

    try {
      final apiUri = Uri.parse(AppConfig.apiBaseUrl);

      final wsUri = apiUri.replace(
        scheme: apiUri.scheme == 'https' ? 'wss' : 'ws',
        path: '/api/ws/notificaciones',
        queryParameters: {
          'token': token,
        },
      );

      _channel = WebSocketChannel.connect(wsUri);

      _activo = true;
      _conectando = false;
      onEstado(true);

      _iniciarPing();

      _subscription = _channel!.stream.listen(
        (event) {
          try {
            final decoded = jsonDecode(event.toString());

            if (decoded is Map) {
              onMensaje(Map<String, dynamic>.from(decoded));
            }
          } catch (_) {
            onMensaje({
              'tipo_alerta': 'MENSAJE_WS',
              'titulo': 'Mensaje recibido',
              'cuerpo': event.toString(),
              'data': {},
            });
          }
        },
        onError: (error) {
          _marcarDesconectado(onEstado);
          onError(error.toString());
        },
        onDone: () {
          _marcarDesconectado(onEstado);
        },
        cancelOnError: true,
      );
    } catch (e) {
      _activo = false;
      _conectando = false;
      _detenerPing();
      onEstado(false);
      onError(e.toString());
    }
  }

  Future<void> reconectar({
    required void Function(bool activo) onEstado,
    required void Function(Map<String, dynamic> mensaje) onMensaje,
    required void Function(String error) onError,
  }) async {
    await desconectar();

    await Future.delayed(const Duration(milliseconds: 400));

    await conectar(
      onEstado: onEstado,
      onMensaje: onMensaje,
      onError: onError,
    );
  }

  void _iniciarPing() {
    _detenerPing();

    _pingTimer = Timer.periodic(
      const Duration(seconds: 20),
      (_) => enviarPing(),
    );
  }

  void _detenerPing() {
    _pingTimer?.cancel();
    _pingTimer = null;
  }

  void enviarPing() {
    if (!_activo || _channel == null) return;

    try {
      _channel!.sink.add('ping');
    } catch (_) {
      _activo = false;
      _detenerPing();
    }
  }

  void _marcarDesconectado(void Function(bool activo) onEstado) {
    _activo = false;
    _conectando = false;
    _detenerPing();
    onEstado(false);
  }

  Future<void> desconectar() async {
    _activo = false;
    _conectando = false;

    _detenerPing();

    await _subscription?.cancel();
    _subscription = null;

    await _channel?.sink.close();
    _channel = null;
  }
}