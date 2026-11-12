import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import 'package:uuid/uuid.dart';
import 'api_client.dart';
import 'catalogo_service.dart';
import '../core/tenant/tenant_context_manager.dart';
import '../core/database/database_helper.dart';

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
  final TenantContextManager _tenantManager = TenantContextManager();

  String _conversationId = const Uuid().v4();
  String _modeloSeleccionado = 'deepseek-chat'; // 'deepseek-chat' (V3) o 'deepseek-reasoner' (R1)
  List<ChatMessageModel> _mensajes = [];
  bool _cargando = false;

  String get conversationId => _conversationId;
  String get modeloSeleccionado => _modeloSeleccionado;
  List<ChatMessageModel> get mensajes => _mensajes;
  bool get cargando => _cargando;

  AsistenteService() {
    _agregarMensajeBienvenida();
  }

  void setModelo(String nuevoModelo) {
    if (_modeloSeleccionado != nuevoModelo) {
      _modeloSeleccionado = nuevoModelo;
      notifyListeners();
    }
  }

  void _agregarMensajeBienvenida() {
    final tienda = _tenantManager.nombreTiendaActiva;
    _mensajes = [
      ChatMessageModel(
        id: 'msg_welcome',
        role: 'assistant',
        content: '¡Hola! Soy Aurora Advisor, tu asistente inteligente en $tienda.\n\nPuedo recomendarte outfits elegantes, consultar disponibilidad de prendas por sucursal, guiarte con devoluciones o resolver dudas sobre tus reservas.\n\n¿En qué puedo ayudarte hoy?',
        timestamp: DateTime.now(),
      ),
    ];
  }

  void limpiarConversacion() {
    _conversationId = const Uuid().v4();
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

      final idEmpresa = _tenantManager.idEmpresaActiva ?? 1;
      final idSucursal = _tenantManager.sucursalActual?.idSucursal;

      final res = await _dio.post(
        '/api/asistente/chat',
        data: {
          'mensaje': mensajeLimpio,
          'historial': historial,
          'id_empresa': idEmpresa,
          if (idSucursal != null) 'id_sucursal': idSucursal,
          'conversation_id': _conversationId,
          'modelo': _modeloSeleccionado,
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
      // Extracción y procesamiento inteligente desde la base de datos SQLite local
      final botOfflineMsg = await _procesarConsultaOffline(mensajeLimpio);
      _mensajes.add(botOfflineMsg);
    } finally {
      _cargando = false;
      notifyListeners();
    }
  }

  Future<ChatMessageModel> _procesarConsultaOffline(String mensajeLimpio) async {
    final dbHelper = DatabaseHelper();
    final idEmpresa = _tenantManager.idEmpresaActiva ?? 1;
    final tienda = _tenantManager.nombreTiendaActiva;

    // Palabras comunes a ignorar para extraer palabras clave reales
    final palabrasDescartadas = {
      'hola', 'buenos', 'dias', 'tardes', 'noches', 'quisiera', 'saber', 'sobre',
      'consulta', 'consultar', 'producto', 'productos', 'prenda', 'prendas',
      'tienen', 'tiene', 'hay', 'precio', 'costo', 'disponible', 'disponibles',
      'un', 'una', 'el', 'la', 'los', 'las', 'de', 'en', 'para', 'por', 'con',
    };

    final tokens = mensajeLimpio
        .toLowerCase()
        .replaceAll(RegExp(r'[^\w\s]'), ' ')
        .split(RegExp(r'\s+'))
        .where((t) => t.length > 2 && !palabrasDescartadas.contains(t))
        .toList();

    List<PrendaModel> resultados = [];
    if (tokens.isNotEmpty) {
      for (final t in tokens) {
        final matches = await dbHelper.searchProductsOffline(t, idEmpresa: idEmpresa);
        for (final m in matches) {
          if (!resultados.any((p) => p.idProducto == m.idProducto)) {
            resultados.add(m);
          }
        }
      }
    }

    // Si no hubo coincidencias exactas con tokens, obtener productos del tenant
    if (resultados.isEmpty) {
      resultados = await dbHelper.getProducts(idEmpresa);
    }

    final topItems = resultados.take(3).toList();

    if (topItems.isNotEmpty) {
      final itemsSummary = topItems
          .map((p) => '• ${p.nombre} — Bs. ${p.precio.toStringAsFixed(2)} (${p.categoriaNombre})')
          .join('\n');

      final content = '✨ [Aurora Advisor - Modo Offline]\n'
          'Actualmente tu dispositivo se encuentra sin conexión a internet. Sin embargo, he consultado la base de datos local en tu móvil para responder a tu consulta en $tienda.\n\n'
          'Prendas disponibles en tu catálogo local:\n'
          '$itemsSummary\n\n'
          'Toca cualquiera de las opciones para ver detalles, verificar stock o reservarla:';

      return ChatMessageModel(
        id: 'msg_bot_offline_${DateTime.now().millisecondsSinceEpoch}',
        role: 'assistant',
        content: content,
        timestamp: DateTime.now(),
        tipo: 'productos',
        datos: topItems.map((p) => {
          'id_producto': p.idProducto,
          'nombre': p.nombre,
          'precio': p.precio.toStringAsFixed(2),
          'categoria': p.categoriaNombre,
          'marca': p.marca,
        }).toList(),
      );
    } else {
      return ChatMessageModel(
        id: 'msg_bot_offline_${DateTime.now().millisecondsSinceEpoch}',
        role: 'assistant',
        content: '✨ [Aurora Advisor - Modo Offline]\n'
            'Actualmente estás sin conexión a internet. Puedes explorar el catálogo guardado en tu dispositivo, gestionar tu bolsa o confirmar tus compras con sincronización diferida.',
        timestamp: DateTime.now(),
      );
    }
  }
}
