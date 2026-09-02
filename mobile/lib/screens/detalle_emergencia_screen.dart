import 'dart:convert';
import 'dart:io';
import 'dart:typed_data';

import 'package:audioplayers/audioplayers.dart';
import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:image_picker/image_picker.dart';
import 'package:latlong2/latlong.dart';
import 'package:path_provider/path_provider.dart';
import 'package:record/record.dart';

import '../services/emergencia_service.dart';
import '../theme/app_theme.dart';
import '../widgets/ev_widgets.dart';
import 'tracking_emergencia_screen.dart';
import '../services/oferta_service.dart';

class DetalleEmergenciaScreen extends StatefulWidget {
  final Map<String, dynamic> emergencia;

  const DetalleEmergenciaScreen({
    super.key,
    required this.emergencia,
  });

  @override
  State<DetalleEmergenciaScreen> createState() =>
      _DetalleEmergenciaScreenState();
}

class _DetalleEmergenciaScreenState extends State<DetalleEmergenciaScreen> {
  final ImagePicker _imagePicker = ImagePicker();
  final AudioRecorder _audioRecorder = AudioRecorder();

  late Future<List<Map<String, dynamic>>> _futureEvidencias;

  bool _agregando = false;
  bool _grabandoAudio = false;

  int get _nroEmergencia {
    return int.parse(widget.emergencia['nro_emergencia'].toString());
  }

  bool _puedeVerTracking(String estado) {
    final e = estado.toUpperCase().replaceAll('_', ' ');

    return e == 'ACEPTADO' ||
        e == 'ACEPTADA' ||
        e == 'EN CURSO' ||
        e == 'ASIGNADA' ||
        e == 'EN PROCESO';
  }
  late Future<List<Map<String, dynamic>>> _futureOfertas;

  bool _respondiendoOferta = false;
  String? _estadoLocal;

  @override
  void initState() {
    super.initState();

    _estadoLocal = widget.emergencia['estado']?.toString();

    _futureEvidencias = EmergenciaService().listarEvidenciasEmergencia(
      nroEmergencia: _nroEmergencia,
    );

    _futureOfertas = OfertaService().listarOfertasPorEmergencia(
      nroEmergencia: _nroEmergencia,
    );
  }

  @override
  void dispose() {
    _audioRecorder.dispose();
    super.dispose();
  }

