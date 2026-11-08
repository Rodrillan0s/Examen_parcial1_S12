import 'dart:async';
import 'package:connectivity_plus/connectivity_plus.dart';
import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import '../../services/api_client.dart';

class ConnectivityService extends ChangeNotifier {
  static final ConnectivityService _instance = ConnectivityService._internal();
  factory ConnectivityService() => _instance;
  ConnectivityService._internal();

  final Connectivity _connectivity = Connectivity();
  StreamSubscription<List<ConnectivityResult>>? _subscription;

  bool _isOnline = true;
  bool _isChecking = false;

  bool get isOnline => _isOnline;
  bool get isOffline => !_isOnline;

  Future<void> inicializar({VoidCallback? onRegainedConnection}) async {
    // 1. Estado inicial
    final results = await _connectivity.checkConnectivity();
    _isOnline = _evaluarResultados(results);
    notifyListeners();

    // 2. Escuchar cambios de red
    _subscription = _connectivity.onConnectivityChanged.listen((results) async {
      final nuevoEstado = _evaluarResultados(results);
      if (nuevoEstado != _isOnline) {
        _isOnline = nuevoEstado;
        notifyListeners();
        if (_isOnline && onRegainedConnection != null) {
          onRegainedConnection();
        }
      }
    });
  }

  bool _evaluarResultados(List<ConnectivityResult> results) {
    if (results.isEmpty) return false;
    return results.any((r) => r != ConnectivityResult.none);
  }

  /// Verifica conectividad real con el backend mediante un ping rápido
  Future<bool> verificarConexionReal() async {
    if (_isChecking) return _isOnline;
    _isChecking = true;
    try {
      final res = await ApiClient.dio.get(
        '/api/catalogo/tenants',
        options: Options(receiveTimeout: const Duration(seconds: 4)),
      );
      _isOnline = (res.statusCode == 200);
    } catch (_) {
      _isOnline = false;
    } finally {
      _isChecking = false;
      notifyListeners();
    }
    return _isOnline;
  }

  @override
  void dispose() {
    _subscription?.cancel();
    super.dispose();
  }
}
