import 'dart:convert';

import 'package:flutter/services.dart';

import '../../domain/models/rings_profile.dart';

class RingsResolver {
  const RingsResolver._();

  static const _ringsSchemaId = 'ajani.rings.schema.v1';

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
      if (schema != _ringsSchemaId) {
        return RingsProfile.fallback;
      }
      if (!_isValidAjaniRingsV1(decoded)) {
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

  static bool _isValidAjaniRingsV1(Map<String, Object?> map) {
    if (!_hasKeys(map, const [r'$schema', 'meta', 'rings', 'snapping', 'labelingDefaults'])) {
      return false;
    }

    final meta = _asMap(map['meta']);
    if (!_hasKeys(meta, const ['id', 'version', 'author'])) {
      return false;
    }
    if (!_isNonEmptyString(meta['id']) ||
        !_isIntInRange(meta['version'], 1, 999) ||
        !_isNonEmptyString(meta['author'])) {
      return false;
    }

    final rings = _asList(map['rings']);
    if (rings.isEmpty) {
      return false;
    }
    for (final ringValue in rings) {
      final ring = _asMap(ringValue);
      if (!_hasKeys(
        ring,
        const ['id', 'label', 'radius', 'segmentCount', 'segments', 'labeling'],
      )) {
        return false;
      }
      if (!_isNonEmptyString(ring['id']) ||
          !_isNonEmptyString(ring['label']) ||
          !_isNumInRange(ring['radius'], 0, 300) ||
          !_isIntInRange(ring['segmentCount'], 1, 20)) {
        return false;
      }

      final segments = _asList(ring['segments']);
      if (segments.isEmpty || segments.length > 20) {
        return false;
      }
      for (final segmentValue in segments) {
        final segment = _asMap(segmentValue);
        if (!_hasKeys(segment, const ['id', 'label'])) {
          return false;
        }
        if (!_isNonEmptyString(segment['id']) || !_isNonEmptyString(segment['label'])) {
          return false;
        }
        final shortLabel = segment['shortLabel'];
        if (shortLabel != null && !_isNonEmptyString(shortLabel)) {
          return false;
        }
        final icon = segment['icon'];
        if (icon != null && !_isNonEmptyString(icon)) {
          return false;
        }
      }

      final labeling = _asMap(ring['labeling']);
      if (!_hasKeys(labeling, const ['alwaysShowLabels', 'showFullLabelWhenCentered'])) {
        return false;
      }
      if (labeling['alwaysShowLabels'] is! bool ||
          labeling['showFullLabelWhenCentered'] is! bool) {
        return false;
      }
    }

    final snapping = _asMap(map['snapping']);
    if (!_hasKeys(snapping, const ['enabled', 'inertia', 'snapStrength', 'bounce'])) {
      return false;
    }
    if (snapping['enabled'] is! bool ||
        !_isNumInRange(snapping['inertia'], 0, 1) ||
        !_isNumInRange(snapping['snapStrength'], 0, 1) ||
        !_isNumInRange(snapping['bounce'], 0, 1)) {
      return false;
    }

    final labelingDefaults = _asMap(map['labelingDefaults']);
    if (!_hasKeys(
      labelingDefaults,
      const ['mode', 'activeLabelScale', 'inactiveOpacityNear', 'inactiveOpacityFar', 'keepLabelsUpright'],
    )) {
      return false;
    }
    if (!const {'partial', 'full'}.contains(labelingDefaults['mode']?.toString()) ||
        !_isNumInRange(labelingDefaults['activeLabelScale'], 1, 2) ||
        !_isNumInRange(labelingDefaults['inactiveOpacityNear'], 0, 1) ||
        !_isNumInRange(labelingDefaults['inactiveOpacityFar'], 0, 1) ||
        labelingDefaults['keepLabelsUpright'] is! bool) {
      return false;
    }

    return true;
  }

  static bool _hasKeys(Map<String, Object?> map, List<String> keys) {
    for (final key in keys) {
      if (!map.containsKey(key)) {
        return false;
      }
    }
    return true;
  }

  static bool _isNonEmptyString(Object? value) {
    return value is String && value.trim().isNotEmpty;
  }

  static bool _isNumInRange(Object? value, double min, double max) {
    if (value is! num) {
      return false;
    }
    final asDouble = value.toDouble();
    return asDouble >= min && asDouble <= max;
  }

  static bool _isIntInRange(Object? value, int min, int max) {
    if (value is! num) {
      return false;
    }
    final asInt = value.toInt();
    if (asInt.toDouble() != value.toDouble()) {
      return false;
    }
    return asInt >= min && asInt <= max;
  }
}

