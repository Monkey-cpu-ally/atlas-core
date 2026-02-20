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
}

