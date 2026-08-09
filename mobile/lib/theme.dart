import 'package:flutter/material.dart';

class RColors {
  static const bg = Color(0xFFF4F6FA);
  static const surface = Color(0xEFFFFFFF);
  static const lavender = Color(0xFFA78BFA);
  static const lavenderDeep = Color(0xFF7C3AED);
  static const accent = Color(0xFF22D3EE);
  static const ok = Color(0xFF10B981);
  static const warn = Color(0xFFFBBF24);
  static const err = Color(0xFFF87171);
  static const ink = Color(0xFF141A2E);
  static const inkSoft = Color(0xFF6B7694);
  static const bgDark = Color(0xFF0A101F);
  static const surfaceDark = Color(0xFF121A2E);

  static const appGrad = LinearGradient(
    begin: Alignment.topLeft, end: Alignment.bottomRight,
    colors: [lavenderDeep, accent],
  );
  static const orbGlow = RadialGradient(colors: [lavender, Color(0x00A78BFA)]);

  static BoxDecoration glass({required bool dark, double radius = 24}) => BoxDecoration(
        color: dark ? surfaceDark.withValues(alpha: .55) : Colors.white.withValues(alpha: .92),
        borderRadius: BorderRadius.circular(radius),
        border: Border.all(color: lavender.withValues(alpha: dark ? .18 : .12), width: 1),
        boxShadow: [
          BoxShadow(
            color: dark ? Colors.black.withValues(alpha: .35) : Colors.black.withValues(alpha: .06),
            blurRadius: 18,
            offset: const Offset(0, 8),
          ),
        ],
      );
}

class RTheme {
  static ThemeData light() => ThemeData(
        useMaterial3: true,
        brightness: Brightness.light,
        colorScheme: ColorScheme.light(primary: RColors.lavenderDeep, secondary: RColors.accent),
        scaffoldBackgroundColor: RColors.bg,
        appBarTheme: const AppBarTheme(backgroundColor: Colors.transparent, elevation: 0, centerTitle: true),
        fontFamily: 'Inter',
      );
  static ThemeData dark() => ThemeData(
        useMaterial3: true,
        brightness: Brightness.dark,
        colorScheme: ColorScheme.dark(primary: RColors.lavender, secondary: RColors.accent),
        scaffoldBackgroundColor: RColors.bgDark,
        appBarTheme: const AppBarTheme(backgroundColor: Colors.transparent, elevation: 0, centerTitle: true),
        fontFamily: 'Inter',
      );
}
