import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_atlas_scaffold/atlas_voice_core.dart';

void main() {
  testWidgets('voice core layer applies dim/scale/sigil timing config', (
    tester,
  ) async {
    const timing = VoiceCoreTiming(
      backgroundDimFadeDuration: Duration(milliseconds: 410),
      coreScaleDuration: Duration(milliseconds: 275),
      sigilFadeInDuration: Duration(milliseconds: 360),
      sigilFadeOutDuration: Duration(milliseconds: 520),
    );

    const state = VoiceCoreVisualState(
      currentSpeaker: null,
      currentState: VoiceCoreUiState.councilActive,
      voiceMode: VoiceMode.council,
      councilPhase: CouncilPhase.councilActive,
      accentColor: VoiceCoreController.ghostPurpleAccent,
      coreOverlayColor: null,
      backgroundDimPercent: 10,
      coreScale: 1.08,
      coreRotationState: CoreRotationState.stopped,
      councilSigil: CouncilSigilState(
        visible: true,
        opacityPercent: 12,
        rotationMode: SigilRotationMode.static,
        rotationPeriodSec: null,
      ),
    );

    await tester.pumpWidget(
      const MaterialApp(
        home: Scaffold(
          body: VoiceCoreLayer(
            state: state,
            coreWidget: SizedBox.expand(),
            timing: timing,
          ),
        ),
      ),
    );

    final backgroundOpacity = tester.widget<AnimatedOpacity>(
      find.byWidgetPredicate(
        (widget) => widget is AnimatedOpacity && widget.child is ColoredBox,
      ),
    );
    expect(backgroundOpacity.opacity, 0.1);
    expect(backgroundOpacity.duration, timing.backgroundDimFadeDuration);

    final coreScale = tester.widget<AnimatedScale>(find.byType(AnimatedScale));
    expect(coreScale.scale, 1.08);
    expect(coreScale.duration, timing.coreScaleDuration);

    final sigilOpacity = tester.widget<TweenAnimationBuilder<double>>(
      find.byWidgetPredicate(
        (widget) =>
            widget is TweenAnimationBuilder<double> &&
            widget.child is RotationTransition,
      ),
    );
    expect(sigilOpacity.duration, timing.sigilFadeInDuration);

    expect(find.byType(NeutralRingShell), findsOneWidget);
  });
}
