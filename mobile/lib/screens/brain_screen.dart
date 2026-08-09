import 'package:flutter/material.dart';
import '../theme.dart';

class BrainScreen extends StatelessWidget {
  const BrainScreen({super.key});
  @override
  Widget build(BuildContext context) {
    final nodes = ['Executive AI', 'Planner AI', 'Task Manager', 'Workflow Engine', 'Model Orchestrator', 'Memory Engine', 'Knowledge Graph', 'Neural Communication', 'Context Engine', 'Decision Engine', 'Reasoning Engine', 'Validation Engine', 'Learning Engine', 'Department Engine', 'Resource Intelligence', 'Security Engine', 'Project Engineer'];
    return Scaffold(
      backgroundColor: RColors.bgDark,
      body: SafeArea(child: Column(children: [
        const Text('Brain', style: TextStyle(color: Colors.white, fontSize: 20, fontWeight: FontWeight.w700)),
        const SizedBox(height: 6),
        Text('${nodes.length} services connected to Richard Brain', style: const TextStyle(color: Colors.white38, fontSize: 12)),
        const Spacer(),
        // central orb-held graph (conceptual)
        Container(
          width: 150, height: 150,
          decoration: BoxDecoration(shape: BoxShape.circle, gradient: RadialGradient(colors: [RColors.lavender.withValues(alpha: .9), RColors.lavender.withValues(alpha: .08)]), boxShadow: [BoxShadow(color: RColors.lavender.withValues(alpha: .4), blurRadius: 40)]),
          child: const Center(child: Text('RICHARD\nBRAIN', textAlign: TextAlign.center, style: TextStyle(color: Colors.white, fontWeight: FontWeight.w800, fontSize: 18))),
        ),
        const Spacer(),
        Wrap(spacing: 8, runSpacing: 8, alignment: WrapAlignment.center, children: nodes.map((s) => Container(padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6), decoration: BoxDecoration(borderRadius: BorderRadius.circular(20), border: Border.all(color: RColors.accent.withValues(alpha: .5))), child: Text(s, style: const TextStyle(fontSize: 11, color: Colors.white70)))).toList()),
        const SizedBox(height: 24),
      ])),
    );
  }
}
