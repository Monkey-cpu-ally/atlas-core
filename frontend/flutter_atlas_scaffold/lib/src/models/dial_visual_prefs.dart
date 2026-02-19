import 'dart:convert';

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

  Map<String, Object?> toMap() {
    return <String, Object?>{
      'panelTiltMode': panelTiltMode.name,
      'panelDepthShadowMode': panelDepthShadowMode.name,
      'panelMaterialMode': panelMaterialMode.name,
      'frameType': frameType.name,
      'frameOpacityMode': frameOpacityMode.name,
      'ringMaterialMode': ringMaterialMode.name,
      'ringTransparencyStrength': ringTransparencyStrength,
      'labelContrastAutoAdjust': labelContrastAutoAdjust,
      'backgroundType': backgroundType.name,
      'councilDimOverlayEnabled': councilDimOverlayEnabled,
    };
  }

  static DialVisualPrefs fromMap(Map<String, Object?> map) {
    T _enum<T extends Enum>(
      List<T> values,
      Object? raw,
      T fallback,
    ) {
      final s = (raw is String) ? raw : '';
      for (final v in values) {
        if (v.name == s) return v;
      }
      return fallback;
    }

    final ringTransparency = map['ringTransparencyStrength'];
    final ringTransparencyValue =
        (ringTransparency is num) ? ringTransparency.toDouble() : defaults.ringTransparencyStrength;

    return DialVisualPrefs(
      panelTiltMode: _enum(
        PanelTiltMode.values,
        map['panelTiltMode'],
        defaults.panelTiltMode,
      ),
      panelDepthShadowMode: _enum(
        PanelDepthShadowMode.values,
        map['panelDepthShadowMode'],
        defaults.panelDepthShadowMode,
      ),
      panelMaterialMode: _enum(
        PanelMaterialMode.values,
        map['panelMaterialMode'],
        defaults.panelMaterialMode,
      ),
      frameType: _enum(
        FrameType.values,
        map['frameType'],
        defaults.frameType,
      ),
      frameOpacityMode: _enum(
        FrameOpacityMode.values,
        map['frameOpacityMode'],
        defaults.frameOpacityMode,
      ),
      ringMaterialMode: _enum(
        RingMaterialMode.values,
        map['ringMaterialMode'],
        defaults.ringMaterialMode,
      ),
      ringTransparencyStrength:
          DialVisualMath.clampRingTransparency(ringTransparencyValue),
      labelContrastAutoAdjust: map['labelContrastAutoAdjust'] is bool
          ? (map['labelContrastAutoAdjust'] as bool)
          : defaults.labelContrastAutoAdjust,
      backgroundType: _enum(
        BackgroundType.values,
        map['backgroundType'],
        defaults.backgroundType,
      ),
      councilDimOverlayEnabled: map['councilDimOverlayEnabled'] is bool
          ? (map['councilDimOverlayEnabled'] as bool)
          : defaults.councilDimOverlayEnabled,
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

class DialVisualPrefsCodec {
  const DialVisualPrefsCodec._();

  static String encode(DialVisualPrefs prefs) => jsonEncode(prefs.toMap());

  static DialVisualPrefs decodeOrDefaults(String? json) {
    final raw = (json ?? '').trim();
    if (raw.isEmpty) return DialVisualPrefs.defaults;
    try {
      final decoded = jsonDecode(raw);
      if (decoded is Map<String, Object?>) {
        return DialVisualPrefs.fromMap(decoded);
      }
      if (decoded is Map) {
        return DialVisualPrefs.fromMap(
          decoded.map((k, v) => MapEntry(k.toString(), v)),
        );
      }
      return DialVisualPrefs.defaults;
    } catch (_) {
      return DialVisualPrefs.defaults;
    }
  }
}