  Future<void> _refrescarOfertas() async {
  final nuevaCarga = OfertaService().listarOfertasPorEmergencia(
    nroEmergencia: _nroEmergencia,
  );

  setState(() {
    _futureOfertas = nuevaCarga;
  });

  await nuevaCarga;
}

Future<void> _responderOferta({
    required Map<String, dynamic> oferta,
    required String estadoOferta,
  }) async {
    final idOferta = int.parse(oferta['id_oferta'].toString());

    final confirmar = await showDialog<bool>(
      context: context,
      builder: (ctx) {
        final acepta = estadoOferta == 'ACEPTADA';

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
      _respondiendoOferta = true;
    });

    try {
      await OfertaService().responderOferta(
        idOferta: idOferta,
        estadoOferta: estadoOferta,
      );

      if (!mounted) return;

      if (estadoOferta == 'ACEPTADA') {
        setState(() {
          _estadoLocal = 'ACEPTADO';
          widget.emergencia['estado'] = 'ACEPTADO';
          widget.emergencia['nro_taller'] = oferta['nro_taller'];
        });
      }

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            estadoOferta == 'ACEPTADA'
                ? 'Cotización aceptada correctamente.'
                : 'Cotización rechazada correctamente.',
          ),
          backgroundColor:
              estadoOferta == 'ACEPTADA' ? AppTheme.success : AppTheme.error,
        ),
      );

      await _refrescarOfertas();
    } catch (e) {
      if (!mounted) return;

      _mostrarError(
        e.toString().replaceAll('Exception: ', ''),
      );
    } finally {
      if (mounted) {
        setState(() {
          _respondiendoOferta = false;
        });
      }
    }
  }

  Future<void> _refrescarEvidencias() async {
    final nuevaCarga = EmergenciaService().listarEvidenciasEmergencia(
      nroEmergencia: _nroEmergencia,
    );

    setState(() {
      _futureEvidencias = nuevaCarga;
    });

    await nuevaCarga;
  }

  String _texto(dynamic valor) {
    if (valor == null) return 'No asignado';
    final texto = valor.toString().trim();
    return texto.isEmpty ? 'No asignado' : texto;
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

  Uint8List? _base64ToBytes(String? value) {
    if (value == null || value.trim().isEmpty) return null;

    try {
      var raw = value.trim();

      if (raw.contains(',')) {
        raw = raw.split(',').last;
      }

      return base64Decode(raw);
    } catch (_) {
      return null;
    }
  }

  Future<void> _agregarImagen(ImageSource source) async {
    try {
      final imagen = await _imagePicker.pickImage(
        source: source,
        imageQuality: 45,
        maxWidth: 1280,
      );

      if (imagen == null) return;

      final bytes = await File(imagen.path).readAsBytes();
      final base64String = base64Encode(bytes);

      await _agregarEvidencias([
        {
          'tipo_archivo': 'IMAGEN',
          'base64': base64String,
        }
      ]);
    } catch (_) {
      _mostrarError('No se pudo cargar la imagen.');
    }
  }

  Future<void> _iniciarGrabacionAudio() async {
    try {
      final permiso = await _audioRecorder.hasPermission();

      if (!permiso) {
        _mostrarError('Se necesita permiso de micrófono.');
        return;
      }

      final dir = await getTemporaryDirectory();
      final path =
          '${dir.path}/evidencia_audio_${DateTime.now().millisecondsSinceEpoch}.m4a';

      await _audioRecorder.start(
        const RecordConfig(
          encoder: AudioEncoder.aacLc,
          bitRate: 64000,
          sampleRate: 44100,
        ),
        path: path,
      );

      setState(() {
        _grabandoAudio = true;
      });
    } catch (_) {
      _mostrarError('No se pudo iniciar la grabación.');
    }
  }

  Future<void> _detenerGrabacionAudio() async {
    try {
      final path = await _audioRecorder.stop();

      setState(() {
        _grabandoAudio = false;
      });

      if (path == null) return;

      final bytes = await File(path).readAsBytes();
      final base64String = base64Encode(bytes);

      await _agregarEvidencias([
        {
          'tipo_archivo': 'AUDIO',
          'base64': base64String,
        }
      ]);
    } catch (_) {
      setState(() {
        _grabandoAudio = false;
      });

      _mostrarError('No se pudo guardar el audio.');
    }
  }

  Future<void> _agregarEvidencias(
    List<Map<String, dynamic>> evidencias,
  ) async {
    setState(() => _agregando = true);

    try {
      await EmergenciaService().agregarEvidencias(
        nroEmergencia: _nroEmergencia,
        evidencias: evidencias,
      );

      if (!mounted) return;

      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Evidencia agregada correctamente.'),
          backgroundColor: AppTheme.success,
        ),
      );

      await _refrescarEvidencias();
    } catch (e) {
      if (!mounted) return;
      _mostrarError(e.toString().replaceAll('Exception: ', ''));
    } finally {
      if (mounted) setState(() => _agregando = false);
    }
  }

  void _mostrarOpcionesEvidencia() {
    showModalBottomSheet(
      context: context,
      backgroundColor: AppTheme.surface,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(
          top: Radius.circular(14),
        ),
      ),
      builder: (_) {
        return SafeArea(
          child: Padding(
            padding: const EdgeInsets.fromLTRB(20, 12, 20, 20),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Container(
                  width: 38,
                  height: 4,
                  decoration: BoxDecoration(
                    color: AppTheme.border,
                    borderRadius: BorderRadius.circular(20),
                  ),
                ),
                const SizedBox(height: 18),
                const Row(
                  children: [
                    Icon(
                      Icons.attach_file_rounded,
                      color: AppTheme.primary,
                      size: 22,
                    ),
                    SizedBox(width: 10),
                    Expanded(
                      child: Text(
                        'Agregar evidencia',
                        style: TextStyle(
                          fontSize: 17,
                          fontWeight: FontWeight.w900,
                          color: AppTheme.textPrimary,
                        ),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 18),
                _EvidenceOptionButton(
                  icon: Icons.photo_camera_outlined,
                  title: 'Tomar foto',
                  subtitle: 'Abrir cámara del celular',
                  onTap: () {
                    Navigator.pop(context);
                    _agregarImagen(ImageSource.camera);
                  },
                ),
                const SizedBox(height: 10),
                _EvidenceOptionButton(
                  icon: Icons.image_outlined,
                  title: 'Elegir imagen',
                  subtitle: 'Seleccionar desde galería',
                  onTap: () {
                    Navigator.pop(context);
                    _agregarImagen(ImageSource.gallery);
                  },
                ),
                const SizedBox(height: 10),
                _EvidenceOptionButton(
                  icon: _grabandoAudio
                      ? Icons.stop_circle_outlined
                      : Icons.mic_none_outlined,
                  title: _grabandoAudio ? 'Detener audio' : 'Grabar audio',
                  subtitle: _grabandoAudio
                      ? 'Finalizar grabación actual'
                      : 'Registrar audio como evidencia',
                  danger: _grabandoAudio,
                  onTap: () {
                    Navigator.pop(context);
                    _grabandoAudio
                        ? _detenerGrabacionAudio()
                        : _iniciarGrabacionAudio();
                  },
                ),
              ],
            ),
          ),
        );
      },
    );
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
    final emergencia = widget.emergencia;

    final estado = _texto(_estadoLocal ?? emergencia['estado']);
    final latitud = emergencia['latitud'];
    final longitud = emergencia['longitud'];
    final puedeTracking = _puedeVerTracking(estado);

    return Scaffold(
      backgroundColor: AppTheme.background,
      appBar: AppBar(
        title: const Text('DETALLE EMERGENCIA'),
        backgroundColor: AppTheme.primary,
        foregroundColor: Colors.white,
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios_new_rounded, size: 18),
          onPressed: () => Navigator.pop(context, true),
        ),
      ),
      bottomNavigationBar: Container(
        color: AppTheme.surface,
        padding: EdgeInsets.only(
          left: 20,
          right: 20,
          top: 12,
          bottom: MediaQuery.of(context).padding.bottom + 12,
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            if (puedeTracking) ...[
              OutlinedButton.icon(
                onPressed: () {
                  Navigator.push(
                    context,
                    MaterialPageRoute(
                      builder: (_) => TrackingEmergenciaScreen(
                        emergencia: emergencia,
                      ),
                    ),
                  );
                },
                icon: const Icon(Icons.map_outlined, size: 18),
                label: const Text('VER TRACKING'),
                style: OutlinedButton.styleFrom(
                  minimumSize: const Size(double.infinity, 48),
                  textStyle: const TextStyle(
                    fontSize: 12,
                    fontWeight: FontWeight.w800,
                    letterSpacing: 0.8,
                  ),
                ),
              ),
              const SizedBox(height: 10),
            ],
            EvPrimaryButton(
              label: _grabandoAudio ? 'Detener Grabación' : 'Agregar Evidencia',
              loading: _agregando,
              onPressed: _grabandoAudio
                  ? _detenerGrabacionAudio
                  : _mostrarOpcionesEvidencia,
            ),
          ],
        ),
      ),
      body: RefreshIndicator(
        color: AppTheme.primary,
        onRefresh: _refrescarEvidencias,
        child: SingleChildScrollView(
          physics: const AlwaysScrollableScrollPhysics(),
          padding: const EdgeInsets.all(20),
          child: Column(
            children: [
              _HeaderDetalle(
                nroEmergencia: _texto(emergencia['nro_emergencia']),
                tipoEmergencia: _texto(emergencia['tipo_emergencia']),
                estado: estado,
                colorEstado: _colorEstado(estado),
              ),
              const SizedBox(height: 14),
              _DetalleCard(
                title: 'Vehículo',
                children: [
                  _InfoRow(
                    icon: Icons.directions_car_rounded,
                    label: 'Placa',
                    value: _texto(emergencia['vehiculo_placa']).toUpperCase(),
                  ),
                  const SizedBox(height: 10),
                  _InfoRow(
                    icon: Icons.car_repair_outlined,
                    label: 'Marca',
                    value: _texto(emergencia['vehiculo_marca']),
                  ),
                  const SizedBox(height: 10),
                  _InfoRow(
                    icon: Icons.calendar_today_outlined,
                    label: 'Año',
                    value: _texto(emergencia['vehiculo_año']),
                  ),
                ],
              ),
              const SizedBox(height: 14),
              _DetalleCard(
                title: 'Información general',
                children: [
                  _InfoRow(
                    icon: Icons.priority_high_rounded,
                    label: 'Prioridad',
                    value: _texto(emergencia['prioridad']).toUpperCase(),
                  ),
                  const SizedBox(height: 10),
                  _InfoRow(
                    icon: Icons.calendar_today_outlined,
                    label: 'Inicio',
                    value: _texto(emergencia['fecha_inicio']),
                  ),
                  const SizedBox(height: 10),
                  _InfoRow(
                    icon: Icons.check_circle_outline_rounded,
                    label: 'Fin',
                    value: _texto(emergencia['fecha_fin']),
                  ),
                  const SizedBox(height: 10),
                  _InfoRow(
                    icon: Icons.build_outlined,
                    label: 'Taller',
                    value: emergencia['nro_taller'] == null
                        ? 'Pendiente de asignación'
                        : 'Taller N° ${emergencia['nro_taller']}',
                  ),
                ],
              ),
              const SizedBox(height: 14),
              _DetalleCard(
                title: 'Ubicación',
                children: [
                  _InfoRow(
                    icon: Icons.location_on_outlined,
                    label: 'Coordenadas',
                    value: latitud == null || longitud == null
                        ? 'Ubicación no disponible'
                        : 'Lat: $latitud\nLng: $longitud',
                  ),
                  if (latitud != null && longitud != null) ...[
                    const SizedBox(height: 14),
                    _MapaDetalle(
                      latitud: double.parse(latitud.toString()),
                      longitud: double.parse(longitud.toString()),
                    ),
                  ],
                ],
              ),
              const SizedBox(height: 14),
                _DetalleCard(
                  title: 'Cotizaciones recibidas',
                  children: [
                    FutureBuilder<List<Map<String, dynamic>>>(
                      future: _futureOfertas,
                      builder: (context, snapshot) {
                        if (snapshot.connectionState == ConnectionState.waiting) {
                          return const Padding(
                            padding: EdgeInsets.all(12),
                            child: Center(
                              child: CircularProgressIndicator(
                                strokeWidth: 2.5,
                                color: AppTheme.primary,
                              ),
                            ),
                          );
                        }

                        if (snapshot.hasError) {
                          return _CotizacionesEmptyMessage(
                            icon: Icons.error_outline_rounded,
                            title: 'No se pudieron cargar las cotizaciones',
                            subtitle: snapshot.error.toString().replaceAll('Exception: ', ''),
                          );
                        }

                        final ofertas = snapshot.data ?? [];

                        if (ofertas.isEmpty) {
                          return const _CotizacionesEmptyMessage(
                            icon: Icons.request_quote_outlined,
                            title: 'Sin cotizaciones recibidas',
                            subtitle:
                                'Cuando un taller envíe una oferta, aparecerá en esta sección.',
                          );
                        }

                        return Column(
                          children: List.generate(ofertas.length, (index) {
                            final oferta = ofertas[index];

                            return Padding(
                              padding: EdgeInsets.only(
                                bottom: index == ofertas.length - 1 ? 0 : 12,
                              ),
                              child: _OfertaCard(
                                oferta: oferta,
                                respondiendo: _respondiendoOferta,
                                onAceptar: () => _responderOferta(
                                  oferta: oferta,
                                  estadoOferta: 'ACEPTADA',
                                ),
                                onRechazar: () => _responderOferta(
                                  oferta: oferta,
                                  estadoOferta: 'RECHAZADA',
                                ),
                              ),
                            );
                          }),
                        );
                      },
                    ),
                  ],
                ),
              const SizedBox(height: 14),
              _DetalleCard(
                title: 'Evidencias',
                children: [
                  FutureBuilder<List<Map<String, dynamic>>>(
                    future: _futureEvidencias,
                    builder: (context, snapshot) {
                      if (snapshot.connectionState == ConnectionState.waiting) {
                        return const Padding(
                          padding: EdgeInsets.all(12),
                          child: Center(
                            child: CircularProgressIndicator(
                              strokeWidth: 2.5,
                              color: AppTheme.primary,
                            ),
                          ),
                        );
                      }

                      if (snapshot.hasError) {
                        return _EvidenceEmptyMessage(
                          icon: Icons.error_outline_rounded,
                          title: 'No se pudieron cargar las evidencias',
                          subtitle: snapshot.error
                              .toString()
                              .replaceAll('Exception: ', ''),
                        );
                      }

                      final evidencias = snapshot.data ?? [];

                      if (evidencias.isEmpty) {
                        return const _EvidenceEmptyMessage(
                          icon: Icons.folder_open_outlined,
                          title: 'Sin evidencias registradas',
                          subtitle:
                              'Puedes agregar fotos o audios desde el botón inferior.',
                        );
                      }

                      return Column(
                        children: List.generate(evidencias.length, (index) {
                          final ev = evidencias[index];
                          final tipo = _texto(ev['tipo_archivo']).toUpperCase();
                          final bytes = _base64ToBytes(ev['base64']);

                          return Padding(
                            padding: EdgeInsets.only(
                              bottom: index == evidencias.length - 1 ? 0 : 12,
                            ),
                            child: _EvidenciaCard(
                              evidencia: ev,
                              tipo: tipo,
                              bytes: bytes,
                            ),
                          );
                        }),
                      );
                    },
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _EvidenceOptionButton extends StatelessWidget {
  final IconData icon;
  final String title;
  final String subtitle;
  final bool danger;
  final VoidCallback onTap;

  const _EvidenceOptionButton({
    required this.icon,
    required this.title,
    required this.subtitle,
    required this.onTap,
    this.danger = false,
  });

  @override
  Widget build(BuildContext context) {
    final color = danger ? AppTheme.error : AppTheme.primary;

    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(8),
      child: Container(
        width: double.infinity,
        padding: const EdgeInsets.all(14),
        decoration: BoxDecoration(
          color: color.withOpacity(0.06),
          borderRadius: BorderRadius.circular(8),
          border: Border.all(
            color: color.withOpacity(0.2),
          ),
        ),
        child: Row(
          children: [
            Icon(icon, color: color, size: 22),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    title.toUpperCase(),
                    style: TextStyle(
                      fontSize: 12,
                      fontWeight: FontWeight.w900,
                      color: color,
                      letterSpacing: 0.8,
                    ),
                  ),
                  const SizedBox(height: 3),
                  Text(
                    subtitle,
                    style: const TextStyle(
                      fontSize: 11,
                      color: AppTheme.textSecondary,
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _EvidenciaCard extends StatelessWidget {
  final Map<String, dynamic> evidencia;
  final String tipo;
  final Uint8List? bytes;

  const _EvidenciaCard({
    required this.evidencia,
    required this.tipo,
    required this.bytes,
  });

  @override
  Widget build(BuildContext context) {
    final fecha = evidencia['fecha_carga']?.toString();
    final transcripcion = evidencia['transcripcion_archivo']?.toString();
    final diagnostico = evidencia['diagnostico_archivo']?.toString();

    return Container(
      width: double.infinity,
      decoration: BoxDecoration(
        color: AppTheme.background,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: AppTheme.border),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (tipo == 'IMAGEN' && bytes != null)
            ClipRRect(
              borderRadius: const BorderRadius.vertical(
                top: Radius.circular(8),
              ),
              child: Image.memory(
                bytes!,
                width: double.infinity,
                height: 190,
                fit: BoxFit.cover,
              ),
            )
          else if (tipo == 'AUDIO' && bytes != null)
            Padding(
              padding: const EdgeInsets.all(12),
              child: _AudioEvidencePlayer(bytes: bytes!),
            )
          else
            const Padding(
              padding: EdgeInsets.all(12),
              child: Text(
                'No se pudo visualizar esta evidencia.',
                style: TextStyle(
                  fontSize: 12,
                  color: AppTheme.textSecondary,
                ),
              ),
            ),
          Padding(
            padding: const EdgeInsets.all(12),
            child: Column(
              children: [
                _InfoRow(
                  icon: tipo == 'AUDIO'
                      ? Icons.audiotrack_rounded
                      : Icons.image_outlined,
                  label: 'Tipo',
                  value: tipo,
                ),
                if (fecha != null && fecha.trim().isNotEmpty) ...[
                  const SizedBox(height: 8),
                  _InfoRow(
                    icon: Icons.access_time_rounded,
                    label: 'Fecha',
                    value: fecha,
                  ),
                ],
                if (transcripcion != null &&
                    transcripcion.trim().isNotEmpty &&
                    transcripcion != 'None') ...[
                  const SizedBox(height: 8),
                  _InfoRow(
                    icon: Icons.notes_outlined,
                    label: 'Transcripción',
                    value: transcripcion,
                  ),
                ],
                if (diagnostico != null &&
                    diagnostico.trim().isNotEmpty &&
                    diagnostico != 'None') ...[
                  const SizedBox(height: 8),
                  _InfoRow(
                    icon: Icons.psychology_outlined,
                    label: 'Diagnóstico',
                    value: diagnostico,
                  ),
                ],
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _AudioEvidencePlayer extends StatefulWidget {
  final Uint8List bytes;

  const _AudioEvidencePlayer({
    required this.bytes,
  });

  @override
  State<_AudioEvidencePlayer> createState() => _AudioEvidencePlayerState();
}

class _AudioEvidencePlayerState extends State<_AudioEvidencePlayer> {
  final AudioPlayer _player = AudioPlayer();
  bool _reproduciendo = false;

  @override
  void initState() {
    super.initState();

    _player.onPlayerComplete.listen((_) {
      if (!mounted) return;

      setState(() {
        _reproduciendo = false;
      });
    });
  }

  @override
  void dispose() {
    _player.dispose();
    super.dispose();
  }

  Future<void> _toggleAudio() async {
    if (_reproduciendo) {
      await _player.stop();

      if (!mounted) return;

      setState(() {
        _reproduciendo = false;
      });

      return;
    }

    await _player.play(BytesSource(widget.bytes));

    if (!mounted) return;

    setState(() {
      _reproduciendo = true;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: AppTheme.surface,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: AppTheme.border),
      ),
      child: Row(
        children: [
          Container(
            width: 42,
            height: 42,
            decoration: BoxDecoration(
              color: AppTheme.primary.withOpacity(0.08),
              shape: BoxShape.circle,
            ),
            child: Icon(
              _reproduciendo
                  ? Icons.stop_rounded
                  : Icons.play_arrow_rounded,
              color: AppTheme.primary,
              size: 26,
            ),
          ),
          const SizedBox(width: 12),
          const Expanded(
            child: Text(
              'Audio de evidencia',
              style: TextStyle(
                fontSize: 13,
                fontWeight: FontWeight.w800,
                color: AppTheme.textPrimary,
              ),
            ),
          ),
          TextButton(
            onPressed: _toggleAudio,
            child: Text(
              _reproduciendo ? 'DETENER' : 'REPRODUCIR',
              style: const TextStyle(
                fontSize: 11,
                fontWeight: FontWeight.w800,
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _EvidenceEmptyMessage extends StatelessWidget {
  final IconData icon;
  final String title;
  final String subtitle;

  const _EvidenceEmptyMessage({
    required this.icon,
    required this.title,
    required this.subtitle,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: AppTheme.background,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: AppTheme.border),
      ),
      child: Row(
        children: [
          Icon(
            icon,
            color: AppTheme.textSecondary,
            size: 24,
          ),
          const SizedBox(width: 10),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: const TextStyle(
                    fontSize: 13,
                    fontWeight: FontWeight.w800,
                    color: AppTheme.textPrimary,
                  ),
                ),
                const SizedBox(height: 3),
                Text(
                  subtitle,
                  style: const TextStyle(
                    fontSize: 11,
                    color: AppTheme.textSecondary,
                    height: 1.4,
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

class _HeaderDetalle extends StatelessWidget {
  final String nroEmergencia;
  final String tipoEmergencia;
  final String estado;
  final Color colorEstado;

  const _HeaderDetalle({
    required this.nroEmergencia,
    required this.tipoEmergencia,
    required this.estado,
    required this.colorEstado,
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
              borderRadius: BorderRadius.circular(6),
            ),
            child: const Icon(
              Icons.car_crash_outlined,
              color: Colors.white,
              size: 26,
            ),
          ),
          const SizedBox(width: 14),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'EMERGENCIA N° $nroEmergencia',
                  style: const TextStyle(
                    color: Color(0xFFBFCFFF),
                    fontSize: 11,
                    fontWeight: FontWeight.w700,
                    letterSpacing: 1,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  tipoEmergencia.toUpperCase(),
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 16,
                    fontWeight: FontWeight.w900,
                  ),
                ),
              ],
            ),
          ),
          Container(
            padding: const EdgeInsets.symmetric(
              horizontal: 8,
              vertical: 4,
            ),
            decoration: BoxDecoration(
              color: colorEstado.withOpacity(0.18),
              borderRadius: BorderRadius.circular(20),
              border: Border.all(
                color: Colors.white.withOpacity(0.2),
              ),
            ),
            child: Text(
              estado.toUpperCase(),
              style: const TextStyle(
                color: Colors.white,
                fontSize: 9,
                fontWeight: FontWeight.w800,
                letterSpacing: 0.6,
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _DetalleCard extends StatelessWidget {
  final String title;
  final List<Widget> children;

  const _DetalleCard({
    required this.title,
    required this.children,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppTheme.surface,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: AppTheme.border),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            title.toUpperCase(),
            style: const TextStyle(
              fontSize: 11,
              fontWeight: FontWeight.w800,
              color: AppTheme.textSecondary,
              letterSpacing: 1.1,
            ),
          ),
          const SizedBox(height: 14),
          ...children,
        ],
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
          size: 16,
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

class _MapaDetalle extends StatelessWidget {
  final double latitud;
  final double longitud;

  const _MapaDetalle({
    required this.latitud,
    required this.longitud,
  });

  @override
  Widget build(BuildContext context) {
    final punto = LatLng(latitud, longitud);

    return Container(
      width: double.infinity,
      height: 190,
      decoration: BoxDecoration(
        color: AppTheme.surface,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: AppTheme.border),
      ),
      clipBehavior: Clip.antiAlias,
      child: FlutterMap(
        options: MapOptions(
          initialCenter: punto,
          initialZoom: 16,
        ),
        children: [
          TileLayer(
            urlTemplate: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
            userAgentPackageName: 'com.example.emergencias_vehiculares',
          ),
          MarkerLayer(
            markers: [
              Marker(
                point: punto,
                width: 44,
                height: 44,
                child: const Icon(
                  Icons.location_on_rounded,
                  color: AppTheme.error,
                  size: 36,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}


class _OfertaCard extends StatelessWidget {
  final Map<String, dynamic> oferta;
  final bool respondiendo;
  final VoidCallback onAceptar;
  final VoidCallback onRechazar;

  const _OfertaCard({
    required this.oferta,
    required this.respondiendo,
    required this.onAceptar,
    required this.onRechazar,
  });

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

  @override
  Widget build(BuildContext context) {
    final estado = _texto(oferta['estado_oferta']).toUpperCase();
    final color = _colorEstado(estado);
    final puedeResponder = _puedeResponder(estado);

    final precio = _texto(oferta['precio_estimado']);
    final tiempo = _texto(oferta['tiempo_estimado_minutos']);
    final taller = _texto(oferta['nombre_taller']);
    final fecha = _texto(oferta['fecha_oferta']);

    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: AppTheme.background,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(
          color: color.withOpacity(puedeResponder ? 0.35 : 0.18),
          width: puedeResponder ? 1.3 : 1,
        ),
      ),
      child: Column(
        children: [
          Row(
            children: [
              Container(
                width: 44,
                height: 44,
                decoration: BoxDecoration(
                  color: color.withOpacity(0.08),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Icon(
                  Icons.request_quote_outlined,
                  color: color,
                  size: 24,
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
                        fontSize: 13,
                        fontWeight: FontWeight.w900,
                        color: AppTheme.textPrimary,
                        height: 1.25,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      'Oferta N° ${_texto(oferta['id_oferta'])}',
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
                  color: color.withOpacity(0.09),
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(
                    color: color.withOpacity(0.3),
                  ),
                ),
                child: Text(
                  estado,
                  style: TextStyle(
                    fontSize: 10,
                    fontWeight: FontWeight.w900,
                    color: color,
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
            icon: Icons.access_time_rounded,
            label: 'Fecha',
            value: fecha,
          ),
          if (puedeResponder) ...[
            const SizedBox(height: 14),
            Row(
              children: [
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
            ),
          ],
        ],
      ),
    );
  }
}

class _CotizacionesEmptyMessage extends StatelessWidget {
  final IconData icon;
  final String title;
  final String subtitle;

  const _CotizacionesEmptyMessage({
    required this.icon,
    required this.title,
    required this.subtitle,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: AppTheme.background,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: AppTheme.border),
      ),
      child: Row(
        children: [
          Icon(
            icon,
            color: AppTheme.textSecondary,
            size: 24,
          ),
          const SizedBox(width: 10),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: const TextStyle(
                    fontSize: 13,
                    fontWeight: FontWeight.w800,
                    color: AppTheme.textPrimary,
                  ),
                ),
                const SizedBox(height: 3),
                Text(
                  subtitle,
                  style: const TextStyle(
                    fontSize: 11,
                    color: AppTheme.textSecondary,
                    height: 1.4,
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