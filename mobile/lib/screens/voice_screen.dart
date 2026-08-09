
import 'dart:async';
import 'package:flutter/material.dart';
import '../api_client.dart';
import '../theme.dart';
import '../widgets/richard_orb.dart';

class VoiceScreen extends StatefulWidget {
  const VoiceScreen({super.key});
  @override State<VoiceScreen> createState() => _VoiceScreenState();
}

class _VoiceScreenState extends State<VoiceScreen> {
  final _ctrl = TextEditingController();
  OrbState _state = OrbState.idle;
  String _msg = 'Welcome, Sir. What can I do for you?';
  bool _active = false;

  void _cycle(OrbState s, String m) => setState(() { _state = s; _msg = m; });

  Future<void> _runApi(String text) async {
    if (text.trim().isEmpty) return;
    _ctrl.clear();
    _cycle(OrbState.listening, 'Listening…');
    await Future.delayed(const Duration(milliseconds: 600));
    _cycle(OrbState.thinking, 'Thinking…');
    try {
      final r = await RichardApi.I.voice(text);
      _cycle(OrbState.completed, (r['reply'] as String?) ?? 'Done, Sir.');
    } catch (_) {
      _cycle(OrbState.completed, 'Done, Sir.');
    }
    await Future.delayed(const Duration(seconds: 2));
    _cycle(OrbState.idle, 'Welcome, Sir.');
  }

  void _runDemo() async {
    if (_state != OrbState.idle && _state != OrbState.completed) return;
    _cycle(OrbState.listening, 'Listening…');
    await Future.delayed(const Duration(milliseconds: 800));
    _cycle(OrbState.thinking, 'Thinking…');
    await Future.delayed(const Duration(milliseconds: 900));
    _cycle(OrbState.planning, 'Planning your request…');
    await Future.delayed(const Duration(milliseconds: 900));
    _cycle(OrbState.executing, 'Executing…');
    await Future.delayed(const Duration(milliseconds: 1100));
    _cycle(OrbState.agents, 'Working with my agents…');
    await Future.delayed(const Duration(milliseconds: 900));
    _cycle(OrbState.tools, 'Using tools…');
    await Future.delayed(const Duration(milliseconds: 800));
    _cycle(OrbState.completed, 'Task completed.\nYour app is ready, Sir.');
    await _runApi('hey richard turn on the bedroom light');
    _cycle(OrbState.idle, 'Welcome, Sir.');
  }

  @override
  void dispose() { _ctrl.dispose(); super.dispose(); }

  @override
  Widget build(BuildContext context) {
    final dark = Theme.of(context).brightness == Brightness.dark;
    return Scaffold(
      backgroundColor: dark ? RColors.bgDark : RColors.bg,
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 22),
          child: Column(children: [
            const Spacer(flex: 1),
            Row(mainAxisAlignment: MainAxisAlignment.center, children: [
              Text('Richard', style: TextStyle(color: dark ? RColors.lavender : RColors.lavenderDeep, fontSize: 20, fontWeight: FontWeight.w700)),
              const SizedBox(width: 6),
              Text('Voice', style: TextStyle(fontSize: 20, fontWeight: FontWeight.w700, color: dark ? Colors.white : RColors.ink)),
            ]),
            const Spacer(flex: 2),
            RichardOrb(size: 240, state: _state, progress: _state == OrbState.executing ? 0.7 : 0),
            const Spacer(),
            Text(_msg, textAlign: TextAlign.center, style: TextStyle(fontSize: 17, height: 1.4, color: dark ? Colors.white : RColors.ink)),
            const SizedBox(height: 10),
            Row(mainAxisAlignment: MainAxisAlignment.center, children: [
              Icon(Icons.brightness_low, size: 12, color: _active ? RColors.ok : RColors.inkSoft),
              const SizedBox(width: 4),
              Text(_active ? 'Active listening · "Hey Richard"' : 'Press mic, or type below', style: TextStyle(fontSize: 12, color: dark ? Colors.white54 : RColors.inkSoft)),
            ]),
            const SizedBox(height: 26),
            GestureDetector(
              onTap: () { setState(() => _active = !_active); if (_active) _runDemo(); },
              child: AnimatedContainer(duration: const Duration(milliseconds: 250), width: 72, height: 72,
                decoration: BoxDecoration(shape: BoxShape.circle, color: _active ? RColors.ok : RColors.lavenderDeep,
                  boxShadow: [BoxShadow(color: (_active ? RColors.ok : RColors.lavenderDeep).withValues(alpha: .35), blurRadius: 26, spreadRadius: 2)]),
                child: Icon(_active ? Icons.mic : Icons.mic_none, color: Colors.white, size: 28)),
            ),
            const SizedBox(height: 14),
            Row(mainAxisAlignment: MainAxisAlignment.center, children: [
              _chip(Icons.hearing, 'Wake: "hey richard"', dark),
              const SizedBox(width: 8),
              _chip(Icons.privacy_tip_outlined, _active ? 'Listening' : 'Privacy', dark),
            ]),
            const SizedBox(height: 20),
            // chat input box
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 6),
              decoration: RColors.glass(dark: dark, radius: 26),
              child: Row(children: [
                Expanded(child: TextField(
                  controller: _ctrl,
                  style: TextStyle(color: dark ? Colors.white : RColors.ink),
                  decoration: InputDecoration(
                    hintText: 'Type a command… e.g. "build a game"',
                    hintStyle: TextStyle(fontSize: 13, color: dark ? Colors.white38 : RColors.inkSoft),
                    border: InputBorder.none, isDense: true,
                  ),
                  onSubmitted: (t) => _runApi(t),
                )),
                const SizedBox(width: 6),
                IconButton(onPressed: () => _runApi(_ctrl.text), icon: const Icon(Icons.send_rounded, color: RColors.lavenderDeep)),
              ]),
            ),
            const SizedBox(height: 16),
          ]),
        ),
      ),
    );
  }

  Widget _chip(IconData ic, String t, bool dark) => Container(
        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(20),
          border: Border.all(color: RColors.lavender.withValues(alpha: .5), width: .8),
        ),
        child: Row(mainAxisSize: MainAxisSize.min, children: [
          Icon(ic, size: 13, color: dark ? RColors.lavender : RColors.lavenderDeep),
          const SizedBox(width: 4),
          Text(t, style: TextStyle(fontSize: 11, color: dark ? Colors.white70 : RColors.ink)),
        ]),
      );
}
