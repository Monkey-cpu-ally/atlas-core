import 'package:flutter/foundation.dart';

enum CouncilStage {
  idle,
  active,
  speakingAjani,
  glowPause,
  speakingMinerva,
  speakingHermes,
}

@immutable
class CouncilState {
  const CouncilState({
    this.active = false,
    this.stage = CouncilStage.idle,
    this.currentTurnIndex = 0,
    this.stillnessLocked = false,
  });

  final bool active;
  final CouncilStage stage;
  final int currentTurnIndex;
  final bool stillnessLocked;

  CouncilState copyWith({
    bool? active,
    CouncilStage? stage,
    int? currentTurnIndex,
    bool? stillnessLocked,
  }) {
    return CouncilState(
      active: active ?? this.active,
      stage: stage ?? this.stage,
      currentTurnIndex: currentTurnIndex ?? this.currentTurnIndex,
      stillnessLocked: stillnessLocked ?? this.stillnessLocked,
    );
  }
}

