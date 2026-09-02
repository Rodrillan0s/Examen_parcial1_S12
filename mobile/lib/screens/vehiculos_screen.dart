import 'package:flutter/material.dart';
import '../services/vehiculo_service.dart';
import '../theme/app_theme.dart';
import '../widgets/ev_widgets.dart';

class VehiculosScreen extends StatefulWidget {
  const VehiculosScreen({super.key});

  @override
  State<VehiculosScreen> createState() => _VehiculosScreenState();
}

class _VehiculosScreenState extends State<VehiculosScreen> {
  late Future<List<Map<String, dynamic>>> _futureVehiculos;
  bool _eliminando = false;

  @override
  void initState() {
    super.initState();
    _futureVehiculos = VehiculoService().listarMisVehiculos();
  }

  Future<void> _refrescar() async {
    final nuevaCarga = VehiculoService().listarMisVehiculos();

    setState(() {
      _futureVehiculos = nuevaCarga;
    });

    await nuevaCarga;
  }

  String _texto(dynamic valor) {
    if (valor == null) return 'No registrado';
    final texto = valor.toString().trim();
    return texto.isEmpty ? 'No registrado' : texto;
  }

  int? _parseAnio(String valor) {
    final anio = int.tryParse(valor.trim());
    if (anio == null) return null;

    final actual = DateTime.now().year + 1;
    if (anio < 1900 || anio > actual) return null;

    return anio;
  }

  void _mostrarError(String mensaje) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(mensaje),
        backgroundColor: AppTheme.error,
      ),
    );
  }

  Future<void> _abrirFormularioVehiculo({
    Map<String, dynamic>? vehiculo,
  }) async {
    final resultado = await showModalBottomSheet<Map<String, dynamic>>(
      context: context,
      isScrollControlled: true,
      backgroundColor: AppTheme.surface,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(
          top: Radius.circular(14),
        ),
      ),
      builder: (sheetContext) {
        return _VehiculoFormSheet(
          vehiculo: vehiculo,
          parseAnio: _parseAnio,
          texto: _texto,
        );
      },
    );

    if (resultado == null) return;

    await _guardarVehiculo(
      vehiculo: vehiculo,
      placa: resultado['placa'].toString(),
      marcaModelo: resultado['marca_modelo'].toString(),
      anio: resultado['anio'] as int,
    );
  }

  Future<void> _guardarVehiculo({
    required Map<String, dynamic>? vehiculo,
    required String placa,
    required String marcaModelo,
    required int anio,
  }) async {
    try {
      if (vehiculo == null) {
        await VehiculoService().registrarVehiculo(
          placa: placa,
          marcaModelo: marcaModelo,
          anio: anio,
        );
      } else {
        await VehiculoService().actualizarVehiculo(
          nroVehiculo: int.parse(
            vehiculo['nro_vehiculo'].toString(),
          ),
          placa: placa,
          marcaModelo: marcaModelo,
          anio: anio,
        );
      }

      if (!mounted) return;

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            vehiculo == null
                ? 'Vehículo registrado correctamente.'
                : 'Vehículo actualizado correctamente.',
          ),
          backgroundColor: AppTheme.success,
        ),
      );

      await _refrescar();
    } catch (e) {
      if (!mounted) return;

      _mostrarError(
        e.toString().replaceAll('Exception: ', ''),
      );
    }
  }

  Future<void> _confirmarEliminar(Map<String, dynamic> vehiculo) async {
    final nroVehiculo = int.parse(vehiculo['nro_vehiculo'].toString());
    final placa = _texto(vehiculo['placa']);

    final confirmar = await showDialog<bool>(
      context: context,
      builder: (ctx) {
        return AlertDialog(
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(8),
          ),
          title: const Text(
            'Eliminar vehículo',
            style: TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.w800,
              color: AppTheme.textPrimary,
            ),
          ),
          content: Text(
            '¿Deseas eliminar el vehículo con placa $placa?',
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
                backgroundColor: AppTheme.error,
                minimumSize: Size.zero,
                padding: const EdgeInsets.symmetric(
                  horizontal: 18,
                  vertical: 10,
                ),
              ),
              onPressed: () => Navigator.pop(ctx, true),
              child: const Text(
                'ELIMINAR',
                style: TextStyle(
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
      _eliminando = true;
    });

    try {
      await VehiculoService().eliminarVehiculo(
        nroVehiculo: nroVehiculo,
      );

      if (!mounted) return;

      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Vehículo eliminado correctamente.'),
          backgroundColor: AppTheme.success,
        ),
      );

      await _refrescar();
    } catch (e) {
      if (!mounted) return;

      _mostrarError(
        e.toString().replaceAll('Exception: ', ''),
      );
    } finally {
      if (mounted) {
        setState(() {
          _eliminando = false;
        });
      }
    }
  }

  Widget _buildContent(List<Map<String, dynamic>> vehiculos) {
    if (vehiculos.isEmpty) {
      return _EmptyState(
        onRefrescar: _refrescar,
        onAgregar: () => _abrirFormularioVehiculo(),
      );
    }

    return RefreshIndicator(
      onRefresh: _refrescar,
      color: AppTheme.primary,
      child: ListView.separated(
        padding: const EdgeInsets.fromLTRB(20, 20, 20, 96),
        itemCount: vehiculos.length + 1,
        separatorBuilder: (_, __) => const SizedBox(height: 12),
        itemBuilder: (context, index) {
          if (index == 0) {
            return _VehiculosHeader(
              total: vehiculos.length,
              onAgregar: () => _abrirFormularioVehiculo(),
            );
          }

          final vehiculo = vehiculos[index - 1];

          return _VehiculoCard(
            vehiculo: vehiculo,
            onEditar: () => _abrirFormularioVehiculo(
              vehiculo: vehiculo,
            ),
            onEliminar: () => _confirmarEliminar(vehiculo),
          );
        },
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.background,
      appBar: AppBar(
        title: const Text('MIS VEHÍCULOS'),
        backgroundColor: AppTheme.primary,
        foregroundColor: Colors.white,
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios_new_rounded, size: 18),
          onPressed: () => Navigator.pop(context),
        ),
      ),
      floatingActionButton: FloatingActionButton.extended(
        backgroundColor: AppTheme.primary,
        foregroundColor: Colors.white,
        elevation: 0,
        onPressed: () => _abrirFormularioVehiculo(),
        icon: const Icon(Icons.add_rounded),
        label: const Text(
          'AGREGAR',
          style: TextStyle(
            fontSize: 12,
            fontWeight: FontWeight.w800,
            letterSpacing: 0.8,
          ),
        ),
      ),
      body: Stack(
        children: [
          FutureBuilder<List<Map<String, dynamic>>>(
            future: _futureVehiculos,
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

              final vehiculos = snapshot.data ?? [];

              return _buildContent(vehiculos);
            },
          ),
          if (_eliminando)
            Container(
              color: Colors.black.withOpacity(0.08),
              child: const Center(
                child: SizedBox(
                  width: 28,
                  height: 28,
                  child: CircularProgressIndicator(
                    strokeWidth: 2.5,
                    color: AppTheme.primary,
                  ),
                ),
              ),
            ),
        ],
      ),
    );
  }
}

