import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';

class PendingEmergenciaService {
  static const String _key = 'pending_emergencias';

  Future<void> guardar(Map<String, dynamic> payload) async {
    final prefs = await SharedPreferences.getInstance();
    final actuales = prefs.getStringList(_key) ?? [];

    final item = {
      'local_id': DateTime.now().microsecondsSinceEpoch.toString(),
      'created_at': DateTime.now().toIso8601String(),
      'payload': payload,
    };

    actuales.add(jsonEncode(item));

    await prefs.setStringList(_key, actuales);
  }

  Future<List<Map<String, dynamic>>> listar() async {
    final prefs = await SharedPreferences.getInstance();
    final actuales = prefs.getStringList(_key) ?? [];

    return actuales
        .map((item) => Map<String, dynamic>.from(jsonDecode(item)))
        .toList();
  }

  Future<int> contar() async {
    final prefs = await SharedPreferences.getInstance();
    return (prefs.getStringList(_key) ?? []).length;
  }

  Future<void> eliminarPorLocalId(String localId) async {
    final prefs = await SharedPreferences.getInstance();
    final actuales = prefs.getStringList(_key) ?? [];

    final filtrados = actuales.where((item) {
      final decoded = Map<String, dynamic>.from(jsonDecode(item));
      return decoded['local_id'].toString() != localId;
    }).toList();

    await prefs.setStringList(_key, filtrados);
  }

  Future<void> limpiarTodo() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_key);
  }
}