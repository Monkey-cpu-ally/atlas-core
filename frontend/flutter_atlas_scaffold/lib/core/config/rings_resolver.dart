import 'dart:convert';

import 'package:flutter/services.dart';

import '../../domain/models/rings_profile.dart';

class RingsResolver {
  const RingsResolver._();

  static Future<RingsProfile> resolveDefaultProfile({
    String path = 'assets/rings/rings_default.json',
  }) async {
    try {
      final raw = await rootBundle.loadString(path);
      final decoded = jsonDecode(raw);
      if (decoded is! Map<String, Object?>) {
        return RingsProfile.fallback;
      }
      final schema = decoded[r'$schema']?.toString() ?? '';
      if (schema != 'ajani.rings.schema.v1') {
        return RingsProfile.fallback;
      }
      return _fromMap(decoded);
    } catch (_) {
      return RingsProfile.fallback;
    }
  }

  static RingsProfile _fromMap(Map<String, Object?> map) {
    final meta = _asMap(map['meta']);
    final rings = _asList(map['rings']);
    final snapping = _asMap(map['snapping']);
    final labelingDefaults = _asMap(map['labelingDefaults']);

    final ringDefinitions = <RingDefinition>[];
    for (final ringValue in rings) {
      final ring = _asMap(ringValue);
      final segmentsRaw = _asList(ring['segments']);
      final labeling = _asMap(ring['labeling']);

      final segments = <RingSegmentDefinition>[];
      for (final segmentValue in segmentsRaw) {
        final segment = _asMap(segmentValue);
        segments.add(
          RingSegmentDefinition(
            id: segment['id']?.toString() ?? 'unknown',
            label: segment['label']?.toString() ?? 'UNKNOWN',
            shortLabel: segment['shortLabel']?.toString(),
            icon: segment['icon']?.toString(),
          ),
        );
      }

      ringDefinitions.add(
        RingDefinition(
          id: ring['id']?.toString() ?? 'unknown',
          label: ring['label']?.toString() ?? 'RING',
          radius: _asDouble(ring['radius'], 128),
          segmentCount: _asInt(ring['segmentCount'], segments.length),
          segments: segments,
          labeling: RingLabelingRule(
            alwaysShowLabels: _asBool(labeling['alwaysShowLabels'], false),
            showFullLabelWhenCentered:
                _asBool(labeling['showFullLabelWhenCentered'], false),
          ),
        ),
      );
    }

    return RingsProfile(
      id: meta['id']?.toString() ?? 'rings_default',
      version: _asInt(meta['version'], 1),
      rings: ringDefinitions.isEmpty ? RingsProfile.fallback.rings : ringDefinitions,
      snapping: RingSnappingConfig(
        enabled: _asBool(snapping['enabled'], true),
        inertia: _asDouble(snapping['inertia'], 0.85),
        snapStrength: _asDouble(snapping['snapStrength'], 0.75),
        bounce: _asDouble(snapping['bounce'], 0.08),
      ),
      labelingDefaults: RingLabelingDefaults(
        mode: labelingDefaults['mode']?.toString() ?? 'partial',
        activeLabelScale: _asDouble(labelingDefaults['activeLabelScale'], 1.15),
        inactiveOpacityNear: _asDouble(labelingDefaults['inactiveOpacityNear'], 0.55),
        inactiveOpacityFar: _asDouble(labelingDefaults['inactiveOpacityFar'], 0.18),
        keepLabelsUpright: _asBool(labelingDefaults['keepLabelsUpright'], true),
      ),
    );
  }

  static Map<String, Object?> _asMap(Object? value) {
    if (value is Map<String, Object?>) {
      return value;
    }
    if (value is Map) {
      final out = <String, Object?>{};
      for (final entry in value.entries) {
        out[entry.key.toString()] = entry.value;
      }
      return out;
    }
    return const <String, Object?>{};
  }

  static List<Object?> _asList(Object? value) {
    if (value is List<Object?>) {
      return value;
    }
    if (value is List) {
      return value.cast<Object?>();
    }
    return const <Object?>[];
  }

  static double _asDouble(Object? value, double fallback) {
    return value is num ? value.toDouble() : fallback;
  }

  static int _asInt(Object? value, int fallback) {
    return value is num ? value.toInt() : fallback;
  }

  static bool _asBool(Object? value, bool fallback) {
    return value is bool ? value : fallback;
  }
}

