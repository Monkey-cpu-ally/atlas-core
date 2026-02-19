import 'dart:math' as math;
import 'dart:ui' show ImageFilter;

import 'package:flutter/material.dart';

import '../models/dial_visual_prefs.dart';

class DialPanel extends StatelessWidget {
  const DialPanel({
    required this.visualPrefs,
    required this.surfaceColor,
    required this.borderColor,
    required this.borderRadius,
    required this.child,
    this.padding = const EdgeInsets.all(12),
    this.dynamicTiltUnit = 0.0,
    super.key,
  });

  final DialVisualPrefs visualPrefs;
  final Color surfaceColor;
  final Color borderColor;
  final BorderRadius borderRadius;
  final EdgeInsets padding;
  final Widget child;

  /// [-1..1] input used only when `panelTiltMode == dynamic`.
  final double dynamicTiltUnit;

  @override
  Widget build(BuildContext context) {
    final tiltMode = visualPrefs.panelTiltMode;

    final baseTiltDeg = DialVisualMath.tiltDegrees(tiltMode);
    final dynamicDeg = tiltMode == PanelTiltMode.dynamic
        ? (dynamicTiltUnit.clamp(-1.0, 1.0) * 4.0)
        : 0.0;

    final rotateX = _degToRad(-baseTiltDeg);
    final rotateY = _degToRad(dynamicDeg);

    final shadow = _panelShadow(visualPrefs.panelDepthShadowMode);
    final material = visualPrefs.panelMaterialMode;

    Widget panelChild = Padding(
      padding: padding,
      child: child,
    );

    panelChild = _materialWrap(
      context,
      material: material,
      borderRadius: borderRadius,
      surfaceColor: surfaceColor,
      borderColor: borderColor,
      shadow: shadow,
      child: panelChild,
    );

    if (tiltMode != PanelTiltMode.off) {
      panelChild = Transform(
        alignment: Alignment.center,
        transform: Matrix4.identity()
          ..setEntry(3, 2, 0.0012)
          ..rotateX(rotateX)
          ..rotateY(rotateY),
        child: panelChild,
      );
    }

    return panelChild;
  }

  static double _degToRad(double degrees) => degrees * math.pi / 180.0;

  static List<BoxShadow> _panelShadow(PanelDepthShadowMode mode) {
    return switch (mode) {
      PanelDepthShadowMode.off => const [],
      PanelDepthShadowMode.softShadow => [
          BoxShadow(
            color: Colors.black.withOpacity(0.20),
            blurRadius: 16,
            spreadRadius: 0,
            offset: const Offset(0, 10),
          ),
        ],
      PanelDepthShadowMode.elevatedPlateShadow => [
          BoxShadow(
            color: Colors.black.withOpacity(0.34),
            blurRadius: 28,
            spreadRadius: 0,
            offset: const Offset(0, 16),
          ),
          BoxShadow(
            color: Colors.black.withOpacity(0.18),
            blurRadius: 10,
            spreadRadius: 0,
            offset: const Offset(0, 6),
          ),
        ],
    };
  }

  static Widget _materialWrap(
    BuildContext context, {
    required PanelMaterialMode material,
    required BorderRadius borderRadius,
    required Color surfaceColor,
    required Color borderColor,
    required List<BoxShadow> shadow,
    required Widget child,
  }) {
    final border = Border.all(color: borderColor, width: 1);

    switch (material) {
      case PanelMaterialMode.matte:
        return Container(
          decoration: BoxDecoration(
            color: surfaceColor,
            borderRadius: borderRadius,
            border: border,
            boxShadow: shadow,
          ),
          child: child,
        );
      case PanelMaterialMode.minimalTransparent:
        return Container(
          decoration: BoxDecoration(
            color: surfaceColor.withOpacity(0.14),
            borderRadius: borderRadius,
            border: borderColor.withOpacity(0.55) == borderColor
                ? border
                : Border.all(color: borderColor.withOpacity(0.55), width: 1),
            boxShadow: shadow,
          ),
          child: child,
        );
      case PanelMaterialMode.glass:
        return ClipRRect(
          borderRadius: borderRadius,
          child: BackdropFilter(
            filter: ImageFilter.blur(sigmaX: 8, sigmaY: 8),
            child: Container(
              decoration: BoxDecoration(
                color: surfaceColor.withOpacity(0.22),
                borderRadius: borderRadius,
                border: Border.all(color: borderColor.withOpacity(0.75), width: 1),
                boxShadow: shadow,
              ),
              child: child,
            ),
          ),
        );
      case PanelMaterialMode.brushedMetal:
        final top = Color.lerp(surfaceColor, Colors.white, 0.06) ?? surfaceColor;
        final mid = surfaceColor;
        final bottom =
            Color.lerp(surfaceColor, Colors.black, 0.12) ?? surfaceColor;
        return Container(
          decoration: BoxDecoration(
            gradient: LinearGradient(
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
              colors: [top, mid, bottom],
              stops: const [0.0, 0.55, 1.0],
            ),
            borderRadius: borderRadius,
            border: border,
            boxShadow: shadow,
          ),
          child: child,
        );
      }
  }
}
