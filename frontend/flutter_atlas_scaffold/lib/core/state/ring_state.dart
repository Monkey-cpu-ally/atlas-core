import 'package:flutter/foundation.dart';

@immutable
class RingLayerState {
  const RingLayerState({
    required this.angleDeg,
    required this.selectedIndex,
  });

  final double angleDeg;
  final int selectedIndex;

  RingLayerState copyWith({
    double? angleDeg,
    int? selectedIndex,
  }) {
    return RingLayerState(
      angleDeg: angleDeg ?? this.angleDeg,
      selectedIndex: selectedIndex ?? this.selectedIndex,
    );
  }
}

@immutable
class RingState {
  const RingState({
    this.command = const RingLayerState(angleDeg: 0, selectedIndex: 0),
    this.domain = const RingLayerState(angleDeg: 0, selectedIndex: 0),
    this.module = const RingLayerState(angleDeg: 0, selectedIndex: 0),
    this.utility = const RingLayerState(angleDeg: 0, selectedIndex: 0),
  });

  final RingLayerState command;
  final RingLayerState domain;
  final RingLayerState module;
  final RingLayerState utility;

  RingState copyWith({
    RingLayerState? command,
    RingLayerState? domain,
    RingLayerState? module,
    RingLayerState? utility,
  }) {
    return RingState(
      command: command ?? this.command,
      domain: domain ?? this.domain,
      module: module ?? this.module,
      utility: utility ?? this.utility,
    );
  }
}

