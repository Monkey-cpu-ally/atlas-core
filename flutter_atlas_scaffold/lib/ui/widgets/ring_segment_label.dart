import 'package:flutter/material.dart';

class RingSegmentLabel extends StatelessWidget {
  const RingSegmentLabel({
    required this.text,
    this.active = false,
    this.color = const Color(0xFFE7EBF8),
    this.opacity = 1.0,
    this.scale = 1.0,
    super.key,
  });

  final String text;
  final bool active;
  final Color color;
  final double opacity;
  final double scale;

  @override
  Widget build(BuildContext context) {
    return Transform.scale(
      scale: scale,
      child: Text(
        text,
        style: TextStyle(
          color: color.withOpacity(opacity.clamp(0.0, 1.0)),
          fontWeight: active ? FontWeight.w700 : FontWeight.w500,
          letterSpacing: 0.2,
        ),
      ),
    );
  }
}

