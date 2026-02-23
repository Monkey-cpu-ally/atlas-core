import 'dart:math' as math;

import 'package:flutter/material.dart';

import '../models/dial_visual_prefs.dart';

class DialBackground extends StatelessWidget {
  const DialBackground({
    required this.type,
    required this.background,
    required this.microDetail,
    super.key,
  });

  final BackgroundType type;
  final Color background;
  final Color microDetail;

  @override
  Widget build(BuildContext context) {
    switch (type) {
      case BackgroundType.solidColor:
        return ColoredBox(color: background);
      case BackgroundType.matteMinimal:
        return ColoredBox(color: background);
      case BackgroundType.gradient:
        return DecoratedBox(
          decoration: BoxDecoration(
            gradient: LinearGradient(
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
              colors: [
                background,
                Color.lerp(background, microDetail, 0.10) ?? background,
              ],
            ),
          ),
        );
      case BackgroundType.softNoiseGrain:
        return CustomPaint(
          painter: _NoisePainter(
            background: background,
            microDetail: microDetail,
          ),
        );
      case BackgroundType.deepCosmicSpace:
        return CustomPaint(
          painter: _CosmicPainter(
            background: background,
            microDetail: microDetail,
          ),
        );
    }
  }
}

class _NoisePainter extends CustomPainter {
  _NoisePainter({
    required this.background,
    required this.microDetail,
  });

  final Color background;
  final Color microDetail;

  @override
  void paint(Canvas canvas, Size size) {
    canvas.drawRect(Offset.zero & size, Paint()..color = background);

    // Deterministic grain (no randomness at runtime).
    final paint = Paint()
      ..color = microDetail.withOpacity(0.06)
      ..strokeWidth = 1;

    const step = 12.0;
    for (var y = 0.0; y < size.height; y += step) {
      for (var x = 0.0; x < size.width; x += step) {
        final dx = (x + y) % (step * 2);
        canvas.drawPoints(
          PointMode.points,
          [
            Offset(x + dx * 0.15, y + (dx % 6) * 0.15),
          ],
          paint,
        );
      }
    }
  }

  @override
  bool shouldRepaint(covariant _NoisePainter oldDelegate) {
    return oldDelegate.background != background ||
        oldDelegate.microDetail != microDetail;
  }
}

class _CosmicPainter extends CustomPainter {
  _CosmicPainter({
    required this.background,
    required this.microDetail,
  });

  final Color background;
  final Color microDetail;

  @override
  void paint(Canvas canvas, Size size) {
    canvas.drawRect(Offset.zero & size, Paint()..color = background);

    final starPaint = Paint()..color = microDetail.withOpacity(0.25);
    final faintPaint = Paint()..color = microDetail.withOpacity(0.10);

    // Deterministic "stars" grid.
    const step = 90.0;
    for (var y = 0.0; y < size.height; y += step) {
      for (var x = 0.0; x < size.width; x += step) {
        final n = ((x * 3 + y * 7) % 11);
        final r = n.isEven ? 1.1 : 0.8;
        canvas.drawCircle(
          Offset(x + (n * 2.0), y + (n * 1.5)),
          r,
          n % 3 == 0 ? starPaint : faintPaint,
        );
      }
    }

    // Soft vignette
    final vignette = RadialGradient(
      colors: [
        Colors.transparent,
        Colors.black.withOpacity(0.22),
      ],
      stops: const [0.62, 1.0],
    );
    final rect = Offset.zero & size;
    final paint = Paint()..shader = vignette.createShader(rect);
    canvas.drawRect(rect, paint);
  }

  @override
  bool shouldRepaint(covariant _CosmicPainter oldDelegate) {
    return oldDelegate.background != background ||
        oldDelegate.microDetail != microDetail;
  }
}
