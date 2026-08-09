import 'package:flutter/material.dart';
import '../theme.dart';

class SecurityScreen extends StatelessWidget {
  const SecurityScreen({super.key});
  @override
  Widget build(BuildContext context) {
    final checks = [
      'API Key Protection', 'Vault', 'Permissions', 'Audit', 'Project Security',
      'MCP Permissions', 'Plugin Permissions', 'Secrets Scan', 'SQL Injection', 'XSS',
    ];
    return Scaffold(
      backgroundColor: Theme.of(context).scaffoldBackgroundColor,
      appBar: AppBar(title: const Text('Security')),
      body: ListView(padding: const EdgeInsets.all(22), children: [
        const Text('System Security', style: TextStyle(fontSize: 20, fontWeight: FontWeight.w800)),
        const SizedBox(height: 12),
        for (final c in checks) ListTile(
          leading: const Icon(Icons.shield_outlined, color: RColors.ok),
          title: Text(c), trailing: const Icon(Icons.check_circle, color: RColors.ok),
        ),
      ]),
    );
  }
}
