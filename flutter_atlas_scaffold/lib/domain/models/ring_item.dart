import 'package:flutter/foundation.dart';

@immutable
class RingItem {
  const RingItem({
    required this.id,
    required this.label,
    this.iconName,
    this.coreState,
    this.action,
  });

  final String id;
  final String label;
  final String? iconName;
  final String? coreState;
  final String? action;

  RingItem copyWith({
    String? id,
    String? label,
    String? iconName,
    String? coreState,
    String? action,
  }) {
    return RingItem(
      id: id ?? this.id,
      label: label ?? this.label,
      iconName: iconName ?? this.iconName,
      coreState: coreState ?? this.coreState,
      action: action ?? this.action,
    );
  }
}

