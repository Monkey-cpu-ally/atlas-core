import 'package:flutter/foundation.dart';

import 'appearance_lab_state.dart';
import 'council_state.dart';
import 'failure_state.dart';
import 'mode_state.dart';
import 'power_state.dart';
import 'ring_state.dart';
import 'skin_state.dart';
import 'speaker_state.dart';

@immutable
class AtlasAppState {
  const AtlasAppState({
    this.mode = const ModeState(),
    this.rings = const RingState(),
    this.speaker = const SpeakerState(),
    this.council = const CouncilState(),
    this.appearanceLab = const AppearanceLabState(),
    this.power = const PowerState(),
    this.failure = const FailureState(),
    this.skin = const SkinState(),
  });

  final ModeState mode;
  final RingState rings;
  final SpeakerState speaker;
  final CouncilState council;
  final AppearanceLabState appearanceLab;
  final PowerState power;
  final FailureState failure;
  final SkinState skin;

  AtlasAppState copyWith({
    ModeState? mode,
    RingState? rings,
    SpeakerState? speaker,
    CouncilState? council,
    AppearanceLabState? appearanceLab,
    PowerState? power,
    FailureState? failure,
    SkinState? skin,
  }) {
    return AtlasAppState(
      mode: mode ?? this.mode,
      rings: rings ?? this.rings,
      speaker: speaker ?? this.speaker,
      council: council ?? this.council,
      appearanceLab: appearanceLab ?? this.appearanceLab,
      power: power ?? this.power,
      failure: failure ?? this.failure,
      skin: skin ?? this.skin,
    );
  }
}

