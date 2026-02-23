import 'dart:math' as math;

import 'package:flutter/material.dart';

import '../models/dial_visual_prefs.dart';

class FramePlate extends StatelessWidget {
  const FramePlate({
    required this.frameType,
    required this.opacityMode,
    required this.color,
    this.size = 320,
    super.key,
  });

  final FrameType frameType;
  final FrameOpacityMode opacityMode;
  final Color color;
  final double size;

  @override
  Widget build(BuildContext context) {
    if (frameType == FrameType.none) {
      return const SizedBox.shrink();
    }

    return SizedBox.square(
      dimension: size,
      child: CustomPaint(
        painter: _FramePlatePainter(
          frameType: frameType,
          opacityMode: opacityMode,
          color: color,
        ),
      ),
    );
  }
}

class _FramePlatePainter extends CustomPainter {
  _FramePlatePainter({
    required this.frameType,
    required this.opacityMode,
    required this.color,
  });

  final FrameType frameType;
  final FrameOpacityMode opacityMode;
  final Color color;

  @override
  void paint(Canvas canvas, Size size) {
    final center = Offset(size.width / 2, size.height / 2);
    final radius = math.min(size.width, size.height) / 2;

    final alpha = DialVisualMath.frameOpacity(opacityMode);
    final outlineOnly = opacityMode == FrameOpacityMode.outlineOnly;

    final fillPaint = Paint()
      ..color = color.withOpacity(alpha)
      ..style = PaintingStyle.fill;
    final strokePaint = Paint()
      ..color = color.withOpacity(0.55)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 1.2;

    final path = Path();

    switch (frameType) {
      case FrameType.circularPlate:
        canvas.drawCircle(
          center,
          radius * 0.92,
          outlineOnly ? strokePaint : fillPaint,
        );
        if (!outlineOnly) {
          canvas.drawCircle(center, radius * 0.92, strokePaint);
        }
        return;
      case FrameType.hexagonalPlate:
        _polygon(path, center, radius * 0.92, 6);
        break;
      case FrameType.angularTechFrame:
        _polygon(path, center, radius * 0.92, 8, insetEveryOther: true);
        break;
      case FrameType.organicSoftFrame:
        _organic(path, center, radius * 0.92);
        break;
      case FrameType.none:
        return;
    }

    if (!outlineOnly) {
      canvas.drawPath(path, fillPaint);
    }
    canvas.drawPath(path, strokePaint);
  }

  void _polygon(
    Path path,
    Offset center,
    double radius,
    int sides, {
    bool insetEveryOther = false,
  }) {
    final step = (math.pi * 2) / sides;
    for (var i = 0; i < sides; i++) {
      final r = insetEveryOther && i.isOdd ? radius * 0.88 : radius;
      final angle = -math.pi / 2 + step * i;
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
  }

  void _organic(Path path, Offset center, double radius) {
    // Soft rounded "blob" (stable, not random).
    final points = <Offset>[];
    const count = 10;
    final step = (math.pi * 2) / count;
    for (var i = 0; i < count; i++) {
      final wobble = (i.isEven ? 0.94 : 1.0) * radius;
      final angle = -math.pi / 2 + step * i;
      points.add(
        Offset(
          center.dx + math.cos(angle) * wobble,
          center.dy + math.sin(angle) * wobble,
        ),
      );
    }

    path.moveTo(points.first.dx, points.first.dy);
    for (var i = 0; i < points.length; i++) {
      final p1 = points[i];
      final p2 = points[(i + 1) % points.length];
      final mid = Offset((p1.dx + p2.dx) / 2, (p1.dy + p2.dy) / 2);
      path.quadraticBezierTo(p1.dx, p1.dy, mid.dx, mid.dy);
    }
    path.close();
  }

  @override
  bool shouldRepaint(covariant _FramePlatePainter oldDelegate) {
    return oldDelegate.frameType != frameType ||
        oldDelegate.opacityMode != opacityMode ||
        oldDelegate.color != color;
  }
}
