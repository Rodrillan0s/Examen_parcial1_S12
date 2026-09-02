import 'package:flutter/material.dart';

import '../services/notificacion_service.dart';
import '../services/emergencia_service.dart';
import '../theme/app_theme.dart';
import 'detalle_emergencia_screen.dart';

class NotificacionesScreen extends StatefulWidget {
  const NotificacionesScreen({super.key});

  @override
  State<NotificacionesScreen> createState() => _NotificacionesScreenState();
}

class _NotificacionesScreenState extends State<NotificacionesScreen> {
  late Future<List<Map<String, dynamic>>> _futureNotificaciones;

  bool _marcandoTodo = false;
  bool _abriendoEmergencia = false;

  @override
  void initState() {
    super.initState();
    _futureNotificaciones = NotificacionService().listarMisNotificaciones();
  }

  Future<void> _refrescar() async {
    final nuevaCarga = NotificacionService().listarMisNotificaciones();

    setState(() {
      _futureNotificaciones = nuevaCarga;
    });

    await nuevaCarga;
  }

  bool _leido(dynamic value) {
    if (value is bool) return value;

    final texto = value?.toString().toLowerCase().trim();

    return texto == 'true' || texto == '1' || texto == 'si';
  }

  String _texto(dynamic value) {
    if (value == null) return '';
    return value.toString().trim();
  }

  Color _colorTipo(String tipo) {
    final t = tipo.toUpperCase();

    if (t == 'NUEVA_OFERTA') return AppTheme.primary;
    if (t == 'RESPUESTA_OFERTA') return AppTheme.success;
    if (t == 'NUEVA_EMERGENCIA') return AppTheme.error;

    return AppTheme.textSecondary;
  }

  IconData _iconoTipo(String tipo) {
    final t = tipo.toUpperCase();

    if (t == 'NUEVA_OFERTA') return Icons.request_quote_outlined;
    if (t == 'RESPUESTA_OFERTA') return Icons.task_alt_rounded;
    if (t == 'NUEVA_EMERGENCIA') return Icons.car_crash_outlined;

    return Icons.notifications_none_rounded;
  }

  Future<void> _marcarTodo() async {
    setState(() {
      _marcandoTodo = true;
    });

    try {
      await NotificacionService().marcarTodasComoLeidas();

      if (!mounted) return;

      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Todas las notificaciones fueron marcadas como leídas.'),
          backgroundColor: AppTheme.success,
        ),
      );

      await _refrescar();
    } catch (e) {
      if (!mounted) return;

      _mostrarError(e.toString().replaceAll('Exception: ', ''));
    } finally {
      if (mounted) {
        setState(() {
          _marcandoTodo = false;
        });
      }
    }
  }

  Future<void> _abrirNotificacion(Map<String, dynamic> notificacion) async {
    final id = int.tryParse(_texto(notificacion['id_notificacion']));
    final nroEmergencia = int.tryParse(_texto(notificacion['nro_emergencia']));

    try {
      if (id != null && !_leido(notificacion['leido'])) {
        await NotificacionService().marcarComoLeida(
          idNotificacion: id,
        );
      }

      if (nroEmergencia != null) {
        await _abrirDetalleEmergencia(nroEmergencia);
      }

      await _refrescar();
    } catch (e) {
      if (!mounted) return;

      _mostrarError(e.toString().replaceAll('Exception: ', ''));
    }
  }

  Future<void> _abrirDetalleEmergencia(int nroEmergencia) async {
    if (_abriendoEmergencia) return;

    setState(() {
      _abriendoEmergencia = true;
    });

    try {
      final emergencias = await EmergenciaService().listarMisEmergencias();

      final emergencia = emergencias.where((item) {
        return item['nro_emergencia'].toString() == nroEmergencia.toString();
      }).cast<Map<String, dynamic>>().firstOrNull;

      if (!mounted) return;

      if (emergencia == null) {
        _mostrarError('No se encontró la emergencia vinculada.');
        return;
      }

      await Navigator.push(
        context,
        MaterialPageRoute(
          builder: (_) => DetalleEmergenciaScreen(
            emergencia: emergencia,
          ),
        ),
      );
    } finally {
      if (mounted) {
        setState(() {
          _abriendoEmergencia = false;
        });
      }
    }
  }

  void _mostrarError(String mensaje) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(mensaje),
        backgroundColor: AppTheme.error,
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.background,
      appBar: AppBar(
        title: const Text('NOTIFICACIONES'),
        backgroundColor: AppTheme.primary,
        foregroundColor: Colors.white,
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios_new_rounded, size: 18),
          onPressed: () => Navigator.pop(context),
        ),
        actions: [
          IconButton(
            onPressed: _marcandoTodo ? null : _marcarTodo,
            tooltip: 'Marcar todo como leído',
            icon: _marcandoTodo
                ? const SizedBox(
                    width: 18,
                    height: 18,
                    child: CircularProgressIndicator(
                      strokeWidth: 2,
                      color: Colors.white,
                    ),
                  )
                : const Icon(Icons.done_all_rounded),
          ),
        ],
      ),
      body: Stack(
        children: [
          FutureBuilder<List<Map<String, dynamic>>>(
            future: _futureNotificaciones,
            builder: (context, snapshot) {
              if (snapshot.connectionState == ConnectionState.waiting) {
                return const _LoadingState();
              }

              if (snapshot.hasError) {
                return _ErrorState(
                  mensaje: snapshot.error.toString().replaceAll('Exception: ', ''),
                  onReintentar: _refrescar,
                );
              }

              final notificaciones = snapshot.data ?? [];

              if (notificaciones.isEmpty) {
                return _EmptyState(onRefrescar: _refrescar);
              }

              final noLeidas = notificaciones
                  .where((item) => !_leido(item['leido']))
                  .length;

              return RefreshIndicator(
                color: AppTheme.primary,
                onRefresh: _refrescar,
                child: ListView.separated(
                  padding: const EdgeInsets.all(20),
                  itemCount: notificaciones.length + 1,
                  separatorBuilder: (_, __) => const SizedBox(height: 12),
                  itemBuilder: (context, index) {
                    if (index == 0) {
                      return _NotificacionesHeader(
                        total: notificaciones.length,
                        noLeidas: noLeidas,
                      );
                    }

                    final item = notificaciones[index - 1];
                    final tipo = _texto(item['tipo_referencia']);
                    final leido = _leido(item['leido']);

                    return _NotificacionCard(
                      titulo: _texto(item['titulo']),
                      cuerpo: _texto(item['cuerpo']),
                      tipo: tipo,
                      fecha: _texto(item['fecha_creacion']),
                      nroEmergencia: _texto(item['nro_emergencia']),
                      leido: leido,
                      color: _colorTipo(tipo),
                      icon: _iconoTipo(tipo),
                      onTap: () => _abrirNotificacion(item),
                    );
                  },
                ),
              );
            },
          ),
          if (_abriendoEmergencia)
            Container(
              color: Colors.black.withOpacity(0.08),
              child: const Center(
                child: CircularProgressIndicator(
                  color: AppTheme.primary,
                ),
              ),
            ),
        ],
      ),
    );
  }
}

