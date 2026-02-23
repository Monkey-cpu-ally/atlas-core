import 'dart:ui';

import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';

import '../../core/constants/ai_identities.dart';
import '../../core/constants/timings.dart';
import '../models/ai_speaker.dart';

enum InteractionState {
  idle,
  touchFocus,
  listenPendingName,
  listenToAi,
  processing,
  speaking,
  councilActive,
  appearanceLab,
  extendedIdle,
}

@immutable
class CoreVisualState {
  const CoreVisualState({
    this.interactionState = InteractionState.idle,
    this.accent = AiIdentities.neutral,
    this.accentMix = 0,
    this.rippleEnabled = false,
    this.energyLevel = 0.2,
    this.brightness = 1.0,
    this.coreScale = 1.0,
    this.parallax = Offset.zero,
    this.stillnessLock = false,
    this.audioAmp = 0,
  });

  final InteractionState interactionState;
  final Color accent;
  final double accentMix;
  final bool rippleEnabled;
  final double energyLevel;
  final double brightness;
  final double coreScale;
  final Offset parallax;
  final bool stillnessLock;
  final double audioAmp;

  CoreVisualState copyWith({
    InteractionState? interactionState,
    Color? accent,
    double? accentMix,
    bool? rippleEnabled,
    double? energyLevel,
    double? brightness,
    double? coreScale,
    Offset? parallax,
    bool? stillnessLock,
    double? audioAmp,
  }) {
    return CoreVisualState(
      interactionState: interactionState ?? this.interactionState,
      accent: accent ?? this.accent,
      accentMix: accentMix ?? this.accentMix,
      rippleEnabled: rippleEnabled ?? this.rippleEnabled,
      energyLevel: energyLevel ?? this.energyLevel,
      brightness: brightness ?? this.brightness,
      coreScale: coreScale ?? this.coreScale,
      parallax: parallax ?? this.parallax,
      stillnessLock: stillnessLock ?? this.stillnessLock,
      audioAmp: audioAmp ?? this.audioAmp,
    );
  }
}

class CoreController extends ChangeNotifier {
  CoreVisualState _state = const CoreVisualState();
  double _expandScale = 1.05;
  double _pressTightenScale = 1.02;

  CoreVisualState get state => _state;

  void applyMotionProfile({
    required double expandScale,
    required double pressTightenScale,
  }) {
    _expandScale = expandScale.clamp(1.02, 1.10).toDouble();
    _pressTightenScale = pressTightenScale.clamp(0.96, 1.02).toDouble();
  }

  void onTouchDown() {
    _state = _state.copyWith(
      interactionState: InteractionState.touchFocus,
      coreScale: _pressTightenScale,
      energyLevel: 0.28,
    );
    notifyListeners();
  }

  void onLongPressStart() {
    _state = _state.copyWith(
      interactionState: InteractionState.listenPendingName,
      coreScale: _expandScale,
      energyLevel: 0.35,
      rippleEnabled: false,
      accentMix: 0,
    );
    notifyListeners();
  }

  void onNameDetected(AiSpeaker speaker) {
    final accent = AiIdentities.fromSpeaker(speaker).accent;
    _state = _state.copyWith(
      interactionState: InteractionState.listenToAi,
      accent: accent,
      accentMix: 0.8,
      rippleEnabled: true,
      energyLevel: 0.5,
      coreScale: 1.05,
    );
    notifyListeners();
  }

  void onUserUtteranceComplete() {
    _state = _state.copyWith(
      interactionState: InteractionState.processing,
      accentMix: 0.7,
      rippleEnabled: true,
      energyLevel: 0.45,
      coreScale: 1.03,
    );
    notifyListeners();
  }

  void onAiResponseStart(AiSpeaker speaker) {
    _state = _state.copyWith(
      interactionState: InteractionState.speaking,
      accent: AiIdentities.fromSpeaker(speaker).accent,
      accentMix: 1.0,
      rippleEnabled: true,
      energyLevel: 0.6,
    );
    notifyListeners();
  }

  Future<void> onAiResponseEnd() async {
    _state = _state.copyWith(
      accentMix: 0,
      rippleEnabled: false,
      coreScale: 1.0,
      energyLevel: 0.2,
      audioAmp: 0,
    );
    notifyListeners();
    await Future<void>.delayed(Timings.accentFadeOut);
    resetIdle();
  }

  void activateCouncil() {
    _state = _state.copyWith(
      interactionState: InteractionState.councilActive,
      accent: AiIdentities.ghostPurple,
      accentMix: 1,
      stillnessLock: true,
      rippleEnabled: false,
      energyLevel: 0.35,
      coreScale: 1.08,
      parallax: Offset.zero,
    );
    notifyListeners();
  }

  void deactivateCouncil() {
    _state = _state.copyWith(
      stillnessLock: false,
      coreScale: 1.0,
    );
    resetIdle();
  }

  void enterAppearanceLab() {
    _state = _state.copyWith(
      interactionState: InteractionState.appearanceLab,
      accent: AiIdentities.Hermes.accent,
      accentMix: 0.55,
      rippleEnabled: false,
      stillnessLock: false,
      energyLevel: 0.3,
      coreScale: 1.0,
    );
    notifyListeners();
  }

  void exitAppearanceLab() {
    _state = _state.copyWith(
      accentMix: 0,
      rippleEnabled: false,
    );
    notifyListeners();
    Future<void>.delayed(Timings.appearanceLabExitFade, resetIdle);
  }

  void setAudioAmplitude(double amplitude) {
    _state = _state.copyWith(audioAmp: amplitude.clamp(0.0, 1.0).toDouble());
    notifyListeners();
  }

  void setParallax(Offset parallax) {
    if (_state.stillnessLock) {
      return;
    }
    _state = _state.copyWith(parallax: parallax);
    notifyListeners();
  }

  void setExtendedIdle(bool enabled) {
    _state = _state.copyWith(
      interactionState:
          enabled ? InteractionState.extendedIdle : InteractionState.idle,
      brightness: enabled ? 0.72 : 1.0,
      energyLevel: enabled ? 0.12 : 0.2,
      rippleEnabled: false,
    );
    notifyListeners();
  }

  void resetIdle() {
    _state = const CoreVisualState();
    notifyListeners();
  }
}

