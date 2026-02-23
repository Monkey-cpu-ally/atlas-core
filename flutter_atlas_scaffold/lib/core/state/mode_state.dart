import 'package:flutter/foundation.dart';

enum ModeId {
  blueprint,
  build,
  modify,
  simulate,
  log,
  reflect,
}

@immutable
class ModeState {
  const ModeState({
    this.active = ModeId.blueprint,
  });

  final ModeId active;

  ModeState copyWith({
    ModeId? active,
  }) {
    return ModeState(
      active: active ?? this.active,
    );
  }
}

