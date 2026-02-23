import 'dart:math' as math;

import 'package:flutter/material.dart';

class WaveformPainter extends CustomPainter {
  WaveformPainter({
    required this.color,
    required this.amplitude,
  });

  final Color color;
  final double amplitude;

  @override
  void paint(Canvas canvas, Size size) {
    final p = Paint()
      ..color = color.withOpacity(0.55)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 2;

    final path = Path();
    final midY = size.height / 2;
    final amp = (size.height * 0.18) * amplitude.clamp(0.0, 1.0);
    for (var x = 0.0; x <= size.width; x += 2) {
      final t = x / size.width;
      final y = midY + math.sin(t * math.pi * 4) * amp;
      if (x == 0) {
        path.moveTo(x, y);
      } else {
        path.lineTo(x, y);
      }
    }
    canvas.drawPath(path, p);
  }

  @override
  bool shouldRepaint(covariant WaveformPainter oldDelegate) {
    return color != oldDelegate.color || amplitude != oldDelegate.amplitude;
  }
}

