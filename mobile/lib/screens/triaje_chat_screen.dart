import 'package:flutter/material.dart';
import '../theme/app_theme.dart';
import '../services/triaje_service.dart';

class TriajeChatScreen extends StatefulWidget {
  const TriajeChatScreen({super.key});

  @override
  State<TriajeChatScreen> createState() => _TriajeChatScreenState();
}

class _TriajeChatScreenState extends State<TriajeChatScreen> {
  final TriajeService _triajeService = TriajeService();
  final TextEditingController _controller = TextEditingController();
  final ScrollController _scrollController = ScrollController();

  int? _idConversacion;
  bool _cargando = true;
  bool _enviando = false;
  String? _error;

  String? _nivelRiesgo;
  bool _escaladoHumano = false;

  final List<_ChatMessage> _mensajes = [];

  @override
  void initState() {
    super.initState();
    _iniciarChat();
  }

  Future<void> _iniciarChat() async {
    setState(() {
      _cargando = true;
      _error = null;
      _mensajes.clear();
      _nivelRiesgo = null;
      _escaladoHumano = false;
    });

    try {
      final data = await _triajeService.iniciarChat();

      setState(() {
        _idConversacion = int.tryParse('${data['id_conversacion']}');
        _mensajes.add(
          _ChatMessage(
            texto: data['mensaje_ia']?.toString() ??
                'Hola, soy el asistente virtual. ¿Qué problema presenta tu vehículo?',
            esUsuario: false,
          ),
        );
        _cargando = false;
      });

      _scrollAlFinal();
    } catch (e) {
      setState(() {
        _error = e.toString().replaceFirst('Exception: ', '');
        _cargando = false;
      });
    }
  }

  Future<void> _enviarMensaje() async {
    final texto = _controller.text.trim();

    if (texto.isEmpty || _enviando || _idConversacion == null) return;

    setState(() {
      _mensajes.add(_ChatMessage(texto: texto, esUsuario: true));
      _controller.clear();
      _enviando = true;
      _error = null;
    });

    _scrollAlFinal();

    try {
      final data = await _triajeService.enviarMensaje(
        idConversacion: _idConversacion!,
        mensaje: texto,
      );

      final respuesta = data['respuesta_al_cliente']?.toString() ??
          'No pude analizar el mensaje en este momento.';

      setState(() {
        _mensajes.add(_ChatMessage(texto: respuesta, esUsuario: false));
        _nivelRiesgo = data['nivel_riesgo_detectado']?.toString();
        _escaladoHumano = data['escalar_a_humano'] == true;
        _enviando = false;
      });

      _scrollAlFinal();
    } catch (e) {
      setState(() {
        _error = e.toString().replaceFirst('Exception: ', '');
        _enviando = false;
      });
    }
  }

  void _scrollAlFinal() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (!_scrollController.hasClients) return;

