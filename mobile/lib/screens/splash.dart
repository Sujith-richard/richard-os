import 'dart:async';
import 'package:flutter/material.dart';
import '../theme.dart';
import '../widgets/richard_orb.dart';
import 'onboarding.dart';

class SplashScreen extends StatefulWidget {
  const SplashScreen({super.key});
  @override State<SplashScreen> createState() => _SplashScreenState();
}

class _SplashScreenState extends State<SplashScreen> {
  @override
  void initState() { super.initState(); Timer(const Duration(milliseconds: 1600), () { if (mounted) Navigator.pushReplacement(context, MaterialPageRoute(builder: (_) => const OnboardingScreen())); }); }

  @override
  Widget build(BuildContext context) {
    final dark = Theme.of(context).brightness == Brightness.dark;
    return Scaffold(
      backgroundColor: dark ? RColors.bgDark : RColors.bg,
      body: Center(
        child: Column(mainAxisSize: MainAxisSize.min, children: [
          const RichardOrb(size: 180, state: OrbState.idle),
          const SizedBox(height: 24),
          const Text('RICHARD OS', style: TextStyle(fontSize: 22, fontWeight: FontWeight.w700, letterSpacing: 6, color: RColors.ink)),
          const SizedBox(height: 6),
          Text('Local First · Cloud Assisted · Continuously Learning', style: TextStyle(fontSize: 12, color: dark ? Colors.white70 : RColors.inkSoft)),
        ]),
      ),
    );
  }
}
