enum AiSpeaker {
  none,
  ajani,
  minerva,
  hermes,
  council,
}

extension AiSpeakerX on AiSpeaker {
  String get id => switch (this) {
        AiSpeaker.none => 'none',
        AiSpeaker.ajani => 'ajani',
        AiSpeaker.minerva => 'minerva',
        AiSpeaker.hermes => 'hermes',
        AiSpeaker.council => 'council',
      };
}

