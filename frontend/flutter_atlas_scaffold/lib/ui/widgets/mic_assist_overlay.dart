import 'package:flutter/material.dart';

class MicAssistOverlay extends StatelessWidget {
  const MicAssistOverlay({
    required this.visible,
    super.key,
  });

  final bool visible;

  @override
  Widget build(BuildContext context) {
    return IgnorePointer(
      child: AnimatedOpacity(
        opacity: visible ? 1 : 0,
        duration: const Duration(milliseconds: 280),
        child: Align(
          alignment: Alignment.topCenter,
          child: Container(
            margin: const EdgeInsets.only(top: 48),
            padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
            decoration: BoxDecoration(
              color: const Color(0xD91A1F2E),
              borderRadius: BorderRadius.circular(10),
              border: Border.all(color: const Color(0xFF35406A)),
            ),
            child: const Text(
              'Mic assist: hold center and say Ajani, Minerva, or Hermes.',
              style: TextStyle(
                color: Color(0xFFEAF0FF),
                fontWeight: FontWeight.w600,
              ),
            ),
          ),
        ),
      ),
    );
  }
}

