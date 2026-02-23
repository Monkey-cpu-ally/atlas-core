import '../controllers/voice_core_controller.dart';
import '../models/voice_core_state.dart';

class BridgePayloadValidationError implements Exception {
  BridgePayloadValidationError(this.message);

  final String message;

  @override
  String toString() => 'BridgePayloadValidationError: $message';
}

class UnsupportedBridgeEventError implements Exception {
  UnsupportedBridgeEventError(this.eventName);

  final String eventName;

  @override
  String toString() => 'UnsupportedBridgeEventError: $eventName';
}

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

class UnityBridgeInboundHandler {
  const UnityBridgeInboundHandler({
    required this.controller,
  });

  final VoiceCoreController controller;

  void handleEvent({
    required String eventName,
    required Map<String, Object?> payload,
  }) {
    switch (eventName) {
      case UnityBridgeEventNames.councilPhaseChanged:
        final parsed = CouncilPhaseChangedPayload.fromMap(payload);
        controller.synchronizeCouncilPhase(
          phase: parsed.phase,
          coreRotationState: parsed.coreRotationState,
          backgroundDimPercent: parsed.backgroundDimPercent,
          sigilVisible: parsed.sigilVisible,
          sigilRotationMode: parsed.sigilRotationMode,
          sigilOpacityPercent: parsed.sigilOpacityPercent,
          sigilRotationPeriodSec: parsed.sigilRotationPeriodSec,
        );
        return;
      default:
        throw UnsupportedBridgeEventError(eventName);
    }
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

  factory CouncilPhaseChangedPayload.fromMap(Map<String, Object?> payload) {
    final phaseRaw = _requiredString(payload, 'phase');
    final rotationRaw = _requiredString(payload, 'coreRotationState');
    final dimPercent = _requiredNum(payload, 'backgroundDimPercent').toDouble();
    final sigilVisible = _requiredBool(payload, 'sigilVisible');
    final sigilModeRaw = _requiredString(payload, 'sigilRotationMode');
    final opacityRaw = payload['sigilOpacityPercent'];
    final rotationPeriodRaw = payload['sigilRotationPeriodSec'];
    final pauseMsRaw = payload['pauseMs'];

    final phase = VoiceCoreController.councilPhaseFromId(phaseRaw);
    final coreRotationState =
        VoiceCoreController.coreRotationStateFromId(rotationRaw);
    final sigilRotationMode =
        VoiceCoreController.sigilRotationModeFromId(sigilModeRaw);

    if (dimPercent < 0 || dimPercent > 10) {
      throw BridgePayloadValidationError(
        'backgroundDimPercent must be within 0-10.',
      );
    }

    if (!sigilVisible) {
      return CouncilPhaseChangedPayload(
        phase: phase,
        coreRotationState: coreRotationState,
        backgroundDimPercent: dimPercent,
        sigilVisible: false,
        sigilRotationMode: sigilRotationMode,
        pauseMs: _optionalInt(pauseMsRaw, key: 'pauseMs'),
      );
    }

    if (opacityRaw is! num) {
      throw BridgePayloadValidationError(
        'sigilOpacityPercent is required when sigilVisible is true.',
      );
    }
    final sigilOpacity = opacityRaw.toDouble();
    if (sigilOpacity < 8 || sigilOpacity > 15) {
      throw BridgePayloadValidationError(
        'sigilOpacityPercent must be within 8-15.',
      );
    }

    double? sigilRotationPeriodSec;
    if (sigilRotationMode == SigilRotationMode.ultraSlow) {
      final rotationValue = rotationPeriodRaw == null ? 45 : _optionalNum(
          rotationPeriodRaw,
          key: 'sigilRotationPeriodSec',
        );
      if (rotationValue == null ||
          rotationValue < 30 ||
          rotationValue > 60) {
        throw BridgePayloadValidationError(
          'sigilRotationPeriodSec must be within 30-60 for ultra_slow mode.',
        );
      }
      sigilRotationPeriodSec = rotationValue.toDouble();
    }

    return CouncilPhaseChangedPayload(
      phase: phase,
      coreRotationState: coreRotationState,
      backgroundDimPercent: dimPercent,
      sigilVisible: true,
      sigilRotationMode: sigilRotationMode,
      sigilOpacityPercent: sigilOpacity,
      sigilRotationPeriodSec: sigilRotationPeriodSec,
      pauseMs: _optionalInt(pauseMsRaw, key: 'pauseMs'),
    );
  }

  factory CouncilPhaseChangedPayload.fromState({
    required VoiceCoreVisualState state,
    int? pauseMs,
  }) {
    return CouncilPhaseChangedPayload(
      phase: state.councilPhase,
      coreRotationState: state.coreRotationState,
      backgroundDimPercent: state.backgroundDimPercent,
      sigilVisible: state.councilSigil.visible,
      sigilRotationMode: state.councilSigil.rotationMode,
      sigilOpacityPercent:
          state.councilSigil.visible ? state.councilSigil.opacityPercent : null,
      sigilRotationPeriodSec: state.councilSigil.visible
          ? state.councilSigil.rotationPeriodSec
          : null,
      pauseMs: pauseMs,
    );
  }

  final CouncilPhase phase;
  final CoreRotationState coreRotationState;
  final double backgroundDimPercent;
  final bool sigilVisible;
  final SigilRotationMode sigilRotationMode;
  final double? sigilOpacityPercent;
  final double? sigilRotationPeriodSec;
  final int? pauseMs;

  Map<String, Object?> toMap() {
    return <String, Object?>{
      'phase': VoiceCoreController.councilPhaseId(phase),
      'coreRotationState': VoiceCoreController.rotationStateId(coreRotationState),
      'backgroundDimPercent': backgroundDimPercent,
      'sigilVisible': sigilVisible,
      'sigilRotationMode':
          VoiceCoreController.sigilRotationModeId(sigilRotationMode),
      if (sigilOpacityPercent != null)
        'sigilOpacityPercent': sigilOpacityPercent,
      if (sigilRotationPeriodSec != null)
        'sigilRotationPeriodSec': sigilRotationPeriodSec,
      if (pauseMs != null) 'pauseMs': pauseMs,
    };
  }

  static String _requiredString(Map<String, Object?> payload, String key) {
    final value = payload[key];
    if (value is String) {
      return value;
    }
    throw BridgePayloadValidationError('$key must be a string.');
  }

  static bool _requiredBool(Map<String, Object?> payload, String key) {
    final value = payload[key];
    if (value is bool) {
      return value;
    }
    throw BridgePayloadValidationError('$key must be a boolean.');
  }

  static num _requiredNum(Map<String, Object?> payload, String key) {
    final value = payload[key];
    if (value is num) {
      return value;
    }
    throw BridgePayloadValidationError('$key must be numeric.');
  }

  static num? _optionalNum(Object? value, {required String key}) {
    if (value == null) {
      return null;
    }
    if (value is num) {
      return value;
    }
    throw BridgePayloadValidationError('$key must be numeric when present.');
  }

  static int? _optionalInt(Object? value, {required String key}) {
    final numeric = _optionalNum(value, key: key);
    return numeric?.toInt();
  }
}
