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
  @override
  Widget build(BuildContext context) {
    final dark = Theme.of(context).brightness == Brightness.dark;
    final bg = dark ? RColors.bgDark : RColors.bg;
    return Scaffold(
      backgroundColor: bg,
      body: SafeArea(child: Padding(padding: const EdgeInsets.all(28), child: Column(children: [
        const Spacer(flex: 2),
        TweenAnimationBuilder<double>(tween: Tween(begin: .6, end: 1), duration: const Duration(milliseconds: 900), builder: (_, v, w) => Transform.scale(scale: v, child: w)),
        _listening ? const RichardOrb(size: 240, state: OrbState.listening) : const RichardOrb(size: 240, state: OrbState.idle),
        const Spacer(),
        const Text('Speak Freely.\nRichard Is Listening.', textAlign: TextAlign.center, style: TextStyle(fontSize: 28, fontWeight: FontWeight.w700, color: RColors.ink, height: 1.15)),
        const SizedBox(height: 14),
        Text('Capture ideas, ask questions, create projects, automate tasks, and control your digital world using your voice.', textAlign: TextAlign.center, style: TextStyle(fontSize: 15, height: 1.4, color: dark ? Colors.white70 : RColors.inkSoft)),
        const Spacer(),
        FilledButton(onPressed: () { Navigator.pushReplacement(context, MaterialPageRoute(builder: (_) => const HomeShell())); }, child: const Padding(padding: EdgeInsets.symmetric(horizontal: 40), child: Text('Get Started', style: TextStyle(fontSize: 16, letterSpacing: .4)))),
        const SizedBox(height: 14),
        TextButton.icon(
          onPressed: () => setState(() => _listening = !_listening),
          icon: Icon(_listening ? Icons.mic : Icons.mic_off, size: 18, color: _listening ? RColors.ok : RColors.lavenderDeep),
          label: Text(_listening ? 'Enable Voice' : 'Configure Wake Word', style: TextStyle(color: RColors.lavenderDeep)),
        ),
        Text('Microphone Settings · Privacy Settings', style: TextStyle(fontSize: 12, color: dark ? Colors.white54 : RColors.inkSoft)),
      ]))),
    );
  }
}
