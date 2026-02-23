import 'dart:async';

import 'package:flutter/foundation.dart';

import '../../core/constants/thresholds.dart';
import '../../core/services/audio_service.dart';
import '../../core/services/bluetooth_wake_service.dart';
import '../../core/services/haptics_service.dart';
import '../../core/services/voice_service.dart';
import '../models/ai_speaker.dart';
import 'appearance_lab_controller.dart';
import 'core_controller.dart';
import 'council_controller.dart';

class VoiceController extends ChangeNotifier {
  VoiceController({
    required VoiceService voiceService,
    required BluetoothWakeService wakeService,
    required AudioService audioService,
    required HapticsService hapticsService,
    required CoreController coreController,
    required CouncilController councilController,
    required AppearanceLabController appearanceLabController,
    int failureOverlayThreshold = Thresholds.failureOverlayThreshold,
    int failureResetThreshold = Thresholds.failureResetThreshold,
    String micAssistHintText =
        'Mic assist: hold center and say Ajani, Minerva, or Hermes.',
    int micAssistHintDurationMs = 4000,
  })  : _voiceService = voiceService,
        _wakeService = wakeService,
        _audioService = audioService,
        _haptics = hapticsService,
        _core = coreController,
        _council = councilController,
        _appearanceLab = appearanceLabController,
        _failureOverlayThreshold = failureOverlayThreshold,
        _failureResetThreshold = failureResetThreshold,
        _micAssistHintText = micAssistHintText,
        _micAssistHintDurationMs = micAssistHintDurationMs {
    _voiceSub = _voiceService.events.listen(_onVoiceEvent);
    _wakeSub = _wakeService.wakeEvents.listen(_onWakeEvent);
    _audioAmpSub = _audioService.playbackAmplitude.listen(_core.setAudioAmplitude);
  }

  final VoiceService _voiceService;
  final BluetoothWakeService _wakeService;
  final AudioService _audioService;
  final HapticsService _haptics;
  final CoreController _core;
  final CouncilController _council;
  final AppearanceLabController _appearanceLab;
  int _failureOverlayThreshold;
  int _failureResetThreshold;
  String _micAssistHintText;
  int _micAssistHintDurationMs;

  StreamSubscription<VoiceEvent>? _voiceSub;
  StreamSubscription<WakeEvent>? _wakeSub;
  StreamSubscription<double>? _audioAmpSub;
  Timer? _micAssistTimer;

  int _failureCount = 0;
  bool _micAssistVisible = false;

  int get failureCount => _failureCount;
  bool get micAssistVisible => _micAssistVisible;
  String get micAssistHintText => _micAssistHintText;
  int get micAssistHintDurationMs => _micAssistHintDurationMs;

  void configureFromPrefs({
    required int failureOverlayThreshold,
    required int failureResetThreshold,
    required String micAssistHintText,
    required int micAssistHintDurationMs,
  }) {
    _failureOverlayThreshold = failureOverlayThreshold;
    _failureResetThreshold = failureResetThreshold;
    _micAssistHintText = micAssistHintText;
    _micAssistHintDurationMs = micAssistHintDurationMs;
    notifyListeners();
  }

  Future<void> onLongPressStart() async {
    _core.onLongPressStart();
    await _voiceService.startPartialListen();
  }

  Future<void> onLongPressEnd() async {
    await _voiceService.stopListen();
    _core.onUserUtteranceComplete();
  }

  Future<void> onAiResponseStart(AiSpeaker speaker) async {
    _core.onAiResponseStart(speaker);
  }

  Future<void> onAiResponseEnd() async {
    await _core.onAiResponseEnd();
  }

  Future<void> _onWakeEvent(WakeEvent event) async {
    await _acceptSpeaker(event.speaker, fromWake: true);
  }

  Future<void> _onVoiceEvent(VoiceEvent event) async {
    switch (event.type) {
      case 'nameDetected':
        await _acceptSpeaker(event.speaker, fromWake: false);
        break;
      case 'phrase':
        final text = event.text?.toLowerCase() ?? '';
        if (text.contains('council')) {
          _activateCouncil();
        } else if (text.contains('hermes') &&
            (text.contains('system mode') || text.contains('appearance'))) {
          _enterAppearanceLab();
        } else if (_appearanceLab.state.active &&
            (text.contains('exit') || text.contains('close') || text.contains('return'))) {
          _exitAppearanceLab();
        }
        break;
      case 'timeout':
      case 'nameNotRecognized':
        registerFailure();
        break;
      default:
        break;
    }
  }

  Future<void> _acceptSpeaker(
    AiSpeaker speaker, {
    required bool fromWake,
  }) async {
    _failureCount = 0;
    _micAssistVisible = false;
    notifyListeners();

    await _haptics.pulseShort();
    await _audioService.playTone(speaker);
    _core.onNameDetected(speaker);
    if (fromWake) {
      await _voiceService.startPartialListen();
    }
  }

  Future<void> _activateCouncil() async {
    _failureCount = 0;
    _micAssistVisible = false;
    await _haptics.pulseCouncil();
    await _audioService.playCouncilTone();
    _council.activate();
    _core.activateCouncil();
    notifyListeners();
  }

  void _enterAppearanceLab() {
    _appearanceLab.enter();
    _core.enterAppearanceLab();
    notifyListeners();
  }

  void _exitAppearanceLab() {
    _appearanceLab.exit();
    _core.exitAppearanceLab();
    notifyListeners();
  }

  void registerFailure() {
    _failureCount += 1;
    if (_failureCount >= _failureResetThreshold) {
      _failureCount = 0;
      _micAssistVisible = false;
      _micAssistTimer?.cancel();
      _core.resetIdle();
    } else if (_failureCount >= _failureOverlayThreshold) {
      _micAssistVisible = true;
      _micAssistTimer?.cancel();
      _micAssistTimer =
          Timer(Duration(milliseconds: _micAssistHintDurationMs), () {
        _micAssistVisible = false;
        notifyListeners();
      });
    }
    notifyListeners();
  }

  @override
  void dispose() {
    _voiceSub?.cancel();
    _wakeSub?.cancel();
    _audioAmpSub?.cancel();
    _micAssistTimer?.cancel();
    super.dispose();
  }
}