class _NotificacionesHeader extends StatelessWidget {
  final int total;
  final int noLeidas;

  const _NotificacionesHeader({
    required this.total,
    required this.noLeidas,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: AppTheme.primary,
        borderRadius: BorderRadius.circular(8),
      ),
      child: Row(
        children: [
          Container(
            width: 48,
            height: 48,
            decoration: BoxDecoration(
              color: Colors.white.withOpacity(0.15),
              borderRadius: BorderRadius.circular(8),
            ),
            child: const Icon(
              Icons.notifications_active_outlined,
              color: Colors.white,
              size: 26,
            ),
          ),
          const SizedBox(width: 14),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'BANDEJA DE ALERTAS',
                  style: TextStyle(
                    color: Color(0xFFBFCFFF),
                    fontSize: 11,
                    fontWeight: FontWeight.w700,
                    letterSpacing: 1,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  '$noLeidas sin leer',
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 20,
                    fontWeight: FontWeight.w900,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  '$total notificación${total == 1 ? '' : 'es'} registradas',
                  style: const TextStyle(
                    color: Color(0xFFBFCFFF),
                    fontSize: 12,
                    height: 1.3,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _NotificacionCard extends StatelessWidget {
  final String titulo;
  final String cuerpo;
  final String tipo;
  final String fecha;
  final String nroEmergencia;
  final bool leido;
  final Color color;
  final IconData icon;
  final VoidCallback onTap;

  const _NotificacionCard({
    required this.titulo,
    required this.cuerpo,
    required this.tipo,
    required this.fecha,
    required this.nroEmergencia,
    required this.leido,
    required this.color,
    required this.icon,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return AnimatedContainer(
      duration: const Duration(milliseconds: 180),
      decoration: BoxDecoration(
        color: leido ? AppTheme.surface : color.withOpacity(0.06),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(
          color: leido ? AppTheme.border : color.withOpacity(0.35),
          width: leido ? 1 : 1.4,
        ),
      ),
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          borderRadius: BorderRadius.circular(8),
          onTap: onTap,
          child: Padding(
            padding: const EdgeInsets.all(14),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Stack(
                  children: [
                    Container(
                      width: 44,
                      height: 44,
                      decoration: BoxDecoration(
                        color: color.withOpacity(0.09),
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Icon(
                        icon,
                        color: color,
                        size: 23,
                      ),
                    ),
                    if (!leido)
                      Positioned(
                        right: 2,
                        top: 2,
                        child: Container(
                          width: 9,
                          height: 9,
                          decoration: const BoxDecoration(
                            color: AppTheme.error,
                            shape: BoxShape.circle,
                          ),
                        ),
                      ),
                  ],
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        tipo.toUpperCase(),
                        style: TextStyle(
                          fontSize: 10,
                          fontWeight: FontWeight.w900,
                          color: color,
                          letterSpacing: 0.8,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        titulo.isEmpty ? 'Notificación' : titulo,
                        style: TextStyle(
                          fontSize: 14,
                          fontWeight: leido ? FontWeight.w700 : FontWeight.w900,
                          color: AppTheme.textPrimary,
                          height: 1.25,
                        ),
                      ),
                      const SizedBox(height: 5),
                      Text(
                        cuerpo,
                        style: const TextStyle(
                          fontSize: 12,
                          color: AppTheme.textSecondary,
                          height: 1.35,
                        ),
                      ),
                      const SizedBox(height: 10),
                      Row(
                        children: [
                          const Icon(
                            Icons.access_time_rounded,
                            size: 13,
                            color: AppTheme.textSecondary,
                          ),
                          const SizedBox(width: 4),
                          Expanded(
                            child: Text(
                              fecha.isEmpty ? 'Sin fecha' : fecha,
                              style: const TextStyle(
                                fontSize: 10,
                                color: AppTheme.textSecondary,
                              ),
                            ),
                          ),
                          if (nroEmergencia.isNotEmpty &&
                              nroEmergencia != 'null') ...[
                            const SizedBox(width: 8),
                            Text(
                              'Emergencia N° $nroEmergencia',
                              style: const TextStyle(
                                fontSize: 10,
                                fontWeight: FontWeight.w800,
                                color: AppTheme.primary,
                              ),
                            ),
                          ],
                        ],
                      ),
                    ],
                  ),
                ),
                const SizedBox(width: 6),
                const Icon(
                  Icons.chevron_right_rounded,
                  color: AppTheme.textHint,
                  size: 22,
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class _LoadingState extends StatelessWidget {
  const _LoadingState();

  @override
  Widget build(BuildContext context) {
    return const Center(
      child: SizedBox(
        width: 26,
        height: 26,
        child: CircularProgressIndicator(
          strokeWidth: 2.5,
          color: AppTheme.primary,
        ),
      ),
    );
  }
}

class _ErrorState extends StatelessWidget {
  final String mensaje;
  final Future<void> Function() onReintentar;

  const _ErrorState({
    required this.mensaje,
    required this.onReintentar,
  });

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(28),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              width: 54,
              height: 54,
              decoration: BoxDecoration(
                color: AppTheme.error.withOpacity(0.08),
                shape: BoxShape.circle,
              ),
              child: const Icon(
                Icons.error_outline_rounded,
                color: AppTheme.error,
                size: 30,
              ),
            ),
            const SizedBox(height: 14),
            const Text(
              'No se pudieron cargar las notificaciones',
              textAlign: TextAlign.center,
              style: TextStyle(
                fontSize: 15,
                fontWeight: FontWeight.w800,
                color: AppTheme.textPrimary,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              mensaje,
              textAlign: TextAlign.center,
              style: const TextStyle(
                fontSize: 12,
                color: AppTheme.textSecondary,
                height: 1.4,
              ),
            ),
            const SizedBox(height: 20),
            OutlinedButton.icon(
              onPressed: onReintentar,
              icon: const Icon(Icons.refresh_rounded, size: 16),
              label: const Text('REINTENTAR'),
            ),
          ],
        ),
      ),
    );
  }
}

class _EmptyState extends StatelessWidget {
  final Future<void> Function() onRefrescar;

  const _EmptyState({
    required this.onRefrescar,
  });

  @override
  Widget build(BuildContext context) {
    return RefreshIndicator(
      color: AppTheme.primary,
      onRefresh: onRefrescar,
      child: ListView(
        padding: const EdgeInsets.all(28),
        children: [
          const SizedBox(height: 100),
          Center(
            child: Container(
              width: 62,
              height: 62,
              decoration: BoxDecoration(
                color: AppTheme.primary.withOpacity(0.08),
                shape: BoxShape.circle,
              ),
              child: const Icon(
                Icons.notifications_none_rounded,
                color: AppTheme.primary,
                size: 32,
              ),
            ),
          ),
          const SizedBox(height: 18),
          const Text(
            'Sin notificaciones',
            textAlign: TextAlign.center,
            style: TextStyle(
              fontSize: 17,
              fontWeight: FontWeight.w900,
              color: AppTheme.textPrimary,
            ),
          ),
          const SizedBox(height: 8),
          const Text(
            'Aquí aparecerán alertas sobre cotizaciones, emergencias y cambios de estado.',
            textAlign: TextAlign.center,
            style: TextStyle(
              fontSize: 13,
              color: AppTheme.textSecondary,
              height: 1.45,
            ),
          ),
        ],
      ),
    );
  }
}