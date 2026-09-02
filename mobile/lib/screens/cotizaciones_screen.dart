import 'package:flutter/material.dart';

import '../services/emergencia_service.dart';
import '../services/oferta_service.dart';
import '../theme/app_theme.dart';
import 'detalle_emergencia_screen.dart';

class CotizacionesScreen extends StatefulWidget {
  const CotizacionesScreen({super.key});

  @override
  State<CotizacionesScreen> createState() => _CotizacionesScreenState();
}

class _CotizacionesScreenState extends State<CotizacionesScreen> {
  late Future<List<Map<String, dynamic>>> _futureCotizaciones;
  bool _respondiendo = false;

  @override
  void initState() {
    super.initState();
    _futureCotizaciones = _cargarCotizaciones();
  }

  Future<List<Map<String, dynamic>>> _cargarCotizaciones() async {
    final emergencias = await EmergenciaService().listarMisEmergencias();

    final List<Map<String, dynamic>> cotizaciones = [];

    for (final emergencia in emergencias) {
      final nroEmergencia = int.tryParse(
        emergencia['nro_emergencia'].toString(),
      );

      if (nroEmergencia == null) continue;

      try {
        final ofertas = await OfertaService().listarOfertasPorEmergencia(
          nroEmergencia: nroEmergencia,
        );

        for (final oferta in ofertas) {
          cotizaciones.add({
            'emergencia': emergencia,
            'oferta': oferta,
          });
        }
      } catch (_) {
        continue;
      }
    }

    return cotizaciones;
  }

  Future<void> _refrescar() async {
    final nuevaCarga = _cargarCotizaciones();

    setState(() {
      _futureCotizaciones = nuevaCarga;
    });

    await nuevaCarga;
  }

  String _texto(dynamic value) {
    if (value == null) return 'No disponible';
    final texto = value.toString().trim();
    return texto.isEmpty ? 'No disponible' : texto;
  }

  Color _colorEstado(String estado) {
    final e = estado.toUpperCase();

    if (e == 'PENDIENTE') return AppTheme.primary;
    if (e == 'ACEPTADA') return AppTheme.success;
    if (e == 'RECHAZADA') return AppTheme.error;

    return AppTheme.textSecondary;
  }

  bool _puedeResponder(String estado) {
    return estado.toUpperCase() == 'PENDIENTE';
  }

