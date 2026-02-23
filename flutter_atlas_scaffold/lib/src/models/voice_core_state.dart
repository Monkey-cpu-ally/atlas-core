import 'package:flutter/material.dart';

enum IdentitySpeaker { ajani, minerva, hermes }

enum VoiceMode { single, council }

enum VoiceCoreUiState {
  idle,
  listeningPendingName,
  listeningToAi,
  processing,
  speaking,
  councilActive,
  councilIdleGlow,
  speakingAjani,
  speakingMinerva,
  speakingHermes,
}

enum CouncilPhase {
  councilActive,
  speakingAjani,
  councilIdleGlow,
  speakingMinerva,
  speakingHermes,
  idle,
}

enum CoreRotationState { rotating, stopped, resumeRamp }

enum SigilRotationMode { static, ultraSlow }

@immutable
class CouncilSigilState {
  const CouncilSigilState({
    required this.visible,
    required this.opacityPercent,
    required this.rotationMode,
    required this.rotationPeriodSec,
  });

  const CouncilSigilState.hidden()
      : visible = false,
        opacityPercent = 0,
        rotationMode = SigilRotationMode.static,
        rotationPeriodSec = null;

  final bool visible;
  final double opacityPercent;
  final SigilRotationMode rotationMode;
  final double? rotationPeriodSec;

  CouncilSigilState copyWith({
    bool? visible,
    double? opacityPercent,
    SigilRotationMode? rotationMode,
    double? rotationPeriodSec,
  }) {
    return CouncilSigilState(
      visible: visible ?? this.visible,
      opacityPercent: opacityPercent ?? this.opacityPercent,
      rotationMode: rotationMode ?? this.rotationMode,
      rotationPeriodSec: rotationPeriodSec ?? this.rotationPeriodSec,
    );
  }
}

@immutable
class VoiceCoreVisualState {
  const VoiceCoreVisualState({
    required this.currentSpeaker,
    required this.currentState,
    required this.voiceMode,
    required this.councilPhase,
    required this.accentColor,
    required this.coreOverlayColor,
    required this.backgroundDimPercent,
    required this.coreScale,
    required this.coreRotationState,
    required this.councilSigil,
  });

  const VoiceCoreVisualState.idle()
      : currentSpeaker = null,
        currentState = VoiceCoreUiState.idle,
        voiceMode = VoiceMode.single,
        councilPhase = CouncilPhase.idle,
        accentColor = const Color(0xFF7A7A80),
        coreOverlayColor = null,
        backgroundDimPercent = 0,
        coreScale = 1.0,
        coreRotationState = CoreRotationState.rotating,
        councilSigil = const CouncilSigilState.hidden();

  final IdentitySpeaker? currentSpeaker;
  final VoiceCoreUiState currentState;
  final VoiceMode voiceMode;
  final CouncilPhase councilPhase;
  final Color accentColor;
  final Color? coreOverlayColor;
  final double backgroundDimPercent;
  final double coreScale;
  final CoreRotationState coreRotationState;
  final CouncilSigilState councilSigil;

  VoiceCoreVisualState copyWith({
    IdentitySpeaker? currentSpeaker,
    bool clearCurrentSpeaker = false,
    VoiceCoreUiState? currentState,
    VoiceMode? voiceMode,
    CouncilPhase? councilPhase,
    Color? accentColor,
    Color? coreOverlayColor,
    bool clearCoreOverlayColor = false,
    double? backgroundDimPercent,
    double? coreScale,
    CoreRotationState? coreRotationState,
    CouncilSigilState? councilSigil,
  }) {
    return VoiceCoreVisualState(
      currentSpeaker:
          clearCurrentSpeaker ? null : (currentSpeaker ?? this.currentSpeaker),
      currentState: currentState ?? this.currentState,
      voiceMode: voiceMode ?? this.voiceMode,
      councilPhase: councilPhase ?? this.councilPhase,
      accentColor: accentColor ?? this.accentColor,
      coreOverlayColor: clearCoreOverlayColor
          ? null
          : (coreOverlayColor ?? this.coreOverlayColor),
      backgroundDimPercent:
          backgroundDimPercent ?? this.backgroundDimPercent,
      coreScale: coreScale ?? this.coreScale,
      coreRotationState: coreRotationState ?? this.coreRotationState,
      councilSigil: councilSigil ?? this.councilSigil,
    );
  }
}
