import 'package:flutter/material.dart';

class NeutralRingShell extends StatelessWidget {
  const NeutralRingShell({
    this.color = const Color(0xFF6A6A72),
    this.opacity = 0.36,
    this.strokeWidth = 1.2,
    super.key,
  });

  final Color color;
  final double opacity;
  final double strokeWidth;

  @override
  Widget build(BuildContext context) {
    return IgnorePointer(
      child: CustomPaint(
        painter: _NeutralRingPainter(
          color: color,
          opacity: opacity,
          strokeWidth: strokeWidth,
        ),
      ),
    );
  }
}

class _NeutralRingPainter extends CustomPainter {
  _NeutralRingPainter({
    required this.color,
    required this.opacity,
    required this.strokeWidth,
  });

  final Color color;
  final double opacity;
  final double strokeWidth;

  @override
  void paint(Canvas canvas, Size size) {
    final center = Offset(size.width / 2, size.height / 2);
    final minSide = size.shortestSide;

    final radii = <double>[
      minSide * 0.22,
      minSide * 0.30,
      minSide * 0.38,
      minSide * 0.46,
    ];

    final paint = Paint()
      ..color = color.withOpacity(opacity)
      ..style = PaintingStyle.stroke
      ..strokeWidth = strokeWidth;

    for (final radius in radii) {
      canvas.drawCircle(center, radius, paint);
    }
  }

  @override
  bool shouldRepaint(covariant _NeutralRingPainter oldDelegate) {
    return oldDelegate.color != color ||
        oldDelegate.opacity != opacity ||
        oldDelegate.strokeWidth != strokeWidth;
  }
}
