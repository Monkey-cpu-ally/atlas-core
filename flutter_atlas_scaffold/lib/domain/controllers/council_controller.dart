import 'package:flutter/foundation.dart';

import '../../core/constants/timings.dart';
import '../../core/state/council_state.dart';
import '../models/ai_speaker.dart';

class CouncilController extends ChangeNotifier {
  CouncilState _state = const CouncilState();

  CouncilState get state => _state;

  static const List<AiSpeaker> order = <AiSpeaker>[
    AiSpeaker.ajani,
    AiSpeaker.minerva,
    AiSpeaker.hermes,
  ];

  void activate() {
    _state = _state.copyWith(
      active: true,
      stage: CouncilStage.active,
      currentTurnIndex: 0,
      stillnessLocked: true,
    );
    notifyListeners();
  }

  AiSpeaker currentSpeaker() {
    if (!_state.active || _state.currentTurnIndex >= order.length) {
      return AiSpeaker.none;
    }
    return order[_state.currentTurnIndex];
  }

  void startCurrentSpeakerTurn() {
    if (!_state.active) {
      return;
    }
    final stage = switch (currentSpeaker()) {
      AiSpeaker.ajani => CouncilStage.speakingAjani,
      AiSpeaker.minerva => CouncilStage.speakingMinerva,
      AiSpeaker.hermes => CouncilStage.speakingHermes,
      _ => CouncilStage.idle,
    };
    _state = _state.copyWith(stage: stage);
    notifyListeners();
  }

  Future<void> pauseBetweenTurns() async {
    if (!_state.active) {
      return;
    }
    _state = _state.copyWith(stage: CouncilStage.glowPause);
    notifyListeners();
    await Future<void>.delayed(Timings.councilPause);
    _state = _state.copyWith(currentTurnIndex: _state.currentTurnIndex + 1);
    notifyListeners();
  }

  Future<void> complete() async {
    _state = _state.copyWith(
      stage: CouncilStage.idle,
      active: false,
      currentTurnIndex: 0,
      stillnessLocked: false,
    );
    notifyListeners();
  }

  void reset() {
    _state = const CouncilState();
    notifyListeners();
  }
}

