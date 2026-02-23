import 'package:flutter/foundation.dart';

@immutable
class AppearanceLabState {
  const AppearanceLabState({
    this.active = false,
    this.overlayVisible = false,
  });

  final bool active;
  final bool overlayVisible;

  AppearanceLabState copyWith({
    bool? active,
    bool? overlayVisible,
  }) {
    return AppearanceLabState(
      active: active ?? this.active,
      overlayVisible: overlayVisible ?? this.overlayVisible,
    );
  }
}