class _VehiculosHeader extends StatelessWidget {
  final int total;
  final VoidCallback onAgregar;

  const _VehiculosHeader({
    required this.total,
    required this.onAgregar,
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
              Icons.directions_car_rounded,
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
                  'VEHÍCULOS REGISTRADOS',
                  style: TextStyle(
                    color: Color(0xFFBFCFFF),
                    fontSize: 11,
                    fontWeight: FontWeight.w700,
                    letterSpacing: 1,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  '$total ${total == 1 ? 'vehículo' : 'vehículos'}',
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 20,
                    fontWeight: FontWeight.w900,
                  ),
                ),
                const SizedBox(height: 4),
                const Text(
                  'Gestiona los vehículos vinculados a tu cuenta.',
                  style: TextStyle(
                    color: Color(0xFFBFCFFF),
                    fontSize: 12,
                    height: 1.3,
                  ),
                ),
              ],
            ),
          ),
          IconButton(
            onPressed: onAgregar,
            icon: const Icon(
              Icons.add_circle_outline_rounded,
              color: Colors.white,
            ),
          ),
        ],
      ),
    );
  }
}

class _VehiculoFormSheet extends StatefulWidget {
  final Map<String, dynamic>? vehiculo;
  final int? Function(String) parseAnio;
  final String Function(dynamic) texto;

  const _VehiculoFormSheet({
    required this.vehiculo,
    required this.parseAnio,
    required this.texto,
  });

  @override
  State<_VehiculoFormSheet> createState() => _VehiculoFormSheetState();
}

class _VehiculoFormSheetState extends State<_VehiculoFormSheet> {
  final _formKey = GlobalKey<FormState>();

  late final TextEditingController _placaController;
  late final TextEditingController _marcaController;
  late final TextEditingController _anioController;

