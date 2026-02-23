import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import '../../domain/models/skin_config.dart';
import '../../domain/models/ui_prefs.dart';
import 'skin_tokens.dart';
import 'skins.dart';

@immutable
class SkinLoadResult {
  const SkinLoadResult({
    required this.tokens,
    required this.prefs,
  });

  final SkinTokens tokens;
  final UiPrefs prefs;
}

class SkinResolver {
  const SkinResolver._();

  static const _skinSchemaId = 'ajani.skin.schema.v1';
  static final _hexColorRegExp = RegExp(r'^#([0-9a-fA-F]{6}|[0-9a-fA-F]{8})$');

  static Future<SkinLoadResult> resolveBundle(String skinId) async {
    final fallback = Skins.byId(skinId);
    try {
      final jsonPath = 'assets/skins/$skinId.json';
      final raw = await rootBundle.loadString(jsonPath);
      final decoded = jsonDecode(raw);
      if (decoded is! Map<String, Object?>) {
        return SkinLoadResult(tokens: fallback, prefs: const UiPrefs());
      }

      final schema = decoded[r'$schema']?.toString() ?? '';
      if (schema == _skinSchemaId) {
        if (!_isValidAjaniSkinV1(decoded)) {
          return SkinLoadResult(tokens: fallback, prefs: const UiPrefs());
        }
        return _fromAjaniSchema(decoded, fallback: fallback);
      }

      final config = SkinConfig.fromMap(decoded);
      return SkinLoadResult(
        tokens: _fromLegacyConfig(config),
        prefs: const UiPrefs(),
      );
    } catch (_) {
      return SkinLoadResult(tokens: fallback, prefs: const UiPrefs());
    }
  }

  static Future<SkinTokens> resolve(String skinId) async {
    final bundle = await resolveBundle(skinId);
    return bundle.tokens;
  }

  static SkinTokens _fromLegacyConfig(SkinConfig config) {
    Color readColor(String key, Color fallback) {
      final value = config.tokens[key]?.toString();
      if (value == null || value.isEmpty) {
        return fallback;
      }
      return _parseHex(value) ?? fallback;
    }

    double readDouble(String key, double fallback) {
      final value = config.tokens[key];
      return value is num ? value.toDouble() : fallback;
    }

    bool readBool(String key, bool fallback) {
      final value = config.tokens[key];
      return value is bool ? value : fallback;
    }

    final base = Skins.byId(config.id);

    return SkinTokens(
      id: config.id,
      background: readColor('background', base.background),
      surface: readColor('surface', base.surface),
      frame: readColor('frame', base.frame),
      ring: readColor('ring', base.ring),
      textPrimary: readColor('textPrimary', base.textPrimary),
      textSecondary: readColor('textSecondary', base.textSecondary),
      accentEnergy: readColor('accentEnergy', base.accentEnergy),
      glassiness: readDouble('glassiness', base.glassiness),
      roughness: readDouble('roughness', base.roughness),
      noiseAmount: readDouble('noiseAmount', base.noiseAmount),
      grainEnabled: readBool('grainEnabled', base.grainEnabled),
    );
  }

