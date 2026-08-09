import 'package:flutter/material.dart';
import '../theme.dart';

class SkillsScreen extends StatefulWidget {
  const SkillsScreen({super.key});
  @override State<SkillsScreen> createState() => _SkillsScreenState();
}
class _SkillsScreenState extends State<SkillsScreen> {
  final skills = <Map<String, String>>[
    {'n': 'Web Development', 'd': 'Frontend/backend conventions', 'dept': 'Web', 'v': '1.1.0'},
    {'n': 'Security Analysis', 'd': 'OWASP patterns, secret scan', 'dept': 'Cyber', 'v': '1.0.3'},
    {'n': 'Research', 'd': 'Repo + knowledge retrieval', 'dept': 'General', 'v': '1.0.0'},
    {'n': '3D Design', 'd': 'Blender/FreeCAD pipelines', 'dept': 'Design', 'v': '0.9.1'},
    {'n': 'Data Analysis', 'd': 'Pandas, SQL, viz', 'dept': 'Data', 'v': '1.0.0'},
    {'n': 'Image Analysis', 'd': 'Vision models, OCR', 'dept': 'AI', 'v': '1.0.2'},
  ];
  @override Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Theme.of(context).scaffoldBackgroundColor,
      appBar: AppBar(title: const Text('Skills')),
      body: ListView(padding: const EdgeInsets.all(22), children: skills.map((sk) => Container(margin: const EdgeInsets.only(bottom: 12), padding: const EdgeInsets.all(14), decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(18)), child: Row(children: [
        Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Text(sk['n']!, style: const TextStyle(fontWeight: FontWeight.w700)),
          Text(sk['d']!, style: TextStyle(fontSize: 12, color: RColors.inkSoft)),
          Text('${sk['i']!} · v${sk['v']!}', style: TextStyle(fontSize: 11, color: RColors.inkSoft)),
        ])),
        Switch(value: true, onChanged: (_) {}),
      ]))).toList()),
    );
  }
}
