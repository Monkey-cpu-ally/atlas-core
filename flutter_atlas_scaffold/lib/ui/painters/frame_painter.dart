import 'dart:math' as math;

import 'package:flutter/material.dart';

class FramePainter extends CustomPainter {
  FramePainter({
    required this.frameType,
    required this.color,
    required this.opacity,
    this.strokeWidth = 1.2,
  });

  final String frameType;
  final Color color;
  final double opacity;
  final double strokeWidth;

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = color.withOpacity(opacity)
      ..style = PaintingStyle.stroke
      ..strokeWidth = strokeWidth;
    final rect = Offset.zero & size;

    switch (frameType) {
      case 'hexagonalPlate':
        final path = Path();
        final center = rect.center;
        final r = size.shortestSide / 2 - 8;
        for (var i = 0; i < 6; i++) {
          final angle = -math.pi / 2 + (math.pi * 2 * i / 6);
          final p = Offset(
            center.dx + math.cos(angle) * r,
            center.dy + math.sin(angle) * r,
          );
          if (i == 0) {
            path.moveTo(p.dx, p.dy);
          } else {
            path.lineTo(p.dx, p.dy);
          }
        }
        path.close();
        canvas.drawPath(path, paint);
        break;
      case 'circularPlate':
        canvas.drawCircle(rect.center, size.shortestSide / 2 - 8, paint);
        break;
      case 'angularTechFrame':
        canvas.drawRRect(
          RRect.fromRectAndRadius(rect.deflate(8), const Radius.circular(10)),
          paint,
        );
        break;
      case 'organicSoftFrame':
        canvas.drawRRect(
          RRect.fromRectAndRadius(rect.deflate(8), const Radius.circular(24)),
          paint,
        );
        break;
      default:
        break;
    }
  }

  @override
  bool shouldRepaint(covariant FramePainter oldDelegate) {
    return frameType != oldDelegate.frameType ||
        color != oldDelegate.color ||
        opacity != oldDelegate.opacity ||
        strokeWidth != oldDelegate.strokeWidth;
  }
}

