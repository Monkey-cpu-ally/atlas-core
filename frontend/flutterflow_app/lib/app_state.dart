import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';

class FFAppState extends ChangeNotifier {
  static FFAppState _instance = FFAppState._internal();

  factory FFAppState() {
    return _instance;
  }

  FFAppState._internal();

  static void reset() {
    _instance = FFAppState._internal();
  }

  Future initializePersistedState() async {
    prefs = await SharedPreferences.getInstance();
    _safeInit(() {
      _aiMode = prefs.getString('ff_aiMode') ?? _aiMode;
      _atlasBaseUrl = prefs.getString('ff_atlasBaseUrl') ?? _atlasBaseUrl;
      _skinId = prefs.getString('ff_skinId') ?? _skinId;
      _dialVisualPrefsJson =
          prefs.getString('ff_dialVisualPrefsJson') ?? _dialVisualPrefsJson;
      _dialPreviewRingsProfilePath = prefs.getString(
            'ff_dialPreviewRingsProfilePath',
          ) ??
          _dialPreviewRingsProfilePath;
      _dialPreviewUiPrefsProfilePath = prefs.getString(
            'ff_dialPreviewUiPrefsProfilePath',
          ) ??
          _dialPreviewUiPrefsProfilePath;
    });
  }

  void update(VoidCallback callback) {
    callback();
    notifyListeners();
  }

  late SharedPreferences prefs;

  /// Control the AI face behavior state: idle,listening, thinking,speaking
  String _aiMode = '';
  String get aiMode => _aiMode;
  set aiMode(String value) {
    _aiMode = value;
    prefs.setString('ff_aiMode', value);
  }

  /// Persisted backend base URL (dev and local LAN setups).
  String _atlasBaseUrl = '';
  String get atlasBaseUrl => _atlasBaseUrl;
  set atlasBaseUrl(String value) {
    _atlasBaseUrl = value;
    prefs.setString('ff_atlasBaseUrl', value);
  }

  /// Persisted UI skin selection (free selection model; manual only).
  String _skinId = 'lumen_core';
  String get skinId => _skinId;
  set skinId(String value) {
    _skinId = value;
    prefs.setString('ff_skinId', value);
  }

  /// Persisted modular visual preferences as JSON.
  String _dialVisualPrefsJson = '';
  String get dialVisualPrefsJson => _dialVisualPrefsJson;
  set dialVisualPrefsJson(String value) {
    _dialVisualPrefsJson = value;
    prefs.setString('ff_dialVisualPrefsJson', value);
  }

  /// Selected rings schema profile used by Dial Preview.
  String _dialPreviewRingsProfilePath = 'assets/rings/rings_default.json';
  String get dialPreviewRingsProfilePath => _dialPreviewRingsProfilePath;
  set dialPreviewRingsProfilePath(String value) {
    _dialPreviewRingsProfilePath = value;
    prefs.setString('ff_dialPreviewRingsProfilePath', value);
  }

  /// Selected UI prefs schema profile used by Dial Preview.
  String _dialPreviewUiPrefsProfilePath = 'assets/prefs/ui_prefs_default.json';
  String get dialPreviewUiPrefsProfilePath => _dialPreviewUiPrefsProfilePath;
  set dialPreviewUiPrefsProfilePath(String value) {
    _dialPreviewUiPrefsProfilePath = value;
    prefs.setString('ff_dialPreviewUiPrefsProfilePath', value);
  }

  /// True while AI is processing a response
  bool _isThinking = false;
  bool get isThinking => _isThinking;
  set isThinking(bool value) {
    _isThinking = value;
  }

  /// True while AI is speaking or outputting text/audio
  bool _isSpeaking = false;
  bool get isSpeaking => _isSpeaking;
  set isSpeaking(bool value) {
    _isSpeaking = value;
  }

  /// True when microphone is actively listening
  bool _isListening = false;
  bool get isListening => _isListening;
  set isListening(bool value) {
    _isListening = value;
  }
}

void _safeInit(Function() initializeField) {
  try {
    initializeField();
  } catch (_) {}
}

Future _safeInitAsync(Function() initializeField) async {
  try {
    await initializeField();
  } catch (_) {}
}
