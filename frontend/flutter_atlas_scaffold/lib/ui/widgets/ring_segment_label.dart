import 'package:flutter/material.dart';

class RingSegmentLabel extends StatelessWidget {
  const RingSegmentLabel({
    required this.text,
    this.active = false,
    this.color = const Color(0xFFE7EBF8),
    super.key,
  });

  final String text;
  final bool active;
  final Color color;

  @override
  Widget build(BuildContext context) {
    return Text(
      text,
      style: TextStyle(
        color: color.withOpacity(active ? 1 : 0.62),
        fontWeight: active ? FontWeight.w700 : FontWeight.w500,
        letterSpacing: 0.2,
      ),
    );
  }
}

