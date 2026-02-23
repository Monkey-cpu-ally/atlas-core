import 'package:flutter/foundation.dart';

import '../controllers/ring_controller.dart';

@immutable
class RingSegmentDefinition {
  const RingSegmentDefinition({
    required this.id,
    required this.label,
    this.shortLabel,
    this.icon,
  });

  final String id;
  final String label;
  final String? shortLabel;
  final String? icon;
}

@immutable
class RingLabelingRule {
  const RingLabelingRule({
    this.alwaysShowLabels = false,
    this.showFullLabelWhenCentered = false,
  });

  final bool alwaysShowLabels;
  final bool showFullLabelWhenCentered;
}

@immutable
class RingDefinition {
  const RingDefinition({
    required this.id,
    required this.label,
    required this.radius,
    required this.segmentCount,
    required this.segments,
    this.labeling = const RingLabelingRule(),
  });

  final String id;
  final String label;
  final double radius;
  final int segmentCount;
  final List<RingSegmentDefinition> segments;
  final RingLabelingRule labeling;

  RingLayer get layer => switch (id) {
        'command' => RingLayer.command,
        'domain' => RingLayer.domain,
        'modules' => RingLayer.module,
        'module' => RingLayer.module,
        'utility' => RingLayer.utility,
        _ => RingLayer.command,
      };
}

@immutable
class RingSnappingConfig {
  const RingSnappingConfig({
    this.enabled = true,
    this.inertia = 0.85,
    this.snapStrength = 0.75,
    this.bounce = 0.08,
  });

  final bool enabled;
  final double inertia;
  final double snapStrength;
  final double bounce;
}

@immutable
class RingLabelingDefaults {
  const RingLabelingDefaults({
    this.mode = 'partial',
    this.activeLabelScale = 1.15,
    this.inactiveOpacityNear = 0.55,
    this.inactiveOpacityFar = 0.18,
    this.keepLabelsUpright = true,
  });

  final String mode;
  final double activeLabelScale;
  final double inactiveOpacityNear;
  final double inactiveOpacityFar;
  final bool keepLabelsUpright;
}

@immutable
class RingsProfile {
  const RingsProfile({
    required this.id,
    required this.version,
    required this.rings,
    this.snapping = const RingSnappingConfig(),
    this.labelingDefaults = const RingLabelingDefaults(),
  });

  final String id;
  final int version;
  final List<RingDefinition> rings;
  final RingSnappingConfig snapping;
  final RingLabelingDefaults labelingDefaults;

  RingDefinition? byLayer(RingLayer layer) {
    for (final ring in rings) {
      if (ring.layer == layer) {
        return ring;
      }
    }
    return null;
  }

  static const fallback = RingsProfile(
    id: 'rings_default',
    version: 1,
    rings: <RingDefinition>[
      RingDefinition(
        id: 'command',
        label: 'COMMAND',
        radius: 128,
        segmentCount: 5,
        segments: <RingSegmentDefinition>[
          RingSegmentDefinition(id: 'blueprint', label: 'BLUEPRINT'),
          RingSegmentDefinition(id: 'build', label: 'BUILD'),
          RingSegmentDefinition(id: 'modify', label: 'MODIFY'),
          RingSegmentDefinition(id: 'simulate', label: 'SIMULATE'),
          RingSegmentDefinition(id: 'log', label: 'LOG'),
        ],
        labeling: RingLabelingRule(alwaysShowLabels: true),
      ),
      RingDefinition(
        id: 'domain',
        label: 'DOMAINS',
        radius: 162,
        segmentCount: 6,
        segments: <RingSegmentDefinition>[
          RingSegmentDefinition(id: 'ai', label: 'AI', shortLabel: 'AI'),
          RingSegmentDefinition(
            id: 'robotics',
            label: 'ROBOTICS',
            shortLabel: 'ROBO',
          ),
          RingSegmentDefinition(id: 'energy', label: 'ENERGY', shortLabel: 'ENRG'),
          RingSegmentDefinition(id: 'bio', label: 'BIOLOGY', shortLabel: 'BIO'),
          RingSegmentDefinition(id: 'aero', label: 'AEROSPACE', shortLabel: 'AERO'),
          RingSegmentDefinition(id: 'env', label: 'ENV SYSTEMS', shortLabel: 'ENV'),
        ],
      ),
      RingDefinition(
        id: 'modules',
        label: 'MODULES',
        radius: 195,
        segmentCount: 6,
        segments: <RingSegmentDefinition>[
          RingSegmentDefinition(id: 'projects', label: 'PROJECTS', shortLabel: 'PROJ'),
          RingSegmentDefinition(id: 'blueprints', label: 'BLUEPRINTS', shortLabel: 'BPL'),
          RingSegmentDefinition(id: 'sim_lab', label: 'SIM LAB', shortLabel: 'SIM'),
          RingSegmentDefinition(id: 'materials_db', label: 'MATERIAL DB', shortLabel: 'DB'),
          RingSegmentDefinition(id: 'skins', label: 'SKINS', shortLabel: 'SKIN'),
          RingSegmentDefinition(id: 'export', label: 'EXPORT', shortLabel: 'EXP'),
        ],
      ),
      RingDefinition(
        id: 'utility',
        label: 'UTILITY',
        radius: 226,
        segmentCount: 8,
        segments: <RingSegmentDefinition>[
          RingSegmentDefinition(id: 'search', label: 'SEARCH', shortLabel: 'SRCH'),
          RingSegmentDefinition(id: 'filters', label: 'FILTERS', shortLabel: 'FLTR'),
          RingSegmentDefinition(id: 'status', label: 'STATUS', shortLabel: 'STAT'),
          RingSegmentDefinition(id: 'alerts', label: 'ALERTS', shortLabel: 'ALRT'),
          RingSegmentDefinition(id: 'privacy', label: 'PRIVACY', shortLabel: 'PRIV'),
          RingSegmentDefinition(id: 'help', label: 'HELP', shortLabel: 'HELP'),
          RingSegmentDefinition(id: 'about', label: 'ABOUT', shortLabel: 'INFO'),
          RingSegmentDefinition(id: 'reset_ui', label: 'RESET UI', shortLabel: 'RSET'),
        ],
      ),
    ],
  );
}

