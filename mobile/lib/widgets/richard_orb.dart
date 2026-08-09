import 'dart:math';
import 'package:flutter/material.dart';
import '../theme.dart';

enum OrbState { idle, listening, thinking, planning, executing, tools, agents, completed, error }

class RichardOrb extends StatefulWidget {
  const RichardOrb({super.key, this.size = 220, this.state = OrbState.idle, this.progress = 0.0});
  final double size;
  final OrbState state;
  final double progress;
  @override
  State<RichardOrb> createState() => _RichardOrbState();
}

class _P {
  double a = 0;
  double b = 0.3;
  double s = 1;
}

class _RichardOrbState extends State<RichardOrb> with SingleTickerProviderStateMixin {
  late final AnimationController _c = AnimationController(vsync: this, duration: const Duration(seconds: 4))..repeat();
  final Random _r = Random();
  final List<_P> _ps = List.generate(44, (_) => _P());

  Color get _col {
    switch (widget.state) {
      case OrbState.listening: return RColors.accent;
      case OrbState.error: return RColors.err;
      case OrbState.thinking:
      case OrbState.planning:
      case OrbState.agents: return RColors.lavender;
      case OrbState.executing:
      case OrbState.completed: return RColors.ok;
      case OrbState.tools: return RColors.accent;
      default: return RColors.lavender;
    }
  }

  double _spd() {
    switch (widget.state) {
      case OrbState.executing: return 1.4;
      case OrbState.thinking: return 1.2;
      case OrbState.tools: return 1.2;
      case OrbState.agents: return 1.1;
      case OrbState.planning: return 0.9;
      case OrbState.listening: return 0.8;
      case OrbState.completed: return 0.4;
      case OrbState.error: return 0.3;
      default: return 0.25;
    }
  }

  @override
  void dispose() { _c.dispose(); super.dispose(); }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _c,
      builder: (_, __) {
        final t = _c.value;
        final s = widget.size;
        final pulse = widget.state == OrbState.listening ? 1 + 0.035 * sin(t * 4 * pi) : 1 + 0.012 * sin(t * 2 * pi);
        return SizedBox(
          width: s, height: s,
          child: CustomPaint(painter: _OrbPainter(t, widget.state, _col, _spd(), pulse, _ps, widget.progress)),
        );
      },
    );
  }
}

class _OrbPainter extends CustomPainter {
  _OrbPainter(this.t, this.st, this.col, this.spd, this.pulse, this.ps, this.prog);
  final double t; final OrbState st; final Color col; final double spd; final double pulse; final List<_P> ps; final double prog;

  @override
  void paint(Canvas c, Size size) {
    final ctr = Offset(size.width / 2, size.height / 2);
    final R = min(size.width, size.height) / 2 * pulse;

    c.drawCircle(ctr, R + 26, Paint()..shader = RadialGradient(colors: [col.withAlpha(100), col.withAlpha(0)]).createShader(Rect.fromCircle(center: ctr, radius: R + 26)));

    c.drawCircle(ctr, R, Paint()..color = Colors.white.withAlpha(10));
    c.drawCircle(ctr, R, Paint()..style = PaintingStyle.stroke..strokeWidth = 1.2..color = col.withAlpha(130));

    for (var i = 0; i < ps.length; i++) {
      final p = ps[i];
      final ang = p.a + t * p.s * 20 * spd;
      final rr = p.b * R;
      final x = ctr.dx + cos(ang) * rr;
      final y = ctr.dy + sin(ang) * rr * 0.9;
      c.drawCircle(Offset(x, y), p.s * 0.8, Paint()..color = col.withAlpha(140));
    }

    c.drawCircle(ctr, R * 0.3, Paint()..shader = RadialGradient(colors: [col.withAlpha(180), col.withAlpha(10)]).createShader(Rect.fromCircle(center: ctr, radius: R * 0.5)));

    if (st == OrbState.planning) {
      for (var k = 0; k < 2; k++) {
        c.drawCircle(ctr, R * (1.12 + k * 0.12 + 0.03 * sin(t * 3 + k)), Paint()..style = PaintingStyle.stroke..strokeWidth = 1..color = col.withAlpha(70));
      }
    }
    if (st == OrbState.executing) {
      for (var i = 0; i < 6; i++) {
        final a = t * 3 + i * pi / 3;
        final e = prog * R * 1.2;
        c.drawCircle(Offset(ctr.dx + cos(a) * e, ctr.dy + sin(a) * e), 3, Paint()..color = RColors.ok.withAlpha(160));
      }
    }
    if (st == OrbState.agents) {
      for (var i = 0; i < 3; i++) {
        final a = i * 2 * pi / 3 + t * 0.8;
        c.drawCircle(Offset(ctr.dx + cos(a) * R * 1.3, ctr.dy + sin(a) * R * 1.3), 5, Paint()..color = col.withAlpha(150));
      }
    }
    if (st == OrbState.completed) {
      c.drawCircle(ctr, R * 1.06, Paint()..style = PaintingStyle.stroke..strokeWidth = 2..color = RColors.ok.withAlpha(120));
    }
    if (st == OrbState.error) {
      c.drawCircle(ctr, R * 1.04, Paint()..style = PaintingStyle.stroke..strokeWidth = 1.6..color = RColors.err.withAlpha(130));
    }
  }

  @override
  bool shouldRepaint(covariant _OrbPainter old) => old.t != t || old.prog != prog;
}
