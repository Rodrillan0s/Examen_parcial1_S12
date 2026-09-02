import 'package:flutter/material.dart';
import '../services/profile_service.dart';
import '../theme/app_theme.dart';
import '../widgets/ev_widgets.dart';

class PerfilScreen extends StatefulWidget {
  const PerfilScreen({super.key});

  @override
  State<PerfilScreen> createState() => _PerfilScreenState();
}

class _PerfilScreenState extends State<PerfilScreen> {
  final _formKey = GlobalKey<FormState>();

  final _telefonoController = TextEditingController();
  final _correoController = TextEditingController();
  final _direccionController = TextEditingController();
  final _passwordController = TextEditingController();

  Map<String, dynamic>? _perfil;
  bool _cargando = true;
  bool _guardando = false;
  bool _obscurePass = true;

  @override
  void initState() {
    super.initState();
    _cargarPerfil();
  }

  @override
  void dispose() {
    _telefonoController.dispose();
    _correoController.dispose();
    _direccionController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  Future<void> _cargarPerfil() async {
    setState(() => _cargando = true);

    try {
      final perfil = await ProfileService().obtenerPerfil();

      _telefonoController.text = _texto(perfil['telefono']);
      _correoController.text = _texto(perfil['correo']);
      _direccionController.text = _texto(perfil['direccion']);

      if (!mounted) return;

      setState(() {
        _perfil = perfil;
        _cargando = false;
      });
    } catch (e) {
      if (!mounted) return;

      setState(() => _cargando = false);

      _mostrarError(e.toString().replaceAll('Exception: ', ''));
    }
  }

  Future<void> _guardarPerfil() async {
    if (_perfil == null) return;
    if (!_formKey.currentState!.validate()) return;

    setState(() => _guardando = true);

    try {
      await ProfileService().actualizarPerfil(
        ci: _texto(_perfil!['ci']),
        telefono: _telefonoController.text.trim(),
        correo: _correoController.text.trim(),
        direccion: _direccionController.text.trim(),
        password: _passwordController.text.trim(),
      );

      if (!mounted) return;

      _passwordController.clear();

      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Perfil actualizado correctamente.'),
          backgroundColor: AppTheme.success,
        ),
      );

      await _cargarPerfil();
    } catch (e) {
      if (!mounted) return;

      _mostrarError(e.toString().replaceAll('Exception: ', ''));
    } finally {
      if (mounted) setState(() => _guardando = false);
    }
  }

  String _texto(dynamic valor) {
    if (valor == null) return '';
    return valor.toString();
  }

  String _textoDefault(dynamic valor) {
    final texto = _texto(valor).trim();
    return texto.isEmpty ? 'No registrado' : texto;
  }

  void _mostrarError(String mensaje) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(mensaje),
        backgroundColor: AppTheme.error,
      ),
    );
  }

  String get _iniciales {
    final nombre = _texto(_perfil?['nombre_completo']).trim();

    if (nombre.isEmpty) return '?';

    final partes = nombre.split(' ');

    if (partes.length >= 2) {
      return '${partes[0][0]}${partes[1][0]}'.toUpperCase();
    }

    return nombre[0].toUpperCase();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.background,
      appBar: AppBar(
        title: const Text('MI PERFIL'),
        backgroundColor: AppTheme.primary,
        foregroundColor: Colors.white,
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios_new_rounded, size: 18),
          onPressed: () => Navigator.pop(context),
        ),
      ),
      body: _cargando
          ? const _LoadingState()
          : _perfil == null
              ? _ErrorState(onReintentar: _cargarPerfil)
              : SingleChildScrollView(
                  padding: const EdgeInsets.all(20),
                  child: Form(
                    key: _formKey,
                    child: Column(
                      children: [
                        _PerfilHeader(
                          iniciales: _iniciales,
                          nombreCompleto: _textoDefault(_perfil!['nombre_completo']),
                          nombreUsuario: _textoDefault(_perfil!['nombre_usuario']),
                          rol: _textoDefault(_perfil!['nombre_rol']),
                        ),
                        const SizedBox(height: 14),

                        _InfoCard(
                          title: 'Datos de cuenta',
                          children: [
                            _InfoRow(
                              icon: Icons.badge_outlined,
                              label: 'CI',
                              value: _textoDefault(_perfil!['ci']),
                            ),
                            const SizedBox(height: 10),
                            _InfoRow(
                              icon: Icons.confirmation_number_outlined,
                              label: 'Usuario N°',
                              value: _textoDefault(_perfil!['nro_usuario']),
                            ),
                            const SizedBox(height: 10),
                            _InfoRow(
                              icon: Icons.verified_user_outlined,
                              label: 'Estado',
                              value: _textoDefault(_perfil!['estado']),
                            ),
                            const SizedBox(height: 10),
                            _InfoRow(
                              icon: Icons.calendar_today_outlined,
                              label: 'Registro',
                              value: _textoDefault(_perfil!['fecha_registro']),
                            ),
                          ],
                        ),

                        const SizedBox(height: 14),

                        _InfoCard(
                          title: 'Información laboral',
                          children: [
                            _InfoRow(
                              icon: Icons.work_outline_rounded,
                              label: 'Rol',
                              value: _textoDefault(_perfil!['nombre_rol']),
                            ),
                            const SizedBox(height: 10),
                            _InfoRow(
                              icon: Icons.business_outlined,
                              label: 'Empresa',
                              value: _textoDefault(_perfil!['nombre_empresa']),
                            ),
                            const SizedBox(height: 10),
                            _InfoRow(
                              icon: Icons.directions_car_outlined,
                              label: 'Vehículos',
                              value: _textoDefault(_perfil!['cant_vehiculos']),
                            ),
                          ],
                        ),

                        const SizedBox(height: 14),

                        _InfoCard(
                          title: 'Editar datos personales',
                          children: [
                            EvTextField(
                              label: 'TELÉFONO',
                              hint: 'Ej: 70012345',
                              controller: _telefonoController,
                              keyboardType: TextInputType.phone,
                              validator: (v) {
                                if (v == null || v.trim().isEmpty) {
                                  return 'Ingrese su teléfono';
                                }
                                if (v.trim().length < 6) {
                                  return 'Teléfono inválido';
                                }
                                return null;
                              },
                            ),
                            const SizedBox(height: 16),
                            EvTextField(
                              label: 'CORREO ELECTRÓNICO',
                              hint: 'usuario@ejemplo.com',
                              controller: _correoController,
                              keyboardType: TextInputType.emailAddress,
                              validator: (v) {
                                if (v == null || v.trim().isEmpty) {
                                  return 'Ingrese su correo';
                                }
                                if (!v.contains('@')) {
                                  return 'Correo inválido';
                                }
                                return null;
                              },
                            ),
                            const SizedBox(height: 16),
                            EvTextField(
                              label: 'DIRECCIÓN',
                              hint: 'Ej: Av. Cristo Redentor, Santa Cruz',
                              controller: _direccionController,
                              keyboardType: TextInputType.streetAddress,
                              validator: (v) {
                                if (v == null || v.trim().isEmpty) {
                                  return 'Ingrese su dirección';
                                }
                                return null;
                              },
                            ),
                            const SizedBox(height: 16),
                            EvTextField(
                              label: 'NUEVA CONTRASEÑA (opcional)',
                              hint: 'Dejar vacío si no desea cambiarla',
                              controller: _passwordController,
                              obscure: _obscurePass,
                              suffixIcon: IconButton(
                                icon: Icon(
                                  _obscurePass
                                      ? Icons.visibility_off_outlined
                                      : Icons.visibility_outlined,
                                  size: 18,
                                  color: AppTheme.textHint,
                                ),
                                onPressed: () {
                                  setState(() {
                                    _obscurePass = !_obscurePass;
                                  });
                                },
                              ),
                              validator: (v) {
                                if (v == null || v.trim().isEmpty) {
                                  return null;
                                }

                                if (v.trim().length < 8) {
                                  return 'Mínimo 8 caracteres';
                                }

                                return null;
                              },
                            ),
                            const SizedBox(height: 20),
                            EvPrimaryButton(
                              label: 'Guardar Cambios',
                              loading: _guardando,
                              onPressed: _guardarPerfil,
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

class _PerfilHeader extends StatelessWidget {
  final String iniciales;
  final String nombreCompleto;
  final String nombreUsuario;
  final String rol;

  const _PerfilHeader({
    required this.iniciales,
    required this.nombreCompleto,
    required this.nombreUsuario,
    required this.rol,
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
          CircleAvatar(
            radius: 28,
            backgroundColor: const Color(0xFF2D3A8C),
            child: Text(
              iniciales,
              style: const TextStyle(
                color: Colors.white,
                fontSize: 18,
                fontWeight: FontWeight.w800,
              ),
            ),
          ),
          const SizedBox(width: 14),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  nombreCompleto.toUpperCase(),
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 15,
                    fontWeight: FontWeight.w900,
                    height: 1.25,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  nombreUsuario,
                  style: const TextStyle(
                    color: Color(0xFFBFCFFF),
                    fontSize: 12,
                    fontWeight: FontWeight.w600,
                  ),
                ),
                const SizedBox(height: 8),
                Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 8,
                    vertical: 3,
                  ),
                  decoration: BoxDecoration(
                    color: Colors.white.withOpacity(0.12),
                    borderRadius: BorderRadius.circular(20),
                    border: Border.all(
                      color: Colors.white.withOpacity(0.2),
                    ),
                  ),
                  child: Text(
                    rol.toUpperCase(),
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
          ),
        ],
      ),
    );
  }
}

class _InfoCard extends StatelessWidget {
  final String title;
  final List<Widget> children;

  const _InfoCard({
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
          width: 90,
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
  final Future<void> Function() onReintentar;

  const _ErrorState({
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
              'No se pudo cargar el perfil',
              textAlign: TextAlign.center,
              style: TextStyle(
                fontSize: 15,
                fontWeight: FontWeight.w800,
                color: AppTheme.textPrimary,
              ),
            ),
            const SizedBox(height: 8),
            const Text(
              'Verificá tu conexión e intentá nuevamente.',
              textAlign: TextAlign.center,
              style: TextStyle(
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