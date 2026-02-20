import 'package:flutter/foundation.dart';

@immutable
class PowerState {
  const PowerState({
    this.lowPowerMode = false,
    this.extendedIdle = false,
  });

  final bool lowPowerMode;
  final bool extendedIdle;

  PowerState copyWith({
    bool? lowPowerMode,
    bool? extendedIdle,
  }) {
    return PowerState(
      lowPowerMode: lowPowerMode ?? this.lowPowerMode,
      extendedIdle: extendedIdle ?? this.extendedIdle,
    );
  }
}

