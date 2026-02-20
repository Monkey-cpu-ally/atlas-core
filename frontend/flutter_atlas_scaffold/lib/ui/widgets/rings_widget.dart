import 'dart:math' as math;

import 'package:flutter/material.dart';

import '../../domain/controllers/ring_controller.dart';
import '../../domain/models/ui_prefs.dart';
import '../painters/ring_painter.dart';
import '../themes/skin_tokens.dart';
import 'ring_segment_label.dart';

class RingsWidget extends StatelessWidget {
  const RingsWidget({
    required this.controller,
    required this.skin,
    required this.prefs,
    this.activeLayer = RingLayer.command,
    this.onSelectionCommitted,
    super.key,
  });

  final RingController controller;
  final SkinTokens skin;
  final UiPrefs prefs;
  final RingLayer activeLayer;
  final void Function(RingLayer layer, int index)? onSelectionCommitted;

  @override
  Widget build(BuildContext context) {
    final layerTransparency = switch (activeLayer) {
      RingLayer.command => prefs.commandRingTransparency,
      RingLayer.domain => prefs.domainRingTransparency,
      RingLayer.module => prefs.moduleRingTransparency,
      RingLayer.utility => prefs.utilityRingTransparency,
    };
    final layerMaterial = switch (activeLayer) {
      RingLayer.command => prefs.commandRingMaterial,
      RingLayer.domain => prefs.domainRingMaterial,
      RingLayer.module => prefs.moduleRingMaterial,
      RingLayer.utility => prefs.utilityRingMaterial,
    };
    final ringOpacity = (0.5 * (1 - layerTransparency)).clamp(0.06, 0.85);
    final baseStroke = switch (layerMaterial) {
      'solidMatte' => 1.9,
      'frostedGlass' => 1.6,
      'transparentGlass' => 1.2,
      'lineOnlyMinimal' => 1.0,
      'mixedInnerSolidOuterTransparent' => 1.5,
      _ => 1.3,
    };
    final ringStroke = (baseStroke * prefs.ringLineWeight).clamp(0.6, 3.6).toDouble();

    return AnimatedBuilder(
      animation: controller,
      builder: (context, _) {
        final layerState = switch (activeLayer) {
          RingLayer.command => controller.state.command,
          RingLayer.domain => controller.state.domain,
          RingLayer.module => controller.state.module,
          RingLayer.utility => controller.state.utility,
        };
        const segments = 6;
        return GestureDetector(
          behavior: HitTestBehavior.translucent,
          onPanUpdate: (details) {
            controller.rotate(
              layer: activeLayer,
              deltaDeg: details.delta.dx * 0.7,
              segmentCount: segments,
            );
          },
          onPanEnd: (_) {
            controller.snapToNearest(layer: activeLayer, segmentCount: segments);
            onSelectionCommitted?.call(activeLayer, layerState.selectedIndex);
          },
          child: Stack(
            alignment: Alignment.center,
            children: [
              Positioned.fill(
                child: CustomPaint(
                  painter: RingPainter(
                    color: skin.ring,
                    opacity: ringOpacity,
                    strokeWidth: ringStroke,
                    segmentCount: segments,
                  ),
                ),
              ),
              ...List<Widget>.generate(segments, (index) {
                final distance = _ringDistance(
                  index,
                  layerState.selectedIndex,
                  segments,
                );
                final opacity = distance == 0
                    ? 1.0
                    : (prefs.partialLabeling
                        ? (distance <= 1
                            ? prefs.inactiveOpacityNear
                            : prefs.inactiveOpacityFar)
                        : prefs.inactiveOpacityNear);
                final scale =
                    distance == 0 ? prefs.activeLabelScale : 1.0;
                final angle =
                    ((index * (360 / segments)) + layerState.angleDeg) * math.pi / 180;
                final r = 155.0;
                return Transform.translate(
                  offset: Offset(math.cos(angle) * r, math.sin(angle) * r),
                  child: RingSegmentLabel(
                    text: _labelFor(activeLayer, index),
                    active: index == layerState.selectedIndex,
                    color: skin.textPrimary,
                    opacity: opacity,
                    scale: scale,
                  ),
                );
              }),
            ],
          ),
        );
      },
    );
  }

  String _labelFor(RingLayer layer, int index) {
    final labels = switch (layer) {
      RingLayer.command => const <String>[
          'Blueprint',
          'Build',
          'Modify',
          'Simulate',
          'Log',
          'Reflect',
        ],
      RingLayer.domain => const <String>[
          'AI',
          'Robotics',
          'Energy',
          'Bio',
          'Aero',
          'Env',
        ],
      RingLayer.module => const <String>[
          'Module A',
          'Module B',
          'Module C',
          'Module D',
          'Module E',
          'Module F',
        ],
      RingLayer.utility => const <String>[
          'Skins',
          'Save',
          'Network',
          'Perf',
          'Security',
          'Lab',
        ],
    };
    return labels[index % labels.length];
  }

  static int _ringDistance(int index, int selected, int count) {
    final delta = (index - selected).abs();
    return math.min(delta, count - delta);
  }
}

