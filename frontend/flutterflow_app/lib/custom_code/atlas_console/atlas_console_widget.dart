import 'package:flutter/foundation.dart'
    show TargetPlatform, defaultTargetPlatform, kIsWeb;
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import 'package:flutter_atlas_scaffold/atlas_voice_core.dart';

import '/app_state.dart';
import '../atlas_backend/atlas_backend_client.dart';
import 'json_download.dart' as json_download;
import 'dart:convert';
import 'dart:math' as math;

enum _AtlasWorkspaceView { console, dialPreview }

class _DialAssetOption {
  const _DialAssetOption({
    required this.label,
    required this.path,
  });

  final String label;
  final String path;
}

class AtlasConsoleWidget extends StatefulWidget {
  const AtlasConsoleWidget({super.key});

  @override
  State<AtlasConsoleWidget> createState() => _AtlasConsoleWidgetState();
}

class _AtlasConsoleWidgetState extends State<AtlasConsoleWidget> {
  static const _defaultRingsProfilePath = 'assets/rings/rings_default.json';
  static const _defaultUiPrefsProfilePath = 'assets/prefs/ui_prefs_default.json';
  static const _customRingsProfilePath = '__custom_rings__';
  static const _customUiPrefsProfilePath = '__custom_ui_prefs__';
  static const _ringsProfileOptions = <_DialAssetOption>[
    _DialAssetOption(
      label: 'Default Rings',
      path: 'assets/rings/rings_default.json',
    ),
    _DialAssetOption(
      label: 'Precision Rings',
      path: 'assets/rings/rings_precision.json',
    ),
    _DialAssetOption(
      label: 'Custom Rings (saved)',
      path: _customRingsProfilePath,
    ),
  ];
  static const _uiPrefsProfileOptions = <_DialAssetOption>[
    _DialAssetOption(
      label: 'Default UI Prefs',
      path: 'assets/prefs/ui_prefs_default.json',
    ),
    _DialAssetOption(
      label: 'Calm UI Prefs',
      path: 'assets/prefs/ui_prefs_calm.json',
    ),
    _DialAssetOption(
      label: 'Custom UI Prefs (saved)',
      path: _customUiPrefsProfilePath,
    ),
  ];

  final _client = AtlasBackendClient();
  final _voiceCore = VoiceCoreController();

  late final TextEditingController _baseUrlController;
  final _projectController =
      TextEditingController(text: 'atlas_core_hybrid_system');
  final _inputController = TextEditingController();

  String _mode = 'mentor';
  late AtlasSkinId _skin;
  late DialVisualPrefs _visualPrefs;
  final ScrollController _scrollController = ScrollController();
  double _dynamicTiltUnit = 0.0;
  bool _appearanceLabActive = false;
  bool _appearanceLabExiting = false;
  bool _accentPreviewEnabled = false;
  String _accentPreviewId = 'hermes';
  _AtlasWorkspaceView _workspaceView = _AtlasWorkspaceView.console;
  String _dialPreviewSkinId = AtlasSkinId.lumenCore.id;
  String _dialPreviewRingsProfilePath = _defaultRingsProfilePath;
  String _dialPreviewUiPrefsProfilePath = _defaultUiPrefsProfilePath;
  String _dialPreviewCustomRingsJson = '';
  String _dialPreviewCustomUiPrefsJson = '';

  bool _loading = false;
  String? _error;
  Map<String, dynamic>? _last;

  bool _healthLoading = false;
  Map<String, dynamic>? _health;
  String? _healthError;

  @override
  void initState() {
    super.initState();
    // Defaults:
    // - Android emulator -> host machine: 10.0.2.2
    // - iOS simulator -> host machine: 127.0.0.1
    // - physical devices -> use your computer LAN IP (e.g. http://192.168.1.20:8000)
    final defaultBaseUrl = kIsWeb
        ? 'http://127.0.0.1:8000'
        : (defaultTargetPlatform == TargetPlatform.android
            ? 'http://10.0.2.2:8000'
            : 'http://127.0.0.1:8000');
    final saved = FFAppState().atlasBaseUrl.trim();
    _baseUrlController = TextEditingController(
      text: saved.isNotEmpty ? saved : defaultBaseUrl,
    );

    _skin = AtlasSkinIdX.fromId(FFAppState().skinId);
    _dialPreviewSkinId = _skin.id;
    _dialPreviewCustomRingsJson = FFAppState().dialPreviewCustomRingsJson;
    _dialPreviewCustomUiPrefsJson = FFAppState().dialPreviewCustomUiPrefsJson;

    final savedRingsPath = FFAppState().dialPreviewRingsProfilePath.trim();
    _dialPreviewRingsProfilePath = _isKnownPath(
      savedRingsPath,
      _ringsProfileOptions,
    )
        ? savedRingsPath
        : _defaultRingsProfilePath;
    if (_dialPreviewRingsProfilePath == _customRingsProfilePath &&
        _dialPreviewCustomRingsJson.trim().isEmpty) {
      _dialPreviewRingsProfilePath = _defaultRingsProfilePath;
    }
    if (_dialPreviewRingsProfilePath == _customRingsProfilePath &&
        RingsResolver.parseRawJson(_dialPreviewCustomRingsJson) == null) {
      _dialPreviewRingsProfilePath = _defaultRingsProfilePath;
    }
    if (_dialPreviewRingsProfilePath != savedRingsPath &&
        savedRingsPath.isNotEmpty) {
      FFAppState().dialPreviewRingsProfilePath = _dialPreviewRingsProfilePath;
    }

    final savedUiPrefsPath = FFAppState().dialPreviewUiPrefsProfilePath.trim();
    _dialPreviewUiPrefsProfilePath = _isKnownPath(
      savedUiPrefsPath,
      _uiPrefsProfileOptions,
    )
        ? savedUiPrefsPath
        : _defaultUiPrefsProfilePath;
    if (_dialPreviewUiPrefsProfilePath == _customUiPrefsProfilePath &&
        _dialPreviewCustomUiPrefsJson.trim().isEmpty) {
      _dialPreviewUiPrefsProfilePath = _defaultUiPrefsProfilePath;
    }
    if (_dialPreviewUiPrefsProfilePath == _customUiPrefsProfilePath &&
        UiPrefsResolver.parseRawJson(_dialPreviewCustomUiPrefsJson) == null) {
      _dialPreviewUiPrefsProfilePath = _defaultUiPrefsProfilePath;
    }
    if (_dialPreviewUiPrefsProfilePath != savedUiPrefsPath &&
        savedUiPrefsPath.isNotEmpty) {
      FFAppState().dialPreviewUiPrefsProfilePath = _dialPreviewUiPrefsProfilePath;
    }

    _visualPrefs = DialVisualPrefsCodec.decodeOrDefaults(
      FFAppState().dialVisualPrefsJson,
    );

    _scrollController.addListener(() {
      if (!mounted) return;
      if (_visualPrefs.panelTiltMode != PanelTiltMode.dynamic) return;
      final o = _scrollController.offset;
      final unit = (math.sin(o / 180.0) * 0.35).clamp(-0.5, 0.5).toDouble();
      if ((unit - _dynamicTiltUnit).abs() > 0.01) {
        setState(() => _dynamicTiltUnit = unit);
      }
    });
  }

