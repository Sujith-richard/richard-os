import 'package:flutter/material.dart';

class KnowledgeScreen extends StatefulWidget {
  const KnowledgeScreen({super.key});
  @override State<KnowledgeScreen> createState() => _KnowledgeScreenState();
}
class _KnowledgeScreenState extends State<KnowledgeScreen> {
  String q = '';
  @override Widget build(BuildContext context) {
    final cats = ['Conversations', 'Documents', 'Projects', 'Skills', 'Knowledge', 'Memory', 'Repositories', 'Notes'];
    return Scaffold(
      backgroundColor: Theme.of(context).scaffoldBackgroundColor,
      appBar: AppBar(title: const Text('Knowledge & Memory')),
      body: ListView(padding: const EdgeInsets.all(22), children: [
        TextField(
          onChanged: (v) => setState(() => q = v),
          decoration: InputDecoration(hintText: 'Search knowledge & memory…', prefixIcon: const Icon(Icons.search), filled: true, border: OutlineInputBorder(borderRadius: BorderRadius.circular(24), borderSide: BorderSide.none)),
        ),
        const SizedBox(height: 18),
        GridView.count(crossAxisCount: 2, shrinkWrap: true, physics: const NeverScrollableScrollPhysics(), mainAxisSpacing: 14, crossAxisSpacing: 14, childAspectRatio: 1.5, children: cats.map((c) => Container(decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(18)), child: Center(child: Text(c, style: const TextStyle(fontWeight: FontWeight.w600))))).toList()),
      ]),
    );
  }
}
