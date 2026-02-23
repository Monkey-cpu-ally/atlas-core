import 'package:flutter/material.dart';

class TooltipHint extends StatelessWidget {
  const TooltipHint({
    required this.visible,
    required this.text,
    this.fadeOutMs = 350,
    super.key,
  });

  final bool visible;
  final String text;
  final int fadeOutMs;

  @override
  Widget build(BuildContext context) {
    return IgnorePointer(
      child: AnimatedOpacity(
        opacity: visible ? 1 : 0,
        duration: Duration(milliseconds: fadeOutMs),
        curve: Curves.easeOut,
        child: Center(
          child: DecoratedBox(
            decoration: BoxDecoration(
              color: const Color(0xCC121521),
              borderRadius: BorderRadius.circular(10),
              border: Border.all(color: const Color(0xFF2D3550)),
            ),
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
              child: Text(
                text,
                style: const TextStyle(
                  color: Color(0xFFE6EAF7),
                  fontWeight: FontWeight.w600,
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}

