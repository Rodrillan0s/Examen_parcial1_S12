import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';

import '../theme/app_theme.dart';
import '../services/routing_service.dart';
import '../services/taller_service.dart';

class TrackingEmergenciaScreen extends StatefulWidget {
  final Map<String, dynamic> emergencia;

  const TrackingEmergenciaScreen({
    super.key,
    required this.emergencia,
  });

  @override
  State<TrackingEmergenciaScreen> createState() =>
      _TrackingEmergenciaScreenState();
}

class _TrackingEmergenciaScreenState extends State<TrackingEmergenciaScreen> {
  LatLng? _cliente;
  LatLng? _auxilio;
  bool _cargando = false;
  bool _trackingSimulado = true;
  List<LatLng> _ruta = [];
  bool _cargandoRuta = false;

  @override
  void initState() {
    super.initState();
    _cargarTrackingInicial();
  }

  Future<void> _cargarTrackingInicial() async {
    final latCliente = _double(widget.emergencia['latitud']);
    final lngCliente = _double(widget.emergencia['longitud']);

    if (latCliente == null || lngCliente == null) {
      return;
    }

    final puntoCliente = LatLng(latCliente, lngCliente);

    final puntoAuxilioDesdeEmergencia = _leerPuntoAuxilioDesdeEmergencia();
    final puntoAuxilioDesdeTaller = await _leerPuntoAuxilioDesdeTaller();

    final puntoAuxilio = puntoAuxilioDesdeEmergencia ?? puntoAuxilioDesdeTaller;

    if (!mounted) return;

    if (puntoAuxilio == null) {
      setState(() {
        _cliente = puntoCliente;
        _auxilio = null;
        _trackingSimulado = false;
        _ruta = [];
      });

      return;
    }

    setState(() {
      _cliente = puntoCliente;
      _auxilio = puntoAuxilio;
      _trackingSimulado = false;
      _ruta = [puntoAuxilio, puntoCliente];
    });

    await _cargarRutaPorCalles(
      origen: puntoAuxilio,
      destino: puntoCliente,
    );
  }

  Future<void> _cargarRutaPorCalles({
    required LatLng origen,
    required LatLng destino,
  }) async {
    setState(() {
      _cargandoRuta = true;
    });

    try {
      final ruta = await RoutingService().obtenerRutaPorCalles(
        origen: origen,
        destino: destino,
      );

      if (!mounted) return;

      setState(() {
        _ruta = ruta.isNotEmpty ? ruta : [origen, destino];
        _cargandoRuta = false;
      });
    } catch (_) {
      if (!mounted) return;

      setState(() {
        _ruta = [origen, destino];
        _cargandoRuta = false;
      });
    }
  }

  LatLng? _leerPuntoAuxilioDesdeEmergencia() {
    final posiblesLat = [
      widget.emergencia['auxilio_latitud'],
      widget.emergencia['mecanico_latitud'],
      widget.emergencia['latitud_auxilio'],
      widget.emergencia['latitud_mecanico'],
      widget.emergencia['taller_latitud'],
    ];

    final posiblesLng = [
      widget.emergencia['auxilio_longitud'],
      widget.emergencia['mecanico_longitud'],
      widget.emergencia['longitud_auxilio'],
      widget.emergencia['longitud_mecanico'],
      widget.emergencia['taller_longitud'],
    ];

    for (int i = 0; i < posiblesLat.length; i++) {
      final lat = _double(posiblesLat[i]);
      final lng = _double(posiblesLng[i]);

      if (lat != null && lng != null) {
        return LatLng(lat, lng);
      }
    }

    return null;
  }

  Future<LatLng?> _leerPuntoAuxilioDesdeTaller() async {
    final nroTaller = _int(widget.emergencia['nro_taller']);

    if (nroTaller == null) {
      return null;
    }

    try {
      return await TallerService().obtenerUbicacionTaller(
        nroTaller: nroTaller,
      );
    } catch (_) {
      return null;
    }
  }

  double? _double(dynamic value) {
    if (value == null) return null;
    return double.tryParse(value.toString());
  }

  int? _int(dynamic value) {
    if (value == null) return null;
    return int.tryParse(value.toString());
  }

  String _texto(dynamic value) {
    if (value == null) return 'No disponible';
    final texto = value.toString().trim();
    return texto.isEmpty ? 'No disponible' : texto;
  }

