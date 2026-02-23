import 'dart:async';

import '../../domain/models/ai_speaker.dart';

abstract class AudioService {
  Stream<double> get playbackAmplitude;

  Future<void> playTone(AiSpeaker speaker);
  Future<void> playCouncilTone();
  Future<void> stopAll();
}

class SilentAudioService implements AudioService {
  SilentAudioService();

  final _ampController = StreamController<double>.broadcast();

  @override
  Stream<double> get playbackAmplitude => _ampController.stream;

  @override
  Future<void> playCouncilTone() async {}

  @override
  Future<void> playTone(AiSpeaker speaker) async {}

  @override
  Future<void> stopAll() async {}

  void dispose() {
    _ampController.close();
  }
}

