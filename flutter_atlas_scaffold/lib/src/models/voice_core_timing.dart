import 'package:flutter/foundation.dart';

@immutable
class VoiceCoreTiming {
  const VoiceCoreTiming({
    this.councilSigilRevealDelay = const Duration(milliseconds: 300),
    this.councilSigilFadeOutDuration = const Duration(milliseconds: 500),
    this.councilIdlePauseDuration = const Duration(seconds: 1),
    this.backgroundDimFadeDuration = const Duration(milliseconds: 300),
    this.coreScaleDuration = const Duration(milliseconds: 250),
    this.sigilFadeInDuration = const Duration(milliseconds: 300),
    this.sigilFadeOutDuration = const Duration(milliseconds: 500),
    this.minBackgroundDimPercent = 0,
    this.maxBackgroundDimPercent = 10,
    this.minSigilOpacityPercent = 8,
    this.maxSigilOpacityPercent = 15,
    this.minSigilRotationPeriodSec = 30,
    this.maxSigilRotationPeriodSec = 60,
  });

  static const VoiceCoreTiming spec = VoiceCoreTiming();

  final Duration councilSigilRevealDelay;
  final Duration councilSigilFadeOutDuration;
  final Duration councilIdlePauseDuration;
  final Duration backgroundDimFadeDuration;
  final Duration coreScaleDuration;
  final Duration sigilFadeInDuration;
  final Duration sigilFadeOutDuration;

  final double minBackgroundDimPercent;
  final double maxBackgroundDimPercent;
  final double minSigilOpacityPercent;
  final double maxSigilOpacityPercent;
  final double minSigilRotationPeriodSec;
  final double maxSigilRotationPeriodSec;
}