  static SkinLoadResult _fromAjaniSchema(
    Map<String, Object?> map, {
    required SkinTokens fallback,
  }) {
    final meta = _asMap(map['meta']);
    final colors = _asMap(map['colors']);
    final background = _asMap(map['background']);
    final gradient = _asMap(background['gradient']);
    final texture = _asMap(background['texture']);
    final noise = _asMap(background['noise']);
    final panel = _asMap(map['panel']);
    final frame = _asMap(map['frame']);
    final rings = _asMap(map['rings']);
    final commandRing = _asMap(rings['commandRing']);
    final domainRing = _asMap(rings['domainRing']);
    final moduleRing = _asMap(rings['moduleRing']);
    final utilityRing = _asMap(rings['utilityRing']);
    final motion = _asMap(map['motion']);
    final core = _asMap(map['core']);
    final ripple = _asMap(core['ripple']);
    final council = _asMap(map['council']);
    final councilDim = _asMap(council['dimOverlay']);

    Color c(String key, Color fallbackColor) {
      return _parseHex(colors[key]?.toString() ?? '') ?? fallbackColor;
    }

    final id = meta['id']?.toString() ?? fallback.id;

    final tokens = fallback.copyWith(
      id: id,
      background: c('bgPrimary', fallback.background),
      surface: c('panelBase', fallback.surface),
      frame: c('stroke', fallback.frame),
      ring: c('stroke', fallback.ring),
      textPrimary: c('textPrimary', fallback.textPrimary),
      textSecondary: c('textSecondary', fallback.textSecondary),
      accentEnergy: c('accentDefault', fallback.accentEnergy),
      glassiness: _materialToGlassiness(frame['material']?.toString(), fallback.glassiness),
      roughness: _materialToRoughness(panel['material']?.toString(), fallback.roughness),
      noiseAmount: _asDouble(noise['opacity'], fallback.noiseAmount),
      grainEnabled: _asBool(texture['enabled'], fallback.grainEnabled),
      panelCornerRadius: _asDouble(panel['cornerRadius'], fallback.panelCornerRadius),
      panelElevation: _asDouble(panel['elevation'], fallback.panelElevation),
      councilDimStrength: _asDouble(councilDim['strength'], fallback.councilDimStrength),
      shadow: c('shadow', fallback.shadow),
      highlight: c('highlight', fallback.highlight),
      gradientFrom: _parseHex(gradient['from']?.toString() ?? ''),
      gradientTo: _parseHex(gradient['to']?.toString() ?? ''),
      gradientAngleDeg: _asDouble(gradient['angleDeg'], fallback.gradientAngleDeg),
      textureEnabled: _asBool(texture['enabled'], false),
      textureAsset: texture['asset']?.toString() ?? '',
      textureOpacity: _asDouble(texture['opacity'], 0),
      noiseEnabled: _asBool(noise['enabled'], false),
      noiseAsset: noise['asset']?.toString() ?? '',
      noiseOpacity: _asDouble(noise['opacity'], 0),
      councilGhostPurple: c('ghostPurpleCouncil', fallback.councilGhostPurple),
      ajaniCrimson: c('aiAjaniCrimson', fallback.ajaniCrimson),
      minervaTeal: c('aiMinervaTeal', fallback.minervaTeal),
      hermesIvory: c('aiHermesIvory', fallback.hermesIvory),
      dangerPulse: c('dangerPulse', fallback.dangerPulse),
    );

    final transparencySamples = <double>[
      _asDouble(commandRing['transparency'], 0),
      _asDouble(domainRing['transparency'], 0),
      _asDouble(moduleRing['transparency'], 0),
      _asDouble(utilityRing['transparency'], 0),
    ];
    final transparencyAvg =
        transparencySamples.reduce((a, b) => a + b) / transparencySamples.length;

    final ringThickness = _asDouble(commandRing['thickness'], 14);
    final ringLineWeight = (ringThickness / 14.0).clamp(0.6, 2.2).toDouble();

    final prefs = UiPrefs(
      panelTiltDegrees: _resolveTiltDegrees(panel),
      frameType: _mapFrameType(frame['type']?.toString() ?? 'none'),
      frameOpacity: _mapFrameOpacity(_asDouble(frame['opacity'], 0.22)),
      ringMaterial: _mapRingMaterial(commandRing['material']?.toString() ?? 'line_only'),
      ringTransparency: transparencyAvg.clamp(0.0, 0.60).toDouble(),
      ringLineWeight: ringLineWeight,
      backgroundType: _mapBackgroundType(background['type']?.toString() ?? 'solid'),
      accentPreviewEnabled: false,
      uiTransitionMs: _asInt(motion['uiTransitionMs'], 500),
      coreExpandScale: _asDouble(motion['coreExpandScale'], 1.07),
      corePressTightenScale: _asDouble(motion['corePressTightenScale'], 0.985),
      rippleAmplitude: _asDouble(ripple['amplitude'], 0.18),
      rippleFrequency: _asDouble(ripple['frequency'], 1.2),
      rippleSpeed: _asDouble(ripple['speed'], 0.55),
      audioAmpToGlow: _asDouble(ripple['audioAmpToGlow'], 0.35),
      extendedIdleMinutes: _asInt(_asMap(map['power'])['extendedIdleMinutes'], 10),
      extendedIdleBrightnessDrop:
          _asDouble(_asMap(map['power'])['extendedIdleBrightnessDrop'], 0.18),
      lowPowerEnabledByDefault:
          _asBool(_asMap(_asMap(map['power'])['lowPowerMode'])['enabledByDefault'], false),
    );

    return SkinLoadResult(tokens: tokens, prefs: prefs);
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

  static double _resolveTiltDegrees(Map<String, Object?> panel) {
    final explicit = panel['tiltDegrees'];
    if (explicit is num) {
      return explicit.toDouble().clamp(0.0, 15.0).toDouble();
    }
    final preset = panel['tiltPreset']?.toString() ?? 'off';
    return switch (preset) {
      'subtle' => 7.0,
      'noticeable' => 12.0,
      'dynamic' => 6.0,
      _ => 0.0,
    };
  }

  static String _mapFrameType(String source) {
    return switch (source) {
      'circular_plate' => 'circularPlate',
      'hexagonal_plate' => 'hexagonalPlate',
      'hex_plate' => 'hexagonalPlate',
      'modular_plate' => 'angularTechFrame',
      'angular_tech' => 'angularTechFrame',
      'angular_tech_frame' => 'angularTechFrame',
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

  static String _mapRingMaterial(String source) {
    return switch (source) {
      'solid_matte' => 'solidMatte',
      'frosted_glass' => 'frostedGlass',
      'transparent_glass' => 'transparentGlass',
      'line_only' => 'lineOnlyMinimal',
      'mixed_inner_solid_outer_transparent' => 'mixedInnerSolidOuterTransparent',
      _ => 'lineOnlyMinimal',
    };
  }

  static String _mapBackgroundType(String source) {
    return switch (source) {
      'gradient' => 'gradient',
      'texture' => 'gradient',
      'deep_cosmic_space' => 'deepCosmicSpace',
      _ => 'solidColor',
    };
  }

  static double _materialToGlassiness(String? material, double fallback) {
    return switch (material) {
      'transparent_glass' => 0.55,
      'frosted_glass' => 0.42,
      'matte' => 0.15,
      _ => fallback,
    };
  }

  static double _materialToRoughness(String? material, double fallback) {
    return switch (material) {
      'matte' => 0.72,
      'frosted_glass' => 0.42,
      'transparent_glass' => 0.35,
      _ => fallback,
    };
  }

  static Color? _parseHex(String raw) {
    final hex = raw.replaceFirst('#', '');
    if (hex.length == 6) {
      return Color(int.parse('FF$hex', radix: 16));
    }
    if (hex.length == 8) {
      return Color(int.parse(hex, radix: 16));
    }
    return null;
  }

  static bool _isValidAjaniSkinV1(Map<String, Object?> map) {
    const topRequired = <String>{
      'meta',
      'colors',
      'background',
      'panel',
      'frame',
      'rings',
      'typography',
      'motion',
      'core',
      'council',
      'power',
      'audio',
    };
    for (final key in topRequired) {
      if (!map.containsKey(key)) {
        return false;
      }
    }

    final meta = _asMap(map['meta']);
    if (!_hasKeys(meta, const ['id', 'name', 'version', 'author'])) {
      return false;
    }

    final colors = _asMap(map['colors']);
    const colorRequired = <String>[
      'bgPrimary',
      'bgSecondary',
      'panelBase',
      'textPrimary',
      'textSecondary',
      'stroke',
      'shadow',
      'highlight',
      'accentDefault',
      'ghostPurpleCouncil',
      'aiAjaniCrimson',
      'aiMinervaTeal',
      'aiHermesIvory',
      'dangerPulse',
    ];
    if (!_hasKeys(colors, colorRequired)) {
      return false;
    }
    for (final key in colorRequired) {
      if (!_isHexColor(colors[key])) {
        return false;
      }
    }

    final background = _asMap(map['background']);
    final backgroundType = background['type']?.toString() ?? '';
    if (!const {'solid', 'gradient', 'texture'}.contains(backgroundType)) {
      return false;
    }
    if (backgroundType == 'solid' && !_isHexColor(background['solid'])) {
      return false;
    }
    if (backgroundType == 'gradient') {
      final gradient = _asMap(background['gradient']);
      if (!_hasKeys(gradient, const ['from', 'to', 'angleDeg'])) {
        return false;
      }
      if (!_isHexColor(gradient['from']) || !_isHexColor(gradient['to'])) {
        return false;
      }
    }
    if (backgroundType == 'texture') {
      if (!_isHexColor(background['solid'])) {
        return false;
      }
      final texture = _asMap(background['texture']);
      if (!_hasKeys(texture, const ['enabled', 'asset', 'opacity'])) {
        return false;
      }
    }

    final panel = _asMap(map['panel']);
    if (!_hasKeys(
      panel,
      const ['tiltPreset', 'tiltDegrees', 'depthShadow', 'material', 'cornerRadius', 'elevation'],
    )) {
      return false;
    }
    if (!const {'off', 'subtle', 'noticeable', 'dynamic'}
        .contains(panel['tiltPreset']?.toString() ?? '')) {
      return false;
    }

    final frame = _asMap(map['frame']);
    if (!_hasKeys(frame, const ['enabled', 'type', 'opacity', 'strokeWidth', 'material'])) {
      return false;
    }
    if (!const {
      'none',
      'hex_plate',
      'circular_plate',
      'angular_tech',
      'organic_soft',
      'modular_plate',
    }.contains(frame['type']?.toString() ?? '')) {
      return false;
    }

    final rings = _asMap(map['rings']);
    if (!_hasKeys(
      rings,
      const ['global', 'commandRing', 'domainRing', 'moduleRing', 'utilityRing'],
    )) {
      return false;
    }
    final ringNames = const ['commandRing', 'domainRing', 'moduleRing', 'utilityRing'];
    for (final ringName in ringNames) {
      final spec = _asMap(rings[ringName]);
      if (!_hasKeys(
        spec,
        const ['thickness', 'material', 'transparency', 'tickStyle', 'alwaysShowLabels'],
      )) {
        return false;
      }
      if (!const {
        'solid_matte',
        'frosted_glass',
        'transparent_glass',
        'line_only',
        'mixed',
        'mixed_inner_solid_outer_transparent',
      }.contains(spec['material']?.toString() ?? '')) {
        return false;
      }
    }

    final motion = _asMap(map['motion']);
    if (!_hasKeys(
      motion,
      const [
        'uiTransitionMs',
        'resumeFadeMs',
        'coldStartFadeMs',
        'coreReturnMs',
        'coreExpandScale',
        'corePressTightenScale',
      ],
    )) {
      return false;
    }

    final core = _asMap(map['core']);
    if (!_hasKeys(core, const ['materialProfile', 'idle', 'interaction', 'ripple'])) {
      return false;
    }
    final council = _asMap(map['council']);
    if (!_hasKeys(council, const ['dimOverlay', 'sigil'])) {
      return false;
    }
    final power = _asMap(map['power']);
    if (!_hasKeys(power, const ['extendedIdleMinutes', 'extendedIdleBrightnessDrop', 'lowPowerMode'])) {
      return false;
    }
    final audio = _asMap(map['audio']);
    if (!_hasKeys(audio, const ['tones', 'hermesReadyTone'])) {
      return false;
    }
    return true;
  }

  static bool _hasKeys(Map<String, Object?> map, List<String> keys) {
    for (final key in keys) {
      if (!map.containsKey(key)) {
        return false;
      }
    }
    return true;
  }

  static bool _isHexColor(Object? value) {
    final raw = value?.toString() ?? '';
    return _hexColorRegExp.hasMatch(raw);
  }
}