  double _distanciaKm() {
    if (_ruta.length < 2) return 0;

    const distance = Distance();
    double metros = 0;

    for (int i = 0; i < _ruta.length - 1; i++) {
        metros += distance.as(
        LengthUnit.Meter,
        _ruta[i],
        _ruta[i + 1],
        );
    }

    return metros / 1000;
    }

  LatLng _centroMapa() {
    if (_cliente == null || _auxilio == null) {
      return const LatLng(-17.7833, -63.1821);
    }

    return LatLng(
      (_cliente!.latitude + _auxilio!.latitude) / 2,
      (_cliente!.longitude + _auxilio!.longitude) / 2,
    );
  }

  Future<void> _refrescarTracking() async {
    setState(() {
      _cargando = true;
    });

    await _cargarTrackingInicial();

    if (!mounted) return;

    setState(() {
      _cargando = false;
    });

    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('Tracking actualizado.'),
        backgroundColor: AppTheme.success,
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final cliente = _cliente;
    final auxilio = _auxilio;

    if (cliente == null || auxilio == null) {
      return Scaffold(
        backgroundColor: AppTheme.background,
        appBar: AppBar(
          title: const Text('TRACKING'),
          backgroundColor: AppTheme.primary,
          foregroundColor: Colors.white,
        ),
        body: const Center(
          child: Padding(
            padding: EdgeInsets.all(28),
            child: Text(
              'No hay coordenadas suficientes para mostrar el tracking.',
              textAlign: TextAlign.center,
              style: TextStyle(
                fontSize: 13,
                color: AppTheme.textSecondary,
                height: 1.4,
              ),
            ),
          ),
        ),
      );
    }

    return Scaffold(
      backgroundColor: AppTheme.background,
      appBar: AppBar(
        title: const Text('TRACKING EN TIEMPO REAL'),
        backgroundColor: AppTheme.primary,
        foregroundColor: Colors.white,
        elevation: 0,
        actions: [
          IconButton(
            onPressed: _cargando ? null : _refrescarTracking,
            icon: _cargando
                ? const SizedBox(
                    width: 18,
                    height: 18,
                    child: CircularProgressIndicator(
                      strokeWidth: 2,
                      color: Colors.white,
                    ),
                  )
                : const Icon(Icons.refresh_rounded),
          ),
        ],
      ),
      body: Stack(
        children: [
          FlutterMap(
            options: MapOptions(
              initialCenter: _centroMapa(),
              initialZoom: 14,
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
              PolylineLayer(
                polylines: [
                    Polyline(
                    points: _ruta.isNotEmpty ? _ruta : [auxilio, cliente],
                    strokeWidth: 4,
                    color: AppTheme.primary,
                    ),
                ],
                ),
              MarkerLayer(
                markers: [
                  Marker(
                    point: cliente,
                    width: 74,
                    height: 78,
                    child: const _MapMarker(
                      icon: Icons.person_pin_circle_rounded,
                      label: 'Tú',
                      color: AppTheme.error,
                    ),
                  ),
                  Marker(
                    point: auxilio,
                    width: 82,
                    height: 78,
                    child: const _MapMarker(
                      icon: Icons.car_repair_rounded,
                      label: 'Auxilio',
                      color: AppTheme.primary,
                    ),
                  ),
                ],
              ),
            ],
          ),
          if (_cargandoRuta)
            Positioned(
                top: 16,
                left: 16,
                right: 16,
                child: Container(
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
                decoration: BoxDecoration(
                    color: AppTheme.surface,
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(color: AppTheme.border),
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
                        'Calculando ruta por calles...',
                        style: TextStyle(
                        fontSize: 12,
                        color: AppTheme.textSecondary,
                        fontWeight: FontWeight.w600,
                        ),
                    ),
                    ],
                ),
                ),
            ),
          Positioned(
            left: 16,
            right: 16,
            bottom: MediaQuery.of(context).padding.bottom + 16,
            child: _TrackingPanel(
              emergencia: widget.emergencia,
              distanciaKm: _distanciaKm(),
              trackingSimulado: _trackingSimulado,
            ),
          ),
        ],
      ),
    );
  }
}

class _MapMarker extends StatelessWidget {
  final IconData icon;
  final String label;
  final Color color;