      _scrollController.animateTo(
        _scrollController.position.maxScrollExtent,
        duration: const Duration(milliseconds: 250),
        curve: Curves.easeOut,
      );
    });
  }

  Color _colorRiesgo(String? nivel) {
    switch ((nivel ?? '').toUpperCase()) {
      case 'ALTO':
        return AppTheme.error;
      case 'MEDIO':
        return Colors.orange;
      case 'BAJO':
        return AppTheme.success;
      default:
        return AppTheme.textSecondary;
    }
  }

  @override
  void dispose() {
    _controller.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final riesgoColor = _colorRiesgo(_nivelRiesgo);

    return Scaffold(
      backgroundColor: AppTheme.background,
      appBar: AppBar(
        backgroundColor: AppTheme.primary,
        title: const Text(
          'Asistente ChatBot IA',
          style: TextStyle(fontSize: 15, fontWeight: FontWeight.w800),
        ),
        actions: [
          IconButton(
            onPressed: _iniciarChat,
            icon: const Icon(Icons.refresh_rounded),
          ),
        ],
      ),
      body: _cargando
          ? const Center(child: CircularProgressIndicator())
          : _error != null && _mensajes.isEmpty
              ? _ErrorState(message: _error!, onRetry: _iniciarChat)
              : Column(
                  children: [
                    if (_nivelRiesgo != null || _escaladoHumano)
                      Container(
                        width: double.infinity,
                        margin: const EdgeInsets.all(12),
                        padding: const EdgeInsets.all(12),
                        decoration: BoxDecoration(
                          color: riesgoColor.withOpacity(0.08),
                          borderRadius: BorderRadius.circular(8),
                          border: Border.all(color: riesgoColor.withOpacity(0.25)),
                        ),
                        child: Row(
                          children: [
                            Icon(
                              _escaladoHumano
                                  ? Icons.support_agent_rounded
                                  : Icons.health_and_safety_outlined,
                              color: riesgoColor,
                              size: 20,
                            ),
                            const SizedBox(width: 10),
                            Expanded(
                              child: Text(
                                _escaladoHumano
                                    ? 'Caso escalado a un mecánico. Riesgo: ${_nivelRiesgo ?? 'SIN DEFINIR'}'
                                    : 'Nivel de riesgo detectado: ${_nivelRiesgo ?? 'SIN DEFINIR'}',
                                style: TextStyle(
                                  color: riesgoColor,
                                  fontSize: 12,
                                  fontWeight: FontWeight.w800,
                                ),
                              ),
                            ),
                          ],
                        ),
                      ),

                    if (_error != null)
                      Container(
                        width: double.infinity,
                        margin: const EdgeInsets.symmetric(horizontal: 12),
                        padding: const EdgeInsets.all(10),
                        decoration: BoxDecoration(
                          color: AppTheme.error.withOpacity(0.08),
                          borderRadius: BorderRadius.circular(8),
                          border: Border.all(color: AppTheme.error.withOpacity(0.25)),
                        ),
                        child: Text(
                          _error!,
                          style: const TextStyle(
                            color: AppTheme.error,
                            fontSize: 12,
                            fontWeight: FontWeight.w700,
                          ),
                        ),
                      ),

                    Expanded(
                      child: ListView.builder(
                        controller: _scrollController,
                        padding: const EdgeInsets.all(14),
                        itemCount: _mensajes.length + (_enviando ? 1 : 0),
                        itemBuilder: (context, index) {
                          if (_enviando && index == _mensajes.length) {
                            return const _TypingBubble();
                          }

                          final mensaje = _mensajes[index];

                          return _MessageBubble(message: mensaje);
                        },
                      ),
                    ),

                    SafeArea(
                      top: false,
                      child: Container(
                        padding: const EdgeInsets.fromLTRB(12, 10, 12, 12),
                        decoration: const BoxDecoration(
                          color: AppTheme.surface,
                          border: Border(
                            top: BorderSide(color: AppTheme.border),
                          ),
                        ),
                        child: Row(
                          children: [
                            Expanded(
                              child: TextField(
                                controller: _controller,
                                minLines: 1,
                                maxLines: 4,
                                textInputAction: TextInputAction.send,
                                onSubmitted: (_) => _enviarMensaje(),
                                decoration: InputDecoration(
                                  hintText: 'Describe el problema del vehículo...',
                                  hintStyle: const TextStyle(fontSize: 13),
                                  filled: true,
                                  fillColor: AppTheme.background,
                                  contentPadding: const EdgeInsets.symmetric(
                                    horizontal: 14,
                                    vertical: 12,
                                  ),
                                  border: OutlineInputBorder(
                                    borderRadius: BorderRadius.circular(8),
                                    borderSide: const BorderSide(color: AppTheme.border),
                                  ),
                                  enabledBorder: OutlineInputBorder(
                                    borderRadius: BorderRadius.circular(8),
                                    borderSide: const BorderSide(color: AppTheme.border),
                                  ),
                                  focusedBorder: OutlineInputBorder(
                                    borderRadius: BorderRadius.circular(8),
                                    borderSide: const BorderSide(color: AppTheme.primary),
                                  ),
                                ),
                              ),
                            ),
                            const SizedBox(width: 8),
                            SizedBox(
                              width: 48,
                              height: 48,
                              child: ElevatedButton(
                                onPressed: _enviando ? null : _enviarMensaje,
                                style: ElevatedButton.styleFrom(
                                  backgroundColor: AppTheme.primary,
                                  padding: EdgeInsets.zero,
                                  shape: RoundedRectangleBorder(
                                    borderRadius: BorderRadius.circular(8),
                                  ),
                                ),
                                child: _enviando
                                    ? const SizedBox(
                                        width: 18,
                                        height: 18,
                                        child: CircularProgressIndicator(
                                          strokeWidth: 2,
                                          color: Colors.white,
                                        ),
                                      )
                                    : const Icon(Icons.send_rounded, size: 20),
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                  ],
                ),
    );
  }
}

class _ChatMessage {
  final String texto;
  final bool esUsuario;

  _ChatMessage({
    required this.texto,
    required this.esUsuario,
  });
}

class _MessageBubble extends StatelessWidget {
  final _ChatMessage message;

  const _MessageBubble({required this.message});

  @override
  Widget build(BuildContext context) {
    final alignment =
        message.esUsuario ? CrossAxisAlignment.end : CrossAxisAlignment.start;

    final color = message.esUsuario ? AppTheme.primary : AppTheme.surface;
    final textColor = message.esUsuario ? Colors.white : AppTheme.textPrimary;

    return Column(
      crossAxisAlignment: alignment,
      children: [
        Container(
          constraints: BoxConstraints(
            maxWidth: MediaQuery.of(context).size.width * 0.78,
          ),
          margin: const EdgeInsets.only(bottom: 10),
          padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 11),
          decoration: BoxDecoration(
            color: color,
            borderRadius: BorderRadius.circular(10),
            border: message.esUsuario ? null : Border.all(color: AppTheme.border),
          ),
          child: Text(
            message.texto,
            style: TextStyle(
              color: textColor,
              fontSize: 13,
              height: 1.35,
            ),
          ),
        ),
      ],
    );
  }
}

class _TypingBubble extends StatelessWidget {
  const _TypingBubble();

  @override
  Widget build(BuildContext context) {
    return Align(
      alignment: Alignment.centerLeft,
      child: Container(
        margin: const EdgeInsets.only(bottom: 10),
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 11),
        decoration: BoxDecoration(
          color: AppTheme.surface,
          borderRadius: BorderRadius.circular(10),
          border: Border.all(color: AppTheme.border),
        ),
        child: const Text(
          'Analizando...',
          style: TextStyle(
            color: AppTheme.textSecondary,
            fontSize: 13,
            fontWeight: FontWeight.w700,
          ),
        ),
      ),
    );
  }
}

class _ErrorState extends StatelessWidget {
  final String message;
  final VoidCallback onRetry;

  const _ErrorState({
    required this.message,
    required this.onRetry,
  });

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(22),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Icon(Icons.error_outline_rounded, color: AppTheme.error, size: 36),
            const SizedBox(height: 12),
            Text(
              message,
              textAlign: TextAlign.center,
              style: const TextStyle(
                fontSize: 13,
                color: AppTheme.textSecondary,
              ),
            ),
            const SizedBox(height: 14),
            ElevatedButton(
              onPressed: onRetry,
              child: const Text('Reintentar'),
            ),
          ],
        ),
      ),
    );
  }
}