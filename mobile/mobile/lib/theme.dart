import 'package:flutter/material.dart';

/// Richard OS — color system (spec: soft lavender/purple accent, light blue-gray,
/// white glass surfaces, deep navy text; dark mode = Studio palette #0A101F).
class RColors {
  // Light theme (default, premium glass)
  static const bg = Color(0xFFF4F6FA);          // soft light blue-gray
  static const surface = Color(0xEFFFFFFF);     // white translucent
  static const lavender = Color(0xFFA78BFA);    // portrait / AI accent
  static const lavenderDeep = Color(0xFF7C3AED);
  static const accent = Color(0xFF22D3EE);      // chrome cyan (secondary)
  static const ok = Color(0xFF10B981);
  static const warn = Color(0xFFFBBF24);
  static const err = Color(0xFFF87171);
  static const ink = Color(0xFF141A2E);         // deep navy text
  static const inkSoft = Color(0xFF6B7694);

  // Dark (Studio palette #0A101F)
  static const bgDark = Color(0xFF0A101F);
  static const surfaceDark = Color(0xFF121A2E);
}

class RTheme {
  static ThemeData light() => _base(Brightness.light).copyWith(
        scaffoldBackgroundColor: RColors.bg,
        colorScheme: ColorScheme.light(
          primary: RColors.lavenderDeep,
          secondary: RColors.accent,
          surface: RColors.surface,
          onSurface: RColors.ink,
        ),
        cardTheme: CardThemeData(
          color: RColors.surface,
          elevation: 0,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(22)),
          margin: EdgeInsets.zero,
        ),
        appBarTheme: const AppBarTheme(
          backgroundColor: Colors.transparent,
          elevation: 0,
          centerTitle: true,
          titleTextStyle: TextStyle(color: RColors.ink, fontWeight: FontWeight.w600, letterSpacing: 0.2),
        ),
        filledButtonTheme: FilledButtonThemeData(
          style: FilledButton.styleFrom(
            backgroundColor: RColors.lavenderDeep,
            foregroundColor: Colors.white,
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(30)),
            padding: const EdgeInsets.symmetric(horizontal: 28, vertical: 16),
          ),
        ),
      );

  static ThemeData dark() => _base(Brightness.dark).copyWith(
        scaffoldBackgroundColor: RColors.bgDark,
        colorScheme: const ColorScheme.dark(
          primary: RColors.lavender,
          secondary: RColors.accent,
          surface: RColors.surfaceDark,
        ),
        appBarTheme: const AppBarTheme(backgroundColor: Colors.transparent, elevation: 0, centerTitle: true),
      );

  static ThemeData _base(Brightness b) {
    final scheme = b == Brightness.dark
        ? const ColorScheme.dark(primary: RColors.lavender)
        : const ColorScheme.light(primary: RColors.lavenderDeep);
    return ThemeData(
      useMaterial3: true,
      brightness: b,
      colorScheme: scheme,
      fontFamily: 'Roboto',
    );
  }
}
