import 'package:flutter/material.dart';
import '../theme.dart';

class ProjectsScreen extends StatelessWidget {
  const ProjectsScreen({super.key});
  @override
  Widget build(BuildContext context) {
    final active = [
      {'t': 'Fitness App', 's': 'Building…', 'p': 0.72},
      {'t': '3D Product Design', 's': 'Rendering…', 'p': 0.55},
      {'t': 'Android Game', 's': 'Testing…', 'p': 0.38},
    ];
    final done = ['Portfolio Website', 'Security Analysis'];
    return Scaffold(
      backgroundColor: RColors.bg,
      body: SafeArea(child: ListView(padding: const EdgeInsets.all(22), children: [
        const Text('Projects', style: TextStyle(fontSize: 24, fontWeight: FontWeight.w800)),
        const SizedBox(height: 18),
        const Text('ACTIVE', style: TextStyle(fontSize: 12, color: RColors.inkSoft, letterSpacing: 1.2)),
        const SizedBox(height: 10),
        ...active.map((p) => Container(margin: const EdgeInsets.only(bottom: 12), padding: const EdgeInsets.all(16), decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(18), boxShadow: [BoxShadow(color: Colors.black.withValues(alpha: .05), blurRadius: 10)]), child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Row(children: [Text(p.$1, style: const TextStyle(fontWeight: FontWeight.w700)), const Spacer(), Text(p.$2, style: const TextStyle(fontSize: 12, color: RColors.lavenderDeep))]),
          const SizedBox(height: 10),
          ClipRRect(borderRadius: BorderRadius.circular(6), child: LinearProgressIndicator(value: p.$3, minHeight: 6, backgroundColor: RColors.lavender.withValues(alpha: .2), color: RColors.lavenderDeep)),
          const SizedBox(height: 6),
          Text('${(p.$3 * 100).round()}%', style: TextStyle(fontSize: 12, color: RColors.inkSoft)),
        ])),
        const SizedBox(height: 8),
        const Text('COMPLETED', style: TextStyle(fontSize: 12, color: RColors.inkSoft, letterSpacing: 1.2)),
        const SizedBox(height: 8),
        ...done.map((d) => Container(margin: const EdgeInsets.only(bottom: 10), padding: const EdgeInsets.all(14), decoration: BoxDecoration(borderRadius: BorderRadius.circular(14), color: Colors.white), child: Row(children: [const Icon(Icons.check_circle, color: RColors.ok, size: 18), const SizedBox(width: 8), Text(d)]))),
      ])),
    );
  }
}
