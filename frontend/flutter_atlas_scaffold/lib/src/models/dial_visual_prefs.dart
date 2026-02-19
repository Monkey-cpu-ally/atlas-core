import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';

enum PanelTiltMode { off, subtle, noticeable, dynamic }

enum PanelDepthShadowMode { off, softShadow, elevatedPlateShadow }

enum PanelMaterialMode { matte, glass, brushedMetal, minimalTransparent }

enum FrameType {
  none,
  hexagonalPlate,
  circularPlate,
  angularTechFrame,
  organicSoftFrame,
}

enum FrameOpacityMode { solid, semiTransparent, outlineOnly }

enum RingMaterialMode {
  solidMatte,
  frostedGlass,
  transparentGlass,
  lineOnlyMinimal,
  mixedInnerSolidOuterTransparent,
}

enum BackgroundType {
  solidColor,
  gradient,
  softNoiseGrain,
  deepCosmicSpace,
  matteMinimal,
}

@immutable
class DialVisualPrefs {
  const DialVisualPrefs({
    this.panelTiltMode = PanelTiltMode.off,
    this.panelDepthShadowMode = PanelDepthShadowMode.softShadow,
    this.panelMaterialMode = PanelMaterialMode.matte,
    this.frameType = FrameType.none,
    this.frameOpacityMode = FrameOpacityMode.semiTransparent,
    this.ringMaterialMode = RingMaterialMode.lineOnlyMinimal,
    this.ringTransparencyStrength = 0.20,
    this.labelContrastAutoAdjust = true,
    this.backgroundType = BackgroundType.solidColor,
    this.councilDimOverlayEnabled = true,
  });

  static const DialVisualPrefs defaults = DialVisualPrefs();

  final PanelTiltMode panelTiltMode;
  final PanelDepthShadowMode panelDepthShadowMode;
  final PanelMaterialMode panelMaterialMode;

  final FrameType frameType;
  final FrameOpacityMode frameOpacityMode;

  final RingMaterialMode ringMaterialMode;
  /// 0.0 – 0.60 per spec.
  final double ringTransparencyStrength;
  final bool labelContrastAutoAdjust;

  final BackgroundType backgroundType;
  final bool councilDimOverlayEnabled;

  DialVisualPrefs copyWith({
    PanelTiltMode? panelTiltMode,
    PanelDepthShadowMode? panelDepthShadowMode,
    PanelMaterialMode? panelMaterialMode,
    FrameType? frameType,
    FrameOpacityMode? frameOpacityMode,
    RingMaterialMode? ringMaterialMode,
    double? ringTransparencyStrength,
    bool? labelContrastAutoAdjust,
    BackgroundType? backgroundType,
    bool? councilDimOverlayEnabled,
  }) {
    return DialVisualPrefs(
      panelTiltMode: panelTiltMode ?? this.panelTiltMode,
      panelDepthShadowMode: panelDepthShadowMode ?? this.panelDepthShadowMode,
      panelMaterialMode: panelMaterialMode ?? this.panelMaterialMode,
      frameType: frameType ?? this.frameType,
      frameOpacityMode: frameOpacityMode ?? this.frameOpacityMode,
      ringMaterialMode: ringMaterialMode ?? this.ringMaterialMode,
      ringTransparencyStrength:
          ringTransparencyStrength ?? this.ringTransparencyStrength,
      labelContrastAutoAdjust:
          labelContrastAutoAdjust ?? this.labelContrastAutoAdjust,
      backgroundType: backgroundType ?? this.backgroundType,
      councilDimOverlayEnabled:
          councilDimOverlayEnabled ?? this.councilDimOverlayEnabled,
    );
  }
}

class DialVisualMath {
  const DialVisualMath._();

  static double clampRingTransparency(double value) {
    return value.clamp(0.0, 0.60).toDouble();
  }

  static double tiltDegrees(PanelTiltMode mode) {
    return switch (mode) {
      PanelTiltMode.off => 0.0,
      PanelTiltMode.subtle => 6.0,
      PanelTiltMode.noticeable => 12.0,
      PanelTiltMode.dynamic => 6.0,
    };
  }

  static double frameOpacity(FrameOpacityMode mode) {
    return switch (mode) {
      FrameOpacityMode.solid => 0.90,
      FrameOpacityMode.semiTransparent => 0.55,
      FrameOpacityMode.outlineOnly => 0.0,
    };
  }
}
