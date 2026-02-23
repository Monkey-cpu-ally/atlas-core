import 'dart:async';

import 'package:flutter/foundation.dart';

import '../../domain/models/ai_speaker.dart';

@immutable
class WakeEvent {
  const WakeEvent({
    required this.speaker,
    this.source = 'bluetooth',
  });

  final AiSpeaker speaker;
  final String source;
}

abstract class BluetoothWakeService {
  Stream<WakeEvent> get wakeEvents;
  Future<void> startPassiveWake();
  Future<void> stopPassiveWake();
}

class MockBluetoothWakeService implements BluetoothWakeService {
  final _events = StreamController<WakeEvent>.broadcast();

  @override
  Stream<WakeEvent> get wakeEvents => _events.stream;

  @override
  Future<void> startPassiveWake() async {}

  @override
  Future<void> stopPassiveWake() async {}

  void emit(WakeEvent event) {
    _events.add(event);
  }

  void dispose() {
    _events.close();
  }
}

