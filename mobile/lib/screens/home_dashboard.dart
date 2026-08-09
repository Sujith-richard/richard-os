
import 'package:flutter/material.dart';
import '../theme.dart';
import '../widgets/richard_orb.dart';

class HomeDashboard extends StatefulWidget {
  const HomeDashboard({super.key});
  @override State<HomeDashboard> createState() => _HomeDashboardState();
}
class _HomeDashboardState extends State<HomeDashboard> {
  final _actions = <(IconData, String)>[
    (Icons.folder_open, 'Start a Build'),
    (Icons.image_search, 'Vision'),
    (Icons.play_circle, 'Run Workflow'),
    (Icons.manage_search, 'Research'),
    (Icons.home_work, 'Smart home'),
    (Icons.phone_iphone, 'Phone'),
    (Icons.memory, 'Memory'),
    (Icons.settings_suggest, 'Automations'),
  ];
  @override Widget build(BuildContext context) {
    final dark = Theme.of(context).brightness == Brightness.dark;
    return Scaffold(
      backgroundColor: dark ? RColors.bgDark : RColors.bg,
      body: SafeArea(child: ListView(padding: const EdgeInsets.all(20), children: [
        // header
        Row(children: [
          Container(decoration: BoxDecoration(shape: BoxShape.circle, gradient: RColors.appGrad, boxShadow: [BoxShadow(color: RColors.lavender.withValues(alpha: .4), blurRadius: 12)]),
            child: const CircleAvatar(radius: 20, backgroundColor: Colors.transparent, child: Icon(Icons.person, color: Colors.white))),
          const SizedBox(width: 12),
          Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            const Text('Welcome Back, Sir', style: TextStyle(fontSize: 20, fontWeight: FontWeight.w800)),
            Text('Good Morning — ask Richard, or start a build.', style: TextStyle(fontSize: 13, color: dark ? Colors.white60 : RColors.inkSoft)),
          ])),
        ]),
        const SizedBox(height: 14),
        // brain pulse card
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(24),
            gradient: LinearGradient(colors: [RColors.lavender.withValues(alpha: .18), RColors.accent.withValues(alpha: .10), RColors.bgDark.withValues(alpha: .04)]),
          ),
          child: Row(children: [
            const SizedBox(width: 64, height: 64, child: RichardOrb(size: 64, state: OrbState.idle)),
            const SizedBox(width: 14),
            Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
              const Text('Richard Brain', style: TextStyle(fontWeight: FontWeight.w800, fontSize: 16)),
              const SizedBox(height: 4),
              Text('● Online  ·  Local-first', style: TextStyle(color: RColors.ok, fontSize: 12)),
              const SizedBox(height: 6),
              Text('Ask "build a fitness app" or delegate to an agent.', style: TextStyle(fontSize: 12, color: dark ? Colors.white70 : RColors.inkSoft)),
            ])),
            const Icon(Icons.chevron_right, color: RColors.lavenderDeep),
          ]),
        ),
        const SizedBox(height: 18),
        Text('Quick actions', style: TextStyle(fontSize: 13, fontWeight: FontWeight.w700, color: dark ? Colors.white70 : RColors.inkSoft)),
        const SizedBox(height: 10),
        GridView.count(crossAxisCount: 2, shrinkWrap: true, physics: const NeverScrollableScrollPhysics(), mainAxisSpacing: 14, crossAxisSpacing: 14, childAspectRatio: 1.3,
          children: _actions.map((a) => Container(
            padding: const EdgeInsets.all(14),
            decoration: BoxDecoration(color: Colors.white.withValues(alpha: .92), borderRadius: BorderRadius.circular(22), boxShadow: [BoxShadow(color: Colors.black.withValues(alpha: .05), blurRadius: 12, offset: const Offset(0, 4))]),
            child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
              Container(width: 34, height: 34, decoration: BoxDecoration(color: RColors.lavender.withValues(alpha: .16), borderRadius: BorderRadius.circular(10)), child: Icon(a.$1, size: 18, color: RColors.lavenderDeep)),
              const Spacer(),
              Text(a.$2, style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 14)),
            ]),
          )).toList()),
      ])),
    );
  }
}
