//solicitar_emergencia_screen.dart
import 'package:flutter/material.dart';
import 'package:geolocator/geolocator.dart';
import '../theme/app_theme.dart';
import '../widgets/ev_widgets.dart';
import '../services/emergencia_service.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';
import '../services/vehiculo_service.dart';
import 'vehiculos_screen.dart';
import 'package:connectivity_plus/connectivity_plus.dart';
import '../services/pending_emergencia_service.dart';
import 'dart:convert';
import 'dart:io';

import 'package:image_picker/image_picker.dart';
import 'package:record/record.dart';
import 'package:path_provider/path_provider.dart';

// Tipos de emergencia disponibles
const _tiposEmergencia = [
  _TipoEmergencia(
    valor: 'bateria',
    label: 'Batería descargada',
    icon: Icons.battery_alert_rounded,
  ),
  _TipoEmergencia(
    valor: 'neumatico',
    label: 'Neumático pinchado',
    icon: Icons.tire_repair_rounded,
  ),
  _TipoEmergencia(
    valor: 'combustible',
    label: 'Sin combustible',
    icon: Icons.local_gas_station_outlined,
  ),
  _TipoEmergencia(
    valor: 'motor',
    label: 'Falla de motor',
    icon: Icons.settings_outlined,
  ),
  _TipoEmergencia(
    valor: 'accidente',
    label: 'Accidente vehicular',
    icon: Icons.car_crash_outlined,
  ),
  _TipoEmergencia(
    valor: 'otro',
    label: 'Otro problema',
    icon: Icons.help_outline_rounded,
  ),
];

class SolicitarEmergenciaScreen extends StatefulWidget {
  const SolicitarEmergenciaScreen({super.key});

  @override
  State<SolicitarEmergenciaScreen> createState() =>
      _SolicitarEmergenciaScreenState();
}

