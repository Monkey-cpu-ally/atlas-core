import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_atlas_scaffold/atlas_voice_core.dart';

void main() {
  test('council phase payload includes sigil and dim fields', () {
    const state = VoiceCoreVisualState(
      currentSpeaker: null,
      currentState: VoiceCoreUiState.councilActive,
      voiceMode: VoiceMode.council,
      councilPhase: CouncilPhase.councilActive,
      accentColor: VoiceCoreController.ghostPurpleAccent,
      coreOverlayColor: null,
      backgroundDimPercent: 8,
      coreScale: 1.08,
      coreRotationState: CoreRotationState.stopped,
      councilSigil: CouncilSigilState(
        visible: true,
        opacityPercent: 12,
        rotationMode: SigilRotationMode.static,
        rotationPeriodSec: null,
      ),
    );

    final payload = CouncilPhaseChangedPayload.fromState(state: state).toMap();

    expect(payload['phase'], 'COUNCIL_ACTIVE');
    expect(payload['coreRotationState'], 'stopped');
    expect(payload['backgroundDimPercent'], 8.0);
    expect(payload['sigilVisible'], isTrue);
    expect(payload['sigilRotationMode'], 'static');
    expect(payload['sigilOpacityPercent'], 12.0);
  });

  test('fromMap rejects visible sigil payload without opacity', () {
    expect(
      () => CouncilPhaseChangedPayload.fromMap(
        <String, Object?>{
          'phase': 'COUNCIL_ACTIVE',
          'coreRotationState': 'stopped',
          'backgroundDimPercent': 8,
          'sigilVisible': true,
          'sigilRotationMode': 'static',
        },
      ),
      throwsA(isA<BridgePayloadValidationError>()),
    );
  });

  test('fromMap rejects dim percent outside range', () {
    expect(
      () => CouncilPhaseChangedPayload.fromMap(
        <String, Object?>{
          'phase': 'COUNCIL_ACTIVE',
          'coreRotationState': 'stopped',
          'backgroundDimPercent': 12,
          'sigilVisible': false,
          'sigilRotationMode': 'static',
        },
      ),
      throwsA(isA<BridgePayloadValidationError>()),
    );
  });

  test('inbound handler applies council phase state to controller', () {
    final controller = VoiceCoreController(
      delayFn: (_) async {},
    );
    final inbound = UnityBridgeInboundHandler(controller: controller);

    inbound.handleEvent(
      eventName: UnityBridgeEventNames.councilPhaseChanged,
      payload: <String, Object?>{
        'phase': 'SPEAKING_MINERVA',
        'coreRotationState': 'stopped',
        'backgroundDimPercent': 8,
        'sigilVisible': true,
        'sigilRotationMode': 'ultra_slow',
        'sigilOpacityPercent': 12,
        'sigilRotationPeriodSec': 45,
      },
    );

    expect(controller.state.currentState, VoiceCoreUiState.speakingMinerva);
    expect(controller.state.voiceMode, VoiceMode.council);
    expect(controller.state.accentColor, VoiceCoreController.ghostPurpleAccent);
    expect(controller.state.coreOverlayColor, VoiceCoreController.minervaAccent);
    expect(controller.state.councilSigil.visible, isTrue);
    expect(controller.state.councilSigil.rotationMode, SigilRotationMode.ultraSlow);
  });

  test('inbound handler rejects unsupported event names', () {
    final inbound = UnityBridgeInboundHandler(
      controller: VoiceCoreController(delayFn: (_) async {}),
    );
    expect(
      () => inbound.handleEvent(
        eventName: 'v1.unknown',
        payload: const <String, Object?>{},
      ),
      throwsA(isA<UnsupportedBridgeEventError>()),
    );
  });

  test('emitter sends council phase event through transport', () async {
    final transport = _FakeTransport();
    final emitter = UnityBridgeEmitter(transport);
    final controller = VoiceCoreController(delayFn: (_) async {});
    await controller.enterCouncilActive();

    await emitter.emitCouncilPhaseChanged(state: controller.state, pauseMs: 1000);

    expect(transport.lastEventName, UnityBridgeEventNames.councilPhaseChanged);
    expect(transport.lastPayload?['pauseMs'], 1000);
    expect(transport.lastPayload?['phase'], 'COUNCIL_ACTIVE');
  });
}

class _FakeTransport implements UnityBridgeTransport {
  String? lastEventName;
  Map<String, Object?>? lastPayload;

  @override
  Future<void> sendEvent({
    required String eventName,
    required Map<String, Object?> payload,
  }) async {
    lastEventName = eventName;
    lastPayload = payload;
  }
}
