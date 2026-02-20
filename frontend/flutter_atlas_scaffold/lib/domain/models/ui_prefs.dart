import 'package:flutter/foundation.dart';

@immutable
class UiPrefs {
  const UiPrefs({
    this.panelTiltDegrees = 6.0,
    this.frameType = 'none',
    this.frameOpacity = 'semiTransparent',
    this.ringMaterial = 'lineOnlyMinimal',
    this.ringTransparency = 0.20,
    this.ringLineWeight = 1.0,
    this.backgroundType = 'solidColor',
    this.accentPreviewEnabled = false,
  });

  final double panelTiltDegrees;
  final String frameType;
  final String frameOpacity;
  final String ringMaterial;
  final double ringTransparency;
  final double ringLineWeight;
  final String backgroundType;
  final bool accentPreviewEnabled;

  UiPrefs copyWith({
    double? panelTiltDegrees,
    String? frameType,
    String? frameOpacity,
    String? ringMaterial,
    double? ringTransparency,
    double? ringLineWeight,
    String? backgroundType,
    bool? accentPreviewEnabled,
  }) {
    return UiPrefs(
      panelTiltDegrees: panelTiltDegrees ?? this.panelTiltDegrees,
      frameType: frameType ?? this.frameType,
      frameOpacity: frameOpacity ?? this.frameOpacity,
      ringMaterial: ringMaterial ?? this.ringMaterial,
      ringTransparency: ringTransparency ?? this.ringTransparency,
      ringLineWeight: ringLineWeight ?? this.ringLineWeight,
      backgroundType: backgroundType ?? this.backgroundType,
      accentPreviewEnabled: accentPreviewEnabled ?? this.accentPreviewEnabled,
    );
  }
}

