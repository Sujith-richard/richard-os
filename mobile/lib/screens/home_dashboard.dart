
import 'package:flutter/material.dart';
import '../theme.dart';
import 'settings_screen.dart';
import '../widgets/richard_orb.dart';

class HomeDashboard extends StatelessWidget {
  const HomeDashboard({super.key, this.onNavigate});
  final ValueChanged<int>? onNavigate;

  static const _actions = <(IconData, String)>[
    (Icons.folder_open, 'Build'),
    (Icons.image_search, 'Vision'),
    (Icons.play_circle, 'Workflow'),
    (Icons.manage_search, 'Research'),
    (Icons.home_work, 'Home'),
    (Icons.phone_iphone, 'Phone'),
    (Icons.memory, 'Memory'),
    (Icons.settings_suggest, 'Automate'),
  ];

  @override
  Widget build(BuildContext context) {
    final dark = Theme.of(context).brightness == Brightness.dark;
    return Scaffold(
      backgroundColor: dark ? RColors.bgDark : RColors.bg,
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsets.fromLTRB(20, 12, 20, 120),
          children: [
            // header
            Row(children: [
              Container(
                decoration: BoxDecoration(shape: BoxShape.circle, gradient: RColors.appGrad),
                child: const CircleAvatar(radius: 18, backgroundColor: Colors.transparent, child: Icon(Icons.person, color: Colors.white, size: 20)),
              ),
              const SizedBox(width: 12),
              Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                Text('Welcome Back, Sir', style: TextStyle(fontSize: 19, fontWeight: FontWeight.w800, color: dark ? Colors.white : RColors.ink)),
                Text('Good Morning — ask Richard, or start a build.', style: TextStyle(fontSize: 12, color: dark ? Colors.white60 : RColors.inkSoft)),
              ])),
            ]),
            const SizedBox(height: 16),
            // brain hero
            Material(
              color: Colors.transparent,
              child: InkWell(
                onTap: () => onNavigate?.call(1),
                borderRadius: BorderRadius.circular(22),
                child: Ink(
                  padding: const EdgeInsets.all(14),
                  decoration: BoxDecoration(
                    borderRadius: BorderRadius.circular(22),
                    gradient: LinearGradient(colors: [RColors.lavenderDeep.withValues(alpha: .22), RColors.accent.withValues(alpha: .10), Colors.transparent]),
                    border: Border.all(color: RColors.lavender.withValues(alpha: .25)),
                  ),
                  child: Row(children: [
                    const SizedBox(width: 56, height: 56, child: RichardOrb(size: 56, state: OrbState.idle)),
                    const SizedBox(width: 14),
                    Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                      Text('Richard Brain', style: TextStyle(fontWeight: FontWeight.w800, fontSize: 15, color: dark ? Colors.white : RColors.ink)),
                      const SizedBox(height: 3),
                      Row(children: [Container(width: 6, height: 6, decoration: BoxDecoration(shape: BoxShape.circle, color: RColors.ok)), const SizedBox(width: 6), Text('Online · Local-first', style: TextStyle(color: RColors.ok, fontSize: 11, fontWeight: FontWeight.w600))]),
                    ])),
                    Icon(Icons.chevron_right_rounded, color: dark ? RColors.lavender : RColors.lavenderDeep),
                  ]),
                ),
              ),
            ),
            const SizedBox(height: 20),
            Text('Quick actions', style: TextStyle(fontSize: 13, fontWeight: FontWeight.w700, color: dark ? Colors.white70 : RColors.inkSoft)),
            const SizedBox(height: 10),
            GridView.count(
              crossAxisCount: 3,
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              mainAxisSpacing: 12,
              crossAxisSpacing: 12,
              childAspectRatio: 2.2,
              children: _actions.asMap().entries.map((e) {
                final tab = switch (e.key) { 0 => 3, 1 => 2, 2 => 2, 3 => 1, 4 => 4, 5 => 4, 6 => 1, _ => 4 };
                final a = e.value;
                return _QuickAction(icon: a.$1, label: a.$2, dark: dark, onTap: () {
              // visible: open a dialog with the action
              showDialog(context: context, builder: (_) => AlertDialog(
                title: Text(a.$2),
                content: const Text('Routing to Richard Brain…'),
                actions: [ TextButton(onPressed: () => Navigator.pop(context), child: const Text('OK')) ],
              ));
              onNavigate?.call(tab);
            });
              }).toList(),
            ),
            const SizedBox(height: 16),
            Material(
              color: Colors.transparent,
              child: InkWell(
                onTap: () => Navigator.push(context, MaterialPageRoute(builder: (_) => const SettingsScreen())),
                borderRadius: BorderRadius.circular(18),
                child: Ink(
                  padding: const EdgeInsets.all(14),
                  decoration: BoxDecoration(color: dark ? RColors.surfaceDark.withValues(alpha: .55) : Colors.white.withValues(alpha: .92), borderRadius: BorderRadius.circular(18), border: Border.all(color: RColors.lavender.withValues(alpha: dark ? .18 : .12))),
                  child: Row(children: [
                    const Icon(Icons.settings_rounded, color: RColors.lavenderDeep),
                    const SizedBox(width: 12),
                    Text('Settings', style: TextStyle(fontWeight: FontWeight.w700, fontSize: 14, color: dark ? Colors.white : RColors.ink)),
                    const Spacer(),
                    const Icon(Icons.chevron_right_rounded, color: RColors.inkSoft),
                  ]),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _QuickAction extends StatelessWidget {
  const _QuickAction({required this.icon, required this.label, required this.dark, required this.onTap});
  final IconData icon; final String label; final bool dark; final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: () {
          // tap handled (future: route to Brain) 
        },
        borderRadius: BorderRadius.circular(20),
        child: Ink(
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: dark ? RColors.surfaceDark.withValues(alpha: .6) : Colors.white.withValues(alpha: .92),
            borderRadius: BorderRadius.circular(20),
            border: Border.all(color: RColors.lavender.withValues(alpha: dark ? .18 : .12)),
          ),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(mainAxisAlignment: MainAxisAlignment.center, children: [
                Icon(icon, size: 15, color: dark ? RColors.lavender : RColors.lavenderDeep),
                const SizedBox(width: 6),
                Text(label, style: TextStyle(fontSize: 11, fontWeight: FontWeight.w700, color: dark ? Colors.white : RColors.ink)),
              ]),
            ],
          ),
        ),
      ),
    );
  }
}
