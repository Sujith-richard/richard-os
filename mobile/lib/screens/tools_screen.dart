import 'package:flutter/material.dart';
import '../theme.dart';

class ToolsScreen extends StatelessWidget {
  const ToolsScreen({super.key});
  @override Widget build(BuildContext context) {
    final tools = <String, String>{
      'MCP Servers': 'Connected', 'Plugins': 'Community', 'GitHub': 'Live', 'Docker': 'Live',
      'APIs': 'Configured', 'Home Assistant': 'Simulated', 'Mobile Tools': 'Remote', 'Repo Tools': 'Intel',
    };
    return Scaffold(
      backgroundColor: Theme.of(context).scaffoldBackgroundColor,
      appBar: AppBar(title: const Text('Tools & MCP')),
      body: ListView(padding: const EdgeInsets.all(22), children: tools.entries.map((e) => ListTile(leading: Icon(_ic(e.key), color: RColors.lavenderDeep), title: Text(e.key), trailing: Text(e.value, style: TextStyle(fontSize: 12, color: e.value == 'Connected' || e.value == 'Live' ? RColors.ok : RColors.warn)), style: ListTileStyle.list)).toList()),
    );
  }
  IconData _ic(String s) => switch (s) {
    'MCP Servers' => Icons.extension, 'Plugins' => Icons.widgets, 'GitHub' => Icons.code,
    'Docker' => Icons.sailing, 'APIs' => Icons.api, 'Home Assistant' => Icons.home_work,
    'Mobile Devices' => Icons.phone_android, _ => Icons.folder,
  };
}
