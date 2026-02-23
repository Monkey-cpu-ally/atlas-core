import 'dart:async';
import 'dart:ui';

abstract class GyroService {
  Stream<Offset> get tiltStream;
  Future<void> start();
  Future<void> stop();
}

/// Placeholder implementation until device sensor integration is wired.
class MockGyroService implements GyroService {
  final _controller = StreamController<Offset>.broadcast();

  @override
  Stream<Offset> get tiltStream => _controller.stream;

  @override
  Future<void> start() async {
    _controller.add(Offset.zero);
  }

  @override
  Future<void> stop() async {}

  void push(Offset tilt) {
    _controller.add(tilt);
  }

  void dispose() {
    _controller.close();
  }
}