class _SolicitarEmergenciaScreenState
    extends State<SolicitarEmergenciaScreen> {
  final _formKey = GlobalKey<FormState>();
  

  String? _tipoSeleccionado;
  Position? _posicion;
  bool _cargandoUbicacion = false;
  bool _enviando = false;
  String? _errorUbicacion;
  double? _latitudSeleccionada;
  double? _longitudSeleccionada;

  // Paso actual del stepper: 0 = vehiculo, 1 = tipo, 2 = ubicacion, 3 = detallees
  int _pasoActual = 0;

  List<Map<String, dynamic>> _vehiculos = [];
  Map<String, dynamic>? _vehiculoSeleccionado;
  bool _cargandoVehiculos = false;
  String? _errorVehiculos;

  final ImagePicker _imagePicker = ImagePicker();
  final AudioRecorder _audioRecorder = AudioRecorder();

  List<Map<String, dynamic>> _evidencias = [];

  bool _grabandoAudio = false;

  @override
  void initState() {
    super.initState();
    _cargarVehiculos();
    _obtenerUbicacion();
  }

  @override
  void dispose() {
    _audioRecorder.dispose();
    super.dispose();
  }

  Future<bool> _hayConexion() async {
    final result = await Connectivity().checkConnectivity();

    if (result is List<ConnectivityResult>) {
      return !result.contains(ConnectivityResult.none);
    }

    return result != ConnectivityResult.none;
  }

  Future<void> _agregarImagenDesdeCamara() async {
    try {
      final imagen = await _imagePicker.pickImage(
        source: ImageSource.camera,
        imageQuality: 45,
        maxWidth: 1280,
      );

      if (imagen == null) return;

      final bytes = await File(imagen.path).readAsBytes();
      final base64String = base64Encode(bytes);

      setState(() {
        _evidencias.add({
          'tipo_archivo': 'IMAGEN',
          'base64': base64String,
          'nombre': imagen.name,
        });
      });

      _mostrarInfo('Imagen agregada correctamente.');
    } catch (e) {
      _mostrarError('No se pudo cargar la imagen.');
    }
  }

  Future<void> _agregarImagenDesdeGaleria() async {
    try {
      final imagen = await _imagePicker.pickImage(
        source: ImageSource.gallery,
        imageQuality: 45,
        maxWidth: 1280,
      );

      if (imagen == null) return;

      final bytes = await File(imagen.path).readAsBytes();
      final base64String = base64Encode(bytes);

      setState(() {
        _evidencias.add({
          'tipo_archivo': 'IMAGEN',
          'base64': base64String,
          'nombre': imagen.name,
        });
      });

      _mostrarInfo('Imagen agregada correctamente.');
    } catch (e) {
      _mostrarError('No se pudo cargar la imagen.');
    }
  }

  Future<void> _iniciarGrabacionAudio() async {
    try {
      final tienePermiso = await _audioRecorder.hasPermission();

      if (!tienePermiso) {
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
    } catch (e) {
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

      setState(() {
        _evidencias.add({
          'tipo_archivo': 'AUDIO',
          'base64': base64String,
          'nombre': path.split('/').last,
        });
      });

      _mostrarInfo('Audio agregado correctamente.');
    } catch (e) {
      setState(() {
        _grabandoAudio = false;
      });

      _mostrarError('No se pudo guardar el audio.');
    }
  }

  void _eliminarEvidencia(int index) {
    setState(() {
      _evidencias.removeAt(index);
    });
  }

  void _mostrarInfo(String msg) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(msg),
        backgroundColor: AppTheme.success,
      ),
    );
  }

  List<Map<String, dynamic>> _evidenciasParaEnviar() {
    if (_evidencias.isEmpty) {
      return const [
        {
          'tipo_archivo': 'SIN_EVIDENCIA',
          'base64': '',
        }
      ];
    }

    return _evidencias
        .map((e) => {
              'tipo_archivo': e['tipo_archivo'],
              'base64': e['base64'],
            })
        .toList();
  }


  bool _esErrorDeConexion(String mensaje) {
    final m = mensaje.toLowerCase();

    return m.contains('conexión') ||
        m.contains('conexion') ||
        m.contains('tiempo de espera') ||
        m.contains('timeout') ||
        m.contains('connection') ||
        m.contains('socket');
  }

  Future<void> _guardarEmergenciaPendiente(Map<String, dynamic> payload) async {
    await PendingEmergenciaService().guardar(payload);

    if (!mounted) return;

    showDialog(
      context: context,
      builder: (_) => AlertDialog(
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(8),
        ),
        contentPadding: const EdgeInsets.all(26),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              width: 56,
              height: 56,
              decoration: BoxDecoration(
                color: AppTheme.primary.withOpacity(0.08),
                shape: BoxShape.circle,
              ),
              child: const Icon(
                Icons.cloud_off_rounded,
                color: AppTheme.primary,
                size: 30,
              ),
            ),
            const SizedBox(height: 16),
            const Text(
              'Emergencia guardada',
              textAlign: TextAlign.center,
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.w800,
                color: AppTheme.textPrimary,
              ),
            ),
            const SizedBox(height: 8),
            const Text(
              'No hay conexión estable. La solicitud se enviará automáticamente cuando vuelva internet.',
              textAlign: TextAlign.center,
              style: TextStyle(
                fontSize: 13,
                color: AppTheme.textSecondary,
                height: 1.5,
              ),
            ),
            const SizedBox(height: 22),
            ElevatedButton(
              onPressed: () {
                Navigator.pop(context);
                Navigator.pop(context);
              },
              child: const Text('VOLVER AL INICIO'),
            ),
          ],
        ),
      ),
    );
  }

  // ── GPS ────────────────────────────────────────────────────────────────
  Future<void> _obtenerUbicacion() async {
    setState(() {
      _cargandoUbicacion = true;
      _errorUbicacion = null;
    });

    try {
      bool serviceEnabled = await Geolocator.isLocationServiceEnabled();
      if (!serviceEnabled) {
        throw Exception('El GPS está desactivado. Activalo en ajustes.');
      }

      LocationPermission permission = await Geolocator.checkPermission();
      if (permission == LocationPermission.denied) {
        permission = await Geolocator.requestPermission();
        if (permission == LocationPermission.denied) {
          throw Exception('Se necesita permiso de ubicación para continuar.');
        }
      }
      if (permission == LocationPermission.deniedForever) {
        throw Exception(
            'Permiso denegado permanentemente. Habilitalo en Ajustes > Aplicaciones.');
      }

      final pos = await Geolocator.getCurrentPosition(
        desiredAccuracy: LocationAccuracy.high,
      );

      setState(() {
        _posicion = pos;
        _latitudSeleccionada = pos.latitude;
        _longitudSeleccionada = pos.longitude;
      });
    } catch (e) {
      setState(() => _errorUbicacion = e.toString().replaceAll('Exception: ', ''));
    } finally {
      setState(() => _cargandoUbicacion = false);
    }
  }

  //CARGAR VEHICULOS
  Future<void> _cargarVehiculos() async {
    setState(() {
      _cargandoVehiculos = true;
      _errorVehiculos = null;
    });

    try {
      final lista = await VehiculoService().listarMisVehiculos();

      if (!mounted) return;

      setState(() {
        _vehiculos = lista;
        _cargandoVehiculos = false;

        if (lista.length == 1) {
          _vehiculoSeleccionado = lista.first;
        }
      });
    } catch (e) {
      if (!mounted) return;

      setState(() {
        _errorVehiculos = e.toString().replaceAll('Exception: ', '');
        _cargandoVehiculos = false;
      });
    }
  }

  // ── Enviar ─────────────────────────────────────────────────────────────
  Future<void> _enviarEmergencia() async {
    if (_vehiculoSeleccionado == null) {
      _mostrarError('Seleccioná el vehículo de la emergencia.');
      return;
    }

    if (_tipoSeleccionado == null) {
      _mostrarError('Seleccioná el tipo de emergencia.');
      return;
    }

    if (_latitudSeleccionada == null || _longitudSeleccionada == null) {
      _mostrarError('No se pudo definir tu ubicación. Intentá de nuevo.');
      return;
    }

    final payload = {
      'tipo_emergencia': _tipoSeleccionado!,
      'latitud': _latitudSeleccionada!,
      'longitud': _longitudSeleccionada!,
      'nro_vehiculo': int.parse(
        _vehiculoSeleccionado!['nro_vehiculo'].toString(),
      ),
      'prioridad': 'MEDIA',
      'descripcion': '',
      'referencia': '',
      'evidencias': _evidenciasParaEnviar(),
    };

    setState(() => _enviando = true);

    try {
      final conectado = await _hayConexion();

      if (!conectado) {
        await _guardarEmergenciaPendiente(payload);
        return;
      }

      final resultado = await EmergenciaService().crearEmergenciaDesdePayload(
        payload,
      );

      if (!mounted) return;

      _mostrarExito(resultado['nro_emergencia']);
    } catch (e) {
      if (!mounted) return;

      final mensaje = e.toString().replaceAll('Exception: ', '');

      if (_esErrorDeConexion(mensaje)) {
        await _guardarEmergenciaPendiente(payload);
        return;
      }

      _mostrarError(mensaje);
    } finally {
      if (mounted) setState(() => _enviando = false);
    }
  }

  void _mostrarError(String msg) {
    ScaffoldMessenger.of(context).showSnackBar(SnackBar(
      content: Text(msg),
      backgroundColor: AppTheme.error,
    ));
  }

  void _mostrarExito(dynamic nroEmergencia) {
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (_) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
        contentPadding: const EdgeInsets.all(28),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              width: 56,
              height: 56,
              decoration: BoxDecoration(
                color: AppTheme.success.withOpacity(0.1),
                shape: BoxShape.circle,
              ),
              child: const Icon(Icons.check_circle_outline_rounded,
                  color: AppTheme.success, size: 32),
            ),
            const SizedBox(height: 16),
            const Text(
              '¡Emergencia enviada!',
              textAlign: TextAlign.center,
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.w800,
                color: AppTheme.textPrimary,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              'Solicitud N° $nroEmergencia registrada correctamente.',
              textAlign: TextAlign.center,
              style: const TextStyle(
                fontSize: 13,
                color: AppTheme.textSecondary,
                height: 1.5,
              ),
            ),
            const SizedBox(height: 24),
            ElevatedButton(
              onPressed: () {
                Navigator.pop(context); // cierra dialog
                Navigator.pop(context); // vuelve al home
              },
              child: const Text('VOLVER AL INICIO'),
            ),
          ],
        ),
      ),
    );
  }

  // ── Build ───────────────────────────────────────────────────────────────
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.background,
      appBar: AppBar(
        title: const Text('SOLICITAR AUXILIO'),
        backgroundColor: AppTheme.primary,
        foregroundColor: Colors.white,
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios_new_rounded, size: 18),
          onPressed: () => Navigator.pop(context),
        ),
      ),
      body: Column(
        children: [
          // ── Stepper indicador ──────────────────────────────────────
          _StepIndicator(pasoActual: _pasoActual),

          // ── Contenido por paso ─────────────────────────────────────
          Expanded(
            child: SingleChildScrollView(
              padding: const EdgeInsets.all(20),
              child: Form(
                key: _formKey,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // PASO 1 — ELEGIR VEHICULO
                    _PasoVehiculo(
                      activo: _pasoActual == 0,
                      completado: _pasoActual > 0,
                      vehiculos: _vehiculos,
                      vehiculoSeleccionado: _vehiculoSeleccionado,
                      cargando: _cargandoVehiculos,
                      error: _errorVehiculos,
                      onSeleccionar: (vehiculo) {
                        setState(() {
                          _vehiculoSeleccionado = vehiculo;
                          _pasoActual = 1;
                        });
                      },
                      onReintentar: _cargarVehiculos,
                      onAgregarVehiculo: () async {
                        await Navigator.push(
                          context,
                          MaterialPageRoute(
                            builder: (_) => const VehiculosScreen(),
                          ),
                        );

                        await _cargarVehiculos();
                      },
                    ),
                    const SizedBox(height: 16),
                    // PASO 1 — Tipo de emergencia
                    _PasoTipo(
                      activo: _pasoActual == 1,
                      completado: _pasoActual > 1,
                      tipoSeleccionado: _tipoSeleccionado,
                      onTipoSeleccionado: (tipo) {
                        setState(() {
                          _tipoSeleccionado = tipo;
                          _pasoActual = 2;
                        });
                      },
                    ),
                    // PASO 1 — Ubicación GPS
                    _PasoUbicacion(
                      activo: _pasoActual == 2,
                      completado: _pasoActual > 2,
                      posicion: _posicion,
                      cargando: _cargandoUbicacion,
                      error: _errorUbicacion,
                      onReintentar: _obtenerUbicacion,
                      latitudSeleccionada: _latitudSeleccionada,
                      longitudSeleccionada: _longitudSeleccionada,
                      onMoverPin: (punto) {
                        setState(() {
                          _latitudSeleccionada = punto.latitude;
                          _longitudSeleccionada = punto.longitude;
                        });
                      },
                      onConfirmar: _posicion != null
                          ? () => setState(() => _pasoActual = 3)
                          : null,
                    ),
                    // PASO 2 — Detalles
                    _PasoDetalles(
                      activo: _pasoActual == 3,
                      tipoSeleccionado: _tipoSeleccionado,
                      posicion: _posicion,
                      latitudSeleccionada: _latitudSeleccionada,
                      longitudSeleccionada: _longitudSeleccionada,
                      vehiculoSeleccionado: _vehiculoSeleccionado,
                      evidencias: _evidencias,
                      grabandoAudio: _grabandoAudio,
                      onCamara: _agregarImagenDesdeCamara,
                      onGaleria: _agregarImagenDesdeGaleria,
                      onAudio: _grabandoAudio ? _detenerGrabacionAudio : _iniciarGrabacionAudio,
                      onEliminarEvidencia: _eliminarEvidencia,
                    ),
                  ],
                ),
              ),
            ),
          ),

          // ── Botón enviar (solo en paso 2) ──────────────────────────
          if (_pasoActual == 3)
            _BarraEnviar(
              enviando: _enviando,
              onEnviar: _enviarEmergencia,
            ),
        ],
      ),
    );
  }
}

