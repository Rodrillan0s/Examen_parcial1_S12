import 'package:flutter/material.dart';
import '../theme/app_theme.dart';
import '../widgets/ev_widgets.dart';
import '../services/auth_service.dart';
import 'package:provider/provider.dart';
import '../services/auth_provider.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});
  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _formKey = GlobalKey<FormState>();
  final _ciController = TextEditingController();
  final _passController = TextEditingController();
  bool _obscurePass = true;
  bool _loading = false;

  @override
  void dispose() {
    _ciController.dispose();
    _passController.dispose();
    super.dispose();
  }

  void _usarUsuarioDemo() {
    setState(() {
      _ciController.text = '12345678';
      _passController.text = '12345678';
      _obscurePass = false;
    });

    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('Usuario demo cargado.'),
        backgroundColor: AppTheme.success,
        duration: Duration(seconds: 2),
      ),
    );
  }

  Future<void> _handleLogin() async {
    if (!_formKey.currentState!.validate()) return;
    setState(() => _loading = true);
    try {
      final usuario = await AuthService().login(
        ci: _ciController.text.trim(),
        password: _passController.text.trim(),
      );
      if (!mounted) return;
      Provider.of<AuthProvider>(context, listen: false).loginExitoso({
        'nombre': usuario['nombre_completo'].toString(),
        'rol': usuario['nombre_rol'].toString(),
      });
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(
        content: Text(e.toString().replaceAll('Exception: ', '')),
        backgroundColor: AppTheme.error,
      ));
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.surface,
      body: Row(
        children: [
          Expanded(
            child: SafeArea(
              child: SingleChildScrollView(
                padding: const EdgeInsets.symmetric(horizontal: 36, vertical: 40),
                child: Form(
                  key: _formKey,
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const EvLogo(fontSize: 18),
                      const SizedBox(height: 10),
                      const EvLogoDivider(),
                      const SizedBox(height: 36),
                      Text(
                        'Acceso al Sistema',
                        style: Theme.of(context).textTheme.displayMedium,
                      ),
                      const SizedBox(height: 6),
                      Text(
                        'Portal exclusivo para personal autorizado.',
                        style: Theme.of(context).textTheme.bodyMedium,
                      ),
                      const SizedBox(height: 18),
                      _DemoUserCard(
                        onUse: _usarUsuarioDemo,
                      ),
                      const SizedBox(height: 24),
                      EvTextField(
                        label: 'CARNET DE IDENTIDAD',
                        hint: 'Ej: 9781936',
                        controller: _ciController,
                        keyboardType: TextInputType.number,
                        autofocus: true,
                        validator: (v) => (v == null || v.trim().isEmpty) ? 'Ingrese su carnet de identidad' : null,
                      ),
                      const SizedBox(height: 20),
                      EvTextField(
                        label: 'CONTRASENA',
                        hint: 'Minimo 6 caracteres',
                        controller: _passController,
                        obscure: _obscurePass,
                        suffixIcon: IconButton(
                          icon: Icon(_obscurePass ? Icons.visibility_off_outlined : Icons.visibility_outlined, size: 18, color: AppTheme.textHint),
                          onPressed: () => setState(() => _obscurePass = !_obscurePass),
                        ),
                        validator: (v) {
                          if (v == null || v.isEmpty) return 'Ingrese su contrasena';
                          if (v.length < 6) return 'Minimo 6 caracteres';
                          return null;
                        },
                      ),
                      const SizedBox(height: 28),
                      EvPrimaryButton(label: 'Iniciar Sesion', loading: _loading, onPressed: _handleLogin),
                      const SizedBox(height: 20),
                      Center(
                        child: TextButton(
                          onPressed: () => Navigator.push(context, MaterialPageRoute(builder: (_) => const RegisterScreen())),
                          child: RichText(
                            text: const TextSpan(
                              style: TextStyle(fontSize: 13),
                              children: [
                                TextSpan(text: 'No tienes cuenta? ', style: TextStyle(color: AppTheme.textSecondary)),
                                TextSpan(text: 'Registrate', style: TextStyle(color: AppTheme.primary, fontWeight: FontWeight.w700)),
                              ],
                            ),
                          ),
                        ),
                      ),
                      const SizedBox(height: 40),
                      const Divider(),
                      const SizedBox(height: 12),
                      Text('2026 Emergencias Vehiculares. Todos los derechos reservados.', style: Theme.of(context).textTheme.bodyMedium?.copyWith(fontSize: 11)),
                    ],
                  ),
                ),
              ),
            ),
          ),
          if (MediaQuery.of(context).size.width > 640)
            Expanded(
              child: Container(
                color: AppTheme.darkBg,
                padding: const EdgeInsets.all(48),
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const EvLogo(fontSize: 16, darkBackground: true),
                    const SizedBox(height: 48),
                    Text('Plataforma Integrada de\nGestion Operativa', style: Theme.of(context).textTheme.displayLarge?.copyWith(color: Colors.white, fontSize: 30, height: 1.25)),
                    const SizedBox(height: 20),
                    const Text('Administracion centralizada de servicios automotrices, flotas de emergencia y facturacion electronica.', style: TextStyle(fontSize: 14, color: Color(0xFFADB5BD), height: 1.65)),
                    const SizedBox(height: 48),
                    _DarkChip(icon: Icons.shield_outlined, text: 'Acceso por roles y permisos'),
                    const SizedBox(height: 12),
                    _DarkChip(icon: Icons.location_on_outlined, text: 'Geolocalizacion en tiempo real'),
                    const SizedBox(height: 12),
                    _DarkChip(icon: Icons.receipt_long_outlined, text: 'Facturacion electronica integrada'),
                  ],
                ),
              ),
            ),
        ],
      ),
    );
  }
}

