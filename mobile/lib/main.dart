import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:provider/provider.dart';
import 'services/asistente_service.dart';
import 'services/auth_provider.dart';
import 'services/carrito_service.dart';
import 'services/catalogo_service.dart';
import 'services/pago_service.dart';
import 'services/pedido_service.dart';
import 'services/reserva_service.dart';
import 'config/app_config.dart';
import 'screens/main_navigation_shell.dart';
import 'theme/app_theme.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  await AppConfig.init();

  SystemChrome.setSystemUIOverlayStyle(
    const SystemUiOverlayStyle(
      statusBarColor: Colors.transparent,
      statusBarIconBrightness: Brightness.dark,
    ),
  );

  await SystemChrome.setPreferredOrientations([
    DeviceOrientation.portraitUp,
  ]);

  final authProvider = AuthProvider();
  await authProvider.verificarSesion();

  runApp(AuroraStoreApp(authProvider: authProvider));
}

class AuroraStoreApp extends StatelessWidget {
  final AuthProvider? authProvider;

  const AuroraStoreApp({super.key, this.authProvider});

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        ChangeNotifierProvider.value(value: authProvider ?? AuthProvider()),
        ChangeNotifierProvider(create: (_) => CatalogoService()),
        ChangeNotifierProvider(create: (_) => CarritoService()),
        ChangeNotifierProvider(create: (_) => PedidoService()),
        ChangeNotifierProvider(create: (_) => ReservaService()),
        ChangeNotifierProvider(create: (_) => PagoService()),
        ChangeNotifierProvider(create: (_) => AsistenteService()),
      ],
      child: MaterialApp(
        title: 'Aurora Store',
        debugShowCheckedModeBanner: false,
        theme: AppTheme.lightTheme,
        home: const MainNavigationShell(),
      ),
    );
  }
}