import 'dart:math';
import 'package:flutter/material.dart';
import '../theme.dart';

enum OrbState { idle, listening, thinking, planning, executing, agents, tools, completed, error }

class RichardOrb extends StatefulWidget {
  const RichardOrb({super.key, required this.size, required this.state, this.progress = 0});
  final double size;
  final OrbState state;
  final double progress;

  @override
  State<RichardOrb> createState() => _RichardOrbState();
}

class _RichardOrbState extends State<RichardOrb> with SingleTickerProviderStateMixin {
  late final AnimationController _c = AnimationController(vsync: this, duration: const Duration(seconds: 4))..repeat();

  @override
  void dispose() {
    _c.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _c,
      builder: (_, __) => CustomPaint(
        size: Size.square(widget.size),
        painter: _OrbPainter(t: _c.value, state: widget.state, progress: widget.progress),
      ),
    );
  }
}

class _OrbPainter extends CustomPainter {
  _OrbPainter({required this.t, required this.state, required this.progress});
  final double t;
  final OrbState state;
  final double progress;

  Color get _tint {
    switch (state) {
      case OrbState.listening:
      case OrbState.executing:
      case OrbState.tools:
        return RColors.accent;
      case OrbState.error:
        return RColors.err;
      case OrbState.completed:
        return RColors.ok;
      case OrbState.idle:
      case OrbState.thinking:
      case OrbState.planning:
      case OrbState.agents:
        return RColors.lavender;
    }
  }

  double get _speed {
    switch (state) {
      case OrbState.thinking:
        return 2.6;
      case OrbState.executing:
      case OrbState.tools:
        return 2.0;
      case OrbState.agents:
      case OrbState.planning:
        return 1.4;
      case OrbState.listening:
        return 1.1;
      case OrbState.error:
        return 0.55;
      case OrbState.completed:
        return 0.35;
      case OrbState.idle:
        return 0.5;
    }
  }

  int get _particleCount {
    switch (state) {
      case OrbState.thinking:
        return 26;
      case OrbState.executing:
      case OrbState.tools:
        return 20;
      case OrbState.agents:
        return 16;
      case OrbState.planning:
        return 14;
      case OrbState.listening:
        return 12;
      case OrbState.idle:
      case OrbState.completed:
      case OrbState.error:
        return 8;
    }
  }

  @override
  void paint(Canvas canvas, Size size) {
    final c = size.center(Offset.zero);
    final r = size.shortestSide / 2;
    final tt = t * _speed * 2 * pi;

    // outer ambient glow
    canvas.drawCircle(
      c,
      r,
      Paint()
        ..shader = RadialGradient(colors: [_tint.withValues(alpha: .35), _tint.withValues(alpha: 0)])
            .createShader(Rect.fromCircle(center: c, radius: r)),
    );

    // pulse ring for listening / error states
    if (state == OrbState.listening || state == OrbState.error) {
      final pr = r * (0.62 + 0.3 * (0.5 + 0.5 * sin(tt)));
      canvas.drawCircle(
        c,
        pr,
        Paint()
          ..style = PaintingStyle.stroke
          ..strokeWidth = 2
          ..color = _tint.withValues(alpha: .5),
      );
    }

    // orbiting energy particles
    final rand = Random(7);
    for (var i = 0; i < _particleCount; i++) {
      final baseAngle = (i / _particleCount) * 2 * pi;
      final wobble = rand.nextDouble() * 0.6;
      final angle = baseAngle + tt + wobble;
      var dist = r * (0.42 + 0.22 * sin(tt * 0.7 + i));
      var fade = 0.7;
      if (state == OrbState.executing || state == OrbState.tools) {
        final cycle = (tt / (2 * pi) + i / _particleCount) % 1.0;
        dist = r * (0.3 + 0.65 * cycle);
        fade = (1 - cycle).clamp(0.0, 1.0);
      }
      final pos = c + Offset(cos(angle) * dist, sin(angle) * dist * 0.94);
      canvas.drawCircle(
        pos,
        1.6 + (i % 3),
        Paint()..color = _tint.withValues(alpha: (0.25 + 0.55 * fade).clamp(0.0, 1.0)),
      );
    }

    // inner 3D-shaded core
    final coreR = r * 0.52 * (state == OrbState.listening ? (0.94 + 0.08 * sin(tt * 2)) : 1.0);
    canvas.drawCircle(
      c,
      coreR,
      Paint()
        ..shader = RadialGradient(
          center: const Alignment(-0.35, -0.4),
          colors: [Colors.white.withValues(alpha: .9), _tint, RColors.lavenderDeep.withValues(alpha: .9)],
          stops: const [0.0, 0.45, 1.0],
        ).createShader(Rect.fromCircle(center: c, radius: coreR)),
    );
    canvas.drawCircle(
      c,
      coreR,
      Paint()
        ..style = PaintingStyle.stroke
        ..strokeWidth = 1
        ..color = Colors.white.withValues(alpha: .35),
    );

    // executing progress arc
    if (state == OrbState.executing && progress > 0) {
      canvas.drawArc(
        Rect.fromCircle(center: c, radius: r * 0.88),
        -pi / 2,
        2 * pi * progress.clamp(0.0, 1.0),
        false,
        Paint()
          ..style = PaintingStyle.stroke
          ..strokeWidth = 3
          ..strokeCap = StrokeCap.round
          ..color = RColors.accent,
      );
    }

    // completed calm ring
    if (state == OrbState.completed) {
      canvas.drawCircle(
        c,
        r * 0.7,
        Paint()
          ..style = PaintingStyle.stroke
          ..strokeWidth = 2
          ..color = RColors.ok.withValues(alpha: .6),
      );
    }
  }

  @override
  bool shouldRepaint(covariant _OrbPainter old) =>
      old.t != t || old.state != state || old.progress != progress;
}
