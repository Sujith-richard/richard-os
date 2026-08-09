import 'package:flutter/material.dart';
import '../theme.dart';
import '../widgets/richard_orb.dart';

class VoiceScreen extends StatefulWidget {
  const VoiceScreen({super.key});
  @override State<VoiceScreen> createState() => _VoiceScreenState();
}

class _VoiceScreenState extends State<VoiceScreen> {
  OrbState _state = OrbState.idle;
  String _msg = 'Welcome, Sir. What can I do for you?';
  bool _active = false;

  void _cycle(OrbState s, String m) {
    setState(() { _state = s; _msg = m; });
  }

  void _runDemo() {
    if (_state != OrbState.idle && _state != OrbState.completed) return;
    final steps = <(OrbState, String, Duration)>[
      (OrbState.listening, 'Listening…', const Duration(milliseconds: 800)),
      (OrbState.thinking, 'Thinking…', const Duration(milliseconds: 900)),
      (OrbState.planning, 'Planning your request…', const Duration(milliseconds: 900)),
      (OrbState.executing, 'Executing…', const Duration(milliseconds: 1100)),
      (OrbState.agents, 'Working with my agents…', const Duration(milliseconds: 900)),
      (OrbState.tools, 'Using tools…', const Duration(milliseconds: 800)),
      (OrbState.completed, 'Task completed.\nYour fitness application has been created, Sir.', const Duration(milliseconds: 200)),
    ];
    var acc = Duration.zero;
    for (final (s, m, d) in steps) {
      acc += d;
      Future.delayed(acc, () { if (mounted) _status(s, m); });
    }
  }

  @override
  Widget build(BuildContext context) {
    final dark = Theme.of(context).brightness == Brightness.dark;
    final bg = dark ? RColors.bgDark : RColors.bg;
    return Scaffold(
      backgroundColor: bg,
      body: SafeArea(child: Padding(padding: const EdgeInsets.symmetric(horizontal: 22), child: Column(children: [
        Row(children: const [
          Text('Richard', style: TextStyle(color: RColors.lavenderDeep)),
          SizedBox(width: 6),
          Text('Voice', style: TextStyle(fontSize: 20, fontWeight: FontWeight.w700)),
        ]),
        const Spacer(flex: 2),
        RichardOrb(size: 230, state: _state, progress: _state == OrbState.executing ? 0.7 : 0),
        const Spacer(),
        Text(_msg, textAlign: TextAlign.center, style: TextStyle(fontSize: 16, height: 1.4, color: dark ? Colors.white : RColors.ink)),
        const SizedBox(height: 10),
        Row(mainAxisAlignment: MainAxisAlignment.center, children: [
          Icon(Icons.brightness_low, size: 12, color: _active ? RColors.ok : RColors.inkSoft),
          const SizedBox(width: 4),
          Text(_active ? 'Active listening · "Hey Richard"' : 'Press mic to speak', style: TextStyle(fontSize: 12, color: dark ? Colors.white54 : RColors.inkSoft)),
        ]),
        const Spacer(flex: 2),
        // mic
        GestureDetector(
          onTap: () { setState(() => _active = !_active); if (_active) _runDemo(); },
          child: AnimatedContainer(
            duration: const Duration(milliseconds: 250),
            width: 74, height: 74,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              color: _active ? RColors.ok : RColors.lavenderDeep,
              boxShadow: [BoxShadow(color: (_active ? RColors.ok : RColors.lavenderDeep).withAlpha(90), blurRadius: 22, spreadRadius: 2)],
            ),
            child: Icon(_active ? Icons.mic : Icons.mic_none, color: Colors.white, size: 30),
          ),
        ),
        const SizedBox(height: 26),
      ]))),
    );
  }
}
