import 'dart:math' as math;

import 'package:flutter/foundation.dart';

import '../../core/state/ring_state.dart';
import '../models/rings_profile.dart';

enum RingLayer {
  command,
  domain,
  module,
  utility,
}

class RingController extends ChangeNotifier {
  RingState _state = const RingState();
  RingSnappingConfig _snapping = const RingSnappingConfig();

  RingState get state => _state;
  RingSnappingConfig get snapping => _snapping;

  void configureSnapping(RingSnappingConfig config) {
    _snapping = config;
  }

  void rotate({
    required RingLayer layer,
    required double deltaDeg,
    required int segmentCount,
  }) {
    if (!_snapping.enabled) {
      return;
    }
    final scaledDelta =
        deltaDeg * (0.55 + (_snapping.inertia.clamp(0.0, 1.5) * 0.45));
    final current = _selectLayer(layer);
    final nextAngle = _normalizeDeg(current.angleDeg + scaledDelta);
    final selected = _nearestIndex(nextAngle, segmentCount);
    _setLayer(layer, current.copyWith(angleDeg: nextAngle, selectedIndex: selected));
  }

  void snapToNearest({
    required RingLayer layer,
    required int segmentCount,
  }) {
    if (!_snapping.enabled) {
      return;
    }
    final current = _selectLayer(layer);
    final index = _nearestIndex(current.angleDeg, segmentCount);
    final rawTargetAngle = -(360 / segmentCount) * index;
    final targetAngle = (current.angleDeg +
            ((rawTargetAngle - current.angleDeg) *
                _snapping.snapStrength.clamp(0.0, 1.0)))
        .toDouble();
    _setLayer(layer, current.copyWith(angleDeg: targetAngle, selectedIndex: index));
  }

  RingLayerState _selectLayer(RingLayer layer) {
    return switch (layer) {
      RingLayer.command => _state.command,
      RingLayer.domain => _state.domain,
      RingLayer.module => _state.module,
      RingLayer.utility => _state.utility,
    };
  }

  RingLayerState layerState(RingLayer layer) => _selectLayer(layer);

  void _setLayer(RingLayer layer, RingLayerState layerState) {
    _state = switch (layer) {
      RingLayer.command => _state.copyWith(command: layerState),
      RingLayer.domain => _state.copyWith(domain: layerState),
      RingLayer.module => _state.copyWith(module: layerState),
      RingLayer.utility => _state.copyWith(utility: layerState),
    };
    notifyListeners();
  }

  static double _normalizeDeg(double value) {
    var normalized = value % 360;
    if (normalized > 180) {
      normalized -= 360;
    } else if (normalized < -180) {
      normalized += 360;
    }
    return normalized;
  }

  static int _nearestIndex(double angleDeg, int count) {
    if (count <= 1) {
      return 0;
    }
    final step = 360 / count;
    final raw = (-angleDeg / step).round();
    return ((raw % count) + count) % count;
  }

  double segmentAngle({
    required int index,
    required int count,
  }) {
    if (count <= 0) {
      return 0;
    }
    return -index * (360 / count) * (math.pi / 180);
  }
}

