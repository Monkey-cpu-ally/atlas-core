import 'package:flutter/material.dart';

import '../models/voice_core_state.dart';

typedef DelayFn = Future<void> Function(Duration duration);

class VoiceCoreController extends ChangeNotifier {
  VoiceCoreController({
    DelayFn? delayFn,
    VoiceCoreVisualState? initialState,
  })  : _delayFn = delayFn ?? Future<void>.delayed,
        _state = initialState ?? const VoiceCoreVisualState.idle();

  static const Duration councilSigilDelay = Duration(milliseconds: 300);
  static const Duration councilSigilFadeOutDuration =
      Duration(milliseconds: 500);

  static const Color neutralAccent = Color(0xFF7A7A80);
  static const Color ghostPurpleAccent = Color(0xFF8D79B8);
  static const Color ajaniAccent = Color(0xFF9A2F3A);
  static const Color minervaAccent = Color(0xFF2B8E9A);
  static const Color hermesAccent = Color(0xFFE7DFC9);

  final DelayFn _delayFn;
  VoiceCoreVisualState _state;

  VoiceCoreVisualState get state => _state;

  Future<void> enterCouncilActive({
    double backgroundDimPercent = 8,
    SigilRotationMode sigilRotationMode = SigilRotationMode.static,
    double sigilOpacityPercent = 12,
    double? sigilRotationPeriodSec,
  }) async {
    final boundedDim = backgroundDimPercent.clamp(0, 10).toDouble();
    final boundedOpacity = sigilOpacityPercent.clamp(8, 15).toDouble();
    final boundedRotationPeriod = sigilRotationMode == SigilRotationMode.ultraSlow
        ? (sigilRotationPeriodSec ?? 45).clamp(30, 60).toDouble()
        : null;

    _state = _state.copyWith(
      clearCurrentSpeaker: true,
      clearCoreOverlayColor: true,
      voiceMode: VoiceMode.council,
      currentState: VoiceCoreUiState.councilActive,
      councilPhase: CouncilPhase.councilActive,
      accentColor: ghostPurpleAccent,
      backgroundDimPercent: boundedDim,
      coreScale: 1.08,
      coreRotationState: CoreRotationState.stopped,
      councilSigil: CouncilSigilState(
        visible: false,
        opacityPercent: boundedOpacity,
        rotationMode: sigilRotationMode,
        rotationPeriodSec: boundedRotationPeriod,
      ),
    );
    notifyListeners();

    await _delayFn(councilSigilDelay);
    if (_state.currentState != VoiceCoreUiState.councilActive) {
      return;
    }
    _state = _state.copyWith(
      councilSigil: _state.councilSigil.copyWith(visible: true),
    );
    notifyListeners();
  }

  void setCouncilSpeaker(IdentitySpeaker speaker) {
    final speakerState = switch (speaker) {
      IdentitySpeaker.ajani => VoiceCoreUiState.speakingAjani,
      IdentitySpeaker.minerva => VoiceCoreUiState.speakingMinerva,
      IdentitySpeaker.hermes => VoiceCoreUiState.speakingHermes,
    };

    final speakerPhase = switch (speaker) {
      IdentitySpeaker.ajani => CouncilPhase.speakingAjani,
      IdentitySpeaker.minerva => CouncilPhase.speakingMinerva,
      IdentitySpeaker.hermes => CouncilPhase.speakingHermes,
    };

    _state = _state.copyWith(
      currentSpeaker: speaker,
      currentState: speakerState,
      councilPhase: speakerPhase,
      accentColor: ghostPurpleAccent,
      coreOverlayColor: _speakerOverlay(speaker),
      councilSigil: _state.councilSigil.copyWith(visible: true),
    );
    notifyListeners();
  }

  void setCouncilPause() {
    _state = _state.copyWith(
      clearCurrentSpeaker: true,
      clearCoreOverlayColor: true,
      currentState: VoiceCoreUiState.councilIdleGlow,
      councilPhase: CouncilPhase.councilIdleGlow,
      accentColor: ghostPurpleAccent,
      councilSigil: _state.councilSigil.copyWith(visible: true),
    );
    notifyListeners();
  }

  Future<void> completeCouncil() async {
    _state = _state.copyWith(
      clearCurrentSpeaker: true,
      clearCoreOverlayColor: true,
      currentState: VoiceCoreUiState.councilActive,
      councilPhase: CouncilPhase.councilActive,
      councilSigil: _state.councilSigil.copyWith(visible: false),
    );
    notifyListeners();

    await _delayFn(councilSigilFadeOutDuration);
    _state = _state.copyWith(
      voiceMode: VoiceMode.single,
      currentState: VoiceCoreUiState.idle,
      councilPhase: CouncilPhase.idle,
      accentColor: neutralAccent,
      backgroundDimPercent: 0,
      coreScale: 1.0,
      coreRotationState: CoreRotationState.resumeRamp,
      councilSigil: const CouncilSigilState.hidden(),
    );
    notifyListeners();
  }

  void resetIdle() {
    _state = const VoiceCoreVisualState.idle();
    notifyListeners();
  }

  static String uiStateId(VoiceCoreUiState state) {
    return switch (state) {
      VoiceCoreUiState.idle => 'IDLE',
      VoiceCoreUiState.listeningPendingName => 'LISTENING_PENDING_NAME',
      VoiceCoreUiState.listeningToAi => 'LISTENING_TO_AI',
      VoiceCoreUiState.processing => 'PROCESSING',
      VoiceCoreUiState.speaking => 'SPEAKING',
      VoiceCoreUiState.councilActive => 'COUNCIL_ACTIVE',
      VoiceCoreUiState.councilIdleGlow => 'COUNCIL_IDLE_GLOW',
      VoiceCoreUiState.speakingAjani => 'SPEAKING_AJANI',
      VoiceCoreUiState.speakingMinerva => 'SPEAKING_MINERVA',
      VoiceCoreUiState.speakingHermes => 'SPEAKING_HERMES',
    };
  }

  static String councilPhaseId(CouncilPhase phase) {
    return switch (phase) {
      CouncilPhase.councilActive => 'COUNCIL_ACTIVE',
      CouncilPhase.speakingAjani => 'SPEAKING_AJANI',
      CouncilPhase.councilIdleGlow => 'COUNCIL_IDLE_GLOW',
      CouncilPhase.speakingMinerva => 'SPEAKING_MINERVA',
      CouncilPhase.speakingHermes => 'SPEAKING_HERMES',
      CouncilPhase.idle => 'IDLE',
    };
  }

  static String rotationStateId(CoreRotationState rotationState) {
    return switch (rotationState) {
      CoreRotationState.rotating => 'rotating',
      CoreRotationState.stopped => 'stopped',
      CoreRotationState.resumeRamp => 'resume_ramp',
    };
  }

  static String sigilRotationModeId(SigilRotationMode mode) {
    return switch (mode) {
      SigilRotationMode.static => 'static',
      SigilRotationMode.ultraSlow => 'ultra_slow',
    };
  }

  Color _speakerOverlay(IdentitySpeaker speaker) {
    return switch (speaker) {
      IdentitySpeaker.ajani => ajaniAccent,
      IdentitySpeaker.minerva => minervaAccent,
      IdentitySpeaker.hermes => hermesAccent,
    };
  }
}
