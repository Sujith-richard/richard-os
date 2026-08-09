
import 'package:flutter/material.dart';
import '../theme.dart';
import '../widgets/richard_orb.dart';
import 'home_shell.dart';

class OnboardingScreen extends StatefulWidget {
  const OnboardingScreen({super.key});
  @override State<OnboardingScreen> createState() => _OnboardingScreenState();
}
class _OnboardingScreenState extends State<OnboardingScreen> {
  bool _listening = false;
  @override Widget build(BuildContext context) {
    final dark = Theme.of(context).brightness == Brightness.dark;
    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(gradient: LinearGradient(begin: Alignment.topCenter, end: Alignment.bottomCenter, colors: [Color(0xFFE9ECF7), Color(0xFFF8F9FE)])),
        child: SafeArea(child: Padding(padding: const EdgeInsets.all(26), child: Column(children: [
          const Spacer(flex: 2),
          TweenAnimationBuilder<double>(tween: Tween(begin: .6, end: 1), duration: const Duration(milliseconds: 900), builder: (_, v, w) => Transform.scale(scale: v, child: w),
            child: _listening ? const RichardOrb(size: 250, state: OrbState.listening) : const RichardOrb(size: 250, state: OrbState.idle)),
          const Spacer(),
          const Text('Speak Freely.\nRichard Is Listening.', textAlign: TextAlign.center, style: TextStyle(fontSize: 30, fontWeight: FontWeight.w800, color: RColors.ink, height: 1.1)),
          const SizedBox(height: 16),
          Text('Capture ideas, ask questions, create projects, automate tasks, and control your digital world using your voice.', textAlign: TextAlign.center, style: TextStyle(fontSize: 15, height: 1.45, color: dark ? Colors.white70 : RColors.inkSoft)),
          const Spacer(),
          Container(
            width: double.infinity, padding: const EdgeInsets.all(2),
            decoration: BoxDecoration(gradient: RColors.appGrad, borderRadius: BorderRadius.circular(40)),
            child: FilledButton(
              style: FilledButton.styleFrom(backgroundColor: Colors.transparent, shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(38)), padding: const EdgeInsets.symmetric(vertical: 16)),
              onPressed: () => Navigator.pushReplacement(context, MaterialPageRoute(builder: (_) => const HomeShell())),
              child: const Text('Get Started', style: TextStyle(fontSize: 16, fontWeight: FontWeight.w700)),
            ),
          ),
          const SizedBox(height: 14),
          TextButton.icon(
            onPressed: () => setState(() => _listening = !_listening),
            icon: Icon(_listening ? Icons.mic : Icons.mic_off, color: _listening ? RColors.ok : RColors.lavenderDeep),
            label: Text(_listening ? 'Enable Voice' : 'Configure Wake Word', style: const TextStyle(color: RColors.lavenderDeep)),
          ),
          Text('Microphone Settings  ·  Privacy Settings', style: TextStyle(fontSize: 12, color: dark ? Colors.white54 : RColors.inkSoft)),
        ]))),
      ),
    );
  }
}
