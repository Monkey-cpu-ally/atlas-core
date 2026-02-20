import 'dart:async';
import 'dart:ui';

import 'package:flutter/material.dart';

import '../../core/config/defaults.dart';
import '../../core/config/ui_prefs_resolver.dart';
import '../../core/services/audio_service.dart';
import '../../core/services/bluetooth_wake_service.dart';
import '../../core/services/gyro_service.dart';
import '../../core/services/haptics_service.dart';
import '../../core/services/voice_service.dart';
import '../../domain/controllers/appearance_lab_controller.dart';
import '../../domain/controllers/core_controller.dart';
import '../../domain/controllers/council_controller.dart';
import '../../domain/controllers/ring_controller.dart';
import '../../domain/controllers/voice_controller.dart';
import '../../domain/models/ui_prefs.dart';
import '../themes/skin_resolver.dart';
import '../themes/skin_tokens.dart';
import '../themes/skins.dart';
import '../widgets/background_layer.dart';
import '../widgets/core_hybrid_widget.dart';
import '../widgets/council_sigil_layer.dart';
import '../widgets/frame_plate_layer.dart';
import '../widgets/mic_assist_overlay.dart';
import '../widgets/rings_widget.dart';
import '../widgets/tooltip_hint.dart';
import 'appearance_lab_overlay.dart';

class DialScreen extends StatefulWidget {
  const DialScreen({
    this.initialSkinId = Defaults.defaultSkinId,
    this.initialPrefs = Defaults.uiPrefs,
    this.gyroService,
    super.key,
  });

  final String initialSkinId;
  final UiPrefs initialPrefs;
  final GyroService? gyroService;

  @override
  State<DialScreen> createState() => _DialScreenState();
}

class _DialScreenState extends State<DialScreen> {
  static bool _firstLaunchHintShownInProcess = false;

  late final CoreController _core;
  late final RingController _rings;
  late final CouncilController _council;
  late final AppearanceLabController _appearanceLab;
  late final VoiceController _voice;
  late final GyroService _gyro;

  late UiPrefs _prefs;
  UiPrefs _skinDefaultPrefs = Defaults.uiPrefs;
  SkinTokens _skin = Skins.lumenCore;
  bool _showFirstLaunchHint = true;
  String _firstLaunchHintText =
      'Say "Hermes, system mode" to customize interface.';
  int _firstLaunchHintFadeOutMs = 300;
  StreamSubscription<Offset>? _gyroSub;

  @override
  void initState() {
    super.initState();
    _prefs = widget.initialPrefs;
    _core = CoreController();
    _rings = RingController();
    _council = CouncilController();
    _appearanceLab = AppearanceLabController();
    _gyro = widget.gyroService ?? MockGyroService();
    _voice = VoiceController(
      voiceService: MockVoiceService(),
      wakeService: MockBluetoothWakeService(),
      audioService: SilentAudioService(),
      hapticsService: SystemHapticsService(),
      coreController: _core,
      councilController: _council,
      appearanceLabController: _appearanceLab,
    );

    _bootstrapDefaults();

    _gyro.start();
    _gyroSub = _gyro.tiltStream.listen((offset) {
      _core.setParallax(offset);
    });
  }

  Future<void> _bootstrapDefaults() async {
    final profile = await UiPrefsResolver.resolveDefaultProfile();
    if (!mounted) {
      return;
    }

    _voice.configureFromPrefs(
      failureOverlayThreshold: profile.failureShowMicAssistAfterFails,
      failureResetThreshold: profile.failureSilentResetAfterFails,
      micAssistHintText: profile.failureHintText,
      micAssistHintDurationMs: profile.failureHintDurationMs,
    );

    final initialSkinId = widget.initialSkinId == Defaults.defaultSkinId
        ? profile.selectedSkinId
        : widget.initialSkinId;

    final bundle = await SkinResolver.resolveBundle(initialSkinId);
    if (!mounted) {
      return;
    }

    _core.applyMotionProfile(
      expandScale: profile.prefs.coreExpandScale,
      pressTightenScale: profile.prefs.corePressTightenScale,
    );
    final shouldShowFirstLaunchHint = profile.firstLaunchHintEnabled &&
        (!profile.firstLaunchHintShowOnce || !_firstLaunchHintShownInProcess);
    if (shouldShowFirstLaunchHint && profile.firstLaunchHintShowOnce) {
      _firstLaunchHintShownInProcess = true;
    }
    setState(() {
      _firstLaunchHintText = profile.firstLaunchHintText;
      _firstLaunchHintFadeOutMs = profile.firstLaunchHintFadeOutMs;
      _showFirstLaunchHint = shouldShowFirstLaunchHint;
      _skin = bundle.tokens;
      _skinDefaultPrefs = profile.prefs;
      if (_isDefaultPrefs(widget.initialPrefs)) {
        _prefs = profile.prefs;
      }
    });

    if (shouldShowFirstLaunchHint) {
      Future<void>.delayed(
        Duration(milliseconds: profile.firstLaunchHintDisplayMs),
        () {
          if (mounted) {
            setState(() => _showFirstLaunchHint = false);
          }
        },
      );
    } else {
      setState(() => _showFirstLaunchHint = false);
    }
  }

