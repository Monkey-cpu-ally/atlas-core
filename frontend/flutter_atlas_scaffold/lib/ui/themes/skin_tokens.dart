import 'package:flutter/material.dart';

@immutable
class SkinTokens {
  const SkinTokens({
    required this.id,
    required this.background,
    required this.surface,
    required this.frame,
    required this.ring,
    required this.textPrimary,
    required this.textSecondary,
    required this.accentEnergy,
    this.glassiness = 0.2,
    this.roughness = 0.5,
    this.noiseAmount = 0.1,
    this.grainEnabled = false,
    this.panelCornerRadius = 12,
    this.panelElevation = 10,
    this.councilDimStrength = 0.08,
    this.shadow = const Color(0xFF000000),
    this.highlight = const Color(0xFFFFFFFF),
    this.gradientFrom,
    this.gradientTo,
    this.gradientAngleDeg = 90,
    this.textureEnabled = false,
    this.textureAsset = '',
    this.textureOpacity = 0,
    this.noiseEnabled = false,
    this.noiseAsset = '',
    this.noiseOpacity = 0,
    this.councilGhostPurple = const Color(0xFFBFA7FF),
    this.ajaniCrimson = const Color(0xFFB21D2A),
    this.minervaTeal = const Color(0xFF2BB9B0),
    this.hermesIvory = const Color(0xFFF2E9DA),
    this.dangerPulse = const Color(0xFFB21D2A),
  });

  final String id;
  final Color background;
  final Color surface;
  final Color frame;
  final Color ring;
  final Color textPrimary;
  final Color textSecondary;
  final Color accentEnergy;
  final double glassiness;
  final double roughness;
  final double noiseAmount;
  final bool grainEnabled;
  final double panelCornerRadius;
  final double panelElevation;
  final double councilDimStrength;
  final Color shadow;
  final Color highlight;
  final Color? gradientFrom;
  final Color? gradientTo;
  final double gradientAngleDeg;
  final bool textureEnabled;
  final String textureAsset;
  final double textureOpacity;
  final bool noiseEnabled;
  final String noiseAsset;
  final double noiseOpacity;
  final Color councilGhostPurple;
  final Color ajaniCrimson;
  final Color minervaTeal;
  final Color hermesIvory;
  final Color dangerPulse;

  SkinTokens copyWith({
    String? id,
    Color? background,
    Color? surface,
    Color? frame,
    Color? ring,
    Color? textPrimary,
    Color? textSecondary,
    Color? accentEnergy,
    double? glassiness,
    double? roughness,
    double? noiseAmount,
    bool? grainEnabled,
    double? panelCornerRadius,
    double? panelElevation,
    double? councilDimStrength,
    Color? shadow,
    Color? highlight,
    Color? gradientFrom,
    bool clearGradientFrom = false,
    Color? gradientTo,
    bool clearGradientTo = false,
    double? gradientAngleDeg,
    bool? textureEnabled,
    String? textureAsset,
    double? textureOpacity,
    bool? noiseEnabled,
    String? noiseAsset,
    double? noiseOpacity,
    Color? councilGhostPurple,
    Color? ajaniCrimson,
    Color? minervaTeal,
    Color? hermesIvory,
    Color? dangerPulse,
  }) {
    return SkinTokens(
      id: id ?? this.id,
      background: background ?? this.background,
      surface: surface ?? this.surface,
      frame: frame ?? this.frame,
      ring: ring ?? this.ring,
      textPrimary: textPrimary ?? this.textPrimary,
      textSecondary: textSecondary ?? this.textSecondary,
      accentEnergy: accentEnergy ?? this.accentEnergy,
      glassiness: glassiness ?? this.glassiness,
      roughness: roughness ?? this.roughness,
      noiseAmount: noiseAmount ?? this.noiseAmount,
      grainEnabled: grainEnabled ?? this.grainEnabled,
      panelCornerRadius: panelCornerRadius ?? this.panelCornerRadius,
      panelElevation: panelElevation ?? this.panelElevation,
      councilDimStrength: councilDimStrength ?? this.councilDimStrength,
      shadow: shadow ?? this.shadow,
      highlight: highlight ?? this.highlight,
      gradientFrom:
          clearGradientFrom ? null : (gradientFrom ?? this.gradientFrom),
      gradientTo: clearGradientTo ? null : (gradientTo ?? this.gradientTo),
      gradientAngleDeg: gradientAngleDeg ?? this.gradientAngleDeg,
      textureEnabled: textureEnabled ?? this.textureEnabled,
      textureAsset: textureAsset ?? this.textureAsset,
      textureOpacity: textureOpacity ?? this.textureOpacity,
      noiseEnabled: noiseEnabled ?? this.noiseEnabled,
      noiseAsset: noiseAsset ?? this.noiseAsset,
      noiseOpacity: noiseOpacity ?? this.noiseOpacity,
      councilGhostPurple: councilGhostPurple ?? this.councilGhostPurple,
      ajaniCrimson: ajaniCrimson ?? this.ajaniCrimson,
      minervaTeal: minervaTeal ?? this.minervaTeal,
      hermesIvory: hermesIvory ?? this.hermesIvory,
      dangerPulse: dangerPulse ?? this.dangerPulse,
    );
  }
}

