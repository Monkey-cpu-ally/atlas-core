import 'package:flutter/foundation.dart';

@immutable
class UiPrefs {
  const UiPrefs({
    this.panelTiltEnabled = true,
    this.panelTiltMode = 'subtle',
    this.panelTiltDegrees = 6.0,
    this.panelDynamicResponseEnabled = false,
    this.panelDynamicDragTiltDegMax = 6.0,
    this.panelDynamicSmoothing = 0.85,
    this.depthShadowEnabled = true,
    this.depthShadowStyle = 'soft',
    this.depthShadowStrength = 0.65,
    this.frameEnabled = true,
    this.frameType = 'none',
    this.frameOpacity = 'semiTransparent',
    this.frameMaterial = 'matte',
    this.partialLabeling = true,
    this.keepLabelsUpright = true,
    this.activeLabelScale = 1.15,
    this.inactiveOpacityNear = 0.55,
    this.inactiveOpacityFar = 0.18,
    this.ringMaterial = 'lineOnlyMinimal',
    this.ringTransparency = 0.20,
    this.ringLineWeight = 1.0,
    this.commandRingMaterial = 'lineOnlyMinimal',
    this.commandRingTransparency = 0.20,
    this.domainRingMaterial = 'lineOnlyMinimal',
    this.domainRingTransparency = 0.20,
    this.moduleRingMaterial = 'lineOnlyMinimal',
    this.moduleRingTransparency = 0.20,
    this.utilityRingMaterial = 'lineOnlyMinimal',
    this.utilityRingTransparency = 0.20,
    this.backgroundType = 'solidColor',
    this.accentPreviewEnabled = false,
    this.uiTransitionMs = 500,
    this.coreExpandScale = 1.07,
    this.corePressTightenScale = 0.985,
    this.rippleAmplitude = 0.18,
    this.rippleFrequency = 1.2,
    this.rippleSpeed = 0.55,
    this.audioAmpToGlow = 0.35,
    this.hybrid2_5d = true,
    this.idleRotationEnabled = false,
    this.internalMotionEnabled = true,
    this.internalDriftSpeed = 0.18,
    this.breathCycleSec = 4.5,
    this.coreBrightness = 0.92,
    this.touchReturnMs = 320,
    this.parallaxPxMax = 6,
    this.microTiltDegMax = 4,
    this.gyroEnabled = true,
    this.gyroCoreOnly = true,
    this.gyroParallaxPxMax = 3,
    this.gyroTiltDegMax = 5,
    this.gyroSmoothing = 0.9,
    this.extendedIdleMinutes = 10,
    this.extendedIdleBrightnessDrop = 0.18,
    this.lowPowerEnabledByDefault = false,
  });

  final bool panelTiltEnabled;
  final String panelTiltMode;
  final double panelTiltDegrees;
  final bool panelDynamicResponseEnabled;
  final double panelDynamicDragTiltDegMax;
  final double panelDynamicSmoothing;
  final bool depthShadowEnabled;
  final String depthShadowStyle;
  final double depthShadowStrength;
  final bool frameEnabled;
  final String frameType;
  final String frameOpacity;
  final String frameMaterial;
  final bool partialLabeling;
  final bool keepLabelsUpright;
  final double activeLabelScale;
  final double inactiveOpacityNear;
  final double inactiveOpacityFar;
  final String ringMaterial;
  final double ringTransparency;
  final double ringLineWeight;
  final String commandRingMaterial;
  final double commandRingTransparency;
  final String domainRingMaterial;
  final double domainRingTransparency;
  final String moduleRingMaterial;
  final double moduleRingTransparency;
  final String utilityRingMaterial;
  final double utilityRingTransparency;
  final String backgroundType;
  final bool accentPreviewEnabled;
  final int uiTransitionMs;
  final double coreExpandScale;
  final double corePressTightenScale;
  final double rippleAmplitude;
  final double rippleFrequency;
  final double rippleSpeed;
  final double audioAmpToGlow;
  final bool hybrid2_5d;
  final bool idleRotationEnabled;
  final bool internalMotionEnabled;
  final double internalDriftSpeed;
  final double breathCycleSec;
  final double coreBrightness;
  final int touchReturnMs;
  final double parallaxPxMax;
  final double microTiltDegMax;
  final bool gyroEnabled;
  final bool gyroCoreOnly;
  final double gyroParallaxPxMax;
  final double gyroTiltDegMax;
  final double gyroSmoothing;
  final int extendedIdleMinutes;
  final double extendedIdleBrightnessDrop;
  final bool lowPowerEnabledByDefault;

