import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import '../../domain/models/skin_config.dart';
import 'skin_tokens.dart';
import 'skins.dart';

class SkinResolver {
  const SkinResolver._();

  static Future<SkinTokens> resolve(String skinId) async {
    try {
      final jsonPath = 'assets/skins/$skinId.json';
      final raw = await rootBundle.loadString(jsonPath);
      final map = jsonDecode(raw);
      if (map is! Map<String, Object?>) {
        return Skins.byId(skinId);
      }
      final config = SkinConfig.fromMap(map);
      return _fromConfig(config);
    } catch (_) {
      return Skins.byId(skinId);
    }
  }

  static SkinTokens _fromConfig(SkinConfig config) {
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
}

