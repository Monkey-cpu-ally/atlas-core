import 'package:flutter/material.dart';

class NeutralRingShell extends StatelessWidget {
  const NeutralRingShell({super.key});

  @override
  Widget build(BuildContext context) {
    return IgnorePointer(
      child: CustomPaint(
        painter: _NeutralRingPainter(),
      ),
    );
  }
}

class _NeutralRingPainter extends CustomPainter {
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
      ..color = const Color(0xFF6A6A72).withOpacity(0.36)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 1.2;

    for (final radius in radii) {
      canvas.drawCircle(center, radius, paint);
    }
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}
