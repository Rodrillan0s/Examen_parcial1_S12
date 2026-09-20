import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:intl/intl.dart';
import 'package:provider/provider.dart';
import '../services/auth_provider.dart';
import '../services/pedido_service.dart';
import '../theme/app_theme.dart';
import '../widgets/aurora_badge.dart';
import '../widgets/aurora_button.dart';
import '../widgets/aurora_empty_state.dart';
import 'auth_screens.dart';
import 'pago_screen.dart';

class MisPedidosScreen extends StatefulWidget {
  final VoidCallback? onIrAlCatalogo;

  const MisPedidosScreen({super.key, this.onIrAlCatalogo});

  @override
  State<MisPedidosScreen> createState() => _MisPedidosScreenState();
}

class _MisPedidosScreenState extends State<MisPedidosScreen> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<PedidoService>().cargarMisPedidos();
    });
  }

  void _mostrarDetallePedido(PedidoModel pedido) {
    final currencyFormatter = NumberFormat.currency(
      locale: 'es_BO',
      symbol: 'Bs. ',
      decimalDigits: 2,
    );

    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (ctx) => Container(
        height: MediaQuery.of(context).size.height * 0.85,
        decoration: const BoxDecoration(
          color: AppTheme.surface,
          borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
        ),
        child: Column(
          children: [
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
              padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 8),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    'Detalle del Pedido',
                    style: GoogleFonts.playfairDisplay(
                      fontSize: 20,
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                  IconButton(
                    icon: const Icon(Icons.close),
                    onPressed: () => Navigator.pop(ctx),
                  ),
                ],
              ),
            ),
            const Divider(height: 1),

            Expanded(
              child: ListView(
                padding: const EdgeInsets.all(20),
                children: [
                  // Código y Estado con Wrap flexible para evitar overflow
                  Row(
                    crossAxisAlignment: CrossAxisAlignment.center,
                    children: [
                      Expanded(
                        child: Text(
                          pedido.codigoPedido,
                          style: GoogleFonts.plusJakartaSans(
                            fontSize: 16,
                            fontWeight: FontWeight.w800,
                            color: AppTheme.primaryGold,
                          ),
                          overflow: TextOverflow.ellipsis,
                        ),
                      ),
                      const SizedBox(width: 8),
                      Wrap(
                        spacing: 6,
                        runSpacing: 4,
                        alignment: WrapAlignment.end,
                        children: [
                          AuroraBadge.status(pedido.estado),
                          AuroraBadge.status(pedido.estadoPago),
                        ],
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),
                  Text(
                    'Fecha de compra: ${pedido.fechaPedido}',
                    style: GoogleFonts.plusJakartaSans(fontSize: 12, color: AppTheme.textMuted),
                  ),

                  const Divider(height: 24),

                  // Modalidad
                  Text(
                    'Modalidad de Entrega',
                    style: GoogleFonts.playfairDisplay(fontSize: 15, fontWeight: FontWeight.w700),
                  ),
                  const SizedBox(height: 6),
                  Text(
                    pedido.modalidadCompra == 'ENTREGA_DOMICILIO'
                        ? 'Entrega a domicilio: ${pedido.direccionEntrega ?? ''}, ${pedido.ciudadEntrega ?? ''}'
                        : 'Retiro en sucursal: ${pedido.sucursalNombre ?? 'Sucursal Central'}',
                    style: GoogleFonts.plusJakartaSans(fontSize: 13, color: AppTheme.textSecondary),
                  ),

                  const Divider(height: 24),

                  // Prendas
                  Text(
                    'Prendas Adquiridas (${pedido.items.length})',
                    style: GoogleFonts.playfairDisplay(fontSize: 15, fontWeight: FontWeight.w700),
                  ),
                  const SizedBox(height: 12),
                  ...pedido.items.map((item) {
                    return Padding(
                      padding: const EdgeInsets.symmetric(vertical: 6),
                      child: Row(
                        children: [
                          Container(
                            width: 44,
                            height: 55,
                            decoration: BoxDecoration(
                              color: AppTheme.surfaceVariant,
                              borderRadius: BorderRadius.circular(8),
                            ),
                            clipBehavior: Clip.antiAlias,
                            child: item.imagenUrl != null
                                ? Image.network(
                                    item.imagenUrl!,
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
                                  item.productoNombre,
                                  style: GoogleFonts.playfairDisplay(
                                    fontSize: 13,
                                    fontWeight: FontWeight.w700,
                                  ),
                                  maxLines: 1,
                                  overflow: TextOverflow.ellipsis,
                                ),
                                Text(
                                  'Talla: ${item.tallaNombre} • Color: ${item.colorNombre}',
                                  style: GoogleFonts.plusJakartaSans(fontSize: 11, color: AppTheme.textMuted),
                                ),
                                Text(
                                  '${item.cantidad} x ${currencyFormatter.format(item.precioUnitario)}',
                                  style: GoogleFonts.plusJakartaSans(fontSize: 12, fontWeight: FontWeight.w600),
                                ),
                              ],
                            ),
                          ),
                          Text(
                            currencyFormatter.format(item.subtotal),
                            style: GoogleFonts.plusJakartaSans(fontSize: 13, fontWeight: FontWeight.w700),
                          ),
                        ],
                      ),
                    );
                  }),

                  const Divider(height: 24),

                  // Totales
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text('Subtotal', style: GoogleFonts.plusJakartaSans(fontSize: 13, color: AppTheme.textSecondary)),
                      Text(currencyFormatter.format(pedido.subtotal), style: GoogleFonts.plusJakartaSans(fontSize: 13, fontWeight: FontWeight.w600)),
                    ],
                  ),
                  const SizedBox(height: 6),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text('Total', style: GoogleFonts.plusJakartaSans(fontSize: 16, fontWeight: FontWeight.w800)),
                      Text(
                        currencyFormatter.format(pedido.total),
                        style: GoogleFonts.plusJakartaSans(fontSize: 18, fontWeight: FontWeight.w800, color: AppTheme.primaryGold),
                      ),
                    ],
                  ),

                  // Botón de pago en caso de encontrarse pendiente
                  if ((pedido.estadoPago == 'PENDIENTE' || pedido.estadoPago == 'PENDIENTE_PAGO') &&
                      pedido.estado != 'CANCELADO') ...[
                    const SizedBox(height: 24),
                    AuroraButton(
                      text: 'Pagar Pedido (${currencyFormatter.format(pedido.total)})',
                      icon: Icons.lock_outline,
                      onPressed: () {
                        Navigator.pop(ctx);
                        Navigator.push(
                          context,
                          MaterialPageRoute(
                            builder: (_) => PagoScreen(
                              idPedido: pedido.idPedido,
                              pedidoInicial: pedido,
                            ),
                          ),
                        );
                      },
                    ),
                  ] else if (pedido.estadoPago == 'PAGADO') ...[
                    const SizedBox(height: 18),
                    Container(
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: AppTheme.successLight,
                        borderRadius: BorderRadius.circular(12),
                        border: Border.all(color: AppTheme.success.withValues(alpha: 0.3)),
                      ),
                      child: Row(
                        children: [
                          const Icon(Icons.check_circle_outline, color: AppTheme.success, size: 20),
                          const SizedBox(width: 10),
                          Expanded(
                            child: Text(
                              'Pago confirmado. Comprobante electrónico emitido.',
                              style: GoogleFonts.plusJakartaSans(
                                fontSize: 12,
                                fontWeight: FontWeight.w600,
                                color: AppTheme.success,
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final authProvider = context.watch<AuthProvider>();
    final pedidoService = context.watch<PedidoService>();

    final currencyFormatter = NumberFormat.currency(
      locale: 'es_BO',
      symbol: 'Bs. ',
      decimalDigits: 2,
    );

    if (!authProvider.estaAutenticado) {
      return Scaffold(
        backgroundColor: AppTheme.background,
        appBar: AppBar(title: const Text('Mis Pedidos')),
        body: Center(
          child: Padding(
            padding: const EdgeInsets.all(32),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                const Icon(Icons.local_shipping_outlined, size: 64, color: AppTheme.primaryGold),
                const SizedBox(height: 16),
                Text(
                  'Inicia sesión para ver tus compras',
                  style: GoogleFonts.playfairDisplay(fontSize: 20, fontWeight: FontWeight.w700),
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: 8),
                Text(
                  'Sigue el estado de tus compras y descarga tus comprobantes en cualquier momento.',
                  style: GoogleFonts.plusJakartaSans(fontSize: 13, color: AppTheme.textSecondary),
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: 24),
                AuroraButton(
                  text: 'Iniciar sesión',
                  onPressed: () {
                    Navigator.push(
                      context,
                      MaterialPageRoute(builder: (_) => const AuthScreen()),
                    );
                  },
                ),
              ],
            ),
          ),
        ),
      );
    }

    return Scaffold(
      backgroundColor: AppTheme.background,
      appBar: AppBar(
        title: Text(
          'Mis Pedidos',
          style: GoogleFonts.playfairDisplay(fontSize: 18, fontWeight: FontWeight.w700),
        ),
      ),
      body: RefreshIndicator(
        onRefresh: () => pedidoService.cargarMisPedidos(),
        child: pedidoService.cargando && pedidoService.misPedidos.isEmpty
            ? const Center(child: CircularProgressIndicator())
            : pedidoService.misPedidos.isEmpty
                ? AuroraEmptyState(
                    icon: Icons.receipt_long_outlined,
                    title: 'Aún no tienes compras',
                    message: 'Cuando realices una compra de alta costura, podrás hacer seguimiento a su entrega aquí.',
                    buttonText: 'Explorar catálogo',
                    onButtonPressed: widget.onIrAlCatalogo,
                  )
                : ListView.separated(
                    padding: const EdgeInsets.all(16),
                    itemCount: pedidoService.misPedidos.length,
                    separatorBuilder: (_, __) => const SizedBox(height: 14),
                    itemBuilder: (context, index) {
                      final pedido = pedidoService.misPedidos[index];

                      return InkWell(
                        onTap: () => _mostrarDetallePedido(pedido),
                        borderRadius: BorderRadius.circular(16),
                        child: Container(
                          padding: const EdgeInsets.all(16),
                          decoration: BoxDecoration(
                            color: AppTheme.surface,
                            borderRadius: BorderRadius.circular(16),
                            border: Border.all(color: AppTheme.border),
                            boxShadow: const [
                              BoxShadow(
                                color: Color(0x06000000),
                                blurRadius: 8,
                                offset: Offset(0, 3),
                              ),
                            ],
                          ),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              // Cabecera del pedido flexible
                              Row(
                                crossAxisAlignment: CrossAxisAlignment.center,
                                children: [
                                  Expanded(
                                    child: Text(
                                      pedido.codigoPedido,
                                      style: GoogleFonts.plusJakartaSans(
                                        fontSize: 15,
                                        fontWeight: FontWeight.w700,
                                        color: AppTheme.primaryGold,
                                      ),
                                      overflow: TextOverflow.ellipsis,
                                    ),
                                  ),
                                  const SizedBox(width: 8),
                                  Wrap(
                                    spacing: 6,
                                    runSpacing: 4,
                                    alignment: WrapAlignment.end,
                                    children: [
                                      AuroraBadge.status(pedido.estado),
                                      AuroraBadge.status(pedido.estadoPago),
                                    ],
                                  ),
                                ],
                              ),
                              const SizedBox(height: 6),
                              Text(
                                pedido.fechaPedido,
                                style: GoogleFonts.plusJakartaSans(fontSize: 12, color: AppTheme.textMuted),
                              ),

                              const Divider(height: 20),

                              Row(
                                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                children: [
                                  Row(
                                    children: [
                                      Icon(
                                        pedido.modalidadCompra == 'ENTREGA_DOMICILIO'
                                            ? Icons.local_shipping_outlined
                                            : Icons.storefront_outlined,
                                        size: 16,
                                        color: AppTheme.textSecondary,
                                      ),
                                      const SizedBox(width: 6),
                                      Text(
                                        pedido.modalidadCompra == 'ENTREGA_DOMICILIO'
                                            ? 'A Domicilio'
                                            : 'Retiro en Tienda',
                                        style: GoogleFonts.plusJakartaSans(
                                          fontSize: 12,
                                          color: AppTheme.textSecondary,
                                        ),
                                      ),
                                    ],
                                  ),
                                  Text(
                                    currencyFormatter.format(pedido.total),
                                    style: GoogleFonts.plusJakartaSans(
                                      fontSize: 16,
                                      fontWeight: FontWeight.w800,
                                      color: AppTheme.textPrimary,
                                    ),
                                  ),
                                ],
                              ),

                              // Acción directa de pago si está pendiente
                              if ((pedido.estadoPago == 'PENDIENTE' || pedido.estadoPago == 'PENDIENTE_PAGO') &&
                                  pedido.estado != 'CANCELADO') ...[
                                const SizedBox(height: 12),
                                SizedBox(
                                  width: double.infinity,
                                  height: 38,
                                  child: ElevatedButton.icon(
                                    style: ElevatedButton.styleFrom(
                                      backgroundColor: AppTheme.primaryGold,
                                      foregroundColor: Colors.white,
                                      elevation: 0,
                                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                                      padding: const EdgeInsets.symmetric(horizontal: 14),
                                    ),
                                    icon: const Icon(Icons.lock_outline, size: 16),
                                    label: Text(
                                      'Pagar ahora (${currencyFormatter.format(pedido.total)})',
                                      style: GoogleFonts.plusJakartaSans(
                                        fontSize: 12,
                                        fontWeight: FontWeight.w700,
                                      ),
                                    ),
                                    onPressed: () {
                                      Navigator.push(
                                        context,
                                        MaterialPageRoute(
                                          builder: (_) => PagoScreen(
                                            idPedido: pedido.idPedido,
                                            pedidoInicial: pedido,
                                          ),
                                        ),
                                      );
                                    },
                                  ),
                                ),
                              ],
                            ],
                          ),
                        ),
                      );
                    },
                  ),
      ),
    );
  }
}
