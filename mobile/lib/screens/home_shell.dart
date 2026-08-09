import 'package:flutter/material.dart';
import 'home_dashboard.dart';
import 'brain_screen.dart';
import 'voice_screen.dart';
import 'projects_screen.dart';
import 'assistant_screen.dart';
import '../theme.dart';

class HomeShell extends StatefulWidget {
  const HomeShell({super.key});
  @override
  State<HomeShell> createState() => _HomeShellState();
}

class _HomeShellState extends State<HomeShell> {
  int _index = 0;

  late final List<Widget> _screens = [HomeDashboard(onNavigate: (i) => setState(() => _index = i)), BrainScreen(), VoiceScreen(), ProjectsScreen(), AssistantScreen()];
  static const _tabs = [
    (Icons.home_rounded, 'Home'),
    (Icons.hub_rounded, 'Brain'),
    (Icons.graphic_eq_rounded, 'Voice'),
    (Icons.rocket_launch_rounded, 'Projects'),
    (Icons.assistant_rounded, 'Assistant'),
  ];

  @override
  Widget build(BuildContext context) {
    final dark = Theme.of(context).brightness == Brightness.dark;
    return Scaffold(
      backgroundColor: dark ? RColors.bgDark : RColors.bg,
      body: Container(padding: const EdgeInsets.only(bottom: 92), child: IndexedStack(index: _index, children: _screens)),
      floatingActionButtonLocation: FloatingActionButtonLocation.centerFloat,
      floatingActionButton: SafeArea(
        child: Container(
          margin: const EdgeInsets.only(bottom: 8),
          padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
          decoration: BoxDecoration(
            color: dark ? RColors.surfaceDark.withValues(alpha: .92) : Colors.white.withValues(alpha: .96),
            borderRadius: BorderRadius.circular(30),
            border: Border.all(color: RColors.lavender.withValues(alpha: .18)),
            boxShadow: [BoxShadow(color: Colors.black.withValues(alpha: dark ? .4 : .08), blurRadius: 20, offset: const Offset(0, 8))],
          ),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: List.generate(_tabs.length, (i) {
              final selected = i == _index;
              final (icon, label) = _tabs[i];
              return GestureDetector(
                onTap: () => setState(() => _index = i),
                child: AnimatedContainer(
                  duration: const Duration(milliseconds: 220),
                  curve: Curves.easeOut,
                  margin: const EdgeInsets.symmetric(horizontal: 3),
                  padding: EdgeInsets.symmetric(horizontal: selected ? 16 : 12, vertical: 10),
                  decoration: BoxDecoration(
                    color: selected ? RColors.accent.withValues(alpha: .18) : Colors.transparent,
                    borderRadius: BorderRadius.circular(22),
                    border: selected ? Border.all(color: RColors.accent.withValues(alpha: .55)) : null,
                  ),
                  child: Row(mainAxisSize: MainAxisSize.min, children: [
                    Icon(icon, size: 20, color: selected ? RColors.accent : (dark ? Colors.white38 : RColors.inkSoft)),
                    if (selected) ...[
                      const SizedBox(width: 6),
                      Text(label, style: const TextStyle(color: RColors.accent, fontSize: 12, fontWeight: FontWeight.w700)),
                    ],
                  ]),
                ),
              );
            }),
          ),
        ),
      ),
    );
  }
}
