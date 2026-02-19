import 'package:flutter/material.dart';

import '../models/voice_core_state.dart';
import '../models/voice_core_timing.dart';

typedef DelayFn = Future<void> Function(Duration duration);

class VoiceCoreController extends ChangeNotifier {
  VoiceCoreController({
    DelayFn? delayFn,
    VoiceCoreVisualState? initialState,
    VoiceCoreTiming timing = VoiceCoreTiming.spec,
  })  : _delayFn = delayFn ?? Future<void>.delayed,
        _timing = timing,
        _state = initialState ?? const VoiceCoreVisualState.idle();

  static const Color neutralAccent = Color(0xFF7A7A80);
  static const Color ghostPurpleAccent = Color(0xFF8D79B8);
  static const Color ajaniAccent = Color(0xFF9A2F3A);
  static const Color minervaAccent = Color(0xFF2B8E9A);
  static const Color hermesAccent = Color(0xFFE7DFC9);
  static const List<IdentitySpeaker> councilSpeakerOrder = <IdentitySpeaker>[
    IdentitySpeaker.ajani,
    IdentitySpeaker.minerva,
    IdentitySpeaker.hermes,
  ];

  final DelayFn _delayFn;
  final VoiceCoreTiming _timing;
  VoiceCoreVisualState _state;
  var _timelineToken = 0;
  var _nextSpeakerIndex = 0;
  var _appearanceLabActive = false;

  VoiceCoreTiming get timing => _timing;
  VoiceCoreVisualState get state => _state;
  bool get isAppearanceLabActive => _appearanceLabActive;

  Future<void> enterCouncilActive({
    double backgroundDimPercent = 8,
    SigilRotationMode sigilRotationMode = SigilRotationMode.static,
    double sigilOpacityPercent = 12,
    double? sigilRotationPeriodSec,
  }) async {
    if (_appearanceLabActive) {
      return;
    }
    final boundedDim = _clampBackgroundDim(backgroundDimPercent);
    final boundedOpacity = _clampSigilOpacity(sigilOpacityPercent);
    final boundedRotationPeriod = sigilRotationMode == SigilRotationMode.ultraSlow
        ? _clampSigilRotationPeriod(sigilRotationPeriodSec ?? 45)
        : null;
    final token = _advanceTimeline();
    _nextSpeakerIndex = 0;

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

    await _delayFn(_timing.councilSigilRevealDelay);
    if (!_isCurrentTimeline(token)) {
      return;
    }
    if (_state.currentState != VoiceCoreUiState.councilActive ||
        _state.voiceMode != VoiceMode.council) {
      return;
    }
    _state = _state.copyWith(
      councilSigil: _state.councilSigil.copyWith(visible: true),
    );
    notifyListeners();
  }

  bool setCouncilSpeaker(IdentitySpeaker speaker) {
    if (_appearanceLabActive) {
      return false;
    }
    if (!_canMoveToSpeaker(speaker)) {
      return false;
    }

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
    _nextSpeakerIndex += 1;
    notifyListeners();
    return true;
  }

  bool setCouncilPause() {
    if (_appearanceLabActive) {
      return false;
    }
    final isPauseAllowed = _state.currentState == VoiceCoreUiState.speakingAjani ||
        _state.currentState == VoiceCoreUiState.speakingMinerva;
    if (!isPauseAllowed) {
      return false;
    }

    _state = _state.copyWith(
      clearCurrentSpeaker: true,
      clearCoreOverlayColor: true,
      currentState: VoiceCoreUiState.councilIdleGlow,
      councilPhase: CouncilPhase.councilIdleGlow,
      accentColor: ghostPurpleAccent,
      councilSigil: _state.councilSigil.copyWith(visible: true),
    );
    notifyListeners();
    return true;
  }

  Future<bool> completeCouncil() async {
    if (_appearanceLabActive) {
      return false;
    }
    if (_state.currentState != VoiceCoreUiState.speakingHermes ||
        _nextSpeakerIndex != councilSpeakerOrder.length) {
      return false;
    }
    final token = _advanceTimeline();

    _state = _state.copyWith(
      clearCurrentSpeaker: true,
      clearCoreOverlayColor: true,
      currentState: VoiceCoreUiState.councilActive,
      councilPhase: CouncilPhase.councilActive,
      councilSigil: _state.councilSigil.copyWith(visible: false),
    );
    notifyListeners();

    await _delayFn(_timing.councilSigilFadeOutDuration);
    if (!_isCurrentTimeline(token)) {
      return false;
    }
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
    _nextSpeakerIndex = 0;
    notifyListeners();
    return true;
  }

