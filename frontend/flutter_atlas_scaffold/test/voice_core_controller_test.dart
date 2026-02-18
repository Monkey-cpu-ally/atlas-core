import 'dart:async';

import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_atlas_scaffold/atlas_voice_core.dart';

void main() {
  test('council activation reveals sigil after delay', () async {
    final delayCompleter = Completer<void>();
    late Duration requestedDelay;

    final controller = VoiceCoreController(
      delayFn: (duration) {
        requestedDelay = duration;
        return delayCompleter.future;
      },
    );

    final pending = controller.enterCouncilActive();

    expect(controller.state.currentState, VoiceCoreUiState.councilActive);
    expect(controller.state.coreRotationState, CoreRotationState.stopped);
    expect(controller.state.backgroundDimPercent, 8);
    expect(controller.state.councilSigil.visible, isFalse);

    delayCompleter.complete();
    await pending;

    expect(requestedDelay, controller.timing.councilSigilRevealDelay);
    expect(controller.state.councilSigil.visible, isTrue);
    expect(controller.state.councilSigil.opacityPercent, inInclusiveRange(8, 15));
  });

  test('speaker order is enforced Ajani -> Minerva -> Hermes', () async {
    final controller = VoiceCoreController(
      delayFn: (_) async {},
    );
    await controller.enterCouncilActive();

    expect(controller.setCouncilSpeaker(IdentitySpeaker.minerva), isFalse);
    expect(controller.state.currentState, VoiceCoreUiState.councilActive);

    expect(controller.setCouncilSpeaker(IdentitySpeaker.ajani), isTrue);
    expect(controller.setCouncilSpeaker(IdentitySpeaker.hermes), isFalse);
    expect(controller.setCouncilPause(), isTrue);
    expect(controller.setCouncilSpeaker(IdentitySpeaker.minerva), isTrue);
    expect(controller.setCouncilPause(), isTrue);
    expect(controller.setCouncilSpeaker(IdentitySpeaker.hermes), isTrue);
  });

  test('council sigil stays ghost purple while speaker overlay changes', () async {
    final controller = VoiceCoreController(
      delayFn: (_) async {},
    );
    await controller.enterCouncilActive();

    expect(controller.setCouncilSpeaker(IdentitySpeaker.ajani), isTrue);
    expect(controller.state.accentColor, VoiceCoreController.ghostPurpleAccent);
    expect(controller.state.coreOverlayColor, VoiceCoreController.ajaniAccent);
    expect(controller.state.councilSigil.visible, isTrue);

    expect(controller.setCouncilPause(), isTrue);
    expect(controller.setCouncilSpeaker(IdentitySpeaker.minerva), isTrue);
    expect(controller.state.accentColor, VoiceCoreController.ghostPurpleAccent);
    expect(controller.state.coreOverlayColor, VoiceCoreController.minervaAccent);
    expect(controller.state.councilSigil.visible, isTrue);

    expect(controller.setCouncilPause(), isTrue);
    expect(controller.setCouncilSpeaker(IdentitySpeaker.hermes), isTrue);
    expect(controller.state.accentColor, VoiceCoreController.ghostPurpleAccent);
    expect(controller.state.coreOverlayColor, VoiceCoreController.hermesAccent);
    expect(controller.state.councilSigil.visible, isTrue);
  });

  test('council completion is rejected until Hermes turn is active', () async {
    final controller = VoiceCoreController(
      delayFn: (_) async {},
    );
    await controller.enterCouncilActive();

    expect(await controller.completeCouncil(), isFalse);
    expect(controller.setCouncilSpeaker(IdentitySpeaker.ajani), isTrue);
    expect(await controller.completeCouncil(), isFalse);
  });

  test('council completion clears sigil and returns to idle', () async {
    var callCount = 0;
    final activationDelayCompleter = Completer<void>()..complete();
    final completionDelayCompleter = Completer<void>();
    final controller = VoiceCoreController(
      delayFn: (_) {
        callCount += 1;
        return callCount == 1
            ? activationDelayCompleter.future
            : completionDelayCompleter.future;
      },
    );

    await controller.enterCouncilActive();
    expect(controller.setCouncilSpeaker(IdentitySpeaker.ajani), isTrue);
    expect(controller.setCouncilPause(), isTrue);
    expect(controller.setCouncilSpeaker(IdentitySpeaker.minerva), isTrue);
    expect(controller.setCouncilPause(), isTrue);
    expect(controller.setCouncilSpeaker(IdentitySpeaker.hermes), isTrue);
    final pending = controller.completeCouncil();

    expect(controller.state.councilSigil.visible, isFalse);
    expect(controller.state.currentState, VoiceCoreUiState.councilActive);

    completionDelayCompleter.complete();
    expect(await pending, isTrue);

    expect(controller.state.currentState, VoiceCoreUiState.idle);
    expect(controller.state.backgroundDimPercent, 0);
    expect(controller.state.voiceMode, VoiceMode.single);
    expect(controller.state.councilSigil.visible, isFalse);
  });

  test('activation clamps dim, opacity, and ultra-slow rotation period', () async {
    final controller = VoiceCoreController(
      delayFn: (_) async {},
    );
    await controller.enterCouncilActive(
      backgroundDimPercent: 50,
      sigilOpacityPercent: 2,
      sigilRotationMode: SigilRotationMode.ultraSlow,
      sigilRotationPeriodSec: 120,
    );

    expect(controller.state.backgroundDimPercent, 10);
    expect(controller.state.councilSigil.opacityPercent, 8);
    expect(controller.state.councilSigil.rotationMode, SigilRotationMode.ultraSlow);
    expect(controller.state.councilSigil.rotationPeriodSec, 60);
  });

  test('stale reveal callback cannot re-open sigil after reset', () async {
    final revealCompleter = Completer<void>();
    final controller = VoiceCoreController(
      delayFn: (_) => revealCompleter.future,
    );

    final pending = controller.enterCouncilActive();
    controller.resetIdle();
    revealCompleter.complete();
    await pending;

    expect(controller.state.currentState, VoiceCoreUiState.idle);
    expect(controller.state.councilSigil.visible, isFalse);
  });
}
