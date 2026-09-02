//auth_provider.dart
import 'package:flutter/material.dart';
import 'token_storage.dart';

class AuthProvider extends ChangeNotifier {
  bool _estaAutenticado = false;
  Map<String, String>? _datosUsuario;

  bool get estaAutenticado => _estaAutenticado;
  Map<String, String>? get datosUsuario => _datosUsuario;

  Future<void> verificarSesion() async {
    final token = await TokenStorage.getToken();
    if (token != null) {
      _estaAutenticado = true;
      notifyListeners();
    }
  }

  void loginExitoso(Map<String, String> datos) {
    _estaAutenticado = true;
    _datosUsuario = datos;
    notifyListeners();
  }

  void logout() {
    _estaAutenticado = false;
    _datosUsuario = null;
    TokenStorage.clearToken();
    notifyListeners();
  }
}