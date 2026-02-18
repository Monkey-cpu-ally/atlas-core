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
}
