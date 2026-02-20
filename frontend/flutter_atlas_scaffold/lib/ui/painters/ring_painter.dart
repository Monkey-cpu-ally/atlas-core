import 'dart:math' as math;

import 'package:flutter/material.dart';

class RingPainter extends CustomPainter {
  RingPainter({
    required this.color,
    required this.opacity,
    required this.strokeWidth,
    this.segmentCount = 12,
  });

  final Color color;
  final double opacity;
  final double strokeWidth;
  final int segmentCount;

  @override
  void paint(Canvas canvas, Size size) {
    final center = Offset(size.width / 2, size.height / 2);
    final radius = size.shortestSide * 0.36;
    final paint = Paint()
      ..color = color.withOpacity(opacity)
      ..style = PaintingStyle.stroke
      ..strokeWidth = strokeWidth;

    canvas.drawCircle(center, radius, paint);

    final tickPaint = Paint()
      ..color = color.withOpacity(opacity * 0.72)
      ..strokeWidth = strokeWidth * 0.8;

    for (var i = 0; i < segmentCount; i++) {
      final angle = (math.pi * 2 * i) / segmentCount;
      final p1 = Offset(
        center.dx + math.cos(angle) * (radius - 8),
        center.dy + math.sin(angle) * (radius - 8),
      );
      final p2 = Offset(
        center.dx + math.cos(angle) * (radius + 8),
        center.dy + math.sin(angle) * (radius + 8),
      );
      canvas.drawLine(p1, p2, tickPaint);
    }
  }

  @override
  bool shouldRepaint(covariant RingPainter oldDelegate) {
    return color != oldDelegate.color ||
        opacity != oldDelegate.opacity ||
        strokeWidth != oldDelegate.strokeWidth ||
        segmentCount != oldDelegate.segmentCount;
  }
}

