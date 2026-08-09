
import 'package:flutter/material.dart';
import '../theme.dart';
import '../api_client.dart';

String? _endpoint(String label) => switch (label) {
      'Home Assistant' => '/api/v1/home/state',
      'Memory' => '/api/v1/memory/counts',
      'Tasks' => '/api/v1/tasks/assignments',
      'Automations' => '/api/v1/automations',
      'Mobile' => '/api/v1/devices',
      _ => null,
    };

class AssistantScreen extends StatelessWidget {
  const AssistantScreen({super.key});

  static const _modules = <(String, IconData)>[
    ('Calendar', Icons.calendar_month),
    ('Email', Icons.mail_outline),
    ('Tasks', Icons.task_alt),
    ('Notes', Icons.sticky_note_2_outlined),
    ('Reminders', Icons.alarm),
    ('Finance', Icons.account_balance_wallet_outlined),
    ('Travel', Icons.flight_takeoff),
    ('Shopping', Icons.shopping_bag_outlined),
    ('Mobile', Icons.phone_android),
    ('Home Assistant', Icons.home_work),
  ];

  static const _items = <(String, IconData)>[
    ('Calendar', Icons.calendar_month),
    ('Email', Icons.mail_outline),
    ('Tasks', Icons.task_alt),
    ('Notes', Icons.sticky_note_2_outlined),
    ('Reminders', Icons.alarm),
    ('Finance', Icons.account_balance_wallet_outlined),
    ('Travel', Icons.flight_takeoff),
    ('Shopping', Icons.shopping_bag_outlined),
    ('Mobile', Icons.phone_android),
    ('Home Assistant', Icons.home_work),
  ];

  @override
  Widget build(BuildContext context) {
    final dark = Theme.of(context).brightness == Brightness.dark;
    return Scaffold(
      backgroundColor: dark ? RColors.bgDark : RColors.bg,
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsets.fromLTRB(20, 14, 20, 120),
          children: [
            Text('Personal Assistant', style: TextStyle(fontSize: 24, fontWeight: FontWeight.w800, color: dark ? Colors.white : RColors.ink)),
            const SizedBox(height: 6),
            Text('An extension of the Richard Brain', style: TextStyle(fontSize: 13, color: dark ? Colors.white54 : RColors.inkSoft)),
            const SizedBox(height: 18),
            GridView.count(
              crossAxisCount: 2,
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              mainAxisSpacing: 12,
              crossAxisSpacing: 12,
              childAspectRatio: 1.35,
              children: _modules.map((m) => _ModuleCard(icon: m.$2, label: m.$1, dark: dark)).toList(),
            ),
          ],
        ),
      ),
    );
  }
}

class _ModuleCard extends StatelessWidget {
  const _ModuleCard({required this.icon, required this.label, required this.dark});
  final IconData icon; final String label; final bool dark;

  @override
  Widget build(BuildContext context) {
    return InkWell(
      borderRadius: BorderRadius.circular(20),
      onTap: () async {
        try {
          final api = _endpoint(label);
          if (api != null) {
            final r = await RichardApi.I.get(api);
            if (!context.mounted) return;
            showDialog(context: context, builder: (_) => AlertDialog(title: Text(label), content: Text(r.toString()), actions: [TextButton(onPressed: () => Navigator.pop(context), child: const Text('OK'))]));
          } else {
            ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('$label — coming soon in Richard Brain'), duration: const Duration(milliseconds: 900), behavior: SnackBarBehavior.floating));
          }
        } catch (_) {}
              },
      child: Ink(
        padding: const EdgeInsets.all(14),
        decoration: BoxDecoration(
          color: dark ? RColors.surfaceDark.withValues(alpha: .55) : Colors.white.withValues(alpha: .92),
          borderRadius: BorderRadius.circular(20),
          border: Border.all(color: RColors.lavender.withValues(alpha: dark ? .18 : .12)),
        ),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Container(width: 42, height: 42, decoration: BoxDecoration(gradient: RColors.appGrad, borderRadius: BorderRadius.circular(14)), child: Icon(icon, color: Colors.white, size: 20)),
            const SizedBox(height: 10),
            Text(label, textAlign: TextAlign.center, style: TextStyle(fontWeight: FontWeight.w700, fontSize: 13, color: dark ? Colors.white : RColors.ink)),
            const SizedBox(height: 4),
            Row(mainAxisAlignment: MainAxisAlignment.center, children: [
              Container(width: 5, height: 5, decoration: const BoxDecoration(shape: BoxShape.circle, color: RColors.ok)),
              const SizedBox(width: 4),
              Text('ready', style: TextStyle(fontSize: 10, color: dark ? Colors.white38 : RColors.inkSoft)),
            ]),
          ],
        ),
      ),
    );
  }
}