  void synchronizeCouncilPhase({
    required CouncilPhase phase,
    required CoreRotationState coreRotationState,
    required double backgroundDimPercent,
    required bool sigilVisible,
    required SigilRotationMode sigilRotationMode,
    double? sigilOpacityPercent,
    double? sigilRotationPeriodSec,
  }) {
    if (_appearanceLabActive) {
      return;
    }
    _advanceTimeline();
    final speaker = _speakerForPhase(phase);
    final boundedDim = _clampBackgroundDim(backgroundDimPercent);
    final boundedOpacity = _clampSigilOpacity(sigilOpacityPercent ?? 12);
    final boundedRotationPeriod = sigilRotationMode == SigilRotationMode.ultraSlow
        ? _clampSigilRotationPeriod(sigilRotationPeriodSec ?? 45)
        : null;
    final isIdle = phase == CouncilPhase.idle;

    _nextSpeakerIndex = _speakerIndexForPhase(phase);
    _state = _state.copyWith(
      currentSpeaker: speaker,
      clearCurrentSpeaker: speaker == null,
      currentState: _uiStateForPhase(phase),
      voiceMode: isIdle ? VoiceMode.single : VoiceMode.council,
      councilPhase: phase,
      accentColor: isIdle ? neutralAccent : ghostPurpleAccent,
      coreOverlayColor: speaker != null ? _speakerOverlay(speaker) : null,
      clearCoreOverlayColor: speaker == null,
      backgroundDimPercent: isIdle ? 0 : boundedDim,
      coreScale: isIdle ? 1.0 : 1.08,
      coreRotationState: coreRotationState,
      councilSigil: isIdle
          ? const CouncilSigilState.hidden()
          : CouncilSigilState(
              visible: sigilVisible,
              opacityPercent: sigilVisible ? boundedOpacity : 0,
              rotationMode: sigilRotationMode,
              rotationPeriodSec: sigilVisible ? boundedRotationPeriod : null,
            ),
    );
    notifyListeners();
  }

  void resetIdle() {
    _advanceTimeline();
    _appearanceLabActive = false;
    _nextSpeakerIndex = 0;
    _state = const VoiceCoreVisualState.idle();
    notifyListeners();
  }

  /// Appearance Lab ("calibration") visual state:
  /// - Hermes active accent (Ivory)
  /// - Background dim (5-8%)
  /// - No council/sigil
  /// - Core rotation should slow but not fully stop (handled by renderer)
  void enterAppearanceLab({
    double backgroundDimPercent = 6,
  }) {
    final boundedDim = backgroundDimPercent.clamp(5, 8).toDouble();
    _advanceTimeline();
    _appearanceLabActive = true;
    _nextSpeakerIndex = 0;

    _state = _state.copyWith(
      voiceMode: VoiceMode.single,
      clearCoreOverlayColor: true,
      currentSpeaker: IdentitySpeaker.hermes,
      currentState: VoiceCoreUiState.idle,
      councilPhase: CouncilPhase.idle,
      accentColor: hermesAccent,
      backgroundDimPercent: boundedDim,
      coreScale: 1.0,
      coreRotationState: CoreRotationState.rotating,
      councilSigil: const CouncilSigilState.hidden(),
    );
    notifyListeners();
  }

