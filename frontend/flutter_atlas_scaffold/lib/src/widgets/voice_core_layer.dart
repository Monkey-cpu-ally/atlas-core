import 'package:flutter/material.dart';

import '../models/voice_core_state.dart';
import '../models/voice_core_timing.dart';
import 'ethereal_sigil_ring.dart';
import 'neutral_ring_shell.dart';

class VoiceCoreLayer extends StatelessWidget {
  const VoiceCoreLayer({
    required this.state,
    required this.coreWidget,
    this.waveform,
    this.sigilSize = 260,
    this.coreSize = 220,
    this.timing = VoiceCoreTiming.spec,
    super.key,
  });

  final VoiceCoreVisualState state;
  final Widget coreWidget;
  final Widget? waveform;
  final double sigilSize;
  final double coreSize;
  final VoiceCoreTiming timing;

  @override
  Widget build(BuildContext context) {
    final dimOpacity = (state.backgroundDimPercent.clamp(0, 10) / 100).toDouble();

    return Stack(
      fit: StackFit.expand,
      children: [
        AnimatedOpacity(
          duration: timing.backgroundDimFadeDuration,
          curve: Curves.easeOut,
          opacity: dimOpacity,
          child: const ColoredBox(color: Colors.black),
        ),
        Center(
          child: SizedBox.square(
            dimension: sigilSize,
            child: Stack(
              alignment: Alignment.center,
              children: [
                EtherealSigilRing(
                  sigilState: state.councilSigil,
                  size: sigilSize,
                  fadeInDuration: timing.sigilFadeInDuration,
                  fadeOutDuration: timing.sigilFadeOutDuration,
                ),
                AnimatedScale(
                  duration: timing.coreScaleDuration,
                  curve: Curves.easeOut,
                  scale: state.coreScale,
                  child: SizedBox.square(
                    dimension: coreSize,
                    child: coreWidget,
                  ),
                ),
                if (waveform != null) waveform!,
              ],
            ),
          ),
        ),
        const NeutralRingShell(),
      ],
    );
  }
}