class _DarkChip extends StatelessWidget {
  final IconData icon;
  final String text;
  const _DarkChip({required this.icon, required this.text});
  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Icon(icon, color: const Color(0xFF6B8CFF), size: 16),
        const SizedBox(width: 10),
        Text(text, style: const TextStyle(color: Color(0xFFCED4DA), fontSize: 13, fontWeight: FontWeight.w500)),
      ],
    );
  }
}

class _DemoUserCard extends StatelessWidget {
  final VoidCallback onUse;

  const _DemoUserCard({
    required this.onUse,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: AppTheme.primary.withOpacity(0.06),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(
          color: AppTheme.primary.withOpacity(0.18),
        ),
      ),
      child: Row(
        children: [
          Container(
            width: 38,
            height: 38,
            decoration: BoxDecoration(
              color: AppTheme.primary.withOpacity(0.10),
              borderRadius: BorderRadius.circular(6),
            ),
            child: const Icon(
              Icons.account_circle_outlined,
              color: AppTheme.primary,
              size: 22,
            ),
          ),
          const SizedBox(width: 12),
          const Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'USUARIO DEMO',
                  style: TextStyle(
                    fontSize: 11,
                    fontWeight: FontWeight.w800,
                    color: AppTheme.primary,
                    letterSpacing: 1,
                  ),
                ),
                SizedBox(height: 4),
                Text(
                  'CI: 12345678  ·  Pass: 12345678',
                  style: TextStyle(
                    fontSize: 12,
                    fontWeight: FontWeight.w600,
                    color: AppTheme.textPrimary,
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(width: 10),
          SizedBox(
            height: 36,
            child: ElevatedButton(
              onPressed: onUse,
              style: ElevatedButton.styleFrom(
                minimumSize: Size.zero,
                padding: const EdgeInsets.symmetric(
                  horizontal: 14,
                  vertical: 8,
                ),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(6),
                ),
              ),
              child: const Text(
                'USAR',
                style: TextStyle(
                  fontSize: 11,
                  fontWeight: FontWeight.w800,
                  letterSpacing: 0.8,
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class RegisterScreen extends StatefulWidget {
  const RegisterScreen({super.key});
  @override
  State<RegisterScreen> createState() => _RegisterScreenState();
}

class _RegisterScreenState extends State<RegisterScreen> {
  final _formKey = GlobalKey<FormState>();
  final _nombreController = TextEditingController();
  final _ciController = TextEditingController();
  final _usuarioController = TextEditingController();
  final _telefonoController = TextEditingController();
  final _emailController = TextEditingController();
  final _passController = TextEditingController();
  final _confirmPassController = TextEditingController();
  bool _obscurePass = true;
  bool _obscureConfirm = true;
  bool _loading = false;
  static const int _nroRolCliente = 4;

  @override
  void dispose() {
    _nombreController.dispose(); _ciController.dispose(); _usuarioController.dispose();
    _telefonoController.dispose(); _emailController.dispose();
    _passController.dispose(); _confirmPassController.dispose();
    super.dispose();
  }

  Future<void> _handleRegister() async {
    if (!_formKey.currentState!.validate()) return;
    setState(() => _loading = true);
    try {
      await AuthService().register(
        ci: _ciController.text.trim(),
        nombreCompleto: _nombreController.text.trim(),
        nombreUsuario: _usuarioController.text.trim(),
        password: _passController.text.trim(),
        telefono: _telefonoController.text.trim(),
        correo: _emailController.text.trim(),
        nroRol: _nroRolCliente,
      );
      if (!mounted) return;
      Navigator.pop(context);
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(
        content: Text('Cuenta creada correctamente. Inicia sesion.'),
        backgroundColor: AppTheme.success,
      ));
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(
        content: Text(e.toString().replaceAll('Exception: ', '')),
        backgroundColor: AppTheme.error,
      ));
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.surface,
      body: SafeArea(
        child: Row(
          children: [
            Expanded(
              child: SingleChildScrollView(
                padding: const EdgeInsets.symmetric(horizontal: 36, vertical: 40),
                child: Form(
                  key: _formKey,
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          if (Navigator.canPop(context)) ...[
                            IconButton(icon: const Icon(Icons.arrow_back, color: AppTheme.primary, size: 20), onPressed: () => Navigator.pop(context), padding: EdgeInsets.zero, constraints: const BoxConstraints()),
                            const SizedBox(width: 8),
                          ],
                          const EvLogo(fontSize: 16),
                        ],
                      ),
                      const SizedBox(height: 10),
                      const EvLogoDivider(),
                      const SizedBox(height: 32),
                      Text('Crear Cuenta', style: Theme.of(context).textTheme.displayMedium),
                      const SizedBox(height: 6),
                      Text('Complete el formulario para registrarse.', style: Theme.of(context).textTheme.bodyMedium),
                      const SizedBox(height: 28),
                      EvTextField(label: 'NOMBRE COMPLETO', hint: 'Ej: Juan Carlos Perez', controller: _nombreController, keyboardType: TextInputType.name, autofocus: true, validator: (v) => (v == null || v.trim().isEmpty) ? 'Campo requerido' : null),
                      const SizedBox(height: 18),
                      Row(
                        children: [
                          Expanded(child: EvTextField(label: 'CARNET DE IDENTIDAD', hint: 'Ej: 9781936', controller: _ciController, keyboardType: TextInputType.number, validator: (v) => (v == null || v.trim().isEmpty) ? 'Requerido' : null)),
                          const SizedBox(width: 16),
                          Expanded(child: EvTextField(label: 'TELEFONO', hint: 'Ej: 70012345', controller: _telefonoController, keyboardType: TextInputType.phone, validator: (v) => (v == null || v.trim().isEmpty) ? 'Requerido' : null)),
                        ],
                      ),
                      const SizedBox(height: 18),
                      EvTextField(label: 'CORREO ELECTRONICO', hint: 'usuario@ejemplo.com', controller: _emailController, keyboardType: TextInputType.emailAddress, validator: (v) { if (v == null || v.trim().isEmpty) return 'Campo requerido'; if (!v.contains('@')) return 'Correo invalido'; return null; }),
                      const SizedBox(height: 18),
                      EvTextField(
                        label: 'NOMBRE DE USUARIO',
                        hint: 'Ej: jperez2026',
                        controller: _usuarioController,
                        validator: (v) {
                          if (v == null || v.trim().isEmpty) return 'Campo requerido';
                          if (v.trim().length < 4) return 'Minimo 4 caracteres';
                          if (v.contains(' ')) return 'Sin espacios';
                          return null;
                        },
                      ),
                      const SizedBox(height: 18),
                      EvTextField(label: 'CONTRASENA', hint: 'Minimo 8 caracteres', controller: _passController, obscure: _obscurePass,
                        suffixIcon: IconButton(icon: Icon(_obscurePass ? Icons.visibility_off_outlined : Icons.visibility_outlined, size: 18, color: AppTheme.textHint), onPressed: () => setState(() => _obscurePass = !_obscurePass)),
                        validator: (v) { if (v == null || v.isEmpty) return 'Campo requerido'; if (v.length < 8) return 'Minimo 8 caracteres'; return null; }),
                      const SizedBox(height: 18),
                      EvTextField(label: 'CONFIRMAR CONTRASENA', hint: 'Repetir contrasena', controller: _confirmPassController, obscure: _obscureConfirm,
                        suffixIcon: IconButton(icon: Icon(_obscureConfirm ? Icons.visibility_off_outlined : Icons.visibility_outlined, size: 18, color: AppTheme.textHint), onPressed: () => setState(() => _obscureConfirm = !_obscureConfirm)),
                        validator: (v) { if (v == null || v.isEmpty) return 'Campo requerido'; if (v != _passController.text) return 'Las contrasenas no coinciden'; return null; }),
                      const SizedBox(height: 28),
                      EvPrimaryButton(label: 'Crear Cuenta', loading: _loading, onPressed: _handleRegister),
                      const SizedBox(height: 18),
                      Center(
                        child: TextButton(
                          onPressed: () => Navigator.pop(context),
                          child: RichText(
                            text: const TextSpan(style: TextStyle(fontSize: 13), children: [
                              TextSpan(text: 'Ya tienes cuenta? ', style: TextStyle(color: AppTheme.textSecondary)),
                              TextSpan(text: 'Iniciar Sesion', style: TextStyle(color: AppTheme.primary, fontWeight: FontWeight.w700)),
                            ]),
                          ),
                        ),
                      ),
                      const SizedBox(height: 32),
                      const Divider(),
                      const SizedBox(height: 12),
                      Text('2026 Emergencias Vehiculares. Todos los derechos reservados.', style: Theme.of(context).textTheme.bodyMedium?.copyWith(fontSize: 11)),
                    ],
                  ),
                ),
              ),
            ),
            if (MediaQuery.of(context).size.width > 640)
              Expanded(
                child: Container(
                  color: AppTheme.darkBg,
                  padding: const EdgeInsets.all(48),
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const EvLogo(fontSize: 16, darkBackground: true),
                      const SizedBox(height: 48),
                      Text('Unete a la\nPlataforma', style: Theme.of(context).textTheme.displayLarge?.copyWith(color: Colors.white, fontSize: 30, height: 1.25)),
                      const SizedBox(height: 20),
                      const Text('Registra tu cuenta como cliente y accede a la red de asistencia vehicular mas eficiente de Bolivia.', style: TextStyle(fontSize: 14, color: Color(0xFFADB5BD), height: 1.65)),
                      const SizedBox(height: 40),
                      _InfoStep(step: '01', text: 'Completa tus datos personales'),
                      const SizedBox(height: 16),
                      _InfoStep(step: '02', text: 'Elige tu nombre de usuario'),
                      const SizedBox(height: 16),
                      _InfoStep(step: '03', text: 'Solicita auxilio cuando lo necesites'),
                    ],
                  ),
                ),
              ),
          ],
        ),
      ),
    );
  }
}

class _InfoStep extends StatelessWidget {
  final String step;
  final String text;
  const _InfoStep({required this.step, required this.text});
  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Container(
          width: 32, height: 32,
          decoration: BoxDecoration(border: Border.all(color: const Color(0xFF4A5BA8), width: 1.5), borderRadius: BorderRadius.circular(4)),
          child: Center(child: Text(step, style: const TextStyle(color: Color(0xFF6B8CFF), fontSize: 11, fontWeight: FontWeight.w800))),
        ),
        const SizedBox(width: 14),
        Text(text, style: const TextStyle(color: Color(0xFFCED4DA), fontSize: 13, fontWeight: FontWeight.w500)),
      ],
    );
  }
}