  Future<void> _responderOferta({
    required Map<String, dynamic> oferta,
    required String estadoOferta,
  }) async {
    final idOferta = int.tryParse(oferta['id_oferta'].toString());

    if (idOferta == null) {
      _mostrarError('No se pudo identificar la oferta.');
      return;
    }

    final acepta = estadoOferta == 'ACEPTADA';

    final confirmar = await showDialog<bool>(
      context: context,
      builder: (ctx) {
        return AlertDialog(
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(8),
          ),
          title: Text(
            acepta ? 'Aceptar cotización' : 'Rechazar cotización',
            style: const TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.w800,
              color: AppTheme.textPrimary,
            ),
          ),
          content: Text(
            acepta
                ? '¿Deseas aceptar esta cotización? Las demás ofertas pendientes serán rechazadas.'
                : '¿Deseas rechazar esta cotización?',
            style: const TextStyle(
              fontSize: 13,
              color: AppTheme.textSecondary,
              height: 1.4,
            ),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(ctx, false),
              child: const Text(
                'Cancelar',
                style: TextStyle(color: AppTheme.textSecondary),
              ),
            ),
            ElevatedButton(
              style: ElevatedButton.styleFrom(
                backgroundColor: acepta ? AppTheme.success : AppTheme.error,
                minimumSize: Size.zero,
                padding: const EdgeInsets.symmetric(
                  horizontal: 18,
                  vertical: 10,
                ),
              ),
              onPressed: () => Navigator.pop(ctx, true),
              child: Text(
                acepta ? 'ACEPTAR' : 'RECHAZAR',
                style: const TextStyle(
                  fontSize: 12,
                  fontWeight: FontWeight.w800,
                ),
              ),
            ),
          ],
        );
      },
    );

    if (confirmar != true) return;

    setState(() {
      _respondiendo = true;
    });

    try {
      await OfertaService().responderOferta(
        idOferta: idOferta,
        estadoOferta: estadoOferta,
      );

      if (!mounted) return;

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            acepta
                ? 'Cotización aceptada correctamente.'
                : 'Cotización rechazada correctamente.',
          ),
          backgroundColor: acepta ? AppTheme.success : AppTheme.error,
        ),
      );

      await _refrescar();
    } catch (e) {
      if (!mounted) return;

      _mostrarError(e.toString().replaceAll('Exception: ', ''));
    } finally {
      if (mounted) {
        setState(() {
          _respondiendo = false;
        });
      }
    }
  }

  Future<void> _abrirDetalle(Map<String, dynamic> emergencia) async {
    await Navigator.push(
      context,
      MaterialPageRoute(
        builder: (_) => DetalleEmergenciaScreen(
          emergencia: emergencia,
        ),
      ),
    );

    if (!mounted) return;

    await _refrescar();
  }

  void _mostrarError(String mensaje) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(mensaje),
        backgroundColor: AppTheme.error,
      ),
    );
  }

  int _contarPendientes(List<Map<String, dynamic>> cotizaciones) {
    return cotizaciones.where((item) {
      final oferta = item['oferta'] as Map<String, dynamic>;
      return _texto(oferta['estado_oferta']).toUpperCase() == 'PENDIENTE';
    }).length;
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.background,
      appBar: AppBar(
        title: const Text('COTIZACIONES'),
        backgroundColor: AppTheme.primary,
        foregroundColor: Colors.white,
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios_new_rounded, size: 18),
          onPressed: () => Navigator.pop(context),
        ),
      ),
      body: Stack(
        children: [
          FutureBuilder<List<Map<String, dynamic>>>(
            future: _futureCotizaciones,
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

              final cotizaciones = snapshot.data ?? [];

              if (cotizaciones.isEmpty) {
                return _EmptyState(onRefrescar: _refrescar);
              }

              final pendientes = _contarPendientes(cotizaciones);

              return RefreshIndicator(
                color: AppTheme.primary,
                onRefresh: _refrescar,
                child: ListView.separated(
                  padding: const EdgeInsets.all(20),
                  itemCount: cotizaciones.length + 1,
                  separatorBuilder: (_, __) => const SizedBox(height: 12),
                  itemBuilder: (context, index) {
                    if (index == 0) {
                      return _CotizacionesHeader(
                        total: cotizaciones.length,
                        pendientes: pendientes,
                      );
                    }

                    final item = cotizaciones[index - 1];
                    final emergencia = item['emergencia'] as Map<String, dynamic>;
                    final oferta = item['oferta'] as Map<String, dynamic>;

                    final estado = _texto(oferta['estado_oferta']).toUpperCase();
                    final color = _colorEstado(estado);

                    return _CotizacionCard(
                      emergencia: emergencia,
                      oferta: oferta,
                      estadoColor: color,
                      respondiendo: _respondiendo,
                      puedeResponder: _puedeResponder(estado),
                      onAceptar: () => _responderOferta(
                        oferta: oferta,
                        estadoOferta: 'ACEPTADA',
                      ),
                      onRechazar: () => _responderOferta(
                        oferta: oferta,
                        estadoOferta: 'RECHAZADA',
                      ),
                      onDetalle: () => _abrirDetalle(emergencia),
                    );
                  },
                ),
              );
            },
          ),
          if (_respondiendo)
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

class _CotizacionesHeader extends StatelessWidget {
  final int total;
  final int pendientes;

  const _CotizacionesHeader({
    required this.total,
    required this.pendientes,
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
              Icons.request_quote_outlined,
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
                  'COTIZACIONES RECIBIDAS',
                  style: TextStyle(
                    color: Color(0xFFBFCFFF),
                    fontSize: 11,
                    fontWeight: FontWeight.w700,
                    letterSpacing: 1,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  '$pendientes pendientes',
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 20,
                    fontWeight: FontWeight.w900,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  '$total cotización${total == 1 ? '' : 'es'} en total',
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

class _CotizacionCard extends StatelessWidget {
  final Map<String, dynamic> emergencia;
  final Map<String, dynamic> oferta;
  final Color estadoColor;
  final bool respondiendo;
  final bool puedeResponder;
  final VoidCallback onAceptar;
  final VoidCallback onRechazar;
  final VoidCallback onDetalle;

  const _CotizacionCard({
    required this.emergencia,
    required this.oferta,
    required this.estadoColor,
    required this.respondiendo,
    required this.puedeResponder,
    required this.onAceptar,
    required this.onRechazar,
    required this.onDetalle,
  });

  String _texto(dynamic value) {
    if (value == null) return 'No disponible';
    final texto = value.toString().trim();
    return texto.isEmpty ? 'No disponible' : texto;
  }

  @override
  Widget build(BuildContext context) {
    final estado = _texto(oferta['estado_oferta']).toUpperCase();
    final precio = _texto(oferta['precio_estimado']);
    final tiempo = _texto(oferta['tiempo_estimado_minutos']);
    final taller = _texto(oferta['nombre_taller']);
    final fecha = _texto(oferta['fecha_oferta']);

    final nroEmergencia = _texto(emergencia['nro_emergencia']);
    final tipoEmergencia = _texto(emergencia['tipo_emergencia']).toUpperCase();
    final vehiculo =
        '${_texto(emergencia['vehiculo_placa']).toUpperCase()} · ${_texto(emergencia['vehiculo_marca'])}';

    return Container(
      width: double.infinity,
      decoration: BoxDecoration(
        color: AppTheme.surface,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(
          color: estadoColor.withOpacity(puedeResponder ? 0.35 : 0.18),
          width: puedeResponder ? 1.3 : 1,
        ),
      ),
      child: Padding(
        padding: const EdgeInsets.all(14),
        child: Column(
          children: [
            Row(
              children: [
                Container(
                  width: 46,
                  height: 46,
                  decoration: BoxDecoration(
                    color: estadoColor.withOpacity(0.08),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Icon(
                    Icons.request_quote_outlined,
                    color: estadoColor,
                    size: 25,
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        taller.toUpperCase(),
                        style: const TextStyle(
                          fontSize: 14,
                          fontWeight: FontWeight.w900,
                          color: AppTheme.textPrimary,
                          height: 1.25,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        'Emergencia N° $nroEmergencia · $tipoEmergencia',
                        style: const TextStyle(
                          fontSize: 11,
                          color: AppTheme.textSecondary,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ],
                  ),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 9,
                    vertical: 5,
                  ),
                  decoration: BoxDecoration(
                    color: estadoColor.withOpacity(0.09),
                    borderRadius: BorderRadius.circular(20),
                    border: Border.all(
                      color: estadoColor.withOpacity(0.3),
                    ),
                  ),
                  child: Text(
                    estado,
                    style: TextStyle(
                      fontSize: 10,
                      fontWeight: FontWeight.w900,
                      color: estadoColor,
                      letterSpacing: 0.5,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 14),
            const Divider(height: 1),
            const SizedBox(height: 14),
            _InfoRow(
              icon: Icons.payments_outlined,
              label: 'Precio',
              value: 'Bs. $precio',
            ),
            const SizedBox(height: 8),
            _InfoRow(
              icon: Icons.timer_outlined,
              label: 'Tiempo',
              value: '$tiempo minutos',
            ),
            const SizedBox(height: 8),
            _InfoRow(
              icon: Icons.directions_car_rounded,
              label: 'Vehículo',
              value: vehiculo,
            ),
            const SizedBox(height: 8),
            _InfoRow(
              icon: Icons.access_time_rounded,
              label: 'Fecha',
              value: fecha,
            ),
            const SizedBox(height: 14),
            Row(
              children: [
                Expanded(
                  child: OutlinedButton.icon(
                    onPressed: onDetalle,
                    icon: const Icon(Icons.visibility_outlined, size: 16),
                    label: const Text('DETALLE'),
                    style: OutlinedButton.styleFrom(
                      minimumSize: const Size(0, 42),
                      textStyle: const TextStyle(
                        fontSize: 11,
                        fontWeight: FontWeight.w800,
                      ),
                    ),
                  ),
                ),
                if (puedeResponder) ...[
                  const SizedBox(width: 10),
                  Expanded(
                    child: OutlinedButton.icon(
                      onPressed: respondiendo ? null : onRechazar,
                      icon: const Icon(Icons.close_rounded, size: 16),
                      label: const Text('RECHAZAR'),
                      style: OutlinedButton.styleFrom(
                        foregroundColor: AppTheme.error,
                        side: const BorderSide(
                          color: AppTheme.error,
                          width: 1.2,
                        ),
                        minimumSize: const Size(0, 42),
                        textStyle: const TextStyle(
                          fontSize: 11,
                          fontWeight: FontWeight.w800,
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(width: 10),
                  Expanded(
                    child: ElevatedButton.icon(
                      onPressed: respondiendo ? null : onAceptar,
                      icon: const Icon(Icons.check_rounded, size: 16),
                      label: const Text('ACEPTAR'),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: AppTheme.success,
                        foregroundColor: Colors.white,
                        minimumSize: const Size(0, 42),
                        textStyle: const TextStyle(
                          fontSize: 11,
                          fontWeight: FontWeight.w800,
                        ),
                      ),
                    ),
                  ),
                ],
              ],
            ),
          ],
        ),
      ),
    );
  }
}

class _InfoRow extends StatelessWidget {
  final IconData icon;
  final String label;
  final String value;

  const _InfoRow({
    required this.icon,
    required this.label,
    required this.value,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Icon(
          icon,
          size: 15,
          color: AppTheme.textSecondary,
        ),
        const SizedBox(width: 8),
        SizedBox(
          width: 78,
          child: Text(
            label,
            style: const TextStyle(
              fontSize: 11,
              color: AppTheme.textSecondary,
            ),
          ),
        ),
        Expanded(
          child: Text(
            value,
            style: const TextStyle(
              fontSize: 12,
              fontWeight: FontWeight.w600,
              color: AppTheme.textPrimary,
              height: 1.35,
            ),
          ),
        ),
      ],
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
              'No se pudieron cargar las cotizaciones',
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
                Icons.request_quote_outlined,
                color: AppTheme.primary,
                size: 32,
              ),
            ),
          ),
          const SizedBox(height: 18),
          const Text(
            'Sin cotizaciones',
            textAlign: TextAlign.center,
            style: TextStyle(
              fontSize: 17,
              fontWeight: FontWeight.w900,
              color: AppTheme.textPrimary,
            ),
          ),
          const SizedBox(height: 8),
          const Text(
            'Cuando un taller envíe una cotización para tus emergencias, aparecerá aquí.',
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