  const _MapMarker({
    required this.icon,
    required this.label,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      height: 78,
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Container(
            width: 42,
            height: 42,
            decoration: BoxDecoration(
              color: color,
              shape: BoxShape.circle,
              border: Border.all(
                color: Colors.white,
                width: 3,
              ),
            ),
            child: Icon(
              icon,
              color: Colors.white,
              size: 24,
            ),
          ),
          const SizedBox(height: 4),
          Container(
            padding: const EdgeInsets.symmetric(
              horizontal: 7,
              vertical: 3,
            ),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(20),
              border: Border.all(color: AppTheme.border),
            ),
            child: Text(
              label,
              style: TextStyle(
                fontSize: 10,
                fontWeight: FontWeight.w800,
                color: color,
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _TrackingPanel extends StatelessWidget {
  final Map<String, dynamic> emergencia;
  final double distanciaKm;
  final bool trackingSimulado;

  const _TrackingPanel({
    required this.emergencia,
    required this.distanciaKm,
    required this.trackingSimulado,
  });

  String _texto(dynamic value) {
    if (value == null) return 'No disponible';
    final texto = value.toString().trim();
    return texto.isEmpty ? 'No disponible' : texto;
  }

  @override
  Widget build(BuildContext context) {
    final estado = _texto(emergencia['estado']).toUpperCase();
    final taller = emergencia['nro_taller'] == null
        ? 'Taller pendiente'
        : 'Taller N° ${emergencia['nro_taller']}';

    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppTheme.surface,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: AppTheme.border),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.12),
            blurRadius: 18,
            offset: const Offset(0, 8),
          ),
        ],
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Row(
            children: [
              Container(
                width: 42,
                height: 42,
                decoration: BoxDecoration(
                  color: AppTheme.primary.withOpacity(0.08),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: const Icon(
                  Icons.route_rounded,
                  color: AppTheme.primary,
                  size: 24,
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'EMERGENCIA N° ${_texto(emergencia['nro_emergencia'])}',
                      style: const TextStyle(
                        fontSize: 11,
                        color: AppTheme.textSecondary,
                        fontWeight: FontWeight.w800,
                        letterSpacing: 0.8,
                      ),
                    ),
                    const SizedBox(height: 3),
                    Text(
                      estado,
                      style: const TextStyle(
                        fontSize: 15,
                        color: AppTheme.textPrimary,
                        fontWeight: FontWeight.w900,
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
                  color: AppTheme.success.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(
                    color: AppTheme.success.withOpacity(0.3),
                  ),
                ),
                child: const Text(
                  'ACTIVO',
                  style: TextStyle(
                    fontSize: 10,
                    color: AppTheme.success,
                    fontWeight: FontWeight.w900,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 14),
          const Divider(height: 1),
          const SizedBox(height: 14),
          _TrackingInfoRow(
            icon: Icons.build_outlined,
            label: 'Auxilio',
            value: taller,
          ),
          const SizedBox(height: 8),
          _TrackingInfoRow(
            icon: Icons.social_distance_outlined,
            label: 'Distancia',
            value: '${distanciaKm.toStringAsFixed(2)} km aprox.',
          ),
          const SizedBox(height: 8),
          _TrackingInfoRow(
            icon: Icons.directions_car_rounded,
            label: 'Vehículo',
            value:
                '${_texto(emergencia['vehiculo_placa']).toUpperCase()} · ${_texto(emergencia['vehiculo_marca'])}',
          ),
          if (trackingSimulado) ...[
            const SizedBox(height: 12),
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(10),
              decoration: BoxDecoration(
                color: AppTheme.primary.withOpacity(0.06),
                borderRadius: BorderRadius.circular(8),
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
                      'Tracking preparado. El punto del auxilio se actualizará con el endpoint real.',
                      style: TextStyle(
                        fontSize: 11,
                        color: AppTheme.textSecondary,
                        height: 1.35,
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ],
      ),
    );
  }
}

class _TrackingInfoRow extends StatelessWidget {
  final IconData icon;
  final String label;
  final String value;

  const _TrackingInfoRow({
    required this.icon,
    required this.label,
    required this.value,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Icon(
          icon,
          size: 16,
          color: AppTheme.textSecondary,
        ),
        const SizedBox(width: 8),
        SizedBox(
          width: 82,
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
              fontWeight: FontWeight.w700,
              color: AppTheme.textPrimary,
            ),
          ),
        ),
      ],
    );
  }
}