  @override
  void dispose() {
    _voiceCore.dispose();
    _baseUrlController.dispose();
    _projectController.dispose();
    _inputController.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  Future<void> _enterAppearanceLab() async {
    setState(() {
      _appearanceLabActive = true;
      _appearanceLabExiting = false;
      _accentPreviewEnabled = false;
      _accentPreviewId = 'hermes';
    });
    _voiceCore.enterAppearanceLab(backgroundDimPercent: 6);
    // Minimal calibration tone + subtle confirmation.
    HapticFeedback.selectionClick();
    // ignore: deprecated_member_use
    SystemSound.play(SystemSoundType.click);
    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Appearance calibration mode active.'),
          duration: Duration(seconds: 2),
        ),
      );
    }
  }

  Future<void> _exitAppearanceLab() async {
    setState(() => _appearanceLabExiting = true);
    await Future<void>.delayed(const Duration(milliseconds: 400));
    if (!mounted) return;
    // Exit auto-saves configuration (no save button in Appearance Lab).
    _persistVisualPrefs();
    _voiceCore.exitAppearanceLab();
    setState(() {
      _appearanceLabActive = false;
      _appearanceLabExiting = false;
    });
  }

  void _resetToSkinDefaults() {
    final defaults = AtlasSkins.visualDefaults(_skin);
    setState(() => _visualPrefs = defaults);
    _persistVisualPrefs();
  }

  void _persistVisualPrefs() {
    FFAppState().dialVisualPrefsJson = DialVisualPrefsCodec.encode(_visualPrefs);
  }

  Widget _buildAppearanceLab(
    BuildContext context,
    AtlasSkinTokens skinTokens,
    double ringOpacity,
    double ringStrokeWidth,
  ) {
    // Appearance Lab rules:
    // - controlled environment
    // - no council (disabled by controller)
    // - Hermes ivory accent
    // - no sigil / halo / particles (not rendered here)
    final scheme = Theme.of(context).colorScheme;

    final previewOn = _accentPreviewEnabled;
    final previewId = _accentPreviewId;
    final previewRim = switch (previewId) {
      'ajani' => VoiceCoreController.ajaniAccent,
      'minerva' => VoiceCoreController.minervaAccent,
      'hermes' => VoiceCoreController.hermesAccent,
      'council' => VoiceCoreController.ghostPurpleAccent,
      _ => VoiceCoreController.hermesAccent,
    };
    final rimColor = _appearanceLabExiting
        ? VoiceCoreController.neutralAccent
        : (previewOn ? previewRim : VoiceCoreController.hermesAccent);

    final dialSize = 340.0;
    final coreRotationPeriod = _appearanceLabExiting
        ? const Duration(seconds: 12)
        : const Duration(seconds: 45); // slow, not stopped

    final overlaysOpacity = _appearanceLabExiting ? 0.0 : 1.0;

    Widget panel(String title, Widget child) {
      return AnimatedOpacity(
        opacity: overlaysOpacity,
        duration: const Duration(milliseconds: 400),
        curve: Curves.easeOut,
        child: SizedBox(
          width: 280,
          child: DialPanel(
            visualPrefs: _visualPrefs,
            surfaceColor: scheme.surface.withOpacity(0.92),
            borderColor: scheme.outline,
            borderRadius: BorderRadius.circular(12),
            dynamicTiltUnit: 0.0,
            tiltBlendDuration: const Duration(milliseconds: 250),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: Theme.of(context).textTheme.titleSmall?.copyWith(
                        fontWeight: FontWeight.w700,
                      ),
                ),
                const SizedBox(height: 8),
                child,
              ],
            ),
          ),
        ),
      );
    }

    return Stack(
      fit: StackFit.expand,
      children: [
        ColoredBox(color: skinTokens.background),
        // Background dim (5–8%).
        AnimatedOpacity(
          opacity: _appearanceLabExiting ? 0.0 : 0.07,
          duration: const Duration(milliseconds: 400),
          curve: Curves.easeOut,
          child: const ColoredBox(color: Colors.black),
        ),
        SafeArea(
          child: LayoutBuilder(
            builder: (context, constraints) {
              final isWide = constraints.maxWidth >= 980;
              final dial = TweenAnimationBuilder<double>(
                duration: const Duration(milliseconds: 250),
                curve: Curves.easeOut,
                tween: Tween<double>(end: ringOpacity),
                builder: (context, smoothedOpacity, _) {
                  return TweenAnimationBuilder<double>(
                    duration: const Duration(milliseconds: 250),
                    curve: Curves.easeOut,
                    tween: Tween<double>(end: ringStrokeWidth),
                    builder: (context, smoothedStroke, __) {
                      return SizedBox(
                        width: dialSize,
                        height: dialSize,
                        child: VoiceCoreLayer(
                          state: _voiceCore.state,
                          // Do not rely on the council dim toggle in Appearance Lab.
                          visualPrefs:
                              _visualPrefs.copyWith(councilDimOverlayEnabled: false),
                          timing: _voiceCore.timing,
                          ringColor: skinTokens.ringStroke,
                          ringOpacity: smoothedOpacity,
                          ringStrokeWidth: smoothedStroke,
                          backgroundColor: skinTokens.background,
                          microDetailColor: skinTokens.border,
                          frameColor: skinTokens.border,
                          coreWidget: _PlaceholderCore(
                            surface: skinTokens.surface,
                            border: skinTokens.border,
                            text: skinTokens.textSecondary,
                            rim: rimColor,
                            rotationPeriod: coreRotationPeriod,
                          ),
                        ),
                      );
                    },
                  );
                },
              );

                final left = panel(
                  'Left',
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Panel tilt (degrees)',
                        style:
                            TextStyle(color: skinTokens.textSecondary, fontSize: 12),
                      ),
                      Text(
                        '${_visualPrefs.panelTiltDegrees.toStringAsFixed(1)}°',
                        style: TextStyle(
                          color: skinTokens.textPrimary,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                      Slider(
                        value: _visualPrefs.panelTiltDegrees,
                        min: 0,
                        max: 15,
                        onChanged: (v) => _setPanelTiltDegrees(v, persist: false),
                        onChangeEnd: (_) => _persistVisualPrefs(),
                      ),
                      const SizedBox(height: 8),
                      Row(
                        children: [
                          Expanded(
                            child: DropdownButton<FrameType>(
                              value: _visualPrefs.frameType,
                              isExpanded: true,
                              items: FrameType.values
                                  .map((f) => DropdownMenuItem(
                                        value: f,
                                        child: Text(f.name),
                                      ))
                                  .toList(),
                              onChanged: (v) {
                                if (v == null) return;
                                _setFrameType(v);
                              },
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 8),
                      DropdownButton<FrameOpacityMode>(
                        value: _visualPrefs.frameOpacityMode,
                        items: FrameOpacityMode.values
                            .map((o) => DropdownMenuItem(
                                  value: o,
                                  child: Text(o.name),
                                ))
                            .toList(),
                        onChanged: (v) {
                          if (v == null) return;
                          _setFrameOpacity(v);
                        },
                      ),
                    ],
                  ),
                );

                final right = panel(
                  'Right',
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      DropdownButton<RingMaterialMode>(
                        value: _visualPrefs.ringMaterialMode,
                        isExpanded: true,
                        items: RingMaterialMode.values
                            .map((m) => DropdownMenuItem(
                                  value: m,
                                  child: Text(m.name),
                                ))
                            .toList(),
                        onChanged: (v) {
                          if (v == null) return;
                          _setRingMaterial(v);
                        },
                      ),
                      const SizedBox(height: 8),
                      Text(
                        'Transparency (0–60%)',
                        style:
                            TextStyle(color: skinTokens.textSecondary, fontSize: 12),
                      ),
                      Text(
                        '${(_visualPrefs.ringTransparencyStrength * 100).toStringAsFixed(0)}%',
                        style: TextStyle(
                          color: skinTokens.textPrimary,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                      Slider(
                        value: _visualPrefs.ringTransparencyStrength,
                        min: 0.0,
                        max: 0.60,
                        onChanged: (v) => _setRingTransparency(v, persist: false),
                        onChangeEnd: (_) => _persistVisualPrefs(),
                      ),
                      Text(
                        'Line weight',
                        style:
                            TextStyle(color: skinTokens.textSecondary, fontSize: 12),
                      ),
                      Text(
                        _visualPrefs.ringLineWeight.toStringAsFixed(2),
                        style: TextStyle(
                          color: skinTokens.textPrimary,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                      Slider(
                        value: _visualPrefs.ringLineWeight,
                        min: 0.6,
                        max: 2.2,
                        onChanged: (v) => _setRingLineWeight(v, persist: false),
                        onChangeEnd: (_) => _persistVisualPrefs(),
                      ),
                    ],
                  ),
                );

                final bottom = panel(
                  'Bottom',
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      DropdownButton<BackgroundType>(
                        value: _visualPrefs.backgroundType,
                        isExpanded: true,
                        items: BackgroundType.values
                            .map((b) => DropdownMenuItem(
                                  value: b,
                                  child: Text(b.name),
                                ))
                            .toList(),
                        onChanged: (v) {
                          if (v == null) return;
                          _setBackgroundType(v);
                        },
                      ),
                      SwitchListTile(
                        value: _accentPreviewEnabled,
                        onChanged: (v) => setState(() => _accentPreviewEnabled = v),
                        title: const Text('Accent preview toggle'),
                        dense: true,
                        contentPadding: EdgeInsets.zero,
                      ),
                      if (_accentPreviewEnabled)
                        Wrap(
                          spacing: 8,
                          children: [
                            for (final id in ['ajani', 'minerva', 'hermes', 'council'])
                              ChoiceChip(
                                label: Text(id),
                                selected: _accentPreviewId == id,
                                onSelected: (_) =>
                                    setState(() => _accentPreviewId = id),
                              ),
                          ],
                        ),
                      const SizedBox(height: 8),
                      Row(
                        children: [
                          OutlinedButton(
                            onPressed: _resetToSkinDefaults,
                            child: const Text('Reset to Default'),
                          ),
                          const Spacer(),
                          Text(
                            'Exit auto-saves',
                            style: TextStyle(
                              color: skinTokens.textSecondary,
                              fontSize: 12,
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                );

              if (!isWide) {
                return Stack(
                  children: [
                    Positioned.fill(
                      child: SingleChildScrollView(
                        padding: const EdgeInsets.fromLTRB(0, 56, 0, 20),
                        child: Column(
                          children: [
                            Center(child: dial),
                            const SizedBox(height: 12),
                            Padding(
                              padding:
                                  const EdgeInsets.symmetric(horizontal: 16),
                              child: Column(
                                children: [
                                  left,
                                  const SizedBox(height: 12),
                                  right,
                                  const SizedBox(height: 12),
                                  bottom,
                                ],
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                    Positioned(
                      top: 12,
                      right: 12,
                      child: AnimatedOpacity(
                        opacity: overlaysOpacity,
                        duration: const Duration(milliseconds: 400),
                        curve: Curves.easeOut,
                        child: ElevatedButton(
                          onPressed: _exitAppearanceLab,
                          child: const Text('Exit'),
                        ),
                      ),
                    ),
                  ],
                );
              }

              return Stack(
                children: [
                  Center(child: dial),
                  Positioned(
                    top: 12,
                    right: 12,
                    child: AnimatedOpacity(
                      opacity: overlaysOpacity,
                      duration: const Duration(milliseconds: 400),
                      curve: Curves.easeOut,
                      child: ElevatedButton(
                        onPressed: _exitAppearanceLab,
                        child: const Text('Exit'),
                      ),
                    ),
                  ),
                  Positioned(
                    top: 64,
                    left: 16,
                    child: left,
                  ),
                  Positioned(
                    top: 64,
                    right: 16,
                    child: right,
                  ),
                  Positioned(
                    bottom: 16,
                    left: (constraints.maxWidth - 620) / 2,
                    child: SizedBox(
                      width: 620,
                      child: bottom,
                    ),
                  ),
                ],
              );
            },
          ),
        ),
      ],
    );
  }

  Future<void> _run() async {
    final baseUrl = _baseUrlController.text.trim();
    final project = _projectController.text.trim();
    final userInput = _inputController.text.trim();

    if (baseUrl.isEmpty || project.isEmpty || userInput.isEmpty) {
      setState(() {
        _error = 'Base URL, project, and input are required.';
      });
      return;
    }

    setState(() {
      _loading = true;
      _error = null;
      _last = null;
    });

    try {
      final res = await _client.orchestrate(
        baseUrl: baseUrl,
        project: project,
        userInput: userInput,
        mode: _mode,
      );
      setState(() {
        _last = res;
      });
    } on AtlasBackendException catch (e) {
      setState(() {
        _error = '${e.message}\nHTTP: ${e.statusCode}\n${e.responseBody ?? ''}';
      });
    } catch (e) {
      setState(() {
        _error = 'Unexpected error: $e';
      });
    } finally {
      if (mounted) {
        setState(() {
          _loading = false;
        });
      }
    }
  }

  Future<void> _checkHealth() async {
    final baseUrl = _baseUrlController.text.trim();
    if (baseUrl.isEmpty) {
      setState(() {
        _healthError = 'Base URL is required.';
      });
      return;
    }
    setState(() {
      _healthLoading = true;
      _healthError = null;
      _health = null;
    });
    try {
      final res = await _client.health(baseUrl: baseUrl);
      setState(() {
        _health = res;
      });
    } on AtlasBackendException catch (e) {
      setState(() {
        _healthError =
            '${e.message}\nHTTP: ${e.statusCode}\n${e.responseBody ?? ''}';
      });
    } catch (e) {
      setState(() {
        _healthError = 'Unexpected error: $e';
      });
    } finally {
      if (mounted) {
        setState(() => _healthLoading = false);
      }
    }
  }

  void _setBaseUrl(String url) {
    _baseUrlController.text = url;
    FFAppState().atlasBaseUrl = url;
    setState(() {});
  }

  void _setSkin(AtlasSkinId skin) {
    setState(() {
      _skin = skin;
      _dialPreviewSkinId = skin.id;
    });
    FFAppState().skinId = skin.id;
  }

  void _setBackgroundType(BackgroundType type) {
    setState(() => _visualPrefs = _visualPrefs.copyWith(backgroundType: type));
    _persistVisualPrefs();
  }

  void _setFrameType(FrameType type) {
    setState(() => _visualPrefs = _visualPrefs.copyWith(frameType: type));
    _persistVisualPrefs();
  }

  void _setDimOverlay(bool enabled) {
    setState(() => _visualPrefs =
        _visualPrefs.copyWith(councilDimOverlayEnabled: enabled));
    _persistVisualPrefs();
  }

  void _setPanelTiltMode(PanelTiltMode mode) {
    // If the user changes mode, nudge degrees into the expected band.
    var degrees = _visualPrefs.panelTiltDegrees;
    if (mode == PanelTiltMode.off) {
      degrees = 0.0;
    } else if (mode == PanelTiltMode.subtle && degrees < 5.0) {
      degrees = 6.0;
    } else if (mode == PanelTiltMode.noticeable && degrees < 10.0) {
      degrees = 12.0;
    } else if (mode == PanelTiltMode.dynamic && degrees < 5.0) {
      degrees = 6.0;
    }
    setState(() => _visualPrefs =
        _visualPrefs.copyWith(panelTiltMode: mode, panelTiltDegrees: degrees));
    _persistVisualPrefs();
  }

  void _setPanelTiltDegrees(double degrees, {bool persist = true}) {
    final d = DialVisualMath.clampTiltDegrees(degrees);
    var mode = d <= 0.0 ? PanelTiltMode.off : _visualPrefs.panelTiltMode;
    // If the user drags the degree slider above 0 from OFF, enable a static tilt.
    if (d > 0.0 && mode == PanelTiltMode.off) {
      mode = PanelTiltMode.subtle;
    }
    setState(
      () => _visualPrefs = _visualPrefs.copyWith(
        panelTiltDegrees: d,
        panelTiltMode: mode,
      ),
    );
    if (persist) {
      _persistVisualPrefs();
    }
  }

  void _setPanelShadowMode(PanelDepthShadowMode mode) {
    setState(
      () => _visualPrefs = _visualPrefs.copyWith(panelDepthShadowMode: mode),
    );
    _persistVisualPrefs();
  }

  void _setPanelMaterialMode(PanelMaterialMode mode) {
    setState(
      () => _visualPrefs = _visualPrefs.copyWith(panelMaterialMode: mode),
    );
    _persistVisualPrefs();
  }

  void _setFrameOpacity(FrameOpacityMode mode) {
    setState(() => _visualPrefs = _visualPrefs.copyWith(frameOpacityMode: mode));
    _persistVisualPrefs();
  }

  void _setRingMaterial(RingMaterialMode mode) {
    setState(() => _visualPrefs = _visualPrefs.copyWith(ringMaterialMode: mode));
    _persistVisualPrefs();
  }

  void _setRingTransparency(double value, {bool persist = true}) {
    setState(() => _visualPrefs = _visualPrefs.copyWith(
          ringTransparencyStrength: DialVisualMath.clampRingTransparency(value),
        ));
    if (persist) {
      _persistVisualPrefs();
    }
  }

  void _setRingLineWeight(double value, {bool persist = true}) {
    setState(() => _visualPrefs = _visualPrefs.copyWith(
          ringLineWeight: DialVisualMath.clampRingLineWeight(value),
        ));
    if (persist) {
      _persistVisualPrefs();
    }
  }

  void _setLabelAutoContrast(bool enabled) {
    setState(() => _visualPrefs =
        _visualPrefs.copyWith(labelContrastAutoAdjust: enabled));
    _persistVisualPrefs();
  }

  static bool _isKnownPath(String path, List<_DialAssetOption> options) {
    if (path.isEmpty) {
      return false;
    }
    for (final option in options) {
      if (option.path == path) {
        return true;
      }
    }
    return false;
  }

  void _setDialPreviewSkinId(String skinId) {
    setState(() {
      _dialPreviewSkinId = skinId;
      _skin = AtlasSkinIdX.fromId(skinId);
    });
    FFAppState().skinId = skinId;
  }

  void _setDialPreviewRingsProfile(String path) {
    if (!_isKnownPath(path, _ringsProfileOptions)) {
      return;
    }
    if (path == _customRingsProfilePath &&
        (_dialPreviewCustomRingsJson.trim().isEmpty ||
            RingsResolver.parseRawJson(_dialPreviewCustomRingsJson) == null)) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Save a valid custom Rings profile first.'),
          duration: Duration(seconds: 2),
        ),
      );
      return;
    }
    setState(() => _dialPreviewRingsProfilePath = path);
    FFAppState().dialPreviewRingsProfilePath = path;
  }

  void _setDialPreviewUiPrefsProfile(String path) {
    if (!_isKnownPath(path, _uiPrefsProfileOptions)) {
      return;
    }
    if (path == _customUiPrefsProfilePath &&
        (_dialPreviewCustomUiPrefsJson.trim().isEmpty ||
            UiPrefsResolver.parseRawJson(_dialPreviewCustomUiPrefsJson) == null)) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Save a valid custom UI prefs profile first.'),
          duration: Duration(seconds: 2),
        ),
      );
      return;
    }
    setState(() => _dialPreviewUiPrefsProfilePath = path);
    FFAppState().dialPreviewUiPrefsProfilePath = path;
  }

  String _labelForPath(String path, List<_DialAssetOption> options) {
    for (final option in options) {
      if (option.path == path) {
        return option.label;
      }
    }
    return path;
  }

  Future<String> _loadJsonTemplate({
    required String selectedPath,
    required String fallbackPath,
  }) async {
    final target = selectedPath.startsWith('__') ? fallbackPath : selectedPath;
    try {
      return await rootBundle.loadString(target);
    } catch (_) {
      return await rootBundle.loadString(fallbackPath);
    }
  }

  Future<String?> _openJsonEditorDialog({
    required String title,
    required String initialJson,
    required String helperText,
  }) async {
    final controller = TextEditingController(text: initialJson);
    final result = await showDialog<String>(
      context: context,
      builder: (context) {
        return AlertDialog(
          title: Text(title),
          content: SizedBox(
            width: 700,
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  helperText,
                  style: Theme.of(context).textTheme.bodySmall,
                ),
                const SizedBox(height: 8),
                SizedBox(
                  height: 320,
                  child: TextField(
                    controller: controller,
                    maxLines: null,
                    expands: true,
                    decoration: const InputDecoration(
                      border: OutlineInputBorder(),
                      alignLabelWithHint: true,
                    ),
                    style: const TextStyle(
                      fontFamily: 'monospace',
                      fontSize: 12,
                    ),
                  ),
                ),
              ],
            ),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(context).pop(null),
              child: const Text('Cancel'),
            ),
            ElevatedButton(
              onPressed: () => Navigator.of(context).pop(controller.text),
              child: const Text('Save Custom'),
            ),
          ],
        );
      },
    );
    controller.dispose();
    return result;
  }

  String _suggestExportFileName(String baseName) {
    final now = DateTime.now();
    String two(int v) => v.toString().padLeft(2, '0');
    final stamp =
        '${now.year}${two(now.month)}${two(now.day)}_${two(now.hour)}${two(now.minute)}${two(now.second)}';
    return '${baseName}_$stamp.json';
  }

  Future<void> _showJsonExportDialog({
    required String title,
    required String fileName,
    required String jsonPayload,
  }) async {
    await showDialog<void>(
      context: context,
      builder: (context) {
        return AlertDialog(
          title: Text(title),
          content: SizedBox(
            width: 700,
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Suggested filename: $fileName',
                  style: Theme.of(context).textTheme.bodySmall,
                ),
                const SizedBox(height: 8),
                Container(
                  height: 320,
                  width: double.infinity,
                  decoration: BoxDecoration(
                    border: Border.all(color: Theme.of(context).dividerColor),
                    borderRadius: BorderRadius.circular(4),
                  ),
                  child: SingleChildScrollView(
                    padding: const EdgeInsets.all(12),
                    child: SelectableText(
                      jsonPayload,
                      style: const TextStyle(
                        fontFamily: 'monospace',
                        fontSize: 12,
                      ),
                    ),
                  ),
                ),
              ],
            ),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(context).pop(),
              child: const Text('Close'),
            ),
            if (kIsWeb)
              OutlinedButton.icon(
                onPressed: () async {
                  final ok = await json_download.downloadJsonFile(
                    fileName: fileName,
                    jsonPayload: jsonPayload,
                  );
                  if (!mounted) return;
                  if (ok) {
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(
                        content: Text('Download started for $fileName.'),
                        duration: const Duration(seconds: 2),
                      ),
                    );
                  } else {
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(
                        content: Text('Download not available on this platform.'),
                        duration: Duration(seconds: 2),
                      ),
                    );
                  }
                },
                icon: const Icon(Icons.download),
                label: const Text('Download .json'),
              ),
            ElevatedButton.icon(
              onPressed: () async {
                await Clipboard.setData(ClipboardData(text: jsonPayload));
                if (!mounted) return;
                Navigator.of(context).pop();
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(
                    content: Text('Copied $fileName payload to clipboard.'),
                    duration: const Duration(seconds: 2),
                  ),
                );
              },
              icon: const Icon(Icons.copy),
              label: const Text('Copy JSON'),
            ),
          ],
        );
      },
    );
  }

  bool _saveCustomRingsJson(String rawJson, {bool showError = true}) {
    if (RingsResolver.parseRawJson(rawJson) == null) {
      if (showError && mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Invalid rings schema JSON. Custom profile not saved.'),
            duration: Duration(seconds: 3),
          ),
        );
      }
      return false;
    }
    setState(() {
      _dialPreviewCustomRingsJson = rawJson;
      _dialPreviewRingsProfilePath = _customRingsProfilePath;
    });
    FFAppState().dialPreviewCustomRingsJson = rawJson;
    FFAppState().dialPreviewRingsProfilePath = _customRingsProfilePath;
    return true;
  }

  bool _saveCustomUiPrefsJson(String rawJson, {bool showError = true}) {
    if (UiPrefsResolver.parseRawJson(rawJson) == null) {
      if (showError && mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Invalid UI prefs schema JSON. Custom profile not saved.'),
            duration: Duration(seconds: 3),
          ),
        );
      }
      return false;
    }
    setState(() {
      _dialPreviewCustomUiPrefsJson = rawJson;
      _dialPreviewUiPrefsProfilePath = _customUiPrefsProfilePath;
    });
    FFAppState().dialPreviewCustomUiPrefsJson = rawJson;
    FFAppState().dialPreviewUiPrefsProfilePath = _customUiPrefsProfilePath;
    return true;
  }

  Future<void> _editCustomRingsProfile() async {
    final seed = _dialPreviewCustomRingsJson.trim().isNotEmpty
        ? _dialPreviewCustomRingsJson
        : await _loadJsonTemplate(
            selectedPath: _dialPreviewRingsProfilePath,
            fallbackPath: _defaultRingsProfilePath,
          );
    final edited = await _openJsonEditorDialog(
      title: 'Custom Rings Profile JSON',
      initialJson: seed,
      helperText:
          'Must conform to ajani.rings.schema.v1. Saving sets Dial Preview to custom rings.',
    );
    if (edited == null) {
      return;
    }
    _saveCustomRingsJson(edited);
  }

  Future<void> _editCustomUiPrefsProfile() async {
    final seed = _dialPreviewCustomUiPrefsJson.trim().isNotEmpty
        ? _dialPreviewCustomUiPrefsJson
        : await _loadJsonTemplate(
            selectedPath: _dialPreviewUiPrefsProfilePath,
            fallbackPath: _defaultUiPrefsProfilePath,
          );
    final edited = await _openJsonEditorDialog(
      title: 'Custom UI Prefs Profile JSON',
      initialJson: seed,
      helperText:
          'Must conform to ajani.ui_prefs.schema.v1. Saving sets Dial Preview to custom UI prefs.',
    );
    if (edited == null) {
      return;
    }
    _saveCustomUiPrefsJson(edited);
  }

  Future<void> _importCustomRingsProfile() async {
    final imported = await _openJsonEditorDialog(
      title: 'Import Rings JSON',
      initialJson: _dialPreviewCustomRingsJson.trim().isNotEmpty
          ? _dialPreviewCustomRingsJson
          : '{\n  "$schema": "ajani.rings.schema.v1"\n}',
      helperText:
          'Paste JSON from an exported rings profile file. Must conform to ajani.rings.schema.v1.',
    );
    if (imported == null) {
      return;
    }
    _saveCustomRingsJson(imported);
  }

  Future<void> _importCustomUiPrefsProfile() async {
    final imported = await _openJsonEditorDialog(
      title: 'Import UI Prefs JSON',
      initialJson: _dialPreviewCustomUiPrefsJson.trim().isNotEmpty
          ? _dialPreviewCustomUiPrefsJson
          : '{\n  "$schema": "ajani.ui_prefs.schema.v1"\n}',
      helperText:
          'Paste JSON from an exported UI prefs profile file. Must conform to ajani.ui_prefs.schema.v1.',
    );
    if (imported == null) {
      return;
    }
    _saveCustomUiPrefsJson(imported);
  }

  Future<void> _exportCustomRingsProfile() async {
    if (RingsResolver.parseRawJson(_dialPreviewCustomRingsJson) == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('No valid custom Rings profile to export yet.'),
          duration: Duration(seconds: 2),
        ),
      );
      return;
    }
    await _showJsonExportDialog(
      title: 'Export Rings JSON',
      fileName: _suggestExportFileName('rings_custom_profile'),
      jsonPayload: _dialPreviewCustomRingsJson,
    );
  }

  Future<void> _exportCustomUiPrefsProfile() async {
    if (UiPrefsResolver.parseRawJson(_dialPreviewCustomUiPrefsJson) == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('No valid custom UI prefs profile to export yet.'),
          duration: Duration(seconds: 2),
        ),
      );
      return;
    }
    await _showJsonExportDialog(
      title: 'Export UI Prefs JSON',
      fileName: _suggestExportFileName('ui_prefs_custom_profile'),
      jsonPayload: _dialPreviewCustomUiPrefsJson,
    );
  }

  Map<String, dynamic>? _tryDecodeJsonObject(String rawJson) {
    try {
      final decoded = jsonDecode(rawJson);
      if (decoded is Map) {
        final mapped = <String, dynamic>{};
        for (final entry in decoded.entries) {
          mapped[entry.key.toString()] = entry.value;
        }
        return mapped;
      }
      return null;
    } catch (_) {
      return null;
    }
  }

  Future<void> _exportAllProfilesBundle() async {
    final ringsValid = RingsResolver.parseRawJson(_dialPreviewCustomRingsJson) != null;
    final uiPrefsValid =
        UiPrefsResolver.parseRawJson(_dialPreviewCustomUiPrefsJson) != null;
    if (!ringsValid && !uiPrefsValid) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('No valid custom profiles to bundle yet.'),
          duration: Duration(seconds: 2),
        ),
      );
      return;
    }

    final ringsObject = ringsValid
        ? _tryDecodeJsonObject(_dialPreviewCustomRingsJson)
        : null;
    final uiPrefsObject = uiPrefsValid
        ? _tryDecodeJsonObject(_dialPreviewCustomUiPrefsJson)
        : null;
    final bundle = <String, dynamic>{
      r'$schema': 'atlas.dial.profile.bundle.v1',
      'meta': <String, dynamic>{
        'version': 1,
        'exportedAtUtc': DateTime.now().toUtc().toIso8601String(),
        'source': 'flutterflow_app',
      },
      'active': <String, dynamic>{
        'skinId': _dialPreviewSkinId,
        'ringsProfilePath': _dialPreviewRingsProfilePath,
        'uiPrefsProfilePath': _dialPreviewUiPrefsProfilePath,
      },
      'profiles': <String, dynamic>{
        'customRings': ringsObject,
        'customUiPrefs': uiPrefsObject,
      },
      'status': <String, dynamic>{
        'customRingsSaved': ringsObject != null,
        'customUiPrefsSaved': uiPrefsObject != null,
      },
    };
    final payload = const JsonEncoder.withIndent('  ').convert(bundle);
    await _showJsonExportDialog(
      title: 'Export Dial Profiles Bundle',
      fileName: _suggestExportFileName('dial_profiles_bundle'),
      jsonPayload: payload,
    );
  }

  void _resetCustomRingsProfile() {
    final wasSelected = _dialPreviewRingsProfilePath == _customRingsProfilePath;
    setState(() {
      _dialPreviewCustomRingsJson = '';
      if (wasSelected) {
        _dialPreviewRingsProfilePath = _defaultRingsProfilePath;
      }
    });
    FFAppState().dialPreviewCustomRingsJson = '';
    if (wasSelected) {
      FFAppState().dialPreviewRingsProfilePath = _defaultRingsProfilePath;
    }
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('Custom Rings profile reset.'),
        duration: Duration(seconds: 2),
      ),
    );
  }

  void _resetCustomUiPrefsProfile() {
    final wasSelected = _dialPreviewUiPrefsProfilePath == _customUiPrefsProfilePath;
    setState(() {
      _dialPreviewCustomUiPrefsJson = '';
      if (wasSelected) {
        _dialPreviewUiPrefsProfilePath = _defaultUiPrefsProfilePath;
      }
    });
    FFAppState().dialPreviewCustomUiPrefsJson = '';
    if (wasSelected) {
      FFAppState().dialPreviewUiPrefsProfilePath = _defaultUiPrefsProfilePath;
    }
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('Custom UI prefs profile reset.'),
        duration: Duration(seconds: 2),
      ),
    );
  }

  void _openDialPreviewWorkspace() {
    setState(() {
      // Leave calibration mode before mounting the new scaffold dial view.
      if (_appearanceLabActive || _appearanceLabExiting) {
        _voiceCore.exitAppearanceLab();
        _appearanceLabActive = false;
        _appearanceLabExiting = false;
      }
      _workspaceView = _AtlasWorkspaceView.dialPreview;
    });
  }

  void _openConsoleWorkspace() {
    if (_workspaceView == _AtlasWorkspaceView.console) {
      return;
    }
    setState(() => _workspaceView = _AtlasWorkspaceView.console);
  }

  Widget _workspaceSwitcher(SkinTokens skinTokens) {
    Widget chip({
      required String label,
      required bool selected,
      required VoidCallback onSelected,
    }) {
      return ChoiceChip(
        selected: selected,
        label: Text(label),
        onSelected: (_) => onSelected(),
        selectedColor: skinTokens.accentEnergy.withOpacity(0.18),
        labelStyle: TextStyle(
          color: selected ? skinTokens.textPrimary : skinTokens.textSecondary,
          fontWeight: selected ? FontWeight.w600 : FontWeight.w500,
        ),
      );
    }

    return Wrap(
      spacing: 8,
      runSpacing: 8,
      children: [
        chip(
          label: 'Console',
          selected: _workspaceView == _AtlasWorkspaceView.console,
          onSelected: _openConsoleWorkspace,
        ),
        chip(
          label: 'Dial Preview',
          selected: _workspaceView == _AtlasWorkspaceView.dialPreview,
          onSelected: _openDialPreviewWorkspace,
        ),
      ],
    );
  }

  Widget _buildDialPreviewWorkspace() {
    final overlayTextColor = Theme.of(context).colorScheme.onSurface;
    final ringsJsonOverride = _dialPreviewRingsProfilePath == _customRingsProfilePath
        ? _dialPreviewCustomRingsJson
        : null;
    final uiPrefsJsonOverride =
        _dialPreviewUiPrefsProfilePath == _customUiPrefsProfilePath
            ? _dialPreviewCustomUiPrefsJson
            : null;
    final resolvedRingsPath =
        ringsJsonOverride == null ? _dialPreviewRingsProfilePath : _defaultRingsProfilePath;
    final resolvedUiPrefsPath = uiPrefsJsonOverride == null
        ? _dialPreviewUiPrefsProfilePath
        : _defaultUiPrefsProfilePath;
    final ringsSignature =
        ringsJsonOverride == null ? resolvedRingsPath : 'custom:${ringsJsonOverride.hashCode}';
    final uiPrefsSignature = uiPrefsJsonOverride == null
        ? resolvedUiPrefsPath
        : 'custom:${uiPrefsJsonOverride.hashCode}';
    final customRingsSaved =
        RingsResolver.parseRawJson(_dialPreviewCustomRingsJson) != null;
    final customUiPrefsSaved =
        UiPrefsResolver.parseRawJson(_dialPreviewCustomUiPrefsJson) != null;
    return Stack(
      fit: StackFit.expand,
      children: [
        DialScreen(
          key: ValueKey(
            'dial-preview|$_dialPreviewSkinId|$ringsSignature|$uiPrefsSignature',
          ),
          initialSkinId: _dialPreviewSkinId,
          uiPrefsProfilePath: resolvedUiPrefsPath,
          ringsProfilePath: resolvedRingsPath,
          uiPrefsProfileJson: uiPrefsJsonOverride,
          ringsProfileJson: ringsJsonOverride,
        ),
        SafeArea(
          child: Align(
            alignment: Alignment.topLeft,
            child: Padding(
              padding: const EdgeInsets.all(12),
              child: ConstrainedBox(
                constraints: const BoxConstraints(maxWidth: 330),
                child: Card(
                  elevation: 6,
                  child: Padding(
                    padding: const EdgeInsets.all(12),
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'Dial Preview Controls',
                          style: TextStyle(
                            color: overlayTextColor,
                            fontWeight: FontWeight.w700,
                          ),
                        ),
                        const SizedBox(height: 10),
                        Text(
                          'Skin',
                          style: TextStyle(
                            color: overlayTextColor.withOpacity(0.8),
                            fontSize: 12,
                          ),
                        ),
                        DropdownButton<String>(
                          isExpanded: true,
                          value: _dialPreviewSkinId,
                          items: AtlasSkinId.values
                              .map(
                                (skin) => DropdownMenuItem<String>(
                                  value: skin.id,
                                  child: Text(skin.label),
                                ),
                              )
                              .toList(),
                          onChanged: (value) {
                            if (value == null) return;
                            _setDialPreviewSkinId(value);
                          },
                        ),
                        const SizedBox(height: 8),
                        Text(
                          'Rings profile',
                          style: TextStyle(
                            color: overlayTextColor.withOpacity(0.8),
                            fontSize: 12,
                          ),
                        ),
                        DropdownButton<String>(
                          isExpanded: true,
                          value: _dialPreviewRingsProfilePath,
                          items: _ringsProfileOptions
                              .map(
                                (option) => DropdownMenuItem<String>(
                                  value: option.path,
                                  child: Text(option.label),
                                ),
                              )
                              .toList(),
                          onChanged: (value) {
                            if (value == null) return;
                            _setDialPreviewRingsProfile(value);
                          },
                        ),
                        const SizedBox(height: 8),
                        Text(
                          'UI prefs profile',
                          style: TextStyle(
                            color: overlayTextColor.withOpacity(0.8),
                            fontSize: 12,
                          ),
                        ),
                        DropdownButton<String>(
                          isExpanded: true,
                          value: _dialPreviewUiPrefsProfilePath,
                          items: _uiPrefsProfileOptions
                              .map(
                                (option) => DropdownMenuItem<String>(
                                  value: option.path,
                                  child: Text(option.label),
                                ),
                              )
                              .toList(),
                          onChanged: (value) {
                            if (value == null) return;
                            _setDialPreviewUiPrefsProfile(value);
                          },
                        ),
                        const SizedBox(height: 10),
                        Text(
                          'Rings custom profile',
                          style: TextStyle(
                            color: overlayTextColor.withOpacity(0.8),
                            fontSize: 12,
                          ),
                        ),
                        const SizedBox(height: 6),
                        Wrap(
                          spacing: 8,
                          runSpacing: 8,
                          children: [
                            OutlinedButton(
                              onPressed: _editCustomRingsProfile,
                              child: const Text('Edit/Save'),
                            ),
                            OutlinedButton(
                              onPressed: _importCustomRingsProfile,
                              child: const Text('Import'),
                            ),
                            OutlinedButton(
                              onPressed: _exportCustomRingsProfile,
                              child: const Text('Export'),
                            ),
                            OutlinedButton(
                              onPressed: _resetCustomRingsProfile,
                              child: const Text('Reset Custom'),
                            ),
                          ],
                        ),
                        const SizedBox(height: 8),
                        Text(
                          'UI prefs custom profile',
                          style: TextStyle(
                            color: overlayTextColor.withOpacity(0.8),
                            fontSize: 12,
                          ),
                        ),
                        const SizedBox(height: 6),
                        Wrap(
                          spacing: 8,
                          runSpacing: 8,
                          children: [
                            OutlinedButton(
                              onPressed: _editCustomUiPrefsProfile,
                              child: const Text('Edit/Save'),
                            ),
                            OutlinedButton(
                              onPressed: _importCustomUiPrefsProfile,
                              child: const Text('Import'),
                            ),
                            OutlinedButton(
                              onPressed: _exportCustomUiPrefsProfile,
                              child: const Text('Export'),
                            ),
                            OutlinedButton(
                              onPressed: _resetCustomUiPrefsProfile,
                              child: const Text('Reset Custom'),
                            ),
                          ],
                        ),
                        const SizedBox(height: 10),
                        Text(
                          'Bundle',
                          style: TextStyle(
                            color: overlayTextColor.withOpacity(0.8),
                            fontSize: 12,
                          ),
                        ),
                        const SizedBox(height: 6),
                        Wrap(
                          spacing: 8,
                          runSpacing: 8,
                          children: [
                            OutlinedButton(
                              onPressed: _exportAllProfilesBundle,
                              child: const Text('Export All Profiles Bundle'),
                            ),
                          ],
                        ),
                        const SizedBox(height: 8),
                        Text(
                          'Active: ${AtlasSkinIdX.fromId(_dialPreviewSkinId).label}\n'
                          'Rings: ${_labelForPath(_dialPreviewRingsProfilePath, _ringsProfileOptions)}\n'
                          'Prefs: ${_labelForPath(_dialPreviewUiPrefsProfilePath, _uiPrefsProfileOptions)}\n'
                          'Custom Rings JSON: ${customRingsSaved ? 'saved' : 'not saved'}\n'
                          'Custom UI Prefs JSON: ${customUiPrefsSaved ? 'saved' : 'not saved'}',
                          style: TextStyle(
                            color: overlayTextColor.withOpacity(0.72),
                            fontSize: 11,
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              ),
            ),
          ),
        ),
        SafeArea(
          child: Align(
            alignment: Alignment.topRight,
            child: Padding(
              padding: const EdgeInsets.all(12),
              child: OutlinedButton.icon(
                onPressed: _openConsoleWorkspace,
                icon: const Icon(Icons.tune),
                label: const Text('Open Console'),
              ),
            ),
          ),
        ),
      ],
    );
  }

  Future<void> _promptLanIp() async {
    final ipController = TextEditingController();
    final value = await showDialog<String>(
      context: context,
      builder: (context) {
        return AlertDialog(
          title: const Text('Computer LAN IP'),
          content: TextField(
            controller: ipController,
            decoration: const InputDecoration(
              hintText: 'Example: 192.168.1.20',
              border: OutlineInputBorder(),
            ),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(context).pop(null),
              child: const Text('Cancel'),
            ),
            ElevatedButton(
              onPressed: () => Navigator.of(context).pop(ipController.text),
              child: const Text('Set'),
            ),
          ],
        );
      },
    );

    final ip = (value ?? '').trim();
    if (ip.isEmpty) return;
    _setBaseUrl('http://$ip:8000');
  }

  Widget _panel(
    BuildContext context, {
    required String title,
    required Widget child,
  }) {
    final scheme = Theme.of(context).colorScheme;
    final titleStyle = Theme.of(context).textTheme.titleSmall?.copyWith(
          fontWeight: FontWeight.w700,
          letterSpacing: 0.4,
        );
    return DialPanel(
      visualPrefs: _visualPrefs,
      surfaceColor: scheme.surface,
      borderColor: scheme.outline,
      borderRadius: BorderRadius.circular(12),
      dynamicTiltUnit: _dynamicTiltUnit,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            title,
            style: titleStyle ??
                const TextStyle(
                  fontSize: 14,
                  fontWeight: FontWeight.w700,
                ),
          ),
          const SizedBox(height: 8),
          child,
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final skinTokens = AtlasSkins.tokens(_skin);
    final skinTheme = AtlasSkins.themeData(
      _skin,
      base: Theme.of(context),
    );

    final ringMaterial = _visualPrefs.ringMaterialMode;
    final ringOpacityBase = switch (ringMaterial) {
      RingMaterialMode.solidMatte => 0.50,
      RingMaterialMode.frostedGlass => 0.30,
      RingMaterialMode.transparentGlass => 0.22,
      RingMaterialMode.lineOnlyMinimal => skinTokens.ringOpacity,
      RingMaterialMode.mixedInnerSolidOuterTransparent => 0.38,
    };
    final ringStrokeWidthBase = switch (ringMaterial) {
      RingMaterialMode.solidMatte => 1.9,
      RingMaterialMode.frostedGlass => 1.6,
      RingMaterialMode.transparentGlass => 1.2,
      RingMaterialMode.lineOnlyMinimal => skinTokens.ringStrokeWidth,
      RingMaterialMode.mixedInnerSolidOuterTransparent => 1.5,
    };
    final ringStrokeWidth = (ringStrokeWidthBase * _visualPrefs.ringLineWeight)
        .clamp(0.6, 4.0)
        .toDouble();
    final ringOpacity = (ringOpacityBase *
            (1.0 - DialVisualMath.clampRingTransparency(
              _visualPrefs.ringTransparencyStrength,
            )))
        .clamp(0.05, 0.85)
        .toDouble();

    final suggestionSummary =
        (_last?['ajani']?['summary'] ?? _last?['ajani']?['goal'] ?? '')
            .toString();
    final minervaSummary = (_last?['minerva']?['summary'] ?? '').toString();
    final hermesSummary = (_last?['hermes']?['summary'] ?? '').toString();

    final validationStatus = (_last?['validation_status'] ?? '').toString();
    final intent = (_last?['intent'] ?? '').toString();
    final version = (_last?['version'] ?? '').toString();

    if (_workspaceView == _AtlasWorkspaceView.dialPreview &&
        !_appearanceLabActive) {
      return _buildDialPreviewWorkspace();
    }

    if (_appearanceLabActive) {
      return AnimatedTheme(
        data: skinTheme,
        duration: AtlasSkins.transitionDuration,
        curve: Curves.easeInOut,
        child: _buildAppearanceLab(
          context,
          skinTokens,
          ringOpacity,
          ringStrokeWidth,
        ),
      );
    }

    return AnimatedTheme(
      data: skinTheme,
      duration: AtlasSkins.transitionDuration,
      curve: Curves.easeInOut,
      child: AnimatedContainer(
        duration: AtlasSkins.transitionDuration,
        curve: Curves.easeInOut,
        color: skinTokens.background,
        child: AnimatedBuilder(
          animation: _voiceCore,
          builder: (context, _) {
            return ListView(
              controller: _scrollController,
              padding: const EdgeInsets.all(16),
              children: [
            // Voice core visual layer (Unity placeholder for now).
            SizedBox(
              height: 280,
              child: VoiceCoreLayer(
                state: _voiceCore.state,
                coreWidget: _PlaceholderCore(
                  surface: skinTokens.surface,
                  border: skinTokens.border,
                  text: skinTokens.textSecondary,
                  rim: _voiceCore.state.accentColor,
                  rotationPeriod:
                      _voiceCore.state.coreRotationState == CoreRotationState.stopped
                          ? Duration.zero
                          : const Duration(seconds: 12),
                ),
                timing: _voiceCore.timing,
                visualPrefs: _visualPrefs,
                ringColor: skinTokens.ringStroke,
                ringOpacity: ringOpacity,
                ringStrokeWidth: ringStrokeWidth,
                backgroundColor: skinTokens.background,
                microDetailColor: skinTokens.border,
                frameColor: skinTokens.border,
              ),
            ),
            const SizedBox(height: 12),
            _panel(
              context,
              title: 'Connection',
              child: Column(
                children: [
                  Align(
                    alignment: Alignment.centerLeft,
                    child: _workspaceSwitcher(skinTokens),
                  ),
                  const SizedBox(height: 10),
                  TextField(
                    controller: _baseUrlController,
                    onChanged: (v) => FFAppState().atlasBaseUrl = v,
                    decoration: const InputDecoration(
                      labelText: 'Atlas Base URL',
                      hintText:
                          'Android emulator: http://10.0.2.2:8000  •  iOS simulator: http://127.0.0.1:8000  •  Physical device: http://<YOUR_LAN_IP>:8000',
                      border: OutlineInputBorder(),
                    ),
                  ),
                  const SizedBox(height: 8),
                  Wrap(
                    spacing: 8,
                    runSpacing: 8,
                    children: [
                      OutlinedButton(
                        onPressed: _enterAppearanceLab,
                        child: const Text('Appearance Lab'),
                      ),
                      OutlinedButton(
                        onPressed: () => _setBaseUrl('http://10.0.2.2:8000'),
                        child: const Text('Android Emulator'),
                      ),
                      OutlinedButton(
                        onPressed: () => _setBaseUrl('http://127.0.0.1:8000'),
                        child: const Text('iOS Simulator'),
                      ),
                      OutlinedButton(
                        onPressed: () => _setBaseUrl('http://127.0.0.1:8000'),
                        child: const Text('Android (adb reverse)'),
                      ),
                      OutlinedButton(
                        onPressed: _promptLanIp,
                        child: const Text('Physical device (LAN IP)'),
                      ),
                      OutlinedButton(
                        onPressed: _healthLoading ? null : _checkHealth,
                        child: Text(_healthLoading ? 'Checking…' : 'Check /health'),
                      ),
                    ],
                  ),
                  const SizedBox(height: 10),
                  Row(
                    children: [
                      Text(
                        'Skin:',
                        style: TextStyle(color: skinTokens.textPrimary),
                      ),
                      const SizedBox(width: 10),
                      DropdownButton<AtlasSkinId>(
                        value: _skin,
                        items: AtlasSkinId.values
                            .map(
                              (s) => DropdownMenuItem(
                                value: s,
                                child: Text(s.label),
                              ),
                            )
                            .toList(),
                        onChanged: (v) {
                          if (v == null) return;
                          _setSkin(v);
                        },
                      ),
                      const Spacer(),
                      Text(
                        'Manual only',
                        style: TextStyle(
                          color: skinTokens.textSecondary,
                          fontSize: 12,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),
                  Row(
                    children: [
                      Text(
                        'Background:',
                        style: TextStyle(color: skinTokens.textPrimary),
                      ),
                      const SizedBox(width: 10),
                      DropdownButton<BackgroundType>(
                        value: _visualPrefs.backgroundType,
                        items: BackgroundType.values
                            .map(
                              (b) => DropdownMenuItem(
                                value: b,
                                child: Text(b.name),
                              ),
                            )
                            .toList(),
                        onChanged: (v) {
                          if (v == null) return;
                          _setBackgroundType(v);
                        },
                      ),
                      const SizedBox(width: 18),
                      Text(
                        'Frame:',
                        style: TextStyle(color: skinTokens.textPrimary),
                      ),
                      const SizedBox(width: 10),
                      DropdownButton<FrameType>(
                        value: _visualPrefs.frameType,
                        items: FrameType.values
                            .map(
                              (f) => DropdownMenuItem(
                                value: f,
                                child: Text(f.name),
                              ),
                            )
                            .toList(),
                        onChanged: (v) {
                          if (v == null) return;
                          _setFrameType(v);
                        },
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),
                  Row(
                    children: [
                      Text(
                        'Frame opacity:',
                        style: TextStyle(color: skinTokens.textPrimary),
                      ),
                      const SizedBox(width: 10),
                      DropdownButton<FrameOpacityMode>(
                        value: _visualPrefs.frameOpacityMode,
                        items: FrameOpacityMode.values
                            .map(
                              (o) => DropdownMenuItem(
                                value: o,
                                child: Text(o.name),
                              ),
                            )
                            .toList(),
                        onChanged: (v) {
                          if (v == null) return;
                          _setFrameOpacity(v);
                        },
                      ),
                    ],
                  ),
                  SwitchListTile(
                    value: _visualPrefs.councilDimOverlayEnabled,
                    onChanged: _setDimOverlay,
                    title: Text(
                      'Council dim overlay',
                      style: TextStyle(color: skinTokens.textPrimary),
                    ),
                    subtitle: Text(
                      'Optional background dim (5–10%) during Council.',
                      style: TextStyle(color: skinTokens.textSecondary),
                    ),
                    dense: true,
                    contentPadding: EdgeInsets.zero,
                  ),
                  const SizedBox(height: 8),
                  Row(
                    children: [
                      Text(
                        'Panel tilt:',
                        style: TextStyle(color: skinTokens.textPrimary),
                      ),
                      const SizedBox(width: 10),
                      DropdownButton<PanelTiltMode>(
                        value: _visualPrefs.panelTiltMode,
                        items: PanelTiltMode.values
                            .map((m) => DropdownMenuItem(value: m, child: Text(m.name)))
                            .toList(),
                        onChanged: (v) {
                          if (v == null) return;
                          _setPanelTiltMode(v);
                        },
                      ),
                      const SizedBox(width: 18),
                      Text(
                        'Shadow:',
                        style: TextStyle(color: skinTokens.textPrimary),
                      ),
                      const SizedBox(width: 10),
                      DropdownButton<PanelDepthShadowMode>(
                        value: _visualPrefs.panelDepthShadowMode,
                        items: PanelDepthShadowMode.values
                            .map((m) => DropdownMenuItem(value: m, child: Text(m.name)))
                            .toList(),
                        onChanged: (v) {
                          if (v == null) return;
                          _setPanelShadowMode(v);
                        },
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),
                  Row(
                    children: [
                      Text(
                        'Panel material:',
                        style: TextStyle(color: skinTokens.textPrimary),
                      ),
                      const SizedBox(width: 10),
                      DropdownButton<PanelMaterialMode>(
                        value: _visualPrefs.panelMaterialMode,
                        items: PanelMaterialMode.values
                            .map((m) => DropdownMenuItem(value: m, child: Text(m.name)))
                            .toList(),
                        onChanged: (v) {
                          if (v == null) return;
                          _setPanelMaterialMode(v);
                        },
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),
                  Row(
                    children: [
                      Text(
                        'Ring material:',
                        style: TextStyle(color: skinTokens.textPrimary),
                      ),
                      const SizedBox(width: 10),
                      DropdownButton<RingMaterialMode>(
                        value: _visualPrefs.ringMaterialMode,
                        items: RingMaterialMode.values
                            .map((m) => DropdownMenuItem(value: m, child: Text(m.name)))
                            .toList(),
                        onChanged: (v) {
                          if (v == null) return;
                          _setRingMaterial(v);
                        },
                      ),
                    ],
                  ),
                  Row(
                    children: [
                      Text(
                        'Ring transparency:',
                        style: TextStyle(color: skinTokens.textPrimary),
                      ),
                      Expanded(
                        child: Slider(
                          value: _visualPrefs.ringTransparencyStrength,
                          min: 0.0,
                          max: 0.60,
                          divisions: 12,
                          label:
                              '${(_visualPrefs.ringTransparencyStrength * 100).round()}%',
                          onChanged: _setRingTransparency,
                        ),
                      ),
                    ],
                  ),
                  SwitchListTile(
                    value: _visualPrefs.labelContrastAutoAdjust,
                    onChanged: _setLabelAutoContrast,
                    title: Text(
                      'Label contrast auto-adjust',
                      style: TextStyle(color: skinTokens.textPrimary),
                    ),
                    subtitle: Text(
                      'Recommended ON',
                      style: TextStyle(color: skinTokens.textSecondary),
                    ),
                    dense: true,
                    contentPadding: EdgeInsets.zero,
                  ),
                  const SizedBox(height: 8),
                  if (_health != null)
                    Align(
                      alignment: Alignment.centerLeft,
                      child: Text(
                        'Backend ok: ${_health?['ok']}  •  version: ${_health?['version'] ?? '(unknown)'}',
                        style: const TextStyle(color: Color(0xFFB8F5C2)),
                      ),
                    ),
                  if (_healthError != null)
                    Align(
                      alignment: Alignment.centerLeft,
                      child: Text(
                        _healthError!,
                        style: const TextStyle(color: Color(0xFFFFB4B4)),
                      ),
                    ),
                  const SizedBox(height: 8),
                  const Align(
                    alignment: Alignment.centerLeft,
                    child: Text(
                      'Tip (Samsung Z Fold over USB): run `adb reverse tcp:8000 tcp:8000` then use http://127.0.0.1:8000',
                      style: TextStyle(color: Color(0xFFB8B8C8), fontSize: 12),
                    ),
                  ),
                  const SizedBox(height: 10),
                  TextField(
                    controller: _projectController,
                    decoration: const InputDecoration(
                      labelText: 'Project ID',
                      border: OutlineInputBorder(),
                    ),
                  ),
                  const SizedBox(height: 10),
                  Row(
                    children: [
                      const Text(
                        'Mode:',
                        style: TextStyle(color: Color(0xFFE6E6F2)),
                      ),
                      const SizedBox(width: 10),
                      DropdownButton<String>(
                        value: _mode,
                        items: const [
                          DropdownMenuItem(
                            value: 'mentor',
                            child: Text('mentor'),
                          ),
                          DropdownMenuItem(
                            value: 'warrior',
                            child: Text('warrior'),
                          ),
                          DropdownMenuItem(
                            value: 'builder',
                            child: Text('builder'),
                          ),
                        ],
                        onChanged: (v) {
                          if (v == null) return;
                          setState(() => _mode = v);
                        },
                      ),
                      const Spacer(),
                      ElevatedButton(
                        onPressed: _loading ? null : _run,
                        child: Text(_loading ? 'Running…' : 'Run /route'),
                      ),
                    ],
                  ),
                ],
              ),
            ),
            const SizedBox(height: 12),
            _panel(
              context,
              title: 'Input',
              child: TextField(
                controller: _inputController,
                maxLines: 5,
                decoration: const InputDecoration(
                  labelText: 'User input',
                  border: OutlineInputBorder(),
                ),
              ),
            ),
            const SizedBox(height: 12),
            _panel(
              context,
              title: 'Council Visual Demo (local only)',
              child: Wrap(
                spacing: 8,
                runSpacing: 8,
                children: [
                  OutlinedButton(
                    onPressed: () => _voiceCore.resetIdle(),
                    child: const Text('Idle'),
                  ),
                  OutlinedButton(
                    onPressed: () => _voiceCore.enterCouncilActive(),
                    child: const Text('Council Activate'),
                  ),
                  OutlinedButton(
                    onPressed: () => _voiceCore.setCouncilSpeaker(
                      IdentitySpeaker.ajani,
                    ),
                    child: const Text('Ajani'),
                  ),
                  OutlinedButton(
                    onPressed: () => _voiceCore.setCouncilPause(),
                    child: const Text('Pause'),
                  ),
                  OutlinedButton(
                    onPressed: () => _voiceCore.setCouncilSpeaker(
                      IdentitySpeaker.minerva,
                    ),
                    child: const Text('Minerva'),
                  ),
                  OutlinedButton(
                    onPressed: () => _voiceCore.setCouncilPause(),
                    child: const Text('Pause'),
                  ),
                  OutlinedButton(
                    onPressed: () => _voiceCore.setCouncilSpeaker(
                      IdentitySpeaker.hermes,
                    ),
                    child: const Text('Hermes'),
                  ),
                  OutlinedButton(
                    onPressed: () => _voiceCore.completeCouncil(),
                    child: const Text('Complete'),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 12),
            if (_error != null)
              _panel(
                context,
                title: 'Error',
                child: SelectableText(
                  _error!,
                  style: const TextStyle(color: Color(0xFFFFB4B4)),
                ),
              ),
            if (_last != null) ...[
              _panel(
                context,
                title: 'Status',
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'intent: $intent',
                      style: const TextStyle(color: Color(0xFFE6E6F2)),
                    ),
                    Text(
                      'validation_status: $validationStatus',
                      style: const TextStyle(color: Color(0xFFE6E6F2)),
                    ),
                    Text(
                      'version: $version',
                      style: const TextStyle(color: Color(0xFFE6E6F2)),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 12),
              _panel(
                context,
                title: 'Ajani',
                child: SelectableText(
                  suggestionSummary,
                  style: TextStyle(color: skinTokens.textPrimary),
                ),
              ),
              const SizedBox(height: 12),
              _panel(
                context,
                title: 'Minerva',
                child: SelectableText(
                  minervaSummary,
                  style: TextStyle(color: skinTokens.textPrimary),
                ),
              ),
              const SizedBox(height: 12),
              _panel(
                context,
                title: 'Hermes',
                child: SelectableText(
                  hermesSummary,
                  style: TextStyle(color: skinTokens.textPrimary),
                ),
              ),
              const SizedBox(height: 12),
              _panel(
                context,
                title: 'Raw JSON',
                child: SelectableText(
                  _last.toString(),
                  style: TextStyle(color: skinTokens.textSecondary),
                ),
              ),
            ],
          ],
        );
          },
        ),
      ),
    );
  }
}

class _PlaceholderCore extends StatelessWidget {
  const _PlaceholderCore({
    required this.surface,
    required this.border,
    required this.text,
    required this.rim,
    required this.rotationPeriod,
  });

  final Color surface;
  final Color border;
  final Color text;
  final Color rim;
  final Duration rotationPeriod;

  @override
  Widget build(BuildContext context) {
    return _RotatingCore(
      rotationPeriod: rotationPeriod,
      child: Container(
        decoration: BoxDecoration(
          shape: BoxShape.circle,
          color: surface,
          border: Border.all(
            color: border,
            width: 2,
          ),
        ),
        child: Stack(
          children: [
            Positioned.fill(
              child: Padding(
                padding: const EdgeInsets.all(6),
                child: AnimatedContainer(
                  duration: const Duration(milliseconds: 400),
                  curve: Curves.easeOut,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    border: Border.all(
                      color: rim.withOpacity(0.42),
                      width: 4,
                    ),
                  ),
                ),
              ),
            ),
            Center(
              child: Text(
                '3D Core',
                style: TextStyle(
                  color: text,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _RotatingCore extends StatefulWidget {
  const _RotatingCore({
    required this.rotationPeriod,
    required this.child,
  });

  final Duration rotationPeriod;
  final Widget child;

  @override
  State<_RotatingCore> createState() => _RotatingCoreState();
}

class _RotatingCoreState extends State<_RotatingCore>
    with SingleTickerProviderStateMixin {
  late final AnimationController _controller;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(vsync: this);
    _sync();
  }

  @override
  void didUpdateWidget(covariant _RotatingCore oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.rotationPeriod != widget.rotationPeriod) {
      _sync();
    }
  }

  void _sync() {
    if (widget.rotationPeriod.inMilliseconds <= 0) {
      _controller.stop();
      _controller.value = 0;
      return;
    }
    _controller
      ..duration = widget.rotationPeriod
      ..repeat();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return RotationTransition(
      turns: _controller,
      child: widget.child,
    );
  }
}
