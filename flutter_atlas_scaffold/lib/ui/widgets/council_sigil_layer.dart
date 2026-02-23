import 'package:flutter/material.dart';

import '../../core/constants/ai_identities.dart';
import '../painters/sigil_painter.dart';

class CouncilSigilLayer extends StatelessWidget {
  const CouncilSigilLayer({
    required this.visible,
    this.opacity = 0.12,
    this.lineWeight = 1.0,
    this.size = 280,
    super.key,
  });

  final bool visible;
  final double opacity;
  final double lineWeight;
  final double size;

  @override
  Widget build(BuildContext context) {
    return IgnorePointer(
      child: Center(
        child: AnimatedOpacity(
          opacity: visible ? 1 : 0,
          duration: const Duration(milliseconds: 500),
          curve: Curves.easeOut,
          child: SizedBox.square(
            dimension: size,
            child: CustomPaint(
              painter: SigilPainter(
                color: AiIdentities.ghostPurple,
                opacity: opacity,
                lineWeight: lineWeight,
              ),
            ),
          ),
        ),
      ),
    );
  }
}

