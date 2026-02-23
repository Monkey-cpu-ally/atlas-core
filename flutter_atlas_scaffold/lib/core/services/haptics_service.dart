import 'package:flutter/services.dart';

abstract class HapticsService {
  Future<void> pulseShort();
  Future<void> pulseCouncil();
}

class SystemHapticsService implements HapticsService {
  @override
  Future<void> pulseShort() async {
    await HapticFeedback.selectionClick();
  }

  @override
  Future<void> pulseCouncil() async {
    await HapticFeedback.mediumImpact();
  }
}

