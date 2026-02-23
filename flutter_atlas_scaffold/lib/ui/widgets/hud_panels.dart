import 'package:flutter/material.dart';

import '../themes/skin_tokens.dart';

class HudPanel extends StatelessWidget {
  const HudPanel({
    required this.title,
    required this.child,
    required this.skin,
    this.width = 280,
    super.key,
  });

  final String title;
  final Widget child;
  final SkinTokens skin;
  final double width;

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: width,
      child: DecoratedBox(
        decoration: BoxDecoration(
          color: skin.surface.withOpacity(0.88),
          borderRadius: BorderRadius.circular(skin.panelCornerRadius),
          border: Border.all(color: skin.frame.withOpacity(0.85)),
          boxShadow: [
            BoxShadow(
              color: skin.shadow.withOpacity(0.2),
              blurRadius: 8 + skin.panelElevation,
              offset: Offset(0, skin.panelElevation),
            ),
          ],
        ),
        child: Padding(
          padding: const EdgeInsets.all(12),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                title,
                style: TextStyle(
                  color: skin.textPrimary,
                  fontWeight: FontWeight.w700,
                ),
              ),
              const SizedBox(height: 8),
              child,
            ],
          ),
        ),
      ),
    );
  }
}