// ── Step Indicator ────────────────────────────────────────────────────────────
class _StepIndicator extends StatelessWidget {
  final int pasoActual;
  const _StepIndicator({required this.pasoActual});

  @override
  Widget build(BuildContext context) {
    const pasos = ['Vehículo', 'Tipo', 'Ubicación', 'Confirmar'];
    return Container(
      color: AppTheme.surface,
      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 14),
      child: Row(
        children: List.generate(pasos.length * 2 - 1, (i) {
          if (i.isOdd) {
            // línea conectora
            final completado = (i ~/ 2) < pasoActual;
            return Expanded(
              child: Container(
                height: 2,
                color: completado ? AppTheme.primary : AppTheme.border,
              ),
            );
          }
          final idx = i ~/ 2;
          final completado = idx < pasoActual;
          final activo = idx == pasoActual;
          return Column(
            children: [
              AnimatedContainer(
                duration: const Duration(milliseconds: 200),
                width: 28,
                height: 28,
                decoration: BoxDecoration(
                  color: completado || activo
                      ? AppTheme.primary
                      : AppTheme.background,
                  shape: BoxShape.circle,
                  border: Border.all(
                    color: completado || activo
                        ? AppTheme.primary
                        : AppTheme.border,
                    width: 1.5,
                  ),
                ),
                child: Center(
                  child: completado
                      ? const Icon(Icons.check_rounded,
                          color: Colors.white, size: 14)
                      : Text(
                          '${idx + 1}',
                          style: TextStyle(
                            fontSize: 11,
                            fontWeight: FontWeight.w700,
                            color: activo
                                ? Colors.white
                                : AppTheme.textSecondary,
                          ),
                        ),
                ),
              ),
              const SizedBox(height: 4),
              Text(
                pasos[idx],
                style: TextStyle(
                  fontSize: 10,
                  fontWeight:
                      activo ? FontWeight.w700 : FontWeight.w400,
                  color: activo
                      ? AppTheme.primary
                      : AppTheme.textSecondary,
                ),
              ),
            ],
          );
        }),
      ),
    );
  }
}

