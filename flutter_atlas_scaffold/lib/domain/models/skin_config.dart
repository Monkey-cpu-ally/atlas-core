import 'package:flutter/foundation.dart';

@immutable
class SkinConfig {
  const SkinConfig({
    required this.id,
    required this.label,
    required this.motionProfileId,
    required this.materialProfileId,
    required this.tokens,
  });

  final String id;
  final String label;
  final String motionProfileId;
  final String materialProfileId;
  final Map<String, Object?> tokens;

  factory SkinConfig.fromMap(Map<String, Object?> map) {
    final rawTokens = map['tokens'];
    return SkinConfig(
      id: map['id']?.toString() ?? 'unknown',
      label: map['label']?.toString() ?? 'Unknown',
      motionProfileId: map['motionProfileId']?.toString() ?? 'default',
      materialProfileId: map['materialProfileId']?.toString() ?? 'default',
      tokens: rawTokens is Map<String, Object?> ? rawTokens : const {},
    );
  }
}

