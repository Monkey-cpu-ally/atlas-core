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
    this.uiTransitionMs = 500,
    this.coreExpandScale = 1.07,
    this.corePressTightenScale = 0.985,
    this.rippleAmplitude = 0.18,
    this.rippleFrequency = 1.2,
    this.rippleSpeed = 0.55,
    this.audioAmpToGlow = 0.35,
    this.extendedIdleMinutes = 10,
    this.extendedIdleBrightnessDrop = 0.18,
    this.lowPowerEnabledByDefault = false,
  });

  final double panelTiltDegrees;
  final String frameType;
  final String frameOpacity;
  final String ringMaterial;
  final double ringTransparency;
  final double ringLineWeight;
  final String backgroundType;
  final bool accentPreviewEnabled;
  final int uiTransitionMs;
  final double coreExpandScale;
  final double corePressTightenScale;
  final double rippleAmplitude;
  final double rippleFrequency;
  final double rippleSpeed;
  final double audioAmpToGlow;
  final int extendedIdleMinutes;
  final double extendedIdleBrightnessDrop;
  final bool lowPowerEnabledByDefault;

  UiPrefs copyWith({
    double? panelTiltDegrees,
    String? frameType,
    String? frameOpacity,
    String? ringMaterial,
    double? ringTransparency,
    double? ringLineWeight,
    String? backgroundType,
    bool? accentPreviewEnabled,
    int? uiTransitionMs,
    double? coreExpandScale,
    double? corePressTightenScale,
    double? rippleAmplitude,
    double? rippleFrequency,
    double? rippleSpeed,
    double? audioAmpToGlow,
    int? extendedIdleMinutes,
    double? extendedIdleBrightnessDrop,
    bool? lowPowerEnabledByDefault,
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
      uiTransitionMs: uiTransitionMs ?? this.uiTransitionMs,
      coreExpandScale: coreExpandScale ?? this.coreExpandScale,
      corePressTightenScale:
          corePressTightenScale ?? this.corePressTightenScale,
      rippleAmplitude: rippleAmplitude ?? this.rippleAmplitude,
      rippleFrequency: rippleFrequency ?? this.rippleFrequency,
      rippleSpeed: rippleSpeed ?? this.rippleSpeed,
      audioAmpToGlow: audioAmpToGlow ?? this.audioAmpToGlow,
      extendedIdleMinutes: extendedIdleMinutes ?? this.extendedIdleMinutes,
      extendedIdleBrightnessDrop:
          extendedIdleBrightnessDrop ?? this.extendedIdleBrightnessDrop,
      lowPowerEnabledByDefault:
          lowPowerEnabledByDefault ?? this.lowPowerEnabledByDefault,
    );
  }
}

