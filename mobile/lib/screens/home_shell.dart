
import 'package:flutter/material.dart';
import 'home_dashboard.dart';
import 'voice_screen.dart';
import 'brain_screen.dart';
import 'projects_screen.dart';
import 'assistant_screen.dart';

class HomeShell extends StatefulWidget {
  const HomeShell({super.key});
  @override State<HomeShell> createState() => _HomeShellState();
}
class _HomeShellState extends State<HomeShell> {
  int _i = 0;
  final _tabs = const [HomeDashboard(), VoiceScreen(), BrainScreen(), ProjectsScreen(), AssistantScreen()];
  @override Widget build(BuildContext context) {
    return Scaffold(
      body: IndexedStack(index: _i, children: _tabs),
      bottomNavigationBar: Container(
        margin: const EdgeInsets.fromLTRB(16, 0, 16, 14),
        padding: const EdgeInsets.all(6),
        decoration: BoxDecoration(
          color: Colors.white.withValues(alpha: .9),
          borderRadius: BorderRadius.circular(30),
          boxShadow: [BoxShadow(color: Colors.black.withValues(alpha: .08), blurRadius: 18, offset: const Offset(0, 6))],
        ),
        child: NavigationBar(
          backgroundColor: Colors.transparent, elevation: 0, selectedIndex: _i,
          onDestinationSelected: (i) => setState(() => _i = i),
          destinations: const [
            NavigationDestination(icon: Icon(Icons.home_outlined), selectedIcon: Icon(Icons.home, color: Color(0xFF7C3AED)), label: 'Home'),
            NavigationDestination(icon: Icon(Icons.chat_bubble_outline), selectedIcon: Icon(Icons.chat_bubble, color: Color(0xFF7C3AED)), label: 'Chat'),
            NavigationDestination(icon: Icon(Icons.blur_circular), selectedIcon: Icon(Icons.blur_on, color: Color(0xFF7C3AED)), label: 'Brain'),
            NavigationDestination(icon: Icon(Icons.folder_outlined), selectedIcon: Icon(Icons.folder, color: Color(0xFF7C3AED)), label: 'Projects'),
            NavigationDestination(icon: Icon(Icons.person_outline), selectedIcon: Icon(Icons.person, color: Color(0xFF7C3AED)), label: 'Assistant'),
          ],
        ),
      ),
    );
  }
}
