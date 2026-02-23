import 'package:flutter/foundation.dart';

import 'ui_prefs.dart';

@immutable
class UiPrefsProfile {
  const UiPrefsProfile({
    required this.selectedSkinId,
    required this.prefs,
    required this.talkTabEnabled,
    required this.longPressMs,
    required this.bluetoothWakeEnabled,
    required this.bluetoothWakeScreenOnOnly,
    required this.hermesReadyToneOnScreenOn,
    required this.idleAmbientEnabled,
    required this.hapticsEnabled,
    required this.nameRecognizedPulseMs,
    required this.councilPulseMs,
    required this.councilEnabled,
    required this.councilPauseBetweenSpeakersMs,
    required this.failureShowMicAssistAfterFails,
    required this.failureSilentResetAfterFails,
    required this.failureHintText,
    required this.failureHintDurationMs,
    required this.firstLaunchHintEnabled,
    required this.firstLaunchHintText,
    required this.firstLaunchHintShowOnce,
    required this.firstLaunchHintFadeOutMs,
    required this.firstLaunchHintDisplayMs,
    required this.launchColdStartFadeMs,
    required this.launchResumeFadeMs,
    this.raw = const {},
  });

  final String selectedSkinId;
  final UiPrefs prefs;
  final bool talkTabEnabled;
  final int longPressMs;
  final bool bluetoothWakeEnabled;
  final bool bluetoothWakeScreenOnOnly;
  final bool hermesReadyToneOnScreenOn;
  final bool idleAmbientEnabled;
  final bool hapticsEnabled;
  final int nameRecognizedPulseMs;
  final int councilPulseMs;
  final bool councilEnabled;
  final int councilPauseBetweenSpeakersMs;
  final int failureShowMicAssistAfterFails;
  final int failureSilentResetAfterFails;
  final String failureHintText;
  final int failureHintDurationMs;
  final bool firstLaunchHintEnabled;
  final String firstLaunchHintText;
  final bool firstLaunchHintShowOnce;
  final int firstLaunchHintFadeOutMs;
  final int firstLaunchHintDisplayMs;
  final int launchColdStartFadeMs;
  final int launchResumeFadeMs;
  final Map<String, Object?> raw;
}

