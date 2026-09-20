import 'package:shared_preferences/shared_preferences.dart';

class AppConfig {
  static const String _keyCustomUrl = 'aurora_custom_api_url';
  static String _overrideBaseUrl = '';

  static const String defaultLocalUrl = 'http://127.0.0.1:5000';
  static const String defaultLanUrl = 'http://192.168.0.9:5000';
  static const String defaultEmulatorUrl = 'http://10.0.2.2:5000';

  static Future<void> init() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final saved = prefs.getString(_keyCustomUrl);
      if (saved != null && saved.isNotEmpty) {
        _overrideBaseUrl = saved.trim();
      }
    } catch (_) {}
  }

  static Future<void> setBaseUrl(String url) async {
    _overrideBaseUrl = url.trim();
    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString(_keyCustomUrl, _overrideBaseUrl);
    } catch (_) {}
  }

  static String get apiBaseUrl {
    if (_overrideBaseUrl.isNotEmpty) {
      return _overrideBaseUrl;
    }

    const envUrl = String.fromEnvironment('API_BASE_URL', defaultValue: '');
    if (envUrl.isNotEmpty) {
      return envUrl;
    }

    // Por defecto 127.0.0.1:5000.
    // En dispositivo físico con 'adb reverse tcp:5000 tcp:5000' redirige directo al PC.
    return defaultLocalUrl;
  }
}