  @override
  void dispose() {
    _gyroSub?.cancel();
    _voice.dispose();
    _core.dispose();
    _rings.dispose();
    _council.dispose();
    _appearanceLab.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: Listenable.merge([
        _core,
        _rings,
        _council,
        _appearanceLab,
        _voice,
      ]),
      builder: (context, _) {
        final councilDimPct = (_skin.councilDimStrength.clamp(0.05, 0.10) * 100);
        final dimPercent = _council.state.active
            ? councilDimPct
            : (_appearanceLab.state.active ? 7.0 : 0.0);
        return Stack(
          fit: StackFit.expand,
          children: [
            BackgroundLayer(
              skin: _skin,
              prefs: _prefs,
              dimPercent: dimPercent,
            ),
            if (_prefs.frameType != 'none')
              FramePlateLayer(
                skin: _skin,
                prefs: _prefs,
              ),
            CouncilSigilLayer(
              visible: _council.state.active,
              lineWeight: _prefs.ringLineWeight,
            ),
            RingsWidget(
              controller: _rings,
              skin: _skin,
              prefs: _prefs,
            ),
            Center(
              child: CoreHybridWidget(
                coreState: _core.state,
                skin: _skin,
                prefs: _prefs,
                onTouchDown: _core.onTouchDown,
                onLongPressStart: () {
                  _voice.onLongPressStart();
                },
                onLongPressEnd: () {
                  _voice.onLongPressEnd();
                },
              ),
            ),
            MicAssistOverlay(
              visible: _voice.micAssistVisible,
              text: _voice.micAssistHintText,
            ),
            TooltipHint(
              visible: _showFirstLaunchHint,
              text: _firstLaunchHintText,
              fadeOutMs: _firstLaunchHintFadeOutMs,
            ),
            AppearanceLabOverlay(
              visible: _appearanceLab.state.overlayVisible,
              skin: _skin,
              prefs: _prefs,
              onExit: _appearanceLabExit,
              onResetDefaults: _appearanceReset,
              onPanelTiltChanged: (value) =>
                  setState(() => _prefs = _prefs.copyWith(panelTiltDegrees: value)),
              onFrameTypeChanged: (value) =>
                  setState(() => _prefs = _prefs.copyWith(frameType: value)),
              onFrameOpacityChanged: (value) =>
                  setState(() => _prefs = _prefs.copyWith(frameOpacity: value)),
              onRingMaterialChanged: (value) =>
                  setState(() => _prefs = _prefs.copyWith(ringMaterial: value)),
              onRingTransparencyChanged: (value) =>
                  setState(() => _prefs = _prefs.copyWith(ringTransparency: value)),
              onRingLineWeightChanged: (value) =>
                  setState(() => _prefs = _prefs.copyWith(ringLineWeight: value)),
              onBackgroundChanged: (value) =>
                  setState(() => _prefs = _prefs.copyWith(backgroundType: value)),
              onAccentPreviewToggle: (value) => setState(
                () => _prefs = _prefs.copyWith(accentPreviewEnabled: value),
              ),
            ),
          ],
        );
      },
    );
  }

  void _appearanceLabExit() {
    _appearanceLab.exit();
    _core.exitAppearanceLab();
  }

  void _appearanceReset() {
    _core.applyMotionProfile(
      expandScale: _skinDefaultPrefs.coreExpandScale,
      pressTightenScale: _skinDefaultPrefs.corePressTightenScale,
    );
    setState(() => _prefs = _skinDefaultPrefs);
  }

  bool _isDefaultPrefs(UiPrefs prefs) {
    return identical(prefs, Defaults.uiPrefs);
  }
}

