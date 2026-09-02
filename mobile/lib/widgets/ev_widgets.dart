import 'package:flutter/material.dart';
import '../theme/app_theme.dart';

/// Logo "EMERGENCIASVEHICULARES" replicando la tipografía de la web.
class EvLogo extends StatelessWidget {
  final double fontSize;
  final bool darkBackground;

  const EvLogo({
    super.key,
    this.fontSize = 20,
    this.darkBackground = false,
  });

  @override
  Widget build(BuildContext context) {
    final baseColor = darkBackground ? Colors.white : AppTheme.primary;
    final accentColor = darkBackground ? const Color(0xFF6B8CFF) : AppTheme.accent;

    return RichText(
      text: TextSpan(
        children: [
          TextSpan(
            text: 'EMERGENCIAS',
            style: TextStyle(
              fontFamily: 'Roboto',
              fontSize: fontSize,
              fontWeight: FontWeight.w900,
              color: baseColor,
              letterSpacing: 0.5,
            ),
          ),
          TextSpan(
            text: 'VEHICULARES',
            style: TextStyle(
              fontFamily: 'Roboto',
              fontSize: fontSize,
              fontWeight: FontWeight.w400,
              color: accentColor,
              letterSpacing: 0.5,
            ),
          ),
        ],
      ),
    );
  }
}

/// Separador decorativo azul (línea bajo el logo en la pantalla de login).
class EvLogoDivider extends StatelessWidget {
  const EvLogoDivider({super.key});

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 36,
      height: 3,
      decoration: BoxDecoration(
        color: AppTheme.primary,
        borderRadius: BorderRadius.circular(2),
      ),
    );
  }
}

/// Icono de rayo del navbar.
class EvBoltIcon extends StatelessWidget {
  final double size;
  final Color color;

  const EvBoltIcon({
    super.key,
    this.size = 20,
    this.color = Colors.white,
  });

  @override
  Widget build(BuildContext context) {
    return Icon(Icons.flash_on_rounded, size: size, color: color);
  }
}

/// Campo de texto con label en MAYÚSCULAS (estilo web).
class EvTextField extends StatelessWidget {
  final String label;
  final String? hint;
  final bool obscure;
  final TextEditingController? controller;
  final String? Function(String?)? validator;
  final TextInputType? keyboardType;
  final Widget? suffixIcon;
  final bool autofocus;
  final TextCapitalization textCapitalization;

  const EvTextField({
    super.key,
    required this.label,
    this.hint,
    this.obscure = false,
    this.controller,
    this.validator,
    this.keyboardType,
    this.suffixIcon,
    this.autofocus = false,
    this.textCapitalization = TextCapitalization.none,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: Theme.of(context).textTheme.labelSmall,
        ),
        const SizedBox(height: 6),
        TextFormField(
          controller: controller,
          obscureText: obscure,
          keyboardType: keyboardType,
          validator: validator,
          autofocus: autofocus,
          textCapitalization: textCapitalization,
          style: const TextStyle(fontSize: 14, color: AppTheme.textPrimary),
          decoration: InputDecoration(
            hintText: hint,
            suffixIcon: suffixIcon,
          ),
        ),
      ],
    );
  }
}

/// Botón primario con estado de carga.
class EvPrimaryButton extends StatelessWidget {
  final String label;
  final bool loading;
  final VoidCallback? onPressed;

  const EvPrimaryButton({
    super.key,
    required this.label,
    this.loading = false,
    this.onPressed,
  });

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: double.infinity,
      height: 52,
      child: ElevatedButton(
        onPressed: loading ? null : onPressed,
        child: loading
            ? const SizedBox(
                width: 20,
                height: 20,
                child: CircularProgressIndicator(
                  strokeWidth: 2,
                  color: Colors.white,
                ),
              )
            : Text(label.toUpperCase()),
      ),
    );
  }
}