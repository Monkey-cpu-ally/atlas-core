import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';

/// Free-selection skin system (Mode != Skin).
///
/// - Mode = function
/// - Skin = atmosphere
///
/// Skins are user-selectable at any time and persist until manually changed.
enum AtlasSkinId {
  lumenCore,
  archiveGrid,
  circuitVeil,
  moduleArray,
}

extension AtlasSkinIdX on AtlasSkinId {
  String get id => switch (this) {
        AtlasSkinId.lumenCore => 'lumen_core',
        AtlasSkinId.archiveGrid => 'archive_grid',
        AtlasSkinId.circuitVeil => 'circuit_veil',
        AtlasSkinId.moduleArray => 'module_array',
      };

  String get label => switch (this) {
        AtlasSkinId.lumenCore => 'LUMEN CORE',
        AtlasSkinId.archiveGrid => 'ARCHIVE GRID',
        AtlasSkinId.circuitVeil => 'CIRCUIT VEIL',
        AtlasSkinId.moduleArray => 'MODULE ARRAY',
      };

  static AtlasSkinId fromId(String? value, {AtlasSkinId fallback = AtlasSkinId.lumenCore}) {
    final v = (value ?? '').trim().toLowerCase();
    return switch (v) {
      'lumen_core' => AtlasSkinId.lumenCore,
      'archive_grid' => AtlasSkinId.archiveGrid,
      'circuit_veil' => AtlasSkinId.circuitVeil,
      'module_array' => AtlasSkinId.moduleArray,
      _ => fallback,
    };
  }
}

@immutable
class AtlasSkinTokens {
  const AtlasSkinTokens({
    required this.brightness,
    required this.background,
    required this.surface,
    required this.border,
    required this.textPrimary,
    required this.textSecondary,
    required this.ringStroke,
    required this.ringOpacity,
    required this.ringStrokeWidth,
  });

  final Brightness brightness;
  final Color background;
  final Color surface;
  final Color border;
  final Color textPrimary;
  final Color textSecondary;
  final Color ringStroke;
  final double ringOpacity;
  final double ringStrokeWidth;
}

class AtlasSkins {
  const AtlasSkins._();

  /// Spec target: 400–600ms smooth crossfade (no hard cuts).
  static const Duration transitionDuration = Duration(milliseconds: 500);

  static AtlasSkinTokens tokens(AtlasSkinId skin) {
    return switch (skin) {
      AtlasSkinId.lumenCore => const AtlasSkinTokens(
          brightness: Brightness.dark,
          background: Color(0xFF0B0B10),
          surface: Color(0xFF12121A),
          border: Color(0xFF222235),
          textPrimary: Color(0xFFE6E6F2),
          textSecondary: Color(0xFFB8B8C8),
          ringStroke: Color(0xFF6A6A72),
          ringOpacity: 0.34,
          ringStrokeWidth: 1.15,
        ),
      AtlasSkinId.archiveGrid => const AtlasSkinTokens(
          brightness: Brightness.dark,
          background: Color(0xFF0A0A0F),
          surface: Color(0xFF141421),
          border: Color(0xFF2A2A44),
          textPrimary: Color(0xFFEDEDF7),
          textSecondary: Color(0xFFC2C2D4),
          ringStroke: Color(0xFF737384),
          ringOpacity: 0.38,
          ringStrokeWidth: 1.35,
        ),
      AtlasSkinId.circuitVeil => const AtlasSkinTokens(
          brightness: Brightness.light,
          background: Color(0xFFF2F3F7),
          surface: Color(0xFFFFFFFF),
          border: Color(0xFFD6D9E5),
          textPrimary: Color(0xFF0B0B10),
          textSecondary: Color(0xFF2D2D3A),
          ringStroke: Color(0xFF6A6A72),
          ringOpacity: 0.22,
          ringStrokeWidth: 1.10,
        ),
      AtlasSkinId.moduleArray => const AtlasSkinTokens(
          brightness: Brightness.dark,
          background: Color(0xFF090A0E),
          surface: Color(0xFF111821),
          border: Color(0xFF1E2A36),
          textPrimary: Color(0xFFE6F0FA),
          textSecondary: Color(0xFFB6C6D6),
          ringStroke: Color(0xFF7A8796),
          ringOpacity: 0.34,
          ringStrokeWidth: 1.25,
        ),
    };
  }

  static ThemeData themeData(
    AtlasSkinId skin, {
    ThemeData? base,
  }) {
    final t = tokens(skin);
    final baseTheme = base ??
        ThemeData(
          brightness: t.brightness,
          useMaterial3: false,
        );

    final scheme = baseTheme.colorScheme.copyWith(
      brightness: t.brightness,
      surface: t.surface,
      outline: t.border,
      onSurface: t.textPrimary,
    );

    final textTheme = baseTheme.textTheme.apply(
      bodyColor: t.textPrimary,
      displayColor: t.textPrimary,
    );

    return baseTheme.copyWith(
      scaffoldBackgroundColor: t.background,
      colorScheme: scheme,
      textTheme: textTheme,
    );
  }
}
