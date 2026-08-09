import 'package:flutter/material.dart';
import '../theme.dart';

class SettingsScreen extends StatefulWidget {
  const SettingsScreen({super.key});
  @override State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  bool _activeMic = false;
  bool _dark = false;
  String _wake = 'hey richard';
  String _persona = 'jarvis';
  String _server = 'http://127.0.0.1:8000';

  final _groups = <String, List<String>>{
    'AI': ['Models', 'Wake Word', 'Persona', 'Active Microphone', 'Notifications'],
    'System': ['Memory', 'Learning', 'Privacy', 'Security', 'Integrations', 'MCP', 'Plugins'],
    'Devices': ['Home Assistant', 'Mobile'],
    'Appearance': ['Theme', 'Language', 'About Richard OS'],
  };

  @override Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Theme.of(context).scaffoldBackgroundColor,
      appBar: AppBar(title: const Text('Settings')),
      body: ListView(padding: const EdgeInsets.all(22), children: [
        _tile('Server URL', _server, Icons.dns, () => _prompt('Server URL', _server, (v) => setState(() => _server = v))),
        _tile('Wake word', _wake, Icons.keyboard_voice, () => _prompt('Wake Word', _wake, (v) => setState(() => _wake = v))),
        switchTile('Active Listening', _activeMic, (v) => setState(() => _activeMic = v)),
        _personaListTile(),
        switchTile('Dark theme', _dark, (v) => setState(() => _dark = v)),
        const Divider(height: 28),
        for (final g in _groups.keys) ...[
          Padding(padding: const EdgeInsets.only(bottom: 8), child: Text(g, style: TextStyle(color: RColors.inkSoft, fontSize: 12, letterSpacing: 1.1))),
          ..._groups[g]!.map((item) => _plain(item)),
        ],
      ]),
    );
  }

  Widget _tile(String t, String v, IconData ic, VoidCallback onTap) => ListTile(
        leading: Icon(ic, color: RColors.lavenderDeep),
        title: Text(t), trailing: Text(v, style: const TextStyle(color: RColors.inkSoft)),
        onTap: onTap,
      );
  Widget _personaListTile() => ListTile(
        leading: const Icon(Icons.face, color: RColors.lavenderDeep),
        title: const Text('Persona'), trailing: DropdownButton<String>(
          value: _persona, underline: const SizedBox.shrink(),
          items: const ['jarvis', 'professional', 'friendly', 'minimal'].map((e) => DropdownMenuItem(value: e, child: Text(e))).toList(),
          onChanged: (v) => setState(() => _persona = v ?? _persona),
        ),
      );
  Widget switchTile(String t, bool v, void f(bool)) => SwitchListTile(secondary: const Icon(Icons.toggle_on, color: RColors.lavenderDeep), title: Text(t), value: v, onChanged: f);
  Widget _plain(String t) => ListTile(leading: const Icon(Icons.chevron_right, color: RColors.inkSoft), title: Text(t), onTap: () {});

  Future<void> _prompt(String title, String init, void Function(String) save) async {
    final c = TextEditingController(text: init);
    final v = await showDialog<String>(context: context, builder: (_) => AlertDialog(title: Text(title), content: TextField(controller: c), actions: [TextButton(onPressed: () => Navigator.pop(context), child: const Text('Cancel')), FilledButton(onPressed: () => Navigator.pop(context, c.text), child: const Text('Save'))]));
    if (v != null) save(v);
  }
}
