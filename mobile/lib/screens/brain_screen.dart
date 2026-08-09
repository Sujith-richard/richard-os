
import 'dart:math';
import 'package:flutter/material.dart';
import '../theme.dart';

class BrainScreen extends StatefulWidget {
  const BrainScreen({super.key});
  @override State<BrainScreen> createState() => _BrainScreenState();
}
class _BrainScreenState extends State<BrainScreen> with SingleTickerProviderStateMixin {
  late final AnimationController _c = AnimationController(vsync: this, duration: const Duration(seconds: 6))..repeat();
  @override void dispose() { _c.dispose(); super.dispose(); }

  @override Widget build(BuildContext context) {
    final dark = Theme.of(context).brightness == Brightness.dark;
    return Scaffold(
      backgroundColor: dark ? RColors.bgDark : RColors.bg,
      body: SafeArea(child: Column(children: [
        const SizedBox(height: 18),
        const Text('Brain', style: TextStyle(fontSize: 22, fontWeight: FontWeight.w800)),
        const SizedBox(height: 4),
        Text('17 services connected to Richard Brain', style: TextStyle(fontSize: 12, color: dark ? Colors.white54 : RColors.inkSoft)),
        Expanded(child: AnimatedBuilder(animation: _c, builder: (_, __) => CustomPaint(
          size: Size.infinite,
          painter: _NeuralPainter(dark: dark, t: _c.value),
        ))),
      ])),
    );
  }
}

class _NeuralPainter extends CustomPainter {
  _NeuralPainter({required this.dark, required this.t});
  final bool dark; final double t;

  static const _names = ['Exec','Plan','Task','Flow','Orch','Mem','KG','Neural'];
  static const _rad = 118;

  @override void paint(Canvas canvas, Size size) {
    final c = Offset(size.width / 2, size.height / 2 - 10);
    final R = min(size.width, size.height) * 0.36;
    // dim background
    canvas.drawRect(Offset.zero & size, Paint()..color = dark ? RColors.bgDark : RColors.bg);
    // core
    final coreRad = 44.0 + 4 * sin(t * 2 * 3.14159);
    canvas.drawCircle(c, coreRad, Paint()..shader = RadialGradient(colors: [RColors.lavender.withAlpha(200), RColors.lavender.withAlpha(10)]).createShader(Rect.fromCircle(center: c, radius: coreRad + 8)));
    canvas.drawCircle(c, coreRad, Paint()..style = PaintingStyle.stroke..color = Colors.white.withAlpha(90)..strokeWidth = 1.2);
    _txt(canvas, c, 'BRAIN', Colors.white);
    // service nodes
    for (var i = 0; i < _names.length; i++) {
      final a = i / _names.length * 2 * pi + t * 0.15;
      final pos = c + Offset(cos(a) * R, sin(a) * R);
      final active = ((t * 8).floor() % _names.length) == i;
      final n = 7.0 + (active ? 2.5 : 0.0);
      canvas.drawCircle(pos, n, Paint()..color = active ? RColors.accent : RColors.lavender.withAlpha(150));
      // connection line (core -> node, pulsing)
      final mt = 0.5 + 0.5 * sin(t * 3 + i);
      canvas.drawLine(c, pos, Paint()..color = (active ? RColors.accent : Colors.white38).withOpacity(0.25 + 0.4 * mt)..strokeWidth = 1);
      _txt(canvas, pos + const Offset(0, -14), _names[i], Colors.white70, 9);
    }
  }
  void _txt(Canvas c, Offset p, String s, Color color, [double size = 11]) {
    final tp = TextPainter(text: TextSpan(text: s, style: TextStyle(color: color, fontSize: size, fontWeight: FontWeight.w700)), textDirection: TextDirection.ltr)..layout();
    tp.paint(c, p - Offset(tp.width / 2, tp.height / 2));
  }
  @override bool shouldRepaint(covariant _NeuralPainter old) => old.t != t;
}
