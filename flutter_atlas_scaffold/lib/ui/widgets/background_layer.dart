import 'package:flutter/material.dart';
import 'dart:math' as math;

import '../../domain/models/ui_prefs.dart';
import '../themes/skin_tokens.dart';

class BackgroundLayer extends StatelessWidget {
  const BackgroundLayer({
    required this.skin,
    required this.prefs,
    this.dimPercent = 0,
    super.key,
  });

  final SkinTokens skin;
  final UiPrefs prefs;
  final double dimPercent;

  @override
  Widget build(BuildContext context) {
    final angleRad = (skin.gradientAngleDeg * math.pi) / 180;
    final gradientBegin = Alignment(
      -math.cos(angleRad),
      -math.sin(angleRad),
    );
    final gradientEnd = Alignment(
      math.cos(angleRad),
      math.sin(angleRad),
    );

    final gradientFrom = skin.gradientFrom ??
        Color.lerp(skin.background, Colors.black, 0.18) ??
        skin.background;
    final gradientTo = skin.gradientTo ??
        Color.lerp(skin.background, skin.surface, 0.36) ??
        skin.background;

    final base = switch (prefs.backgroundType) {
      'gradient' => DecoratedBox(
          decoration: BoxDecoration(
            gradient: LinearGradient(
              colors: <Color>[
                gradientFrom,
                gradientTo,
              ],
              begin: gradientBegin,
              end: gradientEnd,
            ),
          ),
        ),
      'deepCosmicSpace' => DecoratedBox(
          decoration: BoxDecoration(
            gradient: RadialGradient(
              center: const Alignment(0, -0.2),
              radius: 1.2,
              colors: <Color>[
                skin.surface.withOpacity(0.9),
                skin.background,
              ],
            ),
          ),
        ),
      _ => ColoredBox(color: skin.background),
    };

    return Stack(
      fit: StackFit.expand,
      children: [
        base,
        if (skin.textureEnabled && skin.textureOpacity > 0)
          ColoredBox(
            color: skin.highlight.withOpacity(skin.textureOpacity * 0.08),
          ),
        if (skin.noiseEnabled && skin.noiseOpacity > 0)
          ColoredBox(
            color: Colors.black.withOpacity(skin.noiseOpacity * 0.16),
          ),
        if (dimPercent > 0)
          ColoredBox(
            color: Colors.black.withOpacity(dimPercent.clamp(0.0, 10.0) / 100),
          ),
      ],
    );
  }
}

