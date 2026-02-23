import 'package:flutter/foundation.dart';

@immutable
class SkinState {
  const SkinState({
    this.activeSkinId = 'lumen_core',
    this.transitionMs = 500,
  });

  final String activeSkinId;
  final int transitionMs;

  SkinState copyWith({
    String? activeSkinId,
    int? transitionMs,
  }) {
    return SkinState(
      activeSkinId: activeSkinId ?? this.activeSkinId,
      transitionMs: transitionMs ?? this.transitionMs,
    );
  }
}

