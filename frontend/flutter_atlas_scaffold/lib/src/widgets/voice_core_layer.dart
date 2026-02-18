import 'package:flutter/material.dart';

import '../models/voice_core_state.dart';
import 'ethereal_sigil_ring.dart';
import 'neutral_ring_shell.dart';

class VoiceCoreLayer extends StatelessWidget {
  const VoiceCoreLayer({
    required this.state,
    required this.coreWidget,
    this.waveform,
    this.sigilSize = 260,
    this.coreSize = 220,
    super.key,
  });

  final VoiceCoreVisualState state;
  final Widget coreWidget;
  final Widget? waveform;
  final double sigilSize;
  final double coreSize;

  @override
  Widget build(BuildContext context) {
    final dimOpacity = (state.backgroundDimPercent.clamp(0, 10) / 100).toDouble();

    return Stack(
      fit: StackFit.expand,
      children: [
        AnimatedOpacity(
          duration: const Duration(milliseconds: 300),
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
                ),
                AnimatedScale(
                  duration: const Duration(milliseconds: 250),
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
