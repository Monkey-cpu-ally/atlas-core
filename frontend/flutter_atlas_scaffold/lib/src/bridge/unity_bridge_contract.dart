import '../controllers/voice_core_controller.dart';
import '../models/voice_core_state.dart';

abstract class UnityBridgeTransport {
  Future<void> sendEvent({
    required String eventName,
    required Map<String, Object?> payload,
  });
}

class UnityBridgeEventNames {
  const UnityBridgeEventNames._();

  static const String councilPhaseChanged = 'v1.councilPhaseChanged';
}

class UnityBridgeEmitter {
  const UnityBridgeEmitter(this.transport);

  final UnityBridgeTransport transport;

  Future<void> emitCouncilPhaseChanged({
    required VoiceCoreVisualState state,
    int? pauseMs,
  }) {
    final payload = CouncilPhaseChangedPayload.fromState(
      state: state,
      pauseMs: pauseMs,
    );
    return transport.sendEvent(
      eventName: UnityBridgeEventNames.councilPhaseChanged,
      payload: payload.toMap(),
    );
  }
}

class CouncilPhaseChangedPayload {
  const CouncilPhaseChangedPayload({
    required this.phase,
    required this.coreRotationState,
    required this.backgroundDimPercent,
    required this.sigilVisible,
    required this.sigilRotationMode,
    this.sigilOpacityPercent,
    this.sigilRotationPeriodSec,
    this.pauseMs,
  });

  factory CouncilPhaseChangedPayload.fromState({
    required VoiceCoreVisualState state,
    int? pauseMs,
  }) {
    return CouncilPhaseChangedPayload(
      phase: VoiceCoreController.councilPhaseId(state.councilPhase),
      coreRotationState:
          VoiceCoreController.rotationStateId(state.coreRotationState),
      backgroundDimPercent: state.backgroundDimPercent,
      sigilVisible: state.councilSigil.visible,
      sigilRotationMode:
          VoiceCoreController.sigilRotationModeId(state.councilSigil.rotationMode),
      sigilOpacityPercent:
          state.councilSigil.visible ? state.councilSigil.opacityPercent : null,
      sigilRotationPeriodSec: state.councilSigil.visible
          ? state.councilSigil.rotationPeriodSec
          : null,
      pauseMs: pauseMs,
    );
  }

  final String phase;
  final String coreRotationState;
  final double backgroundDimPercent;
  final bool sigilVisible;
  final String sigilRotationMode;
  final double? sigilOpacityPercent;
  final double? sigilRotationPeriodSec;
  final int? pauseMs;

  Map<String, Object?> toMap() {
    return <String, Object?>{
      'phase': phase,
      'coreRotationState': coreRotationState,
      'backgroundDimPercent': backgroundDimPercent,
      'sigilVisible': sigilVisible,
      'sigilRotationMode': sigilRotationMode,
      if (sigilOpacityPercent != null)
        'sigilOpacityPercent': sigilOpacityPercent,
      if (sigilRotationPeriodSec != null)
        'sigilRotationPeriodSec': sigilRotationPeriodSec,
      if (pauseMs != null) 'pauseMs': pauseMs,
    };
  }
}
