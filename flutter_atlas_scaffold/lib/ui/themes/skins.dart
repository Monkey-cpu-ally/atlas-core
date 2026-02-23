import 'package:flutter/material.dart';

import 'skin_tokens.dart';

class Skins {
  const Skins._();

  static const SkinTokens lumenCore = SkinTokens(
    id: 'lumen_core',
    background: Color(0xFF0F1117),
    surface: Color(0xFF1A1D27),
    frame: Color(0xFF2B3044),
    ring: Color(0xFF6B738A),
    textPrimary: Color(0xFFE7EBF8),
    textSecondary: Color(0xFFA7AEC4),
    accentEnergy: Color(0xFF7DB4FF),
    glassiness: 0.18,
    roughness: 0.65,
    noiseAmount: 0.08,
    grainEnabled: false,
  );

  static const SkinTokens archiveGrid = SkinTokens(
    id: 'archive_grid',
    background: Color(0xFF14161E),
    surface: Color(0xFF202433),
    frame: Color(0xFF39425A),
    ring: Color(0xFF8D98B3),
    textPrimary: Color(0xFFF2F5FF),
    textSecondary: Color(0xFFB8C1D8),
    accentEnergy: Color(0xFF9FC2FF),
    glassiness: 0.08,
    roughness: 0.78,
    noiseAmount: 0.15,
    grainEnabled: true,
  );

  static const SkinTokens circuitVeil = SkinTokens(
    id: 'circuit_veil',
    background: Color(0xFFEDEFF5),
    surface: Color(0xFFFFFFFF),
    frame: Color(0xFFD4D9E4),
    ring: Color(0xFF95A1B8),
    textPrimary: Color(0xFF242938),
    textSecondary: Color(0xFF58607A),
    accentEnergy: Color(0xFF4A77C9),
    glassiness: 0.42,
    roughness: 0.35,
    noiseAmount: 0.06,
    grainEnabled: false,
  );

  static const SkinTokens moduleArray = SkinTokens(
    id: 'module_array',
    background: Color(0xFF10131E),
    surface: Color(0xFF1A2133),
    frame: Color(0xFF2A3954),
    ring: Color(0xFF7689B2),
    textPrimary: Color(0xFFE9EEFF),
    textSecondary: Color(0xFFACB7D5),
    accentEnergy: Color(0xFF7CA6FF),
    glassiness: 0.24,
    roughness: 0.58,
    noiseAmount: 0.12,
    grainEnabled: true,
  );

  static const List<SkinTokens> all = <SkinTokens>[
    lumenCore,
    archiveGrid,
    circuitVeil,
    moduleArray,
  ];

  static SkinTokens byId(String id) {
    return all.firstWhere(
      (skin) => skin.id == id,
      orElse: () => lumenCore,
    );
  }
}

