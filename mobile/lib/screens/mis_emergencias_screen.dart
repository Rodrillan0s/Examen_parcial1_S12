import 'package:flutter/material.dart';
import '../services/emergencia_service.dart';
import '../theme/app_theme.dart';
import 'detalle_emergencia_screen.dart';


class MisEmergenciasScreen extends StatefulWidget {
  const MisEmergenciasScreen({super.key});

  @override
  State<MisEmergenciasScreen> createState() => _MisEmergenciasScreenState();
}

class _MisEmergenciasScreenState extends State<MisEmergenciasScreen> {
  late Future<List<Map<String, dynamic>>> _futureEmergencias;
  final Set<int> _cancelandoEmergencias = {};

  @override
  void initState() {
    super.initState();
    _futureEmergencias = EmergenciaService().listarMisEmergencias();
  }

  Future<void> _refrescar() async {
    final nuevaCarga = EmergenciaService().listarMisEmergencias();

    setState(() {
      _futureEmergencias = nuevaCarga;
    });

    await nuevaCarga;
  }

  int? _int(dynamic valor) {
    if (valor == null) return null;
    return int.tryParse(valor.toString());
  }

  bool _puedeCancelar(String estado) {
    final e = estado.toUpperCase().trim();

    return e != 'CANCELADA' &&
        e != 'FINALIZADA' &&
        e != 'COMPLETADA' &&
        e != 'RESUELTO';
  }

  Future<void> _confirmarCancelarEmergencia({
    required int nroEmergencia,
  }) async {
    final confirmar = await showDialog<bool>(
      context: context,
      builder: (context) {
        return AlertDialog(
          title: const Text('Cancelar emergencia'),
          content: Text(
            '¿Quieres cancelar la emergencia N° $nroEmergencia?',
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context, false),
              child: const Text('NO'),
            ),
            ElevatedButton(
              style: ElevatedButton.styleFrom(
                backgroundColor: AppTheme.error,
                foregroundColor: Colors.white,
              ),
              onPressed: () => Navigator.pop(context, true),
              child: const Text('SÍ, CANCELAR'),
            ),
          ],
        );
      },
    );

    if (confirmar != true) return;

    setState(() {
      _cancelandoEmergencias.add(nroEmergencia);
    });

    try {
      await EmergenciaService().cancelarEmergencia(
        nroEmergencia: nroEmergencia,
      );

      if (!mounted) return;

      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Emergencia cancelada correctamente.'),
          backgroundColor: AppTheme.success,
        ),
      );

      await _refrescar();
    } catch (e) {
      if (!mounted) return;

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            e.toString().replaceAll('Exception: ', ''),
          ),
          backgroundColor: AppTheme.error,
        ),
      );
    } finally {
      if (!mounted) return;

      setState(() {
        _cancelandoEmergencias.remove(nroEmergencia);
      });
    }
  }

  Color _colorEstado(String estado) {
    final e = estado.toUpperCase();

    if (e == 'PENDIENTE') return AppTheme.primary;
    if (e == 'ASIGNADA') return AppTheme.accent;
    if (e == 'EN_PROCESO' || e == 'EN PROCESO') return AppTheme.accentLight;
    if (e == 'FINALIZADA' || e == 'COMPLETADA') return AppTheme.success;
    if (e == 'CANCELADA') return AppTheme.error;

    return AppTheme.textSecondary;
  }

  IconData _iconoTipo(String tipo) {
    final t = tipo.toLowerCase();

    if (t.contains('bateria')) return Icons.battery_alert_rounded;
    if (t.contains('neumatico')) return Icons.tire_repair_rounded;
    if (t.contains('combustible')) return Icons.local_gas_station_outlined;
    if (t.contains('motor')) return Icons.settings_outlined;
    if (t.contains('accidente')) return Icons.car_crash_outlined;

    return Icons.help_outline_rounded;
  }

  String _texto(dynamic valor) {
    if (valor == null) return 'No asignado';
    final texto = valor.toString().trim();
    return texto.isEmpty ? 'No asignado' : texto;
  }

  String _fecha(String? fecha) {
    if (fecha == null || fecha.trim().isEmpty) return 'Sin fecha';
    return fecha;
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.background,
      appBar: AppBar(
        title: const Text('MIS EMERGENCIAS'),
        backgroundColor: AppTheme.primary,
        foregroundColor: Colors.white,
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios_new_rounded, size: 18),
          onPressed: () => Navigator.pop(context),
        ),
      ),
      body: FutureBuilder<List<Map<String, dynamic>>>(
        future: _futureEmergencias,
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

          final emergencias = snapshot.data ?? [];

          if (emergencias.isEmpty) {
            return _EmptyState(onRefrescar: _refrescar);
          }

          return RefreshIndicator(
            onRefresh: _refrescar,
            color: AppTheme.primary,
            child: ListView.separated(
              padding: const EdgeInsets.all(20),
              itemCount: emergencias.length,
              separatorBuilder: (_, __) => const SizedBox(height: 12),
              itemBuilder: (context, index) {
                final emergencia = emergencias[index];
                final nroEmergenciaInt = _int(emergencia['nro_emergencia']);
                final estadoEmergencia = _texto(emergencia['estado']);

                return _EmergenciaCard(
                  nroEmergencia: _texto(emergencia['nro_emergencia']),
                  tipoEmergencia: _texto(emergencia['tipo_emergencia']),
                  estado: _texto(emergencia['estado']),
                  prioridad: _texto(emergencia['prioridad']),
                  fechaInicio: _fecha(emergencia['fecha_inicio']?.toString()),
                  fechaFin: emergencia['fecha_fin']?.toString(),
                  latitud: emergencia['latitud'],
                  longitud: emergencia['longitud'],
                  nroTaller: emergencia['nro_taller'],
                  colorEstado: _colorEstado(_texto(emergencia['estado'])),
                  iconoTipo: _iconoTipo(_texto(emergencia['tipo_emergencia'])),
                  vehiculoPlaca: emergencia['vehiculo_placa']?.toString(),
                  vehiculoMarca: emergencia['vehiculo_marca']?.toString(),
                  vehiculoAnio: emergencia['vehiculo_año'],
                  puedeCancelar: nroEmergenciaInt != null && _puedeCancelar(estadoEmergencia),
                  cancelando: nroEmergenciaInt != null &&
                      _cancelandoEmergencias.contains(nroEmergenciaInt),
                  onCancelar: nroEmergenciaInt == null
                      ? null
                      : () {
                          _confirmarCancelarEmergencia(
                            nroEmergencia: nroEmergenciaInt,
                          );
                        },
                  onTap: () async {
                    final refrescar = await Navigator.push(
                      context,
                      MaterialPageRoute(
                        builder: (_) => DetalleEmergenciaScreen(
                          emergencia: emergencia,
                        ),
                      ),
                    );

                    if (refrescar == true && mounted) {
                      _refrescar();
                    }
                  },
                );
              },
            ),
          );
        },
      ),
    );
  }
}

