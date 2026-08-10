
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
  bool _listening = false;


  final _ctrl = TextEditingController();
  final _scroll = ScrollController();
  final _msgs = <({bool me, String text})>[];
  OrbState _state = OrbState.idle;
  String _msg = 'Welcome, Sir. What can I do for you?';
  bool _active = false;

  void _cycle(OrbState s, String m) => setState(() { _state = s; _msg = m; });

  Future<void> _runApi(String text) async {
    final t = text.trim();
    if (t.isEmpty) return;
    setState(() { _msgs.add((me: true, text: t)); });
    _ctrl.clear();
    _cycle(OrbState.listening, 'Listening…');
    await Future.delayed(const Duration(milliseconds: 600));
    _cycle(OrbState.thinking, 'Thinking…');
    String reply = 'Done, Sir.';
    try {
      final r = await RichardApi.I.voice(t);
      reply = (r['reply'] as String?) ?? 'Done, Sir.';
    } catch (_) {}
    setState(() { _msgs.add((me: false, text: reply)); });
    _cycle(OrbState.completed, reply);
    await Future.delayed(const Duration(milliseconds: 400));
    _scrollToBottom();
    await Future.delayed(const Duration(seconds: 2));
    _cycle(OrbState.idle, 'Welcome, Sir.');
  }

  void _scrollToBottom() {
    Future.delayed(const Duration(milliseconds: 120), () {
      if (_scroll.hasClients) _scroll.jumpTo(_scroll.position.maxScrollExtent);
    });
  }

  void _runDemo() {
    if (_state != OrbState.idle && _state != OrbState.completed) return;
    _runApi('turn on the bedroom light');
  }

  @override void dispose() { _ctrl.dispose(); _scroll.dispose(); super.dispose(); }

  @override Widget build(BuildContext context) {
    final dark = Theme.of(context).brightness == Brightness.dark;
    final bg = dark ? RColors.bgDark : RColors.bg;
    return Scaffold(
      backgroundColor: bg,
      body: SafeArea(child: Padding(padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 10), child: Column(children: [
        Row(mainAxisAlignment: MainAxisAlignment.center, children: [
          Text('Richard', style: TextStyle(color: dark ? RColors.lavender : RColors.lavenderDeep, fontSize: 20, fontWeight: FontWeight.w700)),
          const SizedBox(width: 6),
          Text('Voice', style: TextStyle(fontSize: 20, fontWeight: FontWeight.w700, color: dark ? Colors.white : RColors.ink)),
        ]),
        const SizedBox(height: 6),
        Expanded(child: _msgs.isEmpty
          ? Center(child: RichardOrb(size: 220, state: _state, progress: _state == OrbState.executing ? 0.7 : 0))
          : ListView.builder(
              controller: _scroll,
              padding: const EdgeInsets.symmetric(vertical: 10),
              itemCount: _msgs.length,
              itemBuilder: (_, i) => _bubble(_msgs[i], dark),
            )),
        const SizedBox(height: 6),
        Text(_msg, textAlign: TextAlign.center, style: TextStyle(fontSize: 15, height: 1.3, color: dark ? Colors.white : RColors.ink)),
        const SizedBox(height: 8),
        Row(mainAxisAlignment: MainAxisAlignment.center, children: [
          _chip(Icons.hearing, 'Wake: "hey richard"', dark),
          const SizedBox(width: 8),
          _chip(Icons.privacy_tip_outlined, _active ? 'Listening' : 'Privacy', dark),
        ]),
        const SizedBox(height: 12),
        Row(children: [
          GestureDetector(
            onTap: () {
                setState(() => _active = !_active);
                if (_active) _cycle(OrbState.listening, 'Tap again to send');
                else _cycle(OrbState.idle, 'Welcome, Sir.');
              },
            child: AnimatedContainer(duration: const Duration(milliseconds: 250), width: 60, height: 60,
              decoration: BoxDecoration(shape: BoxShape.circle, color: _active ? RColors.ok : RColors.lavenderDeep,
                boxShadow: [BoxShadow(color: (_active ? RColors.ok : RColors.lavenderDeep).withValues(alpha: .35), blurRadius: 22, spreadRadius: 2)]),
              child: const Icon(Icons.mic, color: Colors.white, size: 26)),
          ),
          const SizedBox(width: 14),
          Expanded(
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 4),
              decoration: RColors.glass(dark: dark, radius: 26),
              child: TextField(
                controller: _ctrl,
                style: TextStyle(color: dark ? Colors.white : RColors.ink),
                decoration: InputDecoration(
                  hintText: 'Type a command…',
                  hintStyle: TextStyle(fontSize: 13, color: dark ? Colors.white38 : RColors.inkSoft),
                  border: InputBorder.none, isDense: true,
                ),
                onSubmitted: _runApi,
              ),
            ),
          ),
          const SizedBox(width: 6),
          IconButton(onPressed: () => _runApi(_ctrl.text), icon: const Icon(Icons.send_rounded, color: RColors.lavenderDeep)),
        ]),
        const SizedBox(height: 12),
      ]))),
    );
  }

  Widget _bubble(({bool me, String text}) m, bool dark) {
    final isMe = m.me;
    return Align(
      alignment: isMe ? Alignment.centerRight : Alignment.centerLeft,
      child: Container(
        margin: const EdgeInsets.symmetric(vertical: 3),
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 9),
        constraints: const BoxConstraints(maxWidth: 250),
        decoration: BoxDecoration(
          color: isMe ? RColors.lavenderDeep : (dark ? RColors.surfaceDark : Colors.white),
          borderRadius: BorderRadius.only(
            topLeft: const Radius.circular(18), topRight: const Radius.circular(18),
            bottomLeft: Radius.circular(isMe ? 18 : 4), bottomRight: Radius.circular(isMe ? 4 : 18),
          ),
        ),
        child: Text(m.text, style: TextStyle(color: isMe ? Colors.white : (dark ? Colors.white : RColors.ink), fontSize: 14)),
      ),
    );
  }

  Widget _chip(IconData ic, String t, bool dark) => Container(
        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
        decoration: BoxDecoration(borderRadius: BorderRadius.circular(20), border: Border.all(color: RColors.lavender.withValues(alpha: .5), width: .8)),
        child: Row(mainAxisSize: MainAxisSize.min, children: [
          Icon(ic, size: 13, color: dark ? RColors.lavender : RColors.lavenderDeep),
          const SizedBox(width: 4),
          Text(t, style: TextStyle(fontSize: 11, color: dark ? Colors.white70 : RColors.ink)),
        ]),
      );
}
