import 'dart:math' as math;

import 'package:flutter/material.dart';

import '../../domain/controllers/ring_controller.dart';
import '../../domain/models/rings_profile.dart';
import '../../domain/models/ui_prefs.dart';
import '../painters/ring_painter.dart';
import '../themes/skin_tokens.dart';
import 'ring_segment_label.dart';

class RingsWidget extends StatelessWidget {
  const RingsWidget({
    required this.controller,
    required this.skin,
    required this.prefs,
    this.profile = RingsProfile.fallback,
    this.activeLayer = RingLayer.command,
    this.onSelectionCommitted,
    super.key,
  });

  final RingController controller;
  final SkinTokens skin;
  final UiPrefs prefs;
  final RingsProfile profile;
  final RingLayer activeLayer;
  final void Function(RingLayer layer, int index)? onSelectionCommitted;

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: controller,
      builder: (context, _) {
        final activeRing = profile.byLayer(activeLayer);
        final activeSegmentCount = activeRing?.segmentCount ?? 6;
        return GestureDetector(
          behavior: HitTestBehavior.translucent,
          onPanUpdate: (details) {
            controller.rotate(
              layer: activeLayer,
              deltaDeg: details.delta.dx * 0.7,
              segmentCount: activeSegmentCount,
            );
          },
          onPanEnd: (_) {
            controller.snapToNearest(
              layer: activeLayer,
              segmentCount: activeSegmentCount,
            );
            onSelectionCommitted?.call(
              activeLayer,
              controller.layerState(activeLayer).selectedIndex,
            );
          },
          child: Stack(
            alignment: Alignment.center,
            children: [
              for (final ring in profile.rings) _buildRingLayer(ring),
            ],
          ),
        );
      },
    );
  }

  Widget _buildRingLayer(RingDefinition ring) {
    final layer = ring.layer;
    final layerState = controller.layerState(layer);
    final layerTransparency = _layerTransparency(layer);
    final layerMaterial = _layerMaterial(layer);

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
    final segments = (() {
      final raw = ring.segmentCount <= 0 ? ring.segments.length : ring.segmentCount;
      return raw <= 0 ? 1 : raw;
    })();
    final segmentDefs = ring.segments;
    final stepDeg = 360 / segments;
    final labelRadius = ring.radius + 18;

    return Stack(
      alignment: Alignment.center,
      children: [
        Positioned.fill(
          child: CustomPaint(
            painter: RingPainter(
              color: skin.ring,
              opacity: ringOpacity,
              strokeWidth: ringStroke,
              segmentCount: segments,
              radius: ring.radius,
            ),
          ),
        ),
        ...List<Widget>.generate(segments, (index) {
          final distance = _ringDistance(index, layerState.selectedIndex, segments);
          final showLabel = ring.labeling.alwaysShowLabels ||
              (profile.labelingDefaults.mode == 'partial'
                  ? distance <= 2
                  : distance == 0);
          if (!showLabel) {
            return const SizedBox.shrink();
          }

          final opacity = distance == 0
              ? 1.0
              : (distance <= 1
                  ? profile.labelingDefaults.inactiveOpacityNear
                  : profile.labelingDefaults.inactiveOpacityFar);
          final scale = distance == 0
              ? profile.labelingDefaults.activeLabelScale
              : 1.0;
          final segment = segmentDefs.isEmpty
              ? RingSegmentDefinition(id: 'segment_$index', label: 'SEG')
              : segmentDefs[index % segmentDefs.length];
          final useFull =
              distance == 0 && ring.labeling.showFullLabelWhenCentered;
          final text = useFull
              ? segment.label
              : (segment.shortLabel ?? segment.label);

          final angle = ((index * stepDeg) + layerState.angleDeg) * math.pi / 180;
          final offset = Offset(
            math.cos(angle) * labelRadius,
            math.sin(angle) * labelRadius,
          );

          Widget label = RingSegmentLabel(
            text: text,
            active: distance == 0,
            color: skin.textPrimary,
            opacity: opacity,
            scale: scale,
          );

          if (!profile.labelingDefaults.keepLabelsUpright) {
            label = Transform.rotate(
              angle: angle + (math.pi / 2),
              child: label,
            );
          }

          return Transform.translate(
            offset: offset,
            child: label,
          );
        }),
      ],
    );
  }

  double _layerTransparency(RingLayer layer) {
    return switch (layer) {
      RingLayer.command => prefs.commandRingTransparency,
      RingLayer.domain => prefs.domainRingTransparency,
      RingLayer.module => prefs.moduleRingTransparency,
      RingLayer.utility => prefs.utilityRingTransparency,
    };
  }

  String _layerMaterial(RingLayer layer) {
    return switch (layer) {
      RingLayer.command => prefs.commandRingMaterial,
      RingLayer.domain => prefs.domainRingMaterial,
      RingLayer.module => prefs.moduleRingMaterial,
      RingLayer.utility => prefs.utilityRingMaterial,
    };
  }

  static int _ringDistance(int index, int selected, int count) {
    final delta = (index - selected).abs();
    return math.min(delta, count - delta);
  }
}

