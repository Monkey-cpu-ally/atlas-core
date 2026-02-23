import 'package:flutter/material.dart';

import '../../domain/models/ai_speaker.dart';

@immutable
class AiIdentity {
  const AiIdentity({
    required this.speaker,
    required this.label,
    required this.accent,
    required this.toneAsset,
  });

  final AiSpeaker speaker;
  final String label;
  final Color accent;
  final String toneAsset;
}

class AiIdentities {
  const AiIdentities._();

  static const neutral = Color(0xFF7A7A80);
  static const ghostPurple = Color(0xFF8D79B8);

  static const Ajani = AiIdentity(
    speaker: AiSpeaker.ajani,
    label: 'Ajani',
    accent: Color(0xFF9A2F3A),
    toneAsset: 'assets/audio/tone_ajani.wav',
  );

  static const Minerva = AiIdentity(
    speaker: AiSpeaker.minerva,
    label: 'Minerva',
    accent: Color(0xFF2B8E9A),
    toneAsset: 'assets/audio/tone_minerva.wav',
  );

  static const Hermes = AiIdentity(
    speaker: AiSpeaker.hermes,
    label: 'Hermes',
    accent: Color(0xFFE7DFC9),
    toneAsset: 'assets/audio/tone_hermes.wav',
  );

  static const Council = AiIdentity(
    speaker: AiSpeaker.council,
    label: 'Council',
    accent: ghostPurple,
    toneAsset: 'assets/audio/tone_council.wav',
  );

  static const List<AiIdentity> values = <AiIdentity>[
    Ajani,
    Minerva,
    Hermes,
    Council,
  ];

  static AiIdentity fromSpeaker(AiSpeaker speaker) {
    return values.firstWhere(
      (identity) => identity.speaker == speaker,
      orElse: () => Hermes,
    );
  }
}

