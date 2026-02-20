import 'package:flutter/foundation.dart';

import '../../domain/models/ai_speaker.dart';

@immutable
class SpeakerState {
  const SpeakerState({
    this.currentSpeaker = AiSpeaker.none,
    this.listening = false,
    this.speaking = false,
    this.processing = false,
  });

  final AiSpeaker currentSpeaker;
  final bool listening;
  final bool speaking;
  final bool processing;

  SpeakerState copyWith({
    AiSpeaker? currentSpeaker,
    bool? listening,
    bool? speaking,
    bool? processing,
  }) {
    return SpeakerState(
      currentSpeaker: currentSpeaker ?? this.currentSpeaker,
      listening: listening ?? this.listening,
      speaking: speaking ?? this.speaking,
      processing: processing ?? this.processing,
    );
  }
}

