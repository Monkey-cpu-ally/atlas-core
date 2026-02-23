import 'package:flutter/material.dart';

import '../models/voice_core_state.dart';
import '../models/voice_core_timing.dart';
import '../models/dial_visual_prefs.dart';
import 'dial_background.dart';
import 'ethereal_sigil_ring.dart';
import 'frame_plate.dart';
import 'neutral_ring_shell.dart';

class VoiceCoreLayer extends StatelessWidget {
  const VoiceCoreLayer({
    required this.state,
    required this.coreWidget,
    this.waveform,
    this.sigilSize = 260,
    this.coreSize = 220,
    this.timing = VoiceCoreTiming.spec,
    this.visualPrefs = DialVisualPrefs.defaults,
    this.ringColor = const Color(0xFF6A6A72),
    this.ringOpacity = 0.36,
    this.ringStrokeWidth = 1.2,
    this.backgroundColor = const Color(0xFF0B0B10),
    this.microDetailColor = const Color(0xFF1C1C24),
    this.frameColor = const Color(0xFF2A2A44),
    super.key,
  });

  final VoiceCoreVisualState state;
  final Widget coreWidget;
  final Widget? waveform;
  final double sigilSize;
  final double coreSize;
  final VoiceCoreTiming timing;
  final DialVisualPrefs visualPrefs;
  final Color ringColor;
  final double ringOpacity;
  final double ringStrokeWidth;
  final Color backgroundColor;
  final Color microDetailColor;
  final Color frameColor;

  @override
  Widget build(BuildContext context) {
    final dimOpacity = (state.backgroundDimPercent.clamp(0, 10) / 100).toDouble();

    return Stack(
      fit: StackFit.expand,
      children: [
        // Background surface (configurable).
        DialBackground(
          type: visualPrefs.backgroundType,
          background: backgroundColor,
          microDetail: microDetailColor,
        ),

        // Council dim overlay is optional.
        if (visualPrefs.councilDimOverlayEnabled)
          AnimatedOpacity(
            duration: timing.backgroundDimFadeDuration,
            curve: Curves.easeOut,
            opacity: dimOpacity,
            child: const ColoredBox(color: Colors.black),
          ),

        // Optional frame plate (below sigil/rings/core).
        Center(
          child: FramePlate(
            frameType: visualPrefs.frameType,
            opacityMode: visualPrefs.frameOpacityMode,
            color: frameColor,
            size: sigilSize + 80,
          ),
        ),

        // Optional sigil (council-only). Note: placed below rings by stack order.
        Center(
          child: EtherealSigilRing(
            sigilState: state.councilSigil,
            size: sigilSize,
            fadeInDuration: timing.sigilFadeInDuration,
            fadeOutDuration: timing.sigilFadeOutDuration,
          ),
        ),

        // Rings (neutral; can be styled by skin/prefs).
        NeutralRingShell(
          color: ringColor,
          opacity: ringOpacity,
          strokeWidth: ringStrokeWidth,
        ),

        // 3D core layer (on top of rings).
        Center(
          child: AnimatedScale(
            duration: timing.coreScaleDuration,
            curve: Curves.easeOut,
            scale: state.coreScale,
            child: SizedBox.square(
              dimension: coreSize,
              child: coreWidget,
            ),
          ),
        ),

        // Waveform / AI overlay (top-most).
        if (waveform != null) Center(child: waveform!),
      ],
    );
  }
}
