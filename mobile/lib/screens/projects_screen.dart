
import 'package:flutter/material.dart';
import '../theme.dart';

class ProjectsScreen extends StatelessWidget {
  const ProjectsScreen({super.key});
  static const _stages = ['Plan', 'Build', 'Test', 'Ship'];

  Widget _cards(Map<String, Object> item, bool dark) {
    final t = '${item['t']}';
    final s = '${item['s']}';
    final p = (item['p'] as num).toDouble();
    final done = (p * _stages.length).ceil().clamp(0, _stages.length);
    return Container(
      margin: const EdgeInsets.only(bottom: 14),
      padding: const EdgeInsets.all(16),
      decoration: RColors.glass(dark: dark, radius: 20),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Row(children: [Text(t, style: TextStyle(fontWeight: FontWeight.w700, fontSize: 15, color: dark ? Colors.white : RColors.ink)), const Spacer(), Text(s, style: TextStyle(fontSize: 12, color: RColors.accent, fontWeight: FontWeight.w600))]),
        const SizedBox(height: 12),
        ClipRRect(borderRadius: BorderRadius.circular(6), child: LinearProgressIndicator(value: p, minHeight: 6, backgroundColor: RColors.lavender.withValues(alpha: .2), color: RColors.lavenderDeep)),
        const SizedBox(height: 8),
        Row(children: [
          Text('${(p * 100).round()}%', style: TextStyle(fontSize: 12, color: RColors.ok, fontWeight: FontWeight.w700)),
          const Spacer(),
          ...List.generate(_stages.length, (i) {
            final active = i < done;
            return Padding(padding: const EdgeInsets.only(left: 4), child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
              decoration: BoxDecoration(borderRadius: BorderRadius.circular(10), color: active ? RColors.accent.withValues(alpha: .14) : null, border: Border.all(color: active ? RColors.accent.withValues(alpha: .5) : RColors.lavender.withValues(alpha: .25))),
              child: Text(_stages[i], style: TextStyle(fontSize: 10, color: active ? RColors.accent : (dark ? Colors.white38 : RColors.inkSoft))),
            ));
          }),
        ]),
      ]),
    );
  }

  Widget _Chips(Map<String, dynamic> item, bool dark) {
    final t = '${item['t']}';
    final st = '${item['s']}';
    final p = (item['p'] as num).toDouble();
    final doneIdx = (p * _stages.length).ceil().clamp(0, _stages.length);
    return Container(
      margin: const EdgeInsets.only(bottom: 14),
      padding: const EdgeInsets.all(16),
      decoration: RColors.glass(dark: dark, radius: 20),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Row(children: [Text(t, style: TextStyle(fontWeight: FontWeight.w700, fontSize: 15, color: dark ? Colors.white : RColors.ink)), const Spacer(), Text(st, style: TextStyle(fontSize: 12, color: RColors.accent, fontWeight: FontWeight.w600))]),
        const SizedBox(height: 12),
        ClipRRect(borderRadius: BorderRadius.circular(6), child: LinearProgressIndicator(value: p, minHeight: 6, backgroundColor: RColors.lavender.withValues(alpha: .2), color: RColors.lavenderDeep)),
        const SizedBox(height: 8),
        Row(children: [
          Text('${(p * 100).round()}%', style: TextStyle(fontSize: 12, color: RColors.ok, fontWeight: FontWeight.w700)),
          const Spacer(),
          ...List.generate(_stages.length, (i) {
            final active = i < doneIdx;
            return Padding(padding: const EdgeInsets.only(left: 4), child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
              decoration: BoxDecoration(borderRadius: BorderRadius.circular(10), color: active ? RColors.accent.withValues(alpha: .14) : null, border: Border.all(color: active ? RColors.accent.withValues(alpha: .5) : RColors.lavender.withValues(alpha: .25))),
              child: Text(_stages[i], style: TextStyle(fontSize: 10, color: active ? RColors.accent : (dark ? Colors.white38 : RColors.inkSoft))),
            ));
          }),
        ]),
      ]),
    );
  }

  @override
  Widget build(BuildContext context) {
    final dark = Theme.of(context).brightness == Brightness.dark;
    final active = <Map<String, dynamic>>[
      {'t': 'Fitness App', 's': 'Building', 'p': 0.72},
      {'t': '3D Product Design', 's': 'Rendering', 'p': 0.55},
      {'t': 'Android Game', 's': 'Testing', 'p': 0.38},
    ];
    final done = ['Portfolio Website', 'Security Analysis'];
    return Scaffold(
      backgroundColor: dark ? RColors.bgDark : RColors.bg,
      body: SafeArea(child: ListView(padding: const EdgeInsets.fromLTRB(20, 14, 20, 110), children: [
        Text('Projects', style: TextStyle(fontSize: 24, fontWeight: FontWeight.w800, color: dark ? Colors.white : RColors.ink)),
        const SizedBox(height: 6),
        Text('Live execution view', style: TextStyle(fontSize: 13, color: dark ? Colors.white54 : RColors.inkSoft)),
        const SizedBox(height: 20),
        const Text('ACTIVE', style: TextStyle(fontSize: 12, color: Colors.orangeAccent, letterSpacing: 1.2, fontWeight: FontWeight.w700)),
        const SizedBox(height: 10),
        ...active.map((i) => _Chips(i, dark)),
        const SizedBox(height: 6),
        const Text('COMPLETED', style: TextStyle(fontSize: 12, color: RColors.ok, letterSpacing: 1.2, fontWeight: FontWeight.w700)),
        const SizedBox(height: 10),
        ...done.map((d) => Container(margin: const EdgeInsets.only(bottom: 10), padding: const EdgeInsets.all(14), decoration: RColors.glass(dark: dark, radius: 16), child: Row(children: [
          const Icon(Icons.check_circle, color: RColors.ok, size: 16), const SizedBox(width: 8),
          Text(d, style: TextStyle(color: dark ? Colors.white : RColors.ink)),
        ]))),
      ])),
    );
  }
}
