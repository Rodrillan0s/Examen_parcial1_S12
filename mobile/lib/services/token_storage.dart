import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class TokenStorage {
  static const FlutterSecureStorage _storage = FlutterSecureStorage();

  static const String _keyToken = 'auth_token';
  static const String _keyUserJson = 'auth_user_json';
  static const String _keyEmpresaId = 'selected_empresa_id';

  static Future<void> saveToken(String token) async {
    await _storage.write(key: _keyToken, value: token);
  }

  static Future<String?> getToken() async {
    return _storage.read(key: _keyToken);
  }

  static Future<void> clearToken() async {
    await _storage.delete(key: _keyToken);
    await _storage.delete(key: _keyUserJson);
  }

  static Future<void> saveUserJson(String jsonStr) async {
    await _storage.write(key: _keyUserJson, value: jsonStr);
  }

  static Future<String?> getUserJson() async {
    return _storage.read(key: _keyUserJson);
  }

  static Future<void> saveEmpresaId(int idEmpresa) async {
    await _storage.write(key: _keyEmpresaId, value: idEmpresa.toString());
  }

  static Future<int?> getEmpresaId() async {
    final str = await _storage.read(key: _keyEmpresaId);
    return str != null ? int.tryParse(str) : null;
  }

  static Future<void> clearAll() async {
    await _storage.deleteAll();
  }
}