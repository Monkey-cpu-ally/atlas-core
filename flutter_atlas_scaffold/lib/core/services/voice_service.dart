import 'dart:async';

import 'package:flutter/foundation.dart';

import '../../domain/models/ai_speaker.dart';

@immutable
class VoiceEvent {
  const VoiceEvent({
    required this.type,
    this.speaker = AiSpeaker.none,
    this.confidence = 0,
    this.text,
  });

  final String type;
  final AiSpeaker speaker;
  final double confidence;
  final String? text;
}

abstract class VoiceService {
  Stream<VoiceEvent> get events;
  Future<void> startPartialListen();
  Future<void> stopListen();
}

class MockVoiceService implements VoiceService {
  final _events = StreamController<VoiceEvent>.broadcast();

  @override
  Stream<VoiceEvent> get events => _events.stream;

  @override
  Future<void> startPartialListen() async {}

  @override
  Future<void> stopListen() async {}

  void emit(VoiceEvent event) {
    _events.add(event);
  }

  void dispose() {
    _events.close();
  }
}