  @override
  void initState() {
    super.initState();

    _placaController = TextEditingController(
      text: widget.vehiculo == null
          ? ''
          : widget.texto(widget.vehiculo!['placa']),
    );

    _marcaController = TextEditingController(
      text: widget.vehiculo == null
          ? ''
          : widget.texto(widget.vehiculo!['marca_modelo']),
    );

    _anioController = TextEditingController(
      text: widget.vehiculo == null
          ? ''
          : widget.texto(widget.vehiculo!['anio']),
    );
  }

  @override
  void dispose() {
    _placaController.dispose();
    _marcaController.dispose();
    _anioController.dispose();
    super.dispose();
  }

  void _enviarFormulario() {
    if (!_formKey.currentState!.validate()) return;

    final anio = widget.parseAnio(_anioController.text);

    if (anio == null) return;

    Navigator.pop(context, {
      'placa': _placaController.text.trim(),
      'marca_modelo': _marcaController.text.trim(),
      'anio': anio,
    });
  }

  @override
  Widget build(BuildContext context) {
    final esNuevo = widget.vehiculo == null;

    return Padding(
      padding: EdgeInsets.only(
        left: 20,
        right: 20,
        top: 12,
        bottom: MediaQuery.of(context).viewInsets.bottom +
            MediaQuery.of(context).padding.bottom +
            20,
      ),
      child: SingleChildScrollView(
        child: Form(
          key: _formKey,
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
              Row(
                children: [
                  Container(
                    width: 44,
                    height: 44,
                    decoration: BoxDecoration(
                      color: AppTheme.primary.withOpacity(0.08),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: const Icon(
                      Icons.directions_car_rounded,
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
                          esNuevo ? 'Registrar vehículo' : 'Editar vehículo',
                          style: const TextStyle(
                            fontSize: 18,
                            fontWeight: FontWeight.w900,
                            color: AppTheme.textPrimary,
                          ),
                        ),
                        const SizedBox(height: 3),
                        Text(
                          esNuevo
                              ? 'Agrega los datos básicos de tu vehículo.'
                              : 'Actualiza los datos del vehículo.',
                          style: const TextStyle(
                            fontSize: 12,
                            color: AppTheme.textSecondary,
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 22),
              EvTextField(
                label: 'PLACA',
                hint: 'Ej: 1234ABC',
                controller: _placaController,
                textCapitalization: TextCapitalization.characters,
                validator: (v) {
                  if (v == null || v.trim().isEmpty) {
                    return 'Ingrese la placa';
                  }

                  if (v.trim().length < 5) {
                    return 'Placa inválida';
                  }

                  return null;
                },
              ),
              const SizedBox(height: 16),
              EvTextField(
                label: 'MARCA Y MODELO',
                hint: 'Ej: Toyota Corolla',
                controller: _marcaController,
                keyboardType: TextInputType.text,
                textCapitalization: TextCapitalization.words,
                validator: (v) {
                  if (v == null || v.trim().isEmpty) {
                    return 'Ingrese la marca y modelo';
                  }

                  if (v.trim().length < 3) {
                    return 'Dato inválido';
                  }

                  return null;
                },
              ),
              const SizedBox(height: 16),
              EvTextField(
                label: 'AÑO',
                hint: 'Ej: 2018',
                controller: _anioController,
                keyboardType: TextInputType.number,
                validator: (v) {
                  if (v == null || v.trim().isEmpty) {
                    return 'Ingrese el año';
                  }

                  if (widget.parseAnio(v) == null) {
                    return 'Año inválido';
                  }

                  return null;
                },
              ),
              const SizedBox(height: 22),
              Row(
                children: [
                  Expanded(
                    child: OutlinedButton(
                      onPressed: () => Navigator.pop(context),
                      child: const Text('CANCELAR'),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: EvPrimaryButton(
                      label: esNuevo ? 'Registrar' : 'Guardar',
                      onPressed: _enviarFormulario,
                    ),
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

class _VehiculoCard extends StatelessWidget {
  final Map<String, dynamic> vehiculo;
  final VoidCallback onEditar;
  final VoidCallback onEliminar;

  const _VehiculoCard({
    required this.vehiculo,
    required this.onEditar,
    required this.onEliminar,
  });

  String _texto(dynamic valor) {
    if (valor == null) return 'No registrado';
    final texto = valor.toString().trim();
    return texto.isEmpty ? 'No registrado' : texto;
  }

  @override
  Widget build(BuildContext context) {
    final placa = _texto(vehiculo['placa']);
    final marcaModelo = _texto(vehiculo['marca_modelo']);
    final anio = _texto(vehiculo['anio']);
    final fechaRegistro = _texto(vehiculo['fecha_registro']);
    final nroVehiculo = _texto(vehiculo['nro_vehiculo']);

    return Container(
      decoration: BoxDecoration(
        color: AppTheme.surface,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: AppTheme.border),
      ),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            Row(
              children: [
                Container(
                  width: 52,
                  height: 52,
                  decoration: BoxDecoration(
                    color: AppTheme.primary.withOpacity(0.08),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: const Icon(
                    Icons.directions_car_rounded,
                    color: AppTheme.primary,
                    size: 26,
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        'PLACA',
                        style: TextStyle(
                          fontSize: 10,
                          fontWeight: FontWeight.w800,
                          color: AppTheme.textSecondary,
                          letterSpacing: 1,
                        ),
                      ),
                      const SizedBox(height: 3),
                      Text(
                        placa.toUpperCase(),
                        style: const TextStyle(
                          fontSize: 19,
                          fontWeight: FontWeight.w900,
                          color: AppTheme.textPrimary,
                          letterSpacing: 0.6,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        marcaModelo.toUpperCase(),
                        style: const TextStyle(
                          fontSize: 12,
                          fontWeight: FontWeight.w700,
                          color: AppTheme.textSecondary,
                        ),
                        overflow: TextOverflow.ellipsis,
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
                    color: AppTheme.primary.withOpacity(0.08),
                    borderRadius: BorderRadius.circular(20),
                    border: Border.all(
                      color: AppTheme.primary.withOpacity(0.18),
                    ),
                  ),
                  child: Text(
                    anio,
                    style: const TextStyle(
                      fontSize: 11,
                      fontWeight: FontWeight.w800,
                      color: AppTheme.primary,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 14),
            const Divider(height: 1),
            const SizedBox(height: 14),
            _InfoRow(
              icon: Icons.badge_outlined,
              label: 'Vehículo N°',
              value: nroVehiculo,
            ),
            const SizedBox(height: 8),
            _InfoRow(
              icon: Icons.car_repair_outlined,
              label: 'Marca modelo',
              value: marcaModelo,
            ),
            const SizedBox(height: 8),
            _InfoRow(
              icon: Icons.access_time_rounded,
              label: 'Registro',
              value: fechaRegistro,
            ),
            const SizedBox(height: 14),
            Row(
              children: [
                Expanded(
                  child: OutlinedButton.icon(
                    onPressed: onEditar,
                    icon: const Icon(Icons.edit_outlined, size: 16),
                    label: const Text('EDITAR'),
                    style: OutlinedButton.styleFrom(
                      minimumSize: const Size(0, 42),
                      textStyle: const TextStyle(
                        fontSize: 12,
                        fontWeight: FontWeight.w700,
                      ),
                    ),
                  ),
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: OutlinedButton.icon(
                    onPressed: onEliminar,
                    icon: const Icon(Icons.delete_outline_rounded, size: 16),
                    label: const Text('ELIMINAR'),
                    style: OutlinedButton.styleFrom(
                      foregroundColor: AppTheme.error,
                      side: const BorderSide(
                        color: AppTheme.error,
                        width: 1.2,
                      ),
                      minimumSize: const Size(0, 42),
                      textStyle: const TextStyle(
                        fontSize: 12,
                        fontWeight: FontWeight.w700,
                      ),
                    ),
                  ),
                ),
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
          width: 96,
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
              'No se pudieron cargar tus vehículos',
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
  final VoidCallback onAgregar;

  const _EmptyState({
    required this.onRefrescar,
    required this.onAgregar,
  });

  @override
  Widget build(BuildContext context) {
    return RefreshIndicator(
      onRefresh: onRefrescar,
      color: AppTheme.primary,
      child: ListView(
        padding: const EdgeInsets.all(28),
        children: [
          const SizedBox(height: 90),
          Center(
            child: Container(
              width: 64,
              height: 64,
              decoration: BoxDecoration(
                color: AppTheme.primary.withOpacity(0.08),
                shape: BoxShape.circle,
              ),
              child: const Icon(
                Icons.directions_car_rounded,
                color: AppTheme.primary,
                size: 34,
              ),
            ),
          ),
          const SizedBox(height: 18),
          const Text(
            'Aún no tienes vehículos',
            textAlign: TextAlign.center,
            style: TextStyle(
              fontSize: 17,
              fontWeight: FontWeight.w900,
              color: AppTheme.textPrimary,
            ),
          ),
          const SizedBox(height: 8),
          const Text(
            'Registra tu vehículo para solicitar auxilio de forma más completa.',
            textAlign: TextAlign.center,
            style: TextStyle(
              fontSize: 13,
              color: AppTheme.textSecondary,
              height: 1.45,
            ),
          ),
          const SizedBox(height: 22),
          EvPrimaryButton(
            label: 'Agregar Vehículo',
            onPressed: onAgregar,
          ),
        ],
      ),
    );
  }
}