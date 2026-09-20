import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../services/carrito_service.dart';
import '../theme/app_theme.dart';
import '../widgets/aurora_floating_assistant.dart';
import 'carrito_screen.dart';
import 'catalogo_screen.dart';
import 'mis_pedidos_screen.dart';
import 'mis_reservas_screen.dart';
import 'perfil_screen.dart';

class MainNavigationShell extends StatefulWidget {
  final int initialIndex;

  const MainNavigationShell({super.key, this.initialIndex = 0});

  @override
  State<MainNavigationShell> createState() => _MainNavigationShellState();
}

class _MainNavigationShellState extends State<MainNavigationShell> {
  late int _currentIndex;

  @override
  void initState() {
    super.initState();
    _currentIndex = widget.initialIndex;
  }

  void _irACatalogo() {
    setState(() {
      _currentIndex = 0;
    });
  }

  @override
  Widget build(BuildContext context) {
    final carritoService = context.watch<CarritoService>();
    final totalItemsCarrito = carritoService.totalItems;

    final screens = [
      const CatalogoScreen(),
      CarritoScreen(onIrAlCatalogo: _irACatalogo),
      MisReservasScreen(onIrAlCatalogo: _irACatalogo),
      MisPedidosScreen(onIrAlCatalogo: _irACatalogo),
      const PerfilScreen(),
    ];

    return Scaffold(
      body: IndexedStack(
        index: _currentIndex,
        children: screens,
      ),
      floatingActionButton: const AuroraFloatingAssistant(),
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _currentIndex,
        onTap: (index) {
          setState(() {
            _currentIndex = index;
          });
        },
        items: [
          const BottomNavigationBarItem(
            icon: Icon(Icons.storefront_outlined),
            activeIcon: Icon(Icons.storefront),
            label: 'Catálogo',
          ),
          BottomNavigationBarItem(
            icon: Badge(
              isLabelVisible: totalItemsCarrito > 0,
              label: Text('$totalItemsCarrito'),
              backgroundColor: AppTheme.primaryGold,
              child: const Icon(Icons.shopping_bag_outlined),
            ),
            activeIcon: Badge(
              isLabelVisible: totalItemsCarrito > 0,
              label: Text('$totalItemsCarrito'),
              backgroundColor: AppTheme.primaryGold,
              child: const Icon(Icons.shopping_bag),
            ),
            label: 'Bolsa',
          ),
          const BottomNavigationBarItem(
            icon: Icon(Icons.calendar_today_outlined),
            activeIcon: Icon(Icons.calendar_today),
            label: 'Reservas',
          ),
          const BottomNavigationBarItem(
            icon: Icon(Icons.local_shipping_outlined),
            activeIcon: Icon(Icons.local_shipping),
            label: 'Pedidos',
          ),
          const BottomNavigationBarItem(
            icon: Icon(Icons.person_outline),
            activeIcon: Icon(Icons.person),
            label: 'Perfil',
          ),
        ],
      ),
    );
  }
}
