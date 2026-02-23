import 'dart:convert';

import 'package:flutter/services.dart';

import '../../domain/models/ui_prefs.dart';
import '../../domain/models/ui_prefs_profile.dart';
import 'defaults.dart';

class UiPrefsResolver {
  const UiPrefsResolver._();

  static const _uiPrefsSchemaId = 'ajani.ui_prefs.schema.v1';

  static Future<UiPrefsProfile> resolveDefaultProfile({
    String path = 'assets/prefs/ui_prefs_default.json',
  }) async {
    return resolveProfile(path: path);
  }

  static Future<UiPrefsProfile> resolveProfile({
    String path = 'assets/prefs/ui_prefs_default.json',
    String? rawJson,
  }) async {
    try {
      final source = (rawJson != null && rawJson.trim().isNotEmpty)
          ? rawJson
          : await rootBundle.loadString(path);
      return parseRawJson(source) ?? _fallback();
    } catch (_) {
      return _fallback();
    }
  }

  static UiPrefsProfile? parseRawJson(String rawJson) {
    try {
      final decoded = jsonDecode(rawJson);
      if (decoded is! Map<String, Object?>) {
        return null;
      }
      final schema = decoded[r'$schema']?.toString() ?? '';
      if (schema != _uiPrefsSchemaId) {
        return null;
      }
      return _fromMap(decoded);
    } catch (_) {
      return null;
    }
  }