  void exitAppearanceLab() {
    _advanceTimeline();
    _appearanceLabActive = false;
    _nextSpeakerIndex = 0;
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

  static CouncilPhase councilPhaseFromId(String phase) {
    return switch (phase) {
      'COUNCIL_ACTIVE' => CouncilPhase.councilActive,
      'SPEAKING_AJANI' => CouncilPhase.speakingAjani,
      'COUNCIL_IDLE_GLOW' => CouncilPhase.councilIdleGlow,
      'SPEAKING_MINERVA' => CouncilPhase.speakingMinerva,
      'SPEAKING_HERMES' => CouncilPhase.speakingHermes,
      'IDLE' => CouncilPhase.idle,
      _ => throw FormatException('Unknown council phase: $phase'),
    };
  }

  static CoreRotationState coreRotationStateFromId(String state) {
    return switch (state) {
      'rotating' => CoreRotationState.rotating,
      'stopped' => CoreRotationState.stopped,
      'resume_ramp' => CoreRotationState.resumeRamp,
      _ => throw FormatException('Unknown core rotation state: $state'),
    };
  }

  static SigilRotationMode sigilRotationModeFromId(String mode) {
    return switch (mode) {
      'static' => SigilRotationMode.static,
      'ultra_slow' => SigilRotationMode.ultraSlow,
      _ => throw FormatException('Unknown sigil rotation mode: $mode'),
    };
  }

  bool _canMoveToSpeaker(IdentitySpeaker speaker) {
    if (_state.voiceMode != VoiceMode.council) {
      return false;
    }
    if (_nextSpeakerIndex >= councilSpeakerOrder.length) {
      return false;
    }
    final expectedSpeaker = councilSpeakerOrder[_nextSpeakerIndex];
    if (speaker != expectedSpeaker) {
      return false;
    }

    if (_nextSpeakerIndex == 0) {
      return _state.currentState == VoiceCoreUiState.councilActive ||
          _state.currentState == VoiceCoreUiState.councilIdleGlow;
    }
    return _state.currentState == VoiceCoreUiState.councilIdleGlow;
  }

  IdentitySpeaker? _speakerForPhase(CouncilPhase phase) {
    return switch (phase) {
      CouncilPhase.speakingAjani => IdentitySpeaker.ajani,
      CouncilPhase.speakingMinerva => IdentitySpeaker.minerva,
      CouncilPhase.speakingHermes => IdentitySpeaker.hermes,
      CouncilPhase.councilActive ||
      CouncilPhase.councilIdleGlow ||
      CouncilPhase.idle => null,
    };
  }

  VoiceCoreUiState _uiStateForPhase(CouncilPhase phase) {
    return switch (phase) {
      CouncilPhase.councilActive => VoiceCoreUiState.councilActive,
      CouncilPhase.speakingAjani => VoiceCoreUiState.speakingAjani,
      CouncilPhase.councilIdleGlow => VoiceCoreUiState.councilIdleGlow,
      CouncilPhase.speakingMinerva => VoiceCoreUiState.speakingMinerva,
      CouncilPhase.speakingHermes => VoiceCoreUiState.speakingHermes,
      CouncilPhase.idle => VoiceCoreUiState.idle,
    };
  }

  int _speakerIndexForPhase(CouncilPhase phase) {
    return switch (phase) {
      CouncilPhase.councilActive => 0,
      CouncilPhase.speakingAjani => 1,
      CouncilPhase.speakingMinerva => 2,
      CouncilPhase.speakingHermes => 3,
      CouncilPhase.councilIdleGlow => _nextSpeakerIndex.clamp(1, 2).toInt(),
      CouncilPhase.idle => 0,
    };
  }

  int _advanceTimeline() {
    _timelineToken += 1;
    return _timelineToken;
  }

  bool _isCurrentTimeline(int token) {
    return token == _timelineToken;
  }

  double _clampBackgroundDim(double dimPercent) {
    return dimPercent
        .clamp(_timing.minBackgroundDimPercent, _timing.maxBackgroundDimPercent)
        .toDouble();
  }

  double _clampSigilOpacity(double opacityPercent) {
    return opacityPercent
        .clamp(_timing.minSigilOpacityPercent, _timing.maxSigilOpacityPercent)
        .toDouble();
  }

  double _clampSigilRotationPeriod(double rotationPeriodSec) {
    return rotationPeriodSec
        .clamp(
          _timing.minSigilRotationPeriodSec,
          _timing.maxSigilRotationPeriodSec,
        )
        .toDouble();
  }

  Color _speakerOverlay(IdentitySpeaker speaker) {
    return switch (speaker) {
      IdentitySpeaker.ajani => ajaniAccent,
      IdentitySpeaker.minerva => minervaAccent,
      IdentitySpeaker.hermes => hermesAccent,
    };
  }
}
