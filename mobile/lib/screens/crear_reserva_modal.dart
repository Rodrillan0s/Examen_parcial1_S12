import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:intl/intl.dart';
import 'package:provider/provider.dart';
import '../services/auth_provider.dart';
import '../services/catalogo_service.dart';
import '../services/pedido_service.dart';
import '../services/reserva_service.dart';
import '../theme/app_theme.dart';
import '../widgets/aurora_button.dart';
import 'auth_screens.dart';

class CrearReservaModal extends StatefulWidget {
  final DetallePrendaModel prenda;
  final VarianteModel varianteSeleccionada;

  const CrearReservaModal({
    super.key,
    required this.prenda,
    required this.varianteSeleccionada,
  });

  @override
  State<CrearReservaModal> createState() => _CrearReservaModalState();
}

class _CrearReservaModalState extends State<CrearReservaModal> {
  final TextEditingController _observacionesController = TextEditingController();
  List<SucursalCheckoutModel> _sucursales = [];
  SucursalCheckoutModel? _sucursalSeleccionada;
  DateTime _fechaSeleccionada = DateTime.now().add(const Duration(days: 1));
  TimeOfDay _horaSeleccionada = const TimeOfDay(hour: 15, minute: 0);

  bool _cargandoSucursales = true;
  bool _enviando = false;
  String? _error;

  @override
  void initState() {
    super.initState();
    _cargarSucursales();
  }

  @override
  void dispose() {
    _observacionesController.dispose();
    super.dispose();
  }

  Future<void> _cargarSucursales() async {
    final pedidoService = context.read<PedidoService>();
    final sucursales = await pedidoService.obtenerSucursalesCheckout(
      idEmpresa: widget.prenda.idEmpresa,
    );

    if (mounted) {
      setState(() {
        _sucursales = sucursales;
        if (sucursales.isNotEmpty) {
          _sucursalSeleccionada = sucursales.first;
        }
        _cargandoSucursales = false;
      });
    }
  }

  Future<void> _seleccionarFecha() async {
    final picked = await showDatePicker(
      context: context,
      initialDate: _fechaSeleccionada,
      firstDate: DateTime.now(),
      lastDate: DateTime.now().add(const Duration(days: 30)),
      builder: (context, child) {
        return Theme(
          data: ThemeData.light().copyWith(
            colorScheme: const ColorScheme.light(
              primary: AppTheme.primary,
              onPrimary: Colors.white,
              surface: Colors.white,
            ),
          ),
          child: child!,
        );
      },
    );

    if (picked != null) {
      setState(() {
        _fechaSeleccionada = picked;
      });
    }
  }

  Future<void> _seleccionarHora() async {
    final picked = await showTimePicker(
      context: context,
      initialTime: _horaSeleccionada,
      builder: (context, child) {
        return Theme(
          data: ThemeData.light().copyWith(
            colorScheme: const ColorScheme.light(
              primary: AppTheme.primary,
              onPrimary: Colors.white,
              surface: Colors.white,
            ),
          ),
          child: child!,
        );
      },
    );

    if (picked != null) {
      setState(() {
        _horaSeleccionada = picked;
      });
    }
  }

