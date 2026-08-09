
import 'package:flutter/material.dart';
import '../theme.dart';
class AssistantScreen extends StatelessWidget {
  const AssistantScreen({super.key});
  @override Widget build(BuildContext context) {
    final items = ['Calendar', 'Email', 'Tasks', 'Notes', 'Reminders', 'Finance', 'Travel', 'Shopping', 'Mobile', 'Home Assistant'];
    return Scaffold(
      backgroundColor: Theme.of(context).scaffoldBackgroundColor,
      body: SafeArea(child: ListView(padding: const EdgeInsets.all(22), children: [
        const Text('Personal Assistant', style: TextStyle(fontSize: 24, fontWeight: FontWeight.w800)),
        const SizedBox(height: 8),
        const Text('An extension of the Richard Brain', style: TextStyle(fontSize: 13, color: RColors.inkSoft)),
        const SizedBox(height: 18),
        GridView.count(crossAxisCount: 2, shrinkWrap: true, physics: const NeverScrollableScrollPhysics(), mainAxisSpacing: 14, crossAxisSpacing: 14, childAspectRatio: 1.5,
          children: items.map<Widget>((it) => Container(decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(18)), child: Center(child: Text(it, style: const TextStyle(fontWeight: FontWeight.w600))))).toList()),
      ])),
    );
  }
}
