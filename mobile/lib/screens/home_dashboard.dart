
import 'package:flutter/material.dart';
import '../theme.dart';
class HomeDashboard extends StatelessWidget {
  const HomeDashboard({super.key});
  @override Widget build(BuildContext context) {
    final dark = Theme.of(context).brightness == Brightness.dark;
    final actions = <(IconData, String, String)>[
      (Icons.folder_open, 'Create Project', 'Start a build'),
      (Icons.image_search, 'Analyze Image', 'Vision'),
      (Icons.play_circle, 'Run Workflow', 'Automation'),
      (Icons.manage_search, 'Research', 'Repos & web'),
      (Icons.alarm, 'Set Reminder', 'Assistant'),
      (Icons.translate, 'Translate', 'Language'),
      (Icons.home_work, 'Control Home', 'Smart home'),
      (Icons.phone_iphone, 'Control Mobile', 'Phone'),
    ];
    return Scaffold(
      backgroundColor: dark ? RColors.bgDark : RColors.bg,
      body: SafeArea(child: ListView(padding: const EdgeInsets.all(22), children: [
        Row(children: [
          const CircleAvatar(radius: 24, backgroundColor: RColors.lavender, child: Icon(Icons.person, color: RColors.lavenderDeep)),
          const SizedBox(width: 12),
          Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            const Text('Welcome Back, Sir', style: TextStyle(fontSize: 20, fontWeight: FontWeight.w700)),
            Text('Good Morning. How may I assist you today?', style: TextStyle(fontSize: 13, color: dark ? Colors.white60 : RColors.inkSoft)),
          ]),
        ]),
        const SizedBox(height: 18),
        Row(children: [
          const Icon(Icons.blur_circular, size: 16, color: RColors.ok),
          const SizedBox(width: 6),
          Text('Richard AI  Online  Local-first mode', style: TextStyle(fontSize: 12, color: dark ? Colors.white60 : RColors.inkSoft)),
        ]),
        const SizedBox(height: 18),
        GridView.count(crossAxisCount: 2, shrinkWrap: true, physics: const NeverScrollableScrollPhysics(), mainAxisSpacing: 14, crossAxisSpacing: 14, childAspectRatio: 1.35,
          children: actions.map((c) => _QuickCard(icon: c.$1, title: c.$2, sub: c.$3)).toList()),
      ])),
    );
  }
}
class _QuickCard extends StatelessWidget {
  const _QuickCard({required this.icon, required this.title, required this.sub});
  final IconData icon; final String title; final String sub;
  @override Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(22), boxShadow: [BoxShadow(color: Colors.black26, blurRadius: 12, offset: const Offset(0, 4))]),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Container(width: 34, height: 34, decoration: BoxDecoration(color: RColors.lavender, borderRadius: BorderRadius.circular(10)), child: Icon(icon, size: 18, color: RColors.lavenderDeep)),
        const Spacer(),
        Text(title, style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w600)),
        Text(sub, style: const TextStyle(fontSize: 11, color: RColors.inkSoft)),
      ]),
    );
  }
}