  Future<void> _confirmarReserva() async {
    final authProvider = context.read<AuthProvider>();
    if (!authProvider.estaAutenticado) {
      Navigator.pop(context);
      Navigator.push(
        context,
        MaterialPageRoute(builder: (_) => const AuthScreen()),
      );
      return;
    }

    if (_sucursalSeleccionada == null) {
      setState(() => _error = 'Por favor selecciona una sucursal.');
      return;
    }

    setState(() {
      _enviando = true;
      _error = null;
    });

    final fechaHora = DateTime(
      _fechaSeleccionada.year,
      _fechaSeleccionada.month,
      _fechaSeleccionada.day,
      _horaSeleccionada.hour,
      _horaSeleccionada.minute,
    );

    final fechaFormateada = DateFormat("yyyy-MM-dd HH:mm:ss").format(fechaHora);

    final reservaService = context.read<ReservaService>();

    try {
      final reserva = await reservaService.crearReserva(
        idSucursal: _sucursalSeleccionada!.idSucursal,
        fechaHoraVisita: fechaFormateada,
        items: [
          {
            'id_variante': widget.varianteSeleccionada.idVariante,
            'cantidad': 1,
          }
        ],
        observaciones: _observacionesController.text.trim(),
        idEmpresa: widget.prenda.idEmpresa,
      );

      if (mounted) {
        Navigator.pop(context);
        showDialog(
          context: context,
          builder: (ctx) => AlertDialog(
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
            title: Text(
              '¡Reserva Confirmada!',
              style: GoogleFonts.playfairDisplay(fontSize: 20, fontWeight: FontWeight.w700),
            ),
            content: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Tu reserva ha sido registrada con el código:',
                  style: GoogleFonts.plusJakartaSans(fontSize: 13, color: AppTheme.textSecondary),
                ),
                const SizedBox(height: 8),
                Center(
                  child: Container(
                    padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                    decoration: BoxDecoration(
                      color: AppTheme.goldLight,
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Text(
                      reserva.codigoReserva,
                      style: GoogleFonts.plusJakartaSans(
                        fontSize: 16,
                        fontWeight: FontWeight.w700,
                        color: AppTheme.primaryGold,
                        letterSpacing: 1,
                      ),
                    ),
                  ),
                ),
                const SizedBox(height: 12),
                Text(
                  'Te esperamos en ${_sucursalSeleccionada!.nombre} el día ${DateFormat("dd/MM/yyyy 'a las' HH:mm").format(fechaHora)}.',
                  style: GoogleFonts.plusJakartaSans(fontSize: 13, color: AppTheme.textPrimary),
                ),
              ],
            ),
            actions: [
              ElevatedButton(
                onPressed: () => Navigator.pop(ctx),
                child: const Text('Entendido'),
              ),
            ],
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _enviando = false;
          _error = e.toString().replaceAll('Exception: ', '');
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      height: MediaQuery.of(context).size.height * 0.88,
      decoration: const BoxDecoration(
        color: AppTheme.surface,
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
      child: Column(
        children: [
          // Barra de Arrastre
          Padding(
            padding: const EdgeInsets.symmetric(vertical: 12),
            child: Container(
              width: 40,
              height: 4,
              decoration: BoxDecoration(
                color: AppTheme.borderStrong,
                borderRadius: BorderRadius.circular(2),
              ),
            ),
          ),
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 20),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  'Reservar cita en tienda',
                  style: GoogleFonts.playfairDisplay(
                    fontSize: 20,
                    fontWeight: FontWeight.w700,
                    color: AppTheme.textPrimary,
                  ),
                ),
                IconButton(
                  icon: const Icon(Icons.close),
                  onPressed: () => Navigator.pop(context),
                ),
              ],
            ),
          ),
          const Divider(height: 1),

          Expanded(
            child: _cargandoSucursales
                ? const Center(child: CircularProgressIndicator())
                : ListView(
                    padding: const EdgeInsets.all(20),
                    children: [
                      // Resumen de la prenda a reservar
                      Container(
                        padding: const EdgeInsets.all(12),
                        decoration: BoxDecoration(
                          color: AppTheme.surfaceVariant,
                          borderRadius: BorderRadius.circular(12),
                          border: Border.all(color: AppTheme.border),
                        ),
                        child: Row(
                          children: [
                            Container(
                              width: 50,
                              height: 60,
                              decoration: BoxDecoration(
                                borderRadius: BorderRadius.circular(8),
                                color: Colors.white,
                              ),
                              clipBehavior: Clip.antiAlias,
                              child: widget.prenda.imagenPrincipal != null
                                  ? Image.network(
                                      widget.prenda.imagenPrincipal!,
                                      fit: BoxFit.cover,
                                      errorBuilder: (_, __, ___) => const Icon(Icons.checkroom),
                                    )
                                  : const Icon(Icons.checkroom),
                            ),
                            const SizedBox(width: 12),
                            Expanded(
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text(
                                    widget.prenda.nombre,
                                    style: GoogleFonts.playfairDisplay(
                                      fontSize: 14,
                                      fontWeight: FontWeight.w700,
                                    ),
                                    maxLines: 1,
                                    overflow: TextOverflow.ellipsis,
                                  ),
                                  const SizedBox(height: 4),
                                  Text(
                                    'Talla: ${widget.varianteSeleccionada.tallaNombre} • Color: ${widget.varianteSeleccionada.colorNombre}',
                                    style: GoogleFonts.plusJakartaSans(
                                      fontSize: 12,
                                      color: AppTheme.textSecondary,
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          ],
                        ),
                      ),

                      const SizedBox(height: 20),

                      if (_error != null) ...[
                        Container(
                          padding: const EdgeInsets.all(12),
                          decoration: BoxDecoration(
                            color: AppTheme.errorLight,
                            borderRadius: BorderRadius.circular(10),
                          ),
                          child: Text(
                            _error!,
                            style: GoogleFonts.plusJakartaSans(color: AppTheme.error, fontSize: 12),
                          ),
                        ),
                        const SizedBox(height: 16),
                      ],

                      // Selector de Sucursal
                      Text(
                        'Sucursal para tu visita',
                        style: GoogleFonts.plusJakartaSans(
                          fontSize: 13,
                          fontWeight: FontWeight.w600,
                          color: AppTheme.textPrimary,
                        ),
                      ),
                      const SizedBox(height: 8),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 14),
                        decoration: BoxDecoration(
                          color: AppTheme.surface,
                          borderRadius: BorderRadius.circular(12),
                          border: Border.all(color: AppTheme.border),
                        ),
                        child: DropdownButtonHideUnderline(
                          child: DropdownButton<SucursalCheckoutModel>(
                            value: _sucursalSeleccionada,
                            isExpanded: true,
                            items: _sucursales.map((s) {
                              return DropdownMenuItem(
                                value: s,
                                child: Text('${s.nombre} (${s.ciudad})'),
                              );
                            }).toList(),
                            onChanged: (val) {
                              setState(() {
                                _sucursalSeleccionada = val;
                              });
                            },
                          ),
                        ),
                      ),

                      const SizedBox(height: 20),

                      // Selector de Fecha y Hora
                      Row(
                        children: [
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  'Fecha de visita',
                                  style: GoogleFonts.plusJakartaSans(
                                    fontSize: 13,
                                    fontWeight: FontWeight.w600,
                                  ),
                                ),
                                const SizedBox(height: 8),
                                InkWell(
                                  onTap: _seleccionarFecha,
                                  borderRadius: BorderRadius.circular(12),
                                  child: Container(
                                    padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 12),
                                    decoration: BoxDecoration(
                                      border: Border.all(color: AppTheme.border),
                                      borderRadius: BorderRadius.circular(12),
                                    ),
                                    child: Row(
                                      children: [
                                        const Icon(Icons.calendar_today_outlined, size: 16, color: AppTheme.primaryGold),
                                        const SizedBox(width: 8),
                                        Text(
                                          DateFormat('dd/MM/yyyy').format(_fechaSeleccionada),
                                          style: GoogleFonts.plusJakartaSans(fontSize: 13, fontWeight: FontWeight.w600),
                                        ),
                                      ],
                                    ),
                                  ),
                                ),
                              ],
                            ),
                          ),
                          const SizedBox(width: 12),
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  'Horario aproximado',
                                  style: GoogleFonts.plusJakartaSans(
                                    fontSize: 13,
                                    fontWeight: FontWeight.w600,
                                  ),
                                ),
                                const SizedBox(height: 8),
                                InkWell(
                                  onTap: _seleccionarHora,
                                  borderRadius: BorderRadius.circular(12),
                                  child: Container(
                                    padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 12),
                                    decoration: BoxDecoration(
                                      border: Border.all(color: AppTheme.border),
                                      borderRadius: BorderRadius.circular(12),
                                    ),
                                    child: Row(
                                      children: [
                                        const Icon(Icons.access_time, size: 16, color: AppTheme.primaryGold),
                                        const SizedBox(width: 8),
                                        Text(
                                          _horaSeleccionada.format(context),
                                          style: GoogleFonts.plusJakartaSans(fontSize: 13, fontWeight: FontWeight.w600),
                                        ),
                                      ],
                                    ),
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ],
                      ),

                      const SizedBox(height: 20),

                      // Observaciones
                      Text(
                        'Observaciones o solicitudes especiales',
                        style: GoogleFonts.plusJakartaSans(
                          fontSize: 13,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                      const SizedBox(height: 8),
                      TextField(
                        controller: _observacionesController,
                        maxLines: 3,
                        decoration: const InputDecoration(
                          hintText: 'Ej. Deseo probarme también con calzado de tacón...',
                        ),
                      ),
                    ],
                  ),
          ),

          // Botón Confirmar
          Padding(
            padding: const EdgeInsets.all(20),
            child: AuroraButton(
              text: 'Confirmar reserva',
              isLoading: _enviando,
              onPressed: _confirmarReserva,
              variant: AuroraButtonVariant.primary,
            ),
          ),
        ],
      ),
    );
  }
}
