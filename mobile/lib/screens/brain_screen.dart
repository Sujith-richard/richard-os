import 'dart:math';
import 'package:flutter/material.dart';
import '../theme.dart';

class BrainScreen extends StatefulWidget {
  const BrainScreen({super.key});
  @override
  State<BrainScreen> createState() => _BrainScreenState();
}

class _BrainScreenState extends State<BrainScreen> with SingleTickerProviderStateMixin {
  late final AnimationController _c = AnimationController(vsync: this, duration: const Duration(seconds: 6))..repeat();

  @override
  void dispose() {
    _c.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final dark = Theme.of(context).brightness == Brightness.dark;
    return Scaffold(
      backgroundColor: dark ? RColors.bgDark : RColors.bg,
      body: SafeArea(
        child: Column(children: [
          const SizedBox(height: 18),
          Text('Brain', style: TextStyle(fontSize: 22, fontWeight: FontWeight.w800, color: dark ? Colors.white : RColors.ink)),
          const SizedBox(height: 4),
          Text('8 services connected to Richard Brain', style: TextStyle(fontSize: 12, color: dark ? Colors.white54 : RColors.inkSoft)),
          const SizedBox(height: 8),
          Expanded(
            child: Container(
              margin: const EdgeInsets.all(18),
              decoration: RColors.glass(dark: dark, radius: 28),
              child: ClipRRect(
                borderRadius: BorderRadius.circular(28),
                child: AnimatedBuilder(
                  animation: _c,
                  builder: (_, __) => CustomPaint(
                    size: Size.infinite,
                    painter: _NeuralPainter(dark: dark, t: _c.value),
                  ),
                ),
              ),
            ),
          ),
        ]),
      ),
    );
  }
}

class _NeuralPainter extends CustomPainter {
  _NeuralPainter({required this.dark, required this.t});
  final bool dark;
  final double t;

  static const _names = ['Exec', 'Planner', 'Task Mgr', 'Workflow', 'Orch', 'Memory', 'KG', 'Neural'];

  @override
  void paint(Canvas canvas, Size size) {
    final c = Offset(size.width / 2, size.height / 2);
    final R = min(size.width, size.height) * 0.34;

    // core
    final coreRad = 44.0 + 4 * sin(t * 2 * pi);
    canvas.drawCircle(
      c,
      coreRad + 10,
      Paint()
        ..shader = RadialGradient(colors: [RColors.lavender.withValues(alpha: .8), RColors.lavender.withValues(alpha: 0)])
            .createShader(Rect.fromCircle(center: c, radius: coreRad + 10)),
    );
    canvas.drawCircle(
      c,
      coreRad,
      Paint()
        ..shader = RadialGradient(
          center: const Alignment(-0.3, -0.4),
          colors: [Colors.white.withValues(alpha: .9), RColors.lavender, RColors.lavenderDeep],
        ).createShader(Rect.fromCircle(center: c, radius: coreRad)),
    );
    canvas.drawCircle(c, coreRad, Paint()..style = PaintingStyle.stroke..color = Colors.white.withValues(alpha: .35)..strokeWidth = 1.2);
    _txt(canvas, c, 'RICHARD\nBRAIN', Colors.white, 11);

    // service nodes
    for (var i = 0; i < _names.length; i++) {
      final a = i / _names.length * 2 * pi + t * 2 * pi * 0.08;
      final pos = c + Offset(cos(a) * R, sin(a) * R);
      final active = ((t * 8).floor() % _names.length) == i;
      final n = 7.0 + (active ? 3.0 : 0.0);

      final mt = 0.5 + 0.5 * sin(t * 2 * pi * 1.5 + i);
      canvas.drawLine(
        c,
        pos,
        Paint()
          ..color = (active ? RColors.accent : Colors.white).withValues(alpha: (0.15 + 0.35 * mt).clamp(0.0, 1.0))
          ..strokeWidth = 1,
      );

      canvas.drawCircle(
        pos,
        n + 4,
        Paint()..color = (active ? RColors.accent : RColors.lavender).withValues(alpha: .25),
      );
      canvas.drawCircle(pos, n, Paint()..color = active ? RColors.accent : RColors.lavender.withValues(alpha: .85));
      _txt(canvas, pos + const Offset(0, -18), _names[i], (dark ? Colors.white70 : RColors.inkSoft), 9);
    }
  }

  void _txt(Canvas c, Offset p, String s, Color color, [double size = 11]) {
    final tp = TextPainter(
      text: TextSpan(text: s, style: TextStyle(color: color, fontSize: size, fontWeight: FontWeight.w700, height: 1.1)),
      textAlign: TextAlign.center,
      textDirection: TextDirection.ltr,
    )..layout();
    tp.paint(c, p - Offset(tp.width / 2, tp.height / 2));
  }

  @override
  bool shouldRepaint(covariant _NeuralPainter old) => old.t != t || old.dark != dark;
}