class _PasoVehiculo extends StatelessWidget {
  final bool activo;
  final bool completado;
  final List<Map<String, dynamic>> vehiculos;
  final Map<String, dynamic>? vehiculoSeleccionado;
  final bool cargando;
  final String? error;
  final void Function(Map<String, dynamic>) onSeleccionar;
  final VoidCallback onReintentar;
  final VoidCallback onAgregarVehiculo;

  const _PasoVehiculo({
    required this.activo,
    required this.completado,
    required this.vehiculos,
    required this.vehiculoSeleccionado,
    required this.cargando,
    required this.error,
    required this.onSeleccionar,
    required this.onReintentar,
    required this.onAgregarVehiculo,
  });

  String _texto(dynamic valor) {
    if (valor == null) return 'No registrado';
    final texto = valor.toString().trim();
    return texto.isEmpty ? 'No registrado' : texto;
  }

  @override
  Widget build(BuildContext context) {
    return _PasoCard(
      numero: '01',
      titulo: 'Vehículo',
      subtitulo: 'Seleccioná el vehículo con el problema',
      activo: activo,
      completado: completado,
      child: Column(
        children: [
          if (cargando)
            const _VehiculoLoadingBox()
          else if (error != null)
            _VehiculoErrorBox(
              mensaje: error!,
              onReintentar: onReintentar,
            )
          else if (vehiculos.isEmpty)
            _SinVehiculosBox(
              onAgregarVehiculo: onAgregarVehiculo,
            )
          else
            Column(
              children: vehiculos.map((vehiculo) {
                final seleccionado = vehiculoSeleccionado?['nro_vehiculo']
                        ?.toString() ==
                    vehiculo['nro_vehiculo']?.toString();

                return Padding(
                  padding: const EdgeInsets.only(bottom: 10),
                  child: InkWell(
                    onTap: () => onSeleccionar(vehiculo),
                    borderRadius: BorderRadius.circular(8),
                    child: AnimatedContainer(
                      duration: const Duration(milliseconds: 150),
                      width: double.infinity,
                      padding: const EdgeInsets.all(14),
                      decoration: BoxDecoration(
                        color: seleccionado
                            ? AppTheme.primary.withOpacity(0.08)
                            : AppTheme.background,
                        borderRadius: BorderRadius.circular(8),
                        border: Border.all(
                          color: seleccionado
                              ? AppTheme.primary
                              : AppTheme.border,
                          width: seleccionado ? 1.5 : 1,
                        ),
                      ),
                      child: Row(
                        children: [
                          Container(
                            width: 42,
                            height: 42,
                            decoration: BoxDecoration(
                              color: seleccionado
                                  ? AppTheme.primary
                                  : AppTheme.surface,
                              borderRadius: BorderRadius.circular(6),
                              border: Border.all(
                                color: seleccionado
                                    ? AppTheme.primary
                                    : AppTheme.border,
                              ),
                            ),
                            child: Icon(
                              Icons.directions_car_rounded,
                              color: seleccionado
                                  ? Colors.white
                                  : AppTheme.primary,
                              size: 22,
                            ),
                          ),
                          const SizedBox(width: 12),
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  _texto(vehiculo['placa']).toUpperCase(),
                                  style: const TextStyle(
                                    fontSize: 15,
                                    fontWeight: FontWeight.w900,
                                    color: AppTheme.textPrimary,
                                    letterSpacing: 0.6,
                                  ),
                                ),
                                const SizedBox(height: 3),
                                Text(
                                  '${_texto(vehiculo['marca_modelo'])} · ${_texto(vehiculo['anio'])}',
                                  style: const TextStyle(
                                    fontSize: 12,
                                    color: AppTheme.textSecondary,
                                    fontWeight: FontWeight.w600,
                                  ),
                                  overflow: TextOverflow.ellipsis,
                                ),
                              ],
                            ),
                          ),
                          Icon(
                            seleccionado
                                ? Icons.check_circle_rounded
                                : Icons.radio_button_unchecked_rounded,
                            color: seleccionado
                                ? AppTheme.primary
                                : AppTheme.textHint,
                            size: 22,
                          ),
                        ],
                      ),
                    ),
                  ),
                );
              }).toList(),
            ),
          if (!cargando && vehiculos.isNotEmpty) ...[
            const SizedBox(height: 4),
            OutlinedButton.icon(
              onPressed: onAgregarVehiculo,
              icon: const Icon(Icons.add_rounded, size: 16),
              label: const Text('Agregar otro vehículo'),
              style: OutlinedButton.styleFrom(
                minimumSize: const Size(double.infinity, 44),
                textStyle: const TextStyle(
                  fontSize: 12,
                  fontWeight: FontWeight.w700,
                ),
              ),
            ),
          ],
        ],
      ),
    );
  }
}

