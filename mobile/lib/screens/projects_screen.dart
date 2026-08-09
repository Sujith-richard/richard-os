
import 'package:flutter/material.dart';
import '../theme.dart';
class ProjectsScreen extends StatelessWidget {
  const ProjectsScreen({super.key});
  @override Widget build(BuildContext context) {
    final active = <Map<String, Object>>[
      {'t': 'Fitness App', 's': 'Building…', 'p': 0.72},
      {'t': '3D Product Design', 's': 'Rendering…', 'p': 0.55},
      {'t': 'Android Game', 's': 'Testing…', 'p': 0.38},
    ];
    final done = ['Portfolio Website', 'Security Analysis'];
    return Scaffold(
      backgroundColor: Theme.of(context).scaffoldBackgroundColor,
      body: SafeArea(child: ListView(padding: const EdgeInsets.all(22), children: [
        const Text('Projects', style: TextStyle(fontSize: 24, fontWeight: FontWeight.w800)),
        const SizedBox(height: 18),
        const Text('ACTIVE', style: TextStyle(fontSize: 12, color: RColors.inkSoft, letterSpacing: 1.2)),
        const SizedBox(height: 10),
        ...active.map((item) => Container(margin: const EdgeInsets.only(bottom: 12), padding: const EdgeInsets.all(16), decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(18), boxShadow: [BoxShadow(color: Colors.black26, blurRadius: 10)]), child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Row(children: [Text('${item['t']}', style: const TextStyle(fontWeight: FontWeight.w700)), const Spacer(), Text('${item['s']}', style: const TextStyle(fontSize: 12, color: RColors.lavenderDeep))]),
          const SizedBox(height: 10),
          ClipRRect(borderRadius: BorderRadius.circular(6), child: LinearProgressIndicator(value: (item['p'] as num).toDouble(), minHeight: 6, backgroundColor: RColors.lavender, color: RColors.lavenderDeep)),
          const SizedBox(height: 6),
          Text('${((item['p'] as num) * 100).round()}%', style: const TextStyle(fontSize: 12, color: RColors.inkSoft)),
        ]))),
        const SizedBox(height: 8),
        const Text('COMPLETED', style: TextStyle(fontSize: 12, color: RColors.inkSoft, letterSpacing: 1.2)),
        const SizedBox(height: 8),
        ...done.map((d) => Container(margin: const EdgeInsets.only(bottom: 10), padding: const EdgeInsets.all(14), decoration: BoxDecoration(borderRadius: BorderRadius.circular(14), color: Colors.white), child: Row(children: [const Icon(Icons.check_circle, color: RColors.ok, size: 18), const SizedBox(width: 8), Text(d)]))),
      ])),
    );
  }
}
