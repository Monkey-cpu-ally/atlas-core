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
    final ringOpacity = (0.5 * (1 - prefs.ringTransparency)).clamp(0.06, 0.85);
    final ringStroke = (1.4 * prefs.ringLineWeight).clamp(0.6, 3.6).toDouble();

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
                final angle =
                    ((index * (360 / segments)) + layerState.angleDeg) * math.pi / 180;
                final r = 155.0;
                return Transform.translate(
                  offset: Offset(math.cos(angle) * r, math.sin(angle) * r),
                  child: RingSegmentLabel(
                    text: _labelFor(activeLayer, index),
                    active: index == layerState.selectedIndex,
                    color: skin.textPrimary,
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
}

