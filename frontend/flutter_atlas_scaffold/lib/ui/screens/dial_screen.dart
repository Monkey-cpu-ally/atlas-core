import 'dart:async';
import 'dart:ui';

import 'package:flutter/material.dart';

import '../../core/config/defaults.dart';
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

    SkinResolver.resolveBundle(widget.initialSkinId).then((bundle) {
      if (!mounted) {
        return;
      }
      _core.applyMotionProfile(
        expandScale: bundle.prefs.coreExpandScale,
        pressTightenScale: bundle.prefs.corePressTightenScale,
      );
      setState(() {
        _skin = bundle.tokens;
        _skinDefaultPrefs = bundle.prefs;
        if (_isDefaultPrefs(widget.initialPrefs)) {
          _prefs = bundle.prefs;
        }
      });
    });

    _gyro.start();
    _gyroSub = _gyro.tiltStream.listen((offset) {
      _core.setParallax(offset);
    });

    Future<void>.delayed(const Duration(seconds: 3), () {
      if (mounted) {
        setState(() => _showFirstLaunchHint = false);
      }
    });
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
            MicAssistOverlay(visible: _voice.micAssistVisible),
            TooltipHint(
              visible: _showFirstLaunchHint,
              text: 'Hold the core and say Ajani, Minerva, or Hermes.',
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
    const d = Defaults.uiPrefs;
    return prefs.panelTiltDegrees == d.panelTiltDegrees &&
        prefs.frameType == d.frameType &&
        prefs.frameOpacity == d.frameOpacity &&
        prefs.ringMaterial == d.ringMaterial &&
        prefs.ringTransparency == d.ringTransparency &&
        prefs.ringLineWeight == d.ringLineWeight &&
        prefs.backgroundType == d.backgroundType &&
        prefs.accentPreviewEnabled == d.accentPreviewEnabled &&
        prefs.uiTransitionMs == d.uiTransitionMs &&
        prefs.coreExpandScale == d.coreExpandScale &&
        prefs.corePressTightenScale == d.corePressTightenScale &&
        prefs.rippleAmplitude == d.rippleAmplitude &&
        prefs.rippleFrequency == d.rippleFrequency &&
        prefs.rippleSpeed == d.rippleSpeed &&
        prefs.audioAmpToGlow == d.audioAmpToGlow &&
        prefs.extendedIdleMinutes == d.extendedIdleMinutes &&
        prefs.extendedIdleBrightnessDrop == d.extendedIdleBrightnessDrop &&
        prefs.lowPowerEnabledByDefault == d.lowPowerEnabledByDefault;
  }
}