  static UiPrefsProfile _fromMap(Map<String, Object?> map) {
    final skins = _asMap(map['skins']);
    final panel = _asMap(map['panel']);
    final tilt = _asMap(panel['tilt']);
    final dynamicResponse = _asMap(tilt['dynamicResponse']);
    final depthShadow = _asMap(panel['depthShadow']);
    final frame = _asMap(map['frame']);
    final rings = _asMap(map['rings']);
    final ringMaterials = _asMap(rings['materials']);
    final commandRing = _asMap(ringMaterials['commandRing']);
    final domainRing = _asMap(ringMaterials['domainRing']);
    final moduleRing = _asMap(ringMaterials['moduleRing']);
    final utilityRing = _asMap(ringMaterials['utilityRing']);
    final core = _asMap(map['core']);
    final coreIdle = _asMap(core['idle']);
    final coreTouch = _asMap(core['touch']);
    final coreGyro = _asMap(core['gyro']);
    final coreRipple = _asMap(core['ripple']);
    final voice = _asMap(map['voice']);
    final holdToActivate = _asMap(voice['holdToActivate']);
    final bluetoothWake = _asMap(voice['bluetoothWake']);
    final audio = _asMap(map['audio']);
    final haptics = _asMap(map['haptics']);
    final council = _asMap(map['council']);
    final failureHandling = _asMap(map['failureHandling']);
    final escalation = _asMap(failureHandling['escalation']);
    final onboarding = _asMap(map['onboarding']);
    final firstLaunchHint = _asMap(onboarding['firstLaunchHint']);
    final power = _asMap(map['power']);
    final extendedIdle = _asMap(power['extendedIdle']);
    final lowPowerVisualMode = _asMap(power['lowPowerVisualMode']);
    final launch = _asMap(map['launch']);

    final commandTransparency = _asDouble(commandRing['transparency'], 0.0);
    final domainTransparency = _asDouble(domainRing['transparency'], 0.28);
    final moduleTransparency = _asDouble(moduleRing['transparency'], 0.42);
    final utilityTransparency = _asDouble(utilityRing['transparency'], 0.55);
    final ringTransparencyAvg = ((commandTransparency +
                domainTransparency +
                moduleTransparency +
                utilityTransparency) /
            4)
        .clamp(0.0, 0.60)
        .toDouble();

    final prefs = UiPrefs(
      panelTiltEnabled: _asBool(tilt['enabled'], true),
      panelTiltMode: tilt['mode']?.toString() ?? 'subtle',
      panelTiltDegrees: _asDouble(tilt['degrees'], 7).clamp(0.0, 15.0).toDouble(),
      panelDynamicResponseEnabled: _asBool(dynamicResponse['enabled'], false),
      panelDynamicDragTiltDegMax:
          _asDouble(dynamicResponse['dragTiltDegMax'], 6).clamp(0.0, 20.0).toDouble(),
      panelDynamicSmoothing:
          _asDouble(dynamicResponse['smoothing'], 0.85).clamp(0.0, 1.0).toDouble(),
      depthShadowEnabled: _asBool(depthShadow['enabled'], true),
      depthShadowStyle: depthShadow['style']?.toString() ?? 'soft',
      depthShadowStrength:
          _asDouble(depthShadow['strength'], 0.65).clamp(0.0, 1.0).toDouble(),
      frameEnabled: _asBool(frame['enabled'], true),
      frameType: _mapFrameType(frame['type']?.toString() ?? 'none'),
      frameOpacity: _mapFrameOpacity(_asDouble(frame['opacity'], 0.22)),
      frameMaterial: _mapMaterial(frame['material']?.toString() ?? 'matte'),
      partialLabeling: _asBool(rings['partialLabeling'], true),
      keepLabelsUpright: _asBool(rings['keepLabelsUpright'], true),
      activeLabelScale: _asDouble(rings['activeLabelScale'], 1.15),
      inactiveOpacityNear: _asDouble(rings['inactiveOpacityNear'], 0.55),
      inactiveOpacityFar: _asDouble(rings['inactiveOpacityFar'], 0.18),
      ringMaterial:
          _mapMaterial(commandRing['material']?.toString() ?? 'solid_matte'),
      ringTransparency: ringTransparencyAvg,
      ringLineWeight: 1.0,
      commandRingMaterial:
          _mapMaterial(commandRing['material']?.toString() ?? 'solid_matte'),
      commandRingTransparency: commandTransparency,
      domainRingMaterial:
          _mapMaterial(domainRing['material']?.toString() ?? 'frosted_glass'),
      domainRingTransparency: domainTransparency,
      moduleRingMaterial:
          _mapMaterial(moduleRing['material']?.toString() ?? 'transparent_glass'),
      moduleRingTransparency: moduleTransparency,
      utilityRingMaterial:
          _mapMaterial(utilityRing['material']?.toString() ?? 'line_only'),
      utilityRingTransparency: utilityTransparency,
      backgroundType: _mapBackgroundType(_asMap(map['background'])['type']?.toString() ?? 'gradient'),
      accentPreviewEnabled: false,
      uiTransitionMs: _asInt(launch['coldStartFadeMs'], 560),
      coreExpandScale: _asDouble(coreTouch['expandScale'], 1.07),
      corePressTightenScale: _asDouble(coreTouch['pressTightenScale'], 0.985),
      rippleAmplitude: _asDouble(coreRipple['amplitude'], 0.18),
      rippleFrequency: _asDouble(coreRipple['frequency'], 1.2),
      rippleSpeed: _asDouble(coreRipple['speed'], 0.55),
      audioAmpToGlow: _asDouble(coreRipple['audioAmpToGlow'], 0.35),
      hybrid2_5d: _asBool(core['hybrid2_5d'], true),
      idleRotationEnabled: _asBool(coreIdle['rotationEnabled'], false),
      internalMotionEnabled: _asBool(coreIdle['internalMotionEnabled'], true),
      internalDriftSpeed: _asDouble(coreIdle['internalDriftSpeed'], 0.18),
      breathCycleSec: _asDouble(coreIdle['breathCycleSec'], 4.5),
      coreBrightness: _asDouble(coreIdle['brightness'], 0.92),
      touchReturnMs: _asInt(coreTouch['returnMs'], 320),
      parallaxPxMax: _asDouble(coreTouch['parallaxPxMax'], 6),
      microTiltDegMax: _asDouble(coreTouch['microTiltDegMax'], 4),
      gyroEnabled: _asBool(coreGyro['enabled'], true),
      gyroCoreOnly: _asBool(coreGyro['coreOnly'], true),
      gyroParallaxPxMax: _asDouble(coreGyro['gyroParallaxPxMax'], 3),
      gyroTiltDegMax: _asDouble(coreGyro['gyroTiltDegMax'], 5),
      gyroSmoothing:
          _asDouble(coreGyro['smoothing'], 0.9).clamp(0.0, 1.0).toDouble(),
      extendedIdleMinutes: _asInt(extendedIdle['minutes'], 10),
      extendedIdleBrightnessDrop: _asDouble(extendedIdle['brightnessDrop'], 0.18),
      lowPowerEnabledByDefault: _asBool(lowPowerVisualMode['enabled'], false),
    );

    return UiPrefsProfile(
      selectedSkinId: skins['selectedSkinId']?.toString() ?? Defaults.defaultSkinId,
      prefs: prefs,
      talkTabEnabled: _asBool(voice['talkTabEnabled'], false),
      longPressMs: _asInt(holdToActivate['longPressMs'], 350),
      bluetoothWakeEnabled: _asBool(bluetoothWake['enabled'], true),
      bluetoothWakeScreenOnOnly: _asBool(bluetoothWake['screenOnOnly'], true),
      hermesReadyToneOnScreenOn:
          _asBool(bluetoothWake['hermesReadyToneOnScreenOn'], true),
      idleAmbientEnabled: _asBool(audio['idleAmbientEnabled'], false),
      hapticsEnabled: _asBool(haptics['enabled'], true),
      nameRecognizedPulseMs: _asInt(haptics['nameRecognizedPulseMs'], 15),
      councilPulseMs: _asInt(haptics['councilPulseMs'], 22),
      councilEnabled: _asBool(council['enabled'], true),
      councilPauseBetweenSpeakersMs: _asInt(council['pauseBetweenSpeakersMs'], 1000),
      failureShowMicAssistAfterFails:
          _asInt(escalation['showMicAssistAfterFails'], 3),
      failureSilentResetAfterFails:
          _asInt(failureHandling['silentResetAfterFails'], 6),
      failureHintText:
          escalation['hintText']?.toString() ?? 'Try saying the AI’s name clearly.',
      failureHintDurationMs: _asInt(escalation['hintDurationMs'], 4000),
      firstLaunchHintEnabled: _asBool(firstLaunchHint['enabled'], true),
      firstLaunchHintText: firstLaunchHint['text']?.toString() ??
          'Say "Hermes, system mode" to customize interface.',
      firstLaunchHintShowOnce: _asBool(firstLaunchHint['showOnce'], true),
      firstLaunchHintFadeOutMs: _asInt(firstLaunchHint['fadeOutMs'], 300),
      firstLaunchHintDisplayMs: _asInt(firstLaunchHint['displayMs'], 5000),
      launchColdStartFadeMs: _asInt(launch['coldStartFadeMs'], 560),
      launchResumeFadeMs: _asInt(launch['resumeFadeMs'], 200),
      raw: map,
    );
  }