  UiPrefs copyWith({
    bool? panelTiltEnabled,
    String? panelTiltMode,
    double? panelTiltDegrees,
    bool? panelDynamicResponseEnabled,
    double? panelDynamicDragTiltDegMax,
    double? panelDynamicSmoothing,
    bool? depthShadowEnabled,
    String? depthShadowStyle,
    double? depthShadowStrength,
    bool? frameEnabled,
    String? frameType,
    String? frameOpacity,
    String? frameMaterial,
    bool? partialLabeling,
    bool? keepLabelsUpright,
    double? activeLabelScale,
    double? inactiveOpacityNear,
    double? inactiveOpacityFar,
    String? ringMaterial,
    double? ringTransparency,
    double? ringLineWeight,
    String? commandRingMaterial,
    double? commandRingTransparency,
    String? domainRingMaterial,
    double? domainRingTransparency,
    String? moduleRingMaterial,
    double? moduleRingTransparency,
    String? utilityRingMaterial,
    double? utilityRingTransparency,
    String? backgroundType,
    bool? accentPreviewEnabled,
    int? uiTransitionMs,
    double? coreExpandScale,
    double? corePressTightenScale,
    double? rippleAmplitude,
    double? rippleFrequency,
    double? rippleSpeed,
    double? audioAmpToGlow,
    bool? hybrid2_5d,
    bool? idleRotationEnabled,
    bool? internalMotionEnabled,
    double? internalDriftSpeed,
    double? breathCycleSec,
    double? coreBrightness,
    int? touchReturnMs,
    double? parallaxPxMax,
    double? microTiltDegMax,
    bool? gyroEnabled,
    bool? gyroCoreOnly,
    double? gyroParallaxPxMax,
    double? gyroTiltDegMax,
    double? gyroSmoothing,
    int? extendedIdleMinutes,
    double? extendedIdleBrightnessDrop,
    bool? lowPowerEnabledByDefault,
  }) {
    return UiPrefs(
      panelTiltEnabled: panelTiltEnabled ?? this.panelTiltEnabled,
      panelTiltMode: panelTiltMode ?? this.panelTiltMode,
      panelTiltDegrees: panelTiltDegrees ?? this.panelTiltDegrees,
      panelDynamicResponseEnabled:
          panelDynamicResponseEnabled ?? this.panelDynamicResponseEnabled,
      panelDynamicDragTiltDegMax:
          panelDynamicDragTiltDegMax ?? this.panelDynamicDragTiltDegMax,
      panelDynamicSmoothing: panelDynamicSmoothing ?? this.panelDynamicSmoothing,
      depthShadowEnabled: depthShadowEnabled ?? this.depthShadowEnabled,
      depthShadowStyle: depthShadowStyle ?? this.depthShadowStyle,
      depthShadowStrength: depthShadowStrength ?? this.depthShadowStrength,
      frameEnabled: frameEnabled ?? this.frameEnabled,
      frameType: frameType ?? this.frameType,
      frameOpacity: frameOpacity ?? this.frameOpacity,
      frameMaterial: frameMaterial ?? this.frameMaterial,
      partialLabeling: partialLabeling ?? this.partialLabeling,
      keepLabelsUpright: keepLabelsUpright ?? this.keepLabelsUpright,
      activeLabelScale: activeLabelScale ?? this.activeLabelScale,
      inactiveOpacityNear: inactiveOpacityNear ?? this.inactiveOpacityNear,
      inactiveOpacityFar: inactiveOpacityFar ?? this.inactiveOpacityFar,
      ringMaterial: ringMaterial ?? this.ringMaterial,
      ringTransparency: ringTransparency ?? this.ringTransparency,
      ringLineWeight: ringLineWeight ?? this.ringLineWeight,
      commandRingMaterial: commandRingMaterial ?? this.commandRingMaterial,
      commandRingTransparency:
          commandRingTransparency ?? this.commandRingTransparency,
      domainRingMaterial: domainRingMaterial ?? this.domainRingMaterial,
      domainRingTransparency:
          domainRingTransparency ?? this.domainRingTransparency,
      moduleRingMaterial: moduleRingMaterial ?? this.moduleRingMaterial,
      moduleRingTransparency:
          moduleRingTransparency ?? this.moduleRingTransparency,
      utilityRingMaterial: utilityRingMaterial ?? this.utilityRingMaterial,
      utilityRingTransparency:
          utilityRingTransparency ?? this.utilityRingTransparency,
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
      hybrid2_5d: hybrid2_5d ?? this.hybrid2_5d,
      idleRotationEnabled: idleRotationEnabled ?? this.idleRotationEnabled,
      internalMotionEnabled: internalMotionEnabled ?? this.internalMotionEnabled,
      internalDriftSpeed: internalDriftSpeed ?? this.internalDriftSpeed,
      breathCycleSec: breathCycleSec ?? this.breathCycleSec,
      coreBrightness: coreBrightness ?? this.coreBrightness,
      touchReturnMs: touchReturnMs ?? this.touchReturnMs,
      parallaxPxMax: parallaxPxMax ?? this.parallaxPxMax,
      microTiltDegMax: microTiltDegMax ?? this.microTiltDegMax,
      gyroEnabled: gyroEnabled ?? this.gyroEnabled,
      gyroCoreOnly: gyroCoreOnly ?? this.gyroCoreOnly,
      gyroParallaxPxMax: gyroParallaxPxMax ?? this.gyroParallaxPxMax,
      gyroTiltDegMax: gyroTiltDegMax ?? this.gyroTiltDegMax,
      gyroSmoothing: gyroSmoothing ?? this.gyroSmoothing,
      extendedIdleMinutes: extendedIdleMinutes ?? this.extendedIdleMinutes,
      extendedIdleBrightnessDrop:
          extendedIdleBrightnessDrop ?? this.extendedIdleBrightnessDrop,
      lowPowerEnabledByDefault:
          lowPowerEnabledByDefault ?? this.lowPowerEnabledByDefault,
    );
  }
}

