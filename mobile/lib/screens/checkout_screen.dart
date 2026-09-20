import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:intl/intl.dart';
import 'package:provider/provider.dart';
import '../services/carrito_service.dart';
import '../services/pedido_service.dart';
import '../services/profile_service.dart';
import '../theme/app_theme.dart';
import '../widgets/aurora_button.dart';
import '../widgets/aurora_text_field.dart';
import 'pago_screen.dart';

class CheckoutScreen extends StatefulWidget {
  final CarritoModel carrito;

  const CheckoutScreen({super.key, required this.carrito});

  @override
  State<CheckoutScreen> createState() => _CheckoutScreenState();
}

class _CheckoutScreenState extends State<CheckoutScreen> {
  final _formKey = GlobalKey<FormState>();

  List<SucursalCheckoutModel> _sucursales = [];
  SucursalCheckoutModel? _sucursalSeleccionada;
  String _modalidad = 'ENTREGA_DOMICILIO'; // 'ENTREGA_DOMICILIO' o 'RETIRO_SUCURSAL'

  final _nombreCtrl = TextEditingController();
  final _telefonoCtrl = TextEditingController();
  final _correoCtrl = TextEditingController();
  final _direccionCtrl = TextEditingController();
  final _ciudadCtrl = TextEditingController(text: 'La Paz');
  final _notasCtrl = TextEditingController();

  bool _cargandoSucursales = true;
  bool _procesando = false;
  String? _error;

  @override
  void initState() {
    super.initState();
    _cargarDatosIniciales();
  }

  @override
  void dispose() {
    _nombreCtrl.dispose();
    _telefonoCtrl.dispose();
    _correoCtrl.dispose();
    _direccionCtrl.dispose();
    _ciudadCtrl.dispose();
    _notasCtrl.dispose();
    super.dispose();
  }

  Future<void> _cargarDatosIniciales() async {
    final pedidoService = context.read<PedidoService>();
    final profileService = ProfileService();

    try {
      final sucursales = await pedidoService.obtenerSucursalesCheckout(
        idEmpresa: widget.carrito.idEmpresa,
      );

      final perfil = await profileService.obtenerPerfil();

      if (mounted) {
        setState(() {
          _sucursales = sucursales;
          if (sucursales.isNotEmpty) {
            _sucursalSeleccionada = sucursales.first;
          }
          _nombreCtrl.text = '${perfil.nombre} ${perfil.apellido}'.trim();
          _correoCtrl.text = perfil.correo;
          _telefonoCtrl.text = perfil.telefono ?? '';
          _direccionCtrl.text = perfil.direccion ?? '';
          _ciudadCtrl.text = perfil.ciudad ?? 'La Paz';
          _cargandoSucursales = false;
        });
      }
    } catch (_) {
      if (mounted) {
        setState(() {
          _cargandoSucursales = false;
        });
      }
    }
  }