  static UiPrefsProfile _fallback() {
    return const UiPrefsProfile(
      selectedSkinId: Defaults.defaultSkinId,
      prefs: Defaults.uiPrefs,
      talkTabEnabled: false,
      longPressMs: 350,
      bluetoothWakeEnabled: true,
      bluetoothWakeScreenOnOnly: true,
      hermesReadyToneOnScreenOn: true,
      idleAmbientEnabled: false,
      hapticsEnabled: true,
      nameRecognizedPulseMs: 15,
      councilPulseMs: 22,
      councilEnabled: true,
      councilPauseBetweenSpeakersMs: 1000,
      failureShowMicAssistAfterFails: 3,
      failureSilentResetAfterFails: 6,
      failureHintText: 'Try saying the AI’s name clearly.',
      failureHintDurationMs: 4000,
      firstLaunchHintEnabled: true,
      firstLaunchHintText:
          'Say "Hermes, system mode" to customize interface.',
      firstLaunchHintShowOnce: true,
      firstLaunchHintFadeOutMs: 300,
      firstLaunchHintDisplayMs: 5000,
      launchColdStartFadeMs: 560,
      launchResumeFadeMs: 200,
    );
  }

  static Map<String, Object?> _asMap(Object? value) {
    if (value is Map<String, Object?>) {
      return value;
    }
    if (value is Map) {
      final out = <String, Object?>{};
      for (final entry in value.entries) {
        out[entry.key.toString()] = entry.value;
      }
      return out;
    }
    return const <String, Object?>{};
  }

  static double _asDouble(Object? value, double fallback) {
    return value is num ? value.toDouble() : fallback;
  }

  static int _asInt(Object? value, int fallback) {
    return value is num ? value.toInt() : fallback;
  }

  static bool _asBool(Object? value, bool fallback) {
    return value is bool ? value : fallback;
  }

  static String _mapFrameType(String source) {
    return switch (source) {
      'circular_plate' => 'circularPlate',
      'hexagonal_plate' => 'hexagonalPlate',
      'hex_plate' => 'hexagonalPlate',
      'angular_tech' => 'angularTechFrame',
      'angular_tech_frame' => 'angularTechFrame',
      'modular_plate' => 'angularTechFrame',
      'organic_soft_frame' => 'organicSoftFrame',
      _ => 'none',
    };
  }

  static String _mapFrameOpacity(double opacity) {
    if (opacity >= 0.75) {
      return 'solid';
    }
    if (opacity <= 0.30) {
      return 'outlineOnly';
    }
    return 'semiTransparent';
  }

  static String _mapBackgroundType(String source) {
    return switch (source) {
      'gradient' => 'gradient',
      'texture' => 'gradient',
      'deep_cosmic_space' => 'deepCosmicSpace',
      _ => 'solidColor',
    };
  }

  static String _mapMaterial(String source) {
    return switch (source) {
      'solid_matte' => 'solidMatte',
      'frosted_glass' => 'frostedGlass',
      'transparent_glass' => 'transparentGlass',
      'line_only' => 'lineOnlyMinimal',
      'mixed_inner_solid_outer_transparent' =>
        'mixedInnerSolidOuterTransparent',
      _ => 'lineOnlyMinimal',
    };
  }
}