class _VehiculoLoadingBox extends StatelessWidget {
  const _VehiculoLoadingBox();

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: AppTheme.primary.withOpacity(0.06),
        borderRadius: BorderRadius.circular(6),
        border: Border.all(
          color: AppTheme.primary.withOpacity(0.2),
        ),
      ),
      child: const Row(
        children: [
          SizedBox(
            width: 16,
            height: 16,
            child: CircularProgressIndicator(
              strokeWidth: 2,
              color: AppTheme.primary,
            ),
          ),
          SizedBox(width: 10),
          Text(
            'Cargando vehículos...',
            style: TextStyle(
              fontSize: 13,
              color: AppTheme.textSecondary,
            ),
          ),
        ],
      ),
    );
  }
}

class _VehiculoErrorBox extends StatelessWidget {
  final String mensaje;
  final VoidCallback onReintentar;

  const _VehiculoErrorBox({
    required this.mensaje,
    required this.onReintentar,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: AppTheme.error.withOpacity(0.06),
        borderRadius: BorderRadius.circular(6),
        border: Border.all(
          color: AppTheme.error.withOpacity(0.25),
        ),
      ),
      child: Column(
        children: [
          Row(
            children: [
              const Icon(
                Icons.error_outline_rounded,
                size: 16,
                color: AppTheme.error,
              ),
              const SizedBox(width: 8),
              Expanded(
                child: Text(
                  mensaje,
                  style: const TextStyle(
                    fontSize: 12,
                    color: AppTheme.error,
                    height: 1.4,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          OutlinedButton.icon(
            onPressed: onReintentar,
            icon: const Icon(Icons.refresh_rounded, size: 16),
            label: const Text('Reintentar'),
            style: OutlinedButton.styleFrom(
              minimumSize: const Size(double.infinity, 42),
            ),
          ),
        ],
      ),
    );
  }
}

class _SinVehiculosBox extends StatelessWidget {
  final VoidCallback onAgregarVehiculo;

  const _SinVehiculosBox({
    required this.onAgregarVehiculo,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppTheme.primary.withOpacity(0.06),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(
          color: AppTheme.primary.withOpacity(0.18),
        ),
      ),
      child: Column(
        children: [
          Container(
            width: 46,
            height: 46,
            decoration: BoxDecoration(
              color: AppTheme.primary.withOpacity(0.08),
              shape: BoxShape.circle,
            ),
            child: const Icon(
              Icons.directions_car_rounded,
              color: AppTheme.primary,
              size: 24,
            ),
          ),
          const SizedBox(height: 12),
          const Text(
            'No tienes vehículos registrados',
            textAlign: TextAlign.center,
            style: TextStyle(
              fontSize: 14,
              fontWeight: FontWeight.w800,
              color: AppTheme.textPrimary,
            ),
          ),
          const SizedBox(height: 6),
          const Text(
            'Registra un vehículo antes de solicitar auxilio.',
            textAlign: TextAlign.center,
            style: TextStyle(
              fontSize: 12,
              color: AppTheme.textSecondary,
              height: 1.4,
            ),
          ),
          const SizedBox(height: 14),
          EvPrimaryButton(
            label: 'Registrar Vehículo',
            onPressed: onAgregarVehiculo,
          ),
        ],
      ),
    );
  }
}
// ── Paso 0 — Tipo ─────────────────────────────────────────────────────────────
class _PasoTipo extends StatelessWidget {
  final bool activo;
  final bool completado;
  final String? tipoSeleccionado;
  final void Function(String) onTipoSeleccionado;

  const _PasoTipo({
    required this.activo,
    required this.completado,
    required this.tipoSeleccionado,
    required this.onTipoSeleccionado,
  });

  @override
  Widget build(BuildContext context) {
    return _PasoCard(
      numero: '02',
      titulo: 'Tipo de emergencia',
      subtitulo: 'Seleccioná qué le pasó a tu vehículo',
      activo: activo,
      completado: completado,
      child: GridView.count(
        crossAxisCount: 2,
        shrinkWrap: true,
        physics: const NeverScrollableScrollPhysics(),
        crossAxisSpacing: 10,
        mainAxisSpacing: 10,
        childAspectRatio: 2.4,
        children: _tiposEmergencia.map((tipo) {
          final selected = tipoSeleccionado == tipo.valor;
          return InkWell(
            onTap: () => onTipoSeleccionado(tipo.valor),
            borderRadius: BorderRadius.circular(6),
            child: AnimatedContainer(
              duration: const Duration(milliseconds: 150),
              padding:
                  const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
              decoration: BoxDecoration(
                color: selected
                    ? AppTheme.primary
                    : AppTheme.background,
                borderRadius: BorderRadius.circular(6),
                border: Border.all(
                  color: selected ? AppTheme.primary : AppTheme.border,
                  width: selected ? 1.5 : 1,
                ),
              ),
              child: Row(
                children: [
                  Icon(
                    tipo.icon,
                    size: 16,
                    color: selected ? Colors.white : AppTheme.textSecondary,
                  ),
                  const SizedBox(width: 6),
                  Expanded(
                    child: Text(
                      tipo.label,
                      style: TextStyle(
                        fontSize: 11,
                        fontWeight: FontWeight.w600,
                        color: selected
                            ? Colors.white
                            : AppTheme.textPrimary,
                      ),
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                ],
              ),
            ),
          );
        }).toList(),
      ),
    );
  }
}

// ── Paso 1 — Ubicación ────────────────────────────────────────────────────────
class _PasoUbicacion extends StatelessWidget {
  final bool activo;
  final bool completado;
  final Position? posicion;
  final bool cargando;
  final String? error;
  final VoidCallback onReintentar;
  final VoidCallback? onConfirmar;

  final double? latitudSeleccionada;
  final double? longitudSeleccionada;
  final void Function(LatLng) onMoverPin;

  const _PasoUbicacion({
    required this.activo,
    required this.completado,
    required this.posicion,
    required this.cargando,
    required this.error,
    required this.onReintentar,
    required this.onConfirmar,
    required this.latitudSeleccionada,
    required this.longitudSeleccionada,
    required this.onMoverPin,
  });

  @override
  Widget build(BuildContext context) {
    return _PasoCard(
      numero: '03',
      titulo: 'Tu ubicación',
      subtitulo: 'Necesitamos saber dónde estás',
      activo: activo,
      completado: completado,
      child: Column(
        children: [
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(14),
            decoration: BoxDecoration(
              color: posicion != null
                  ? AppTheme.success.withOpacity(0.06)
                  : error != null
                      ? AppTheme.error.withOpacity(0.06)
                      : AppTheme.primary.withOpacity(0.06),
              borderRadius: BorderRadius.circular(6),
              border: Border.all(
                color: posicion != null
                    ? AppTheme.success.withOpacity(0.3)
                    : error != null
                        ? AppTheme.error.withOpacity(0.3)
                        : AppTheme.primary.withOpacity(0.2),
              ),
            ),
            child: cargando
                ? const Row(
                    children: [
                      SizedBox(
                        width: 16,
                        height: 16,
                        child: CircularProgressIndicator(
                          strokeWidth: 2,
                          color: AppTheme.primary,
                        ),
                      ),
                      SizedBox(width: 10),
                      Text(
                        'Obteniendo ubicación...',
                        style: TextStyle(
                          fontSize: 13,
                          color: AppTheme.textSecondary,
                        ),
                      ),
                    ],
                  )
                : posicion != null
                    ? Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Row(
                            children: [
                              Icon(
                                Icons.location_on_rounded,
                                color: AppTheme.success,
                                size: 16,
                              ),
                              SizedBox(width: 6),
                              Text(
                                'Ubicación obtenida',
                                style: TextStyle(
                                  fontSize: 13,
                                  fontWeight: FontWeight.w700,
                                  color: AppTheme.success,
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(height: 6),
                          Text(
                          'Lat: ${latitudSeleccionada!.toStringAsFixed(6)}\n'
                          'Lng: ${longitudSeleccionada!.toStringAsFixed(6)}',
                            style: const TextStyle(
                              fontSize: 11,
                              fontFamily: 'monospace',
                              color: AppTheme.textSecondary,
                              height: 1.6,
                            ),
                          ),
                          const SizedBox(height: 4),
                          Text(
                            'Precisión: ±${posicion!.accuracy.toStringAsFixed(0)}m',
                            style: const TextStyle(
                              fontSize: 11,
                              color: AppTheme.textSecondary,
                            ),
                          ),
                          const SizedBox(height: 12),
                          _MapaUbicacion(
                            latitud: latitudSeleccionada!,
                            longitud: longitudSeleccionada!,
                            onMoverPin: onMoverPin,
                          ),
                          const SizedBox(height: 8),
                            const Row(
                              children: [
                                Icon(
                                  Icons.touch_app_rounded,
                                  size: 13,
                                  color: AppTheme.textSecondary,
                                ),
                                SizedBox(width: 6),
                                Expanded(
                                  child: Text(
                                    'Toca el mapa para ajustar el punto exacto de la emergencia.',
                                    style: TextStyle(
                                      fontSize: 11,
                                      color: AppTheme.textSecondary,
                                      height: 1.4,
                                    ),
                                  ),
                                ),
                              ],
                            ),
                        ],
                      )
                    : Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: [
                              const Icon(
                                Icons.location_off_outlined,
                                color: AppTheme.error,
                                size: 16,
                              ),
                              const SizedBox(width: 6),
                              Expanded(
                                child: Text(
                                  error ?? 'No se pudo obtener la ubicación',
                                  style: const TextStyle(
                                    fontSize: 12,
                                    color: AppTheme.error,
                                  ),
                                ),
                              ),
                            ],
                          ),
                        ],
                      ),
          ),
          const SizedBox(height: 12),
          Row(
            children: [
              Expanded(
                child: OutlinedButton.icon(
                  onPressed: cargando ? null : onReintentar,
                  icon: const Icon(Icons.refresh_rounded, size: 16),
                  label: const Text('Reintentar'),
                  style: OutlinedButton.styleFrom(
                    minimumSize: const Size(0, 44),
                    textStyle: const TextStyle(
                      fontSize: 12,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ),
              ),
              if (posicion != null) ...[
                const SizedBox(width: 10),
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed: onConfirmar,
                    icon: const Icon(Icons.check_rounded, size: 16),
                    label: const Text('Confirmar'),
                    style: ElevatedButton.styleFrom(
                      minimumSize: const Size(0, 44),
                      textStyle: const TextStyle(
                        fontSize: 12,
                        fontWeight: FontWeight.w700,
                      ),
                    ),
                  ),
                ),
              ],
            ],
          ),
        ],
      ),
    );
  }
}

// ── Paso 2 — Detalles ─────────────────────────────────────────────────────────
class _PasoDetalles extends StatelessWidget {
  final bool activo;
  final String? tipoSeleccionado;
  final Position? posicion;
  final Map<String, dynamic>? vehiculoSeleccionado;
  final double? latitudSeleccionada;
  final double? longitudSeleccionada;
  final List<Map<String, dynamic>> evidencias;
  final bool grabandoAudio;
  final VoidCallback onCamara;
  final VoidCallback onGaleria;
  final VoidCallback onAudio;
  final void Function(int) onEliminarEvidencia;

  const _PasoDetalles({
    required this.activo,
    required this.tipoSeleccionado,
    required this.posicion,
    required this.vehiculoSeleccionado,
    required this.latitudSeleccionada,
    required this.longitudSeleccionada,
    required this.evidencias,
    required this.grabandoAudio,
    required this.onCamara,
    required this.onGaleria,
    required this.onAudio,
    required this.onEliminarEvidencia,
  });

  String _texto(dynamic valor) {
    if (valor == null) return 'No registrado';
    final texto = valor.toString().trim();
    return texto.isEmpty ? 'No registrado' : texto;
  }

  @override
  Widget build(BuildContext context) {
    return _PasoCard(
      numero: '04',
      titulo: 'Confirmar solicitud',
      subtitulo: 'Revisá los datos antes de enviar',
      activo: activo,
      completado: false,
      child: Column(
        children: [
          _ResumenItem(
            icon: Icons.directions_car_rounded,
            label: 'VEHÍCULO',
            value: vehiculoSeleccionado == null
                ? 'NO SELECCIONADO'
                : '${_texto(vehiculoSeleccionado!['placa']).toUpperCase()} · ${_texto(vehiculoSeleccionado!['marca_modelo'])} · ${_texto(vehiculoSeleccionado!['anio'])}',
          ),
          const SizedBox(height: 12),
          _ResumenItem(
            icon: Icons.car_crash_outlined,
            label: 'TIPO DE EMERGENCIA',
            value: tipoSeleccionado?.toUpperCase() ?? 'NO SELECCIONADO',
          ),
          const SizedBox(height: 12),
          _ResumenItem(
            icon: Icons.location_on_outlined,
            label: 'UBICACIÓN',
            value: latitudSeleccionada == null || longitudSeleccionada == null
                ? 'NO DISPONIBLE'
                : 'Lat: ${latitudSeleccionada!.toStringAsFixed(6)}\nLng: ${longitudSeleccionada!.toStringAsFixed(6)}',
          ),
          const SizedBox(height: 12),
          const _ResumenItem(
            icon: Icons.priority_high_rounded,
            label: 'PRIORIDAD',
            value: 'MEDIA',
          ),
          const SizedBox(height: 12),
          _EvidenciasBox(
            evidencias: evidencias,
            grabandoAudio: grabandoAudio,
            onCamara: onCamara,
            onGaleria: onGaleria,
            onAudio: onAudio,
            onEliminar: onEliminarEvidencia,
          ),
          const SizedBox(height: 14),
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: AppTheme.primary.withOpacity(0.06),
              borderRadius: BorderRadius.circular(6),
              border: Border.all(
                color: AppTheme.primary.withOpacity(0.18),
              ),
            ),
            child: const Row(
              children: [
                Icon(
                  Icons.info_outline_rounded,
                  size: 16,
                  color: AppTheme.primary,
                ),
                SizedBox(width: 8),
                Expanded(
                  child: Text(
                    'Se enviará tu emergencia con el vehículo seleccionado y tu ubicación actual.',
                    style: TextStyle(
                      fontSize: 12,
                      color: AppTheme.textSecondary,
                      height: 1.4,
                    ),
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

class _ResumenItem extends StatelessWidget {
  final IconData icon;
  final String label;
  final String value;

  const _ResumenItem({
    required this.icon,
    required this.label,
    required this.value,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: AppTheme.background,
        borderRadius: BorderRadius.circular(6),
        border: Border.all(color: AppTheme.border),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(
            icon,
            size: 18,
            color: AppTheme.primary,
          ),
          const SizedBox(width: 10),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  label,
                  style: const TextStyle(
                    fontSize: 10,
                    fontWeight: FontWeight.w700,
                    color: AppTheme.textSecondary,
                    letterSpacing: 1,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  value,
                  style: const TextStyle(
                    fontSize: 13,
                    fontWeight: FontWeight.w600,
                    color: AppTheme.textPrimary,
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

// ── Barra de envío inferior ───────────────────────────────────────────────────
class _BarraEnviar extends StatelessWidget {
  final bool enviando;
  final VoidCallback onEnviar;

  const _BarraEnviar({required this.enviando, required this.onEnviar});

  @override
  Widget build(BuildContext context) {
    return Container(
      color: AppTheme.surface,
      padding: EdgeInsets.only(
        left: 20,
        right: 20,
        top: 12,
        bottom: MediaQuery.of(context).padding.bottom + 12,
      ),
      child: EvPrimaryButton(
        label: 'Enviar Solicitud de Auxilio',
        loading: enviando,
        onPressed: onEnviar,
      ),
    );
  }
}

// ── Card contenedor de paso ───────────────────────────────────────────────────
class _PasoCard extends StatelessWidget {
  final String numero;
  final String titulo;
  final String subtitulo;
  final bool activo;
  final bool completado;
  final Widget child;

  const _PasoCard({
    required this.numero,
    required this.titulo,
    required this.subtitulo,
    required this.activo,
    required this.completado,
    required this.child,
  });

  @override
  Widget build(BuildContext context) {
    return AnimatedOpacity(
      duration: const Duration(milliseconds: 250),
      opacity: activo || completado ? 1.0 : 0.45,
      child: Container(
        width: double.infinity,
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: AppTheme.surface,
          borderRadius: BorderRadius.circular(8),
          border: Border.all(
            color: activo ? AppTheme.primary : AppTheme.border,
            width: activo ? 1.5 : 1,
          ),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header del paso
            Row(
              children: [
                Container(
                  padding:
                      const EdgeInsets.symmetric(horizontal: 7, vertical: 2),
                  decoration: BoxDecoration(
                    color: completado
                        ? AppTheme.success
                        : activo
                            ? AppTheme.primary
                            : AppTheme.border,
                    borderRadius: BorderRadius.circular(4),
                  ),
                  child: completado
                      ? const Icon(Icons.check_rounded,
                          color: Colors.white, size: 11)
                      : Text(
                          numero,
                          style: TextStyle(
                            fontSize: 10,
                            fontWeight: FontWeight.w800,
                            color: activo ? Colors.white : AppTheme.textSecondary,
                            letterSpacing: 0.5,
                          ),
                        ),
                ),
                const SizedBox(width: 10),
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      titulo,
                      style: const TextStyle(
                        fontSize: 13,
                        fontWeight: FontWeight.w700,
                        color: AppTheme.textPrimary,
                      ),
                    ),
                    Text(
                      subtitulo,
                      style: const TextStyle(
                        fontSize: 11,
                        color: AppTheme.textSecondary,
                      ),
                    ),
                  ],
                ),
              ],
            ),
            if (activo) ...[
              const SizedBox(height: 16),
              const Divider(height: 1),
              const SizedBox(height: 16),
              child,
            ],
          ],
        ),
      ),
    );
  }
}

class _MapaUbicacion extends StatelessWidget {
  final double latitud;
  final double longitud;
  final void Function(LatLng) onMoverPin;

  const _MapaUbicacion({
    required this.latitud,
    required this.longitud,
    required this.onMoverPin,
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
          onTap: (tapPosition, point) {
            onMoverPin(point);
          },
          interactionOptions: const InteractionOptions(
            flags: InteractiveFlag.drag |
                InteractiveFlag.pinchZoom |
                InteractiveFlag.doubleTapZoom |
                InteractiveFlag.scrollWheelZoom,
          ),
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
                width: 48,
                height: 48,
                child: const Icon(
                  Icons.location_on_rounded,
                  color: AppTheme.error,
                  size: 40,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}

// ── Modelo interno ────────────────────────────────────────────────────────────
class _TipoEmergencia {
  final String valor;
  final String label;
  final IconData icon;
  const _TipoEmergencia(
      {required this.valor, required this.label, required this.icon});
}

class _EvidenciasBox extends StatelessWidget {
  final List<Map<String, dynamic>> evidencias;
  final bool grabandoAudio;
  final VoidCallback onCamara;
  final VoidCallback onGaleria;
  final VoidCallback onAudio;
  final void Function(int) onEliminar;

  const _EvidenciasBox({
    required this.evidencias,
    required this.grabandoAudio,
    required this.onCamara,
    required this.onGaleria,
    required this.onAudio,
    required this.onEliminar,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: AppTheme.background,
        borderRadius: BorderRadius.circular(6),
        border: Border.all(color: AppTheme.border),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Row(
            children: [
              Icon(
                Icons.attach_file_rounded,
                size: 18,
                color: AppTheme.primary,
              ),
              SizedBox(width: 8),
              Expanded(
                child: Text(
                  'EVIDENCIAS OPCIONALES',
                  style: TextStyle(
                    fontSize: 10,
                    fontWeight: FontWeight.w800,
                    color: AppTheme.textSecondary,
                    letterSpacing: 1,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 6),
          const Text(
            'Puedes adjuntar una foto o grabar un audio para ayudar al taller.',
            style: TextStyle(
              fontSize: 11,
              color: AppTheme.textSecondary,
              height: 1.4,
            ),
          ),
          const SizedBox(height: 12),
          Row(
            children: [
              Expanded(
                child: OutlinedButton.icon(
                  onPressed: onCamara,
                  icon: const Icon(Icons.photo_camera_outlined, size: 16),
                  label: const Text('Cámara'),
                  style: OutlinedButton.styleFrom(
                    minimumSize: const Size(0, 42),
                    textStyle: const TextStyle(
                      fontSize: 11,
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                ),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: OutlinedButton.icon(
                  onPressed: onGaleria,
                  icon: const Icon(Icons.image_outlined, size: 16),
                  label: const Text('Galería'),
                  style: OutlinedButton.styleFrom(
                    minimumSize: const Size(0, 42),
                    textStyle: const TextStyle(
                      fontSize: 11,
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          OutlinedButton.icon(
            onPressed: onAudio,
            icon: Icon(
              grabandoAudio
                  ? Icons.stop_circle_outlined
                  : Icons.mic_none_outlined,
              size: 16,
            ),
            label: Text(
              grabandoAudio ? 'Detener grabación' : 'Grabar audio',
            ),
            style: OutlinedButton.styleFrom(
              foregroundColor: grabandoAudio ? AppTheme.error : AppTheme.primary,
              side: BorderSide(
                color: grabandoAudio ? AppTheme.error : AppTheme.primary,
                width: 1.2,
              ),
              minimumSize: const Size(double.infinity, 42),
              textStyle: const TextStyle(
                fontSize: 11,
                fontWeight: FontWeight.w800,
              ),
            ),
          ),
          if (evidencias.isNotEmpty) ...[
            const SizedBox(height: 12),
            Column(
              children: List.generate(evidencias.length, (index) {
                final evidencia = evidencias[index];
                final tipo = evidencia['tipo_archivo']?.toString() ?? '';
                final nombre = evidencia['nombre']?.toString() ?? 'Evidencia';

                return Container(
                  margin: const EdgeInsets.only(bottom: 8),
                  padding: const EdgeInsets.all(10),
                  decoration: BoxDecoration(
                    color: AppTheme.surface,
                    borderRadius: BorderRadius.circular(6),
                    border: Border.all(color: AppTheme.border),
                  ),
                  child: Row(
                    children: [
                      Icon(
                        tipo == 'AUDIO'
                            ? Icons.audiotrack_rounded
                            : Icons.image_outlined,
                        size: 18,
                        color: AppTheme.primary,
                      ),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          '$tipo · $nombre',
                          style: const TextStyle(
                            fontSize: 12,
                            fontWeight: FontWeight.w600,
                            color: AppTheme.textPrimary,
                          ),
                          overflow: TextOverflow.ellipsis,
                        ),
                      ),
                      IconButton(
                        onPressed: () => onEliminar(index),
                        icon: const Icon(
                          Icons.close_rounded,
                          size: 18,
                          color: AppTheme.error,
                        ),
                        constraints: const BoxConstraints(),
                        padding: EdgeInsets.zero,
                      ),
                    ],
                  ),
                );
              }),
            ),
          ],
        ],
      ),
    );
  }
}