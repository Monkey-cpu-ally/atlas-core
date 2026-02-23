import 'package:flutter/material.dart';

import '../../domain/models/ui_prefs.dart';
import '../painters/frame_painter.dart';
import '../themes/skin_tokens.dart';

class FramePlateLayer extends StatelessWidget {
  const FramePlateLayer({
    required this.skin,
    required this.prefs,
    this.size = 360,
    super.key,
  });

  final SkinTokens skin;
  final UiPrefs prefs;
  final double size;

  @override
  Widget build(BuildContext context) {
    final opacity = switch (prefs.frameOpacity) {
      'solid' => 0.92,
      'outlineOnly' => 0.38,
      _ => 0.62,
    };

    return IgnorePointer(
      child: Center(
        child: SizedBox.square(
          dimension: size,
          child: CustomPaint(
            painter: FramePainter(
              frameType: prefs.frameType,
              color: skin.frame,
              opacity: opacity,
            ),
          ),
        ),
      ),
    );
  }
}