class _EmergenciaCard extends StatelessWidget {
  final String nroEmergencia;
  final String tipoEmergencia;
  final String estado;
  final String prioridad;
  final String fechaInicio;
  final String? fechaFin;
  final dynamic latitud;
  final dynamic longitud;
  final dynamic nroTaller;
  final Color colorEstado;
  final IconData iconoTipo;
  final VoidCallback onTap;
  final String? vehiculoPlaca;
  final String? vehiculoMarca;
  final dynamic vehiculoAnio;

  final bool puedeCancelar;
  final bool cancelando;
  final VoidCallback? onCancelar;

  const _EmergenciaCard({
    required this.nroEmergencia,
    required this.tipoEmergencia,
    required this.estado,
    required this.prioridad,
    required this.fechaInicio,
    required this.fechaFin,
    required this.latitud,
    required this.longitud,
    required this.nroTaller,
    required this.colorEstado,
    required this.iconoTipo,
    required this.onTap,
    this.vehiculoPlaca,
    this.vehiculoMarca,
    this.vehiculoAnio,
    required this.puedeCancelar,
    required this.cancelando,
    required this.onCancelar,
  });

  String _coordenadas() {
    if (latitud == null || longitud == null) return 'Ubicación no disponible';
    return '${latitud.toString()}, ${longitud.toString()}';
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: AppTheme.surface,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: AppTheme.border),
      ),
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          borderRadius: BorderRadius.circular(8),
          onTap: onTap,
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Container(
                      width: 42,
                      height: 42,
                      decoration: BoxDecoration(
                        color: AppTheme.primary.withOpacity(0.08),
                        borderRadius: BorderRadius.circular(6),
                      ),
                      child: Icon(
                        iconoTipo,
                        color: AppTheme.primary,
                        size: 22,
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            'EMERGENCIA N° $nroEmergencia',
                            style: const TextStyle(
                              fontSize: 11,
                              fontWeight: FontWeight.w800,
                              color: AppTheme.textSecondary,
                              letterSpacing: 1,
                            ),
                          ),
                          const SizedBox(height: 3),
                          Text(
                            tipoEmergencia.toUpperCase(),
                            style: const TextStyle(
                              fontSize: 15,
                              fontWeight: FontWeight.w800,
                              color: AppTheme.textPrimary,
                            ),
                          ),
                          const SizedBox(height: 8),
                            _InfoRow(
                              icon: Icons.directions_car_rounded,
                              label: 'Vehículo',
                              value: vehiculoPlaca == null || vehiculoPlaca!.trim().isEmpty
                                  ? 'No registrado'
                                  : '${vehiculoPlaca!.toUpperCase()} · ${vehiculoMarca ?? ''} · ${vehiculoAnio ?? ''}',
                            ),
                        ],
                      ),
                    ),
                    _EstadoBadge(
                      texto: estado,
                      color: colorEstado,
                    ),
                  ],
                ),
                const SizedBox(height: 14),
                const Divider(height: 1),
                const SizedBox(height: 14),
                _InfoRow(
                  icon: Icons.priority_high_rounded,
                  label: 'Prioridad',
                  value: prioridad.toUpperCase(),
                ),
                const SizedBox(height: 8),
                _InfoRow(
                  icon: Icons.calendar_today_outlined,
                  label: 'Fecha inicio',
                  value: fechaInicio,
                ),
                const SizedBox(height: 8),
                _InfoRow(
                  icon: Icons.location_on_outlined,
                  label: 'Ubicación',
                  value: _coordenadas(),
                ),
                const SizedBox(height: 8),
                _InfoRow(
                  icon: Icons.build_outlined,
                  label: 'Taller asignado',
                  value: nroTaller == null ? 'Pendiente de asignación' : 'Taller N° $nroTaller',
                ),
                if (fechaFin != null && fechaFin!.trim().isNotEmpty) ...[
                  const SizedBox(height: 8),
                  _InfoRow(
                    icon: Icons.check_circle_outline_rounded,
                    label: 'Fecha fin',
                    value: fechaFin!,
                  ),
                ],
                if (puedeCancelar) ...[
                  const SizedBox(height: 14),
                  SizedBox(
                    width: double.infinity,
                    child: OutlinedButton.icon(
                      onPressed: cancelando ? null : onCancelar,
                      style: OutlinedButton.styleFrom(
                        foregroundColor: AppTheme.error,
                        side: BorderSide(
                          color: AppTheme.error.withOpacity(0.45),
                        ),
                        padding: const EdgeInsets.symmetric(
                          horizontal: 12,
                          vertical: 11,
                        ),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(8),
                        ),
                      ),
                      icon: cancelando
                          ? const SizedBox(
                              width: 16,
                              height: 16,
                              child: CircularProgressIndicator(
                                strokeWidth: 2,
                                color: AppTheme.error,
                              ),
                            )
                          : const Icon(
                              Icons.cancel_outlined,
                              size: 17,
                            ),
                      label: Text(
                        cancelando ? 'CANCELANDO...' : 'CANCELAR EMERGENCIA',
                        style: const TextStyle(
                          fontSize: 11,
                          fontWeight: FontWeight.w900,
                          letterSpacing: 0.5,
                        ),
                      ),
                    ),
                  ),
                ],
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class _EstadoBadge extends StatelessWidget {
  final String texto;
  final Color color;

  const _EstadoBadge({
    required this.texto,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(
        horizontal: 8,
        vertical: 4,
      ),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: color.withOpacity(0.35)),
      ),
      child: Text(
        texto.toUpperCase(),
        style: TextStyle(
          fontSize: 9,
          fontWeight: FontWeight.w800,
          color: color,
          letterSpacing: 0.6,
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
          width: 92,
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
              'No se pudieron cargar tus emergencias',
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
      onRefresh: onRefrescar,
      color: AppTheme.primary,
      child: ListView(
        padding: const EdgeInsets.all(28),
        children: [
          const SizedBox(height: 110),
          Container(
            width: 58,
            height: 58,
            decoration: BoxDecoration(
              color: AppTheme.primary.withOpacity(0.08),
              shape: BoxShape.circle,
            ),
            child: const Icon(
              Icons.history_rounded,
              color: AppTheme.primary,
              size: 30,
            ),
          ),
          const SizedBox(height: 16),
          const Text(
            'Aún no tienes emergencias',
            textAlign: TextAlign.center,
            style: TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.w800,
              color: AppTheme.textPrimary,
            ),
          ),
          const SizedBox(height: 8),
          const Text(
            'Cuando solicites auxilio, tus emergencias aparecerán aquí.',
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