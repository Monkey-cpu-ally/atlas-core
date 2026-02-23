import 'package:flutter/foundation.dart';

@immutable
class FailureState {
  const FailureState({
    this.failureCount = 0,
    this.lastFailureAt,
  });

  final int failureCount;
  final DateTime? lastFailureAt;

  FailureState copyWith({
    int? failureCount,
    DateTime? lastFailureAt,
    bool clearLastFailureAt = false,
  }) {
    return FailureState(
      failureCount: failureCount ?? this.failureCount,
      lastFailureAt:
          clearLastFailureAt ? null : (lastFailureAt ?? this.lastFailureAt),
    );
  }
}

