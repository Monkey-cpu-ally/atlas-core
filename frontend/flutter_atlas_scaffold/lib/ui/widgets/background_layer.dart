import 'package:flutter/material.dart';

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
    final base = switch (prefs.backgroundType) {
      'gradient' => DecoratedBox(
          decoration: BoxDecoration(
            gradient: LinearGradient(
              colors: <Color>[
                skin.background,
                Color.lerp(skin.background, skin.surface, 0.36) ?? skin.background,
              ],
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
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
        if (dimPercent > 0)
          ColoredBox(
            color: Colors.black.withOpacity(dimPercent.clamp(0.0, 10.0) / 100),
          ),
      ],
    );
  }
}