  Future<void> _confirmarPedido() async {
    if (!_formKey.currentState!.validate()) return;

    if (_modalidad == 'RETIRO_SUCURSAL' && _sucursalSeleccionada == null) {
      setState(() => _error = 'Por favor selecciona una sucursal para el retiro.');
      return;
    }

    setState(() {
      _procesando = true;
      _error = null;
    });

    final pedidoService = context.read<PedidoService>();
    final carritoService = context.read<CarritoService>();

    try {
      final idSuc = _sucursalSeleccionada?.idSucursal ?? (_sucursales.isNotEmpty ? _sucursales.first.idSucursal : 1);

      final nuevoPedido = await pedidoService.crearPedido(
        idSucursal: idSuc,
        modalidadCompra: _modalidad,
        nombreContacto: _nombreCtrl.text.trim(),
        telefonoContacto: _telefonoCtrl.text.trim(),
        correoContacto: _correoCtrl.text.trim(),
        direccionEntrega: _modalidad == 'ENTREGA_DOMICILIO' ? _direccionCtrl.text.trim() : null,
        ciudadEntrega: _modalidad == 'ENTREGA_DOMICILIO' ? _ciudadCtrl.text.trim() : null,
        notasEntrega: _notasCtrl.text.trim(),
        idEmpresa: widget.carrito.idEmpresa,
      );

      // Recargar bolsa para reflejar que se procesó
      await carritoService.cargarCarrito();

      if (mounted) {
        showDialog(
          context: context,
          barrierDismissible: false,
          builder: (ctx) => AlertDialog(
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
            title: Row(
              children: [
                const Icon(Icons.check_circle, color: AppTheme.primaryGold, size: 28),
                const SizedBox(width: 10),
                Expanded(
                  child: Text(
                    '¡Pedido Registrado!',
                    style: GoogleFonts.playfairDisplay(fontSize: 20, fontWeight: FontWeight.w700),
                  ),
                ),
              ],
            ),
            content: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Tu pedido ha sido registrado con éxito bajo el código:',
                  style: GoogleFonts.plusJakartaSans(fontSize: 13, color: AppTheme.textSecondary),
                ),
                const SizedBox(height: 10),
                Center(
                  child: Container(
                    padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                    decoration: BoxDecoration(
                      color: AppTheme.goldLight,
                      borderRadius: BorderRadius.circular(10),
                      border: Border.all(color: AppTheme.primaryGold.withValues(alpha: 0.3)),
                    ),
                    child: Text(
                      nuevoPedido.codigoPedido,
                      style: GoogleFonts.plusJakartaSans(
                        fontSize: 18,
                        fontWeight: FontWeight.w800,
                        color: AppTheme.primaryGold,
                        letterSpacing: 1,
                      ),
                    ),
                  ),
                ),
                const SizedBox(height: 14),
                Text(
                  'Para asegurar el despacho de tus prendas de alta costura, completa el pago electrónico ahora.',
                  style: GoogleFonts.plusJakartaSans(fontSize: 12, color: AppTheme.textSecondary),
                ),
              ],
            ),
            actions: [
              AuroraButton(
                text: 'Proceder al Pago Seguro',
                icon: Icons.lock_outline,
                onPressed: () {
                  Navigator.pop(ctx); // Cierra diálogo
                  Navigator.pushReplacement(
                    context,
                    MaterialPageRoute(
                      builder: (_) => PagoScreen(
                        idPedido: nuevoPedido.idPedido,
                        pedidoInicial: nuevoPedido,
                      ),
                    ),
                  );
                },
              ),
              const SizedBox(height: 8),
              AuroraButton(
                text: 'Pagar más tarde',
                variant: AuroraButtonVariant.outline,
                onPressed: () {
                  Navigator.pop(ctx); // Cierra diálogo
                  Navigator.pop(context); // Cierra checkout y vuelve a la tienda
                },
              ),
            ],
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _procesando = false;
          _error = e.toString().replaceAll('Exception: ', '');
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final currencyFormatter = NumberFormat.currency(
      locale: 'es_BO',
      symbol: 'Bs. ',
      decimalDigits: 2,
    );

    return Scaffold(
      backgroundColor: AppTheme.background,
      appBar: AppBar(
        title: Text(
          'Confirmar Compra',
          style: GoogleFonts.playfairDisplay(fontSize: 18, fontWeight: FontWeight.w700),
        ),
      ),
      body: _cargandoSucursales
          ? const Center(child: CircularProgressIndicator())
          : Form(
              key: _formKey,
              child: ListView(
                padding: const EdgeInsets.all(20),
                children: [
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

                  // Resumen de la Bolsa
                  Container(
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: AppTheme.surface,
                      borderRadius: BorderRadius.circular(16),
                      border: Border.all(color: AppTheme.border),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Text(
                              'Resumen de compra',
                              style: GoogleFonts.playfairDisplay(
                                fontSize: 16,
                                fontWeight: FontWeight.w700,
                              ),
                            ),
                            Text(
                              '${widget.carrito.totalItems} prendas',
                              style: GoogleFonts.plusJakartaSans(
                                fontSize: 12,
                                color: AppTheme.textMuted,
                              ),
                            ),
                          ],
                        ),
                        const Divider(height: 20),
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Text(
                              'Subtotal',
                              style: GoogleFonts.plusJakartaSans(fontSize: 13, color: AppTheme.textSecondary),
                            ),
                            Text(
                              currencyFormatter.format(widget.carrito.subtotal),
                              style: GoogleFonts.plusJakartaSans(fontSize: 13, fontWeight: FontWeight.w600),
                            ),
                          ],
                        ),
                        const SizedBox(height: 6),
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Text(
                              'Total a pagar',
                              style: GoogleFonts.plusJakartaSans(
                                fontSize: 16,
                                fontWeight: FontWeight.w700,
                                color: AppTheme.textPrimary,
                              ),
                            ),
                            Text(
                              currencyFormatter.format(widget.carrito.total),
                              style: GoogleFonts.plusJakartaSans(
                                fontSize: 18,
                                fontWeight: FontWeight.w800,
                                color: AppTheme.primaryGold,
                              ),
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),

                  const SizedBox(height: 20),

                  // Modalidad de Compra
                  Text(
                    'Modalidad de Entrega',
                    style: GoogleFonts.plusJakartaSans(
                      fontSize: 14,
                      fontWeight: FontWeight.w700,
                      color: AppTheme.textPrimary,
                    ),
                  ),
                  const SizedBox(height: 10),
                  Row(
                    children: [
                      Expanded(
                        child: InkWell(
                          onTap: () => setState(() => _modalidad = 'RETIRO_SUCURSAL'),
                          borderRadius: BorderRadius.circular(12),
                          child: Container(
                            padding: const EdgeInsets.symmetric(vertical: 14, horizontal: 12),
                            decoration: BoxDecoration(
                              color: _modalidad == 'RETIRO_SUCURSAL' ? AppTheme.goldLight : AppTheme.surface,
                              borderRadius: BorderRadius.circular(12),
                              border: Border.all(
                                color: _modalidad == 'RETIRO_SUCURSAL' ? AppTheme.primaryGold : AppTheme.border,
                                width: _modalidad == 'RETIRO_SUCURSAL' ? 1.5 : 1,
                              ),
                            ),
                            child: Column(
                              children: [
                                Icon(
                                  Icons.storefront,
                                  color: _modalidad == 'RETIRO_SUCURSAL' ? AppTheme.primaryGold : AppTheme.textMuted,
                                ),
                                const SizedBox(height: 6),
                                Text(
                                  'Retiro en Sucursal',
                                  style: GoogleFonts.plusJakartaSans(
                                    fontSize: 12,
                                    fontWeight: FontWeight.w600,
                                    color: _modalidad == 'RETIRO_SUCURSAL' ? AppTheme.primaryGold : AppTheme.textPrimary,
                                  ),
                                  textAlign: TextAlign.center,
                                ),
                              ],
                            ),
                          ),
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: InkWell(
                          onTap: () => setState(() => _modalidad = 'ENTREGA_DOMICILIO'),
                          borderRadius: BorderRadius.circular(12),
                          child: Container(
                            padding: const EdgeInsets.symmetric(vertical: 14, horizontal: 12),
                            decoration: BoxDecoration(
                              color: _modalidad == 'ENTREGA_DOMICILIO' ? AppTheme.goldLight : AppTheme.surface,
                              borderRadius: BorderRadius.circular(12),
                              border: Border.all(
                                color: _modalidad == 'ENTREGA_DOMICILIO' ? AppTheme.primaryGold : AppTheme.border,
                                width: _modalidad == 'ENTREGA_DOMICILIO' ? 1.5 : 1,
                              ),
                            ),
                            child: Column(
                              children: [
                                Icon(
                                  Icons.local_shipping_outlined,
                                  color: _modalidad == 'ENTREGA_DOMICILIO' ? AppTheme.primaryGold : AppTheme.textMuted,
                                ),
                                const SizedBox(height: 6),
                                Text(
                                  'Entrega a Domicilio',
                                  style: GoogleFonts.plusJakartaSans(
                                    fontSize: 12,
                                    fontWeight: FontWeight.w600,
                                    color: _modalidad == 'ENTREGA_DOMICILIO' ? AppTheme.primaryGold : AppTheme.textPrimary,
                                  ),
                                  textAlign: TextAlign.center,
                                ),
                              ],
                            ),
                          ),
                        ),
                      ),
                    ],
                  ),

                  const SizedBox(height: 20),

                  // Selector de Sucursal (siempre relevante para el stock o para el retiro)
                  Text(
                    _modalidad == 'RETIRO_SUCURSAL' ? 'Sucursal de Retiro' : 'Sucursal de Origen / Despacho',
                    style: GoogleFonts.plusJakartaSans(
                      fontSize: 13,
                      fontWeight: FontWeight.w600,
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

                  // Datos del Cliente
                  Text(
                    'Datos de Contacto',
                    style: GoogleFonts.playfairDisplay(
                      fontSize: 16,
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                  const SizedBox(height: 12),
                  AuroraTextField(
                    controller: _nombreCtrl,
                    label: 'Nombre completo',
                    validator: (v) => v == null || v.trim().isEmpty ? 'Requerido' : null,
                  ),
                  const SizedBox(height: 12),
                  Row(
                    children: [
                      Expanded(
                        child: AuroraTextField(
                          controller: _telefonoCtrl,
                          label: 'Teléfono de contacto',
                          keyboardType: TextInputType.phone,
                          validator: (v) => v == null || v.trim().isEmpty ? 'Requerido' : null,
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: AuroraTextField(
                          controller: _correoCtrl,
                          label: 'Correo electrónico',
                          keyboardType: TextInputType.emailAddress,
                        ),
                      ),
                    ],
                  ),

                  if (_modalidad == 'ENTREGA_DOMICILIO') ...[
                    const SizedBox(height: 16),
                    Text(
                      'Dirección de Envío',
                      style: GoogleFonts.playfairDisplay(
                        fontSize: 16,
                        fontWeight: FontWeight.w700,
                      ),
                    ),
                    const SizedBox(height: 12),
                    AuroraTextField(
                      controller: _direccionCtrl,
                      label: 'Dirección completa',
                      hint: 'Calle, número, barrio o edificio',
                      validator: (v) => _modalidad == 'ENTREGA_DOMICILIO' && (v == null || v.trim().isEmpty)
                          ? 'Ingresa tu dirección de entrega'
                          : null,
                    ),
                    const SizedBox(height: 12),
                    AuroraTextField(
                      controller: _ciudadCtrl,
                      label: 'Ciudad',
                      validator: (v) => _modalidad == 'ENTREGA_DOMICILIO' && (v == null || v.trim().isEmpty)
                          ? 'Ingresa tu ciudad'
                          : null,
                    ),
                  ],

                  const SizedBox(height: 12),
                  AuroraTextField(
                    controller: _notasCtrl,
                    label: 'Notas adicionales (opcional)',
                    hint: 'Instrucciones para el paquete o retiro',
                  ),

                  const SizedBox(height: 32),

                  AuroraButton(
                    text: 'Confirmar pedido',
                    isLoading: _procesando,
                    onPressed: _confirmarPedido,
                    variant: AuroraButtonVariant.primary,
                  ),
                ],
              ),
            ),
    );
  }
}
