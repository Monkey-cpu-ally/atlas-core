import 'dart:math' as math;

import 'package:flutter/material.dart';

class SigilPainter extends CustomPainter {
  SigilPainter({
    required this.color,
    required this.opacity,
    this.lineWeight = 1.0,
  });

  final Color color;
  final double opacity;
  final double lineWeight;

  @override
  void paint(Canvas canvas, Size size) {
    final center = Offset(size.width / 2, size.height / 2);
    final base = Paint()
      ..color = color.withOpacity(opacity)
      ..style = PaintingStyle.stroke
      ..strokeWidth = lineWeight;

    final r1 = size.shortestSide * 0.40;
    final r2 = size.shortestSide * 0.33;
    final r3 = size.shortestSide * 0.26;
    canvas.drawCircle(center, r1, base);
    canvas.drawCircle(center, r2, base);
    canvas.drawCircle(center, r3, base);

    for (var i = 0; i < 12; i++) {
      final angle = (math.pi * 2 * i) / 12;
      final p1 = Offset(
        center.dx + math.cos(angle) * r3,
        center.dy + math.sin(angle) * r3,
      );
      final p2 = Offset(
        center.dx + math.cos(angle) * r1,
        center.dy + math.sin(angle) * r1,
      );
      canvas.drawLine(p1, p2, base);
    }
  }

  @override
  bool shouldRepaint(covariant SigilPainter oldDelegate) {
    return color != oldDelegate.color ||
        opacity != oldDelegate.opacity ||
        lineWeight != oldDelegate.lineWeight;
  }
}

