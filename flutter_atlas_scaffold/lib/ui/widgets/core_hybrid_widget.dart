import 'dart:math' as math;

import 'package:flutter/material.dart';

import '../../core/utils/math.dart';
import '../../domain/controllers/core_controller.dart';
import '../../domain/models/ui_prefs.dart';
import '../painters/waveform_painter.dart';
import '../themes/skin_tokens.dart';

class CoreHybridWidget extends StatelessWidget {
  const CoreHybridWidget({
    required this.coreState,
    required this.skin,
    required this.prefs,
    this.onTouchDown,
    this.onLongPressStart,
    this.onLongPressEnd,
    super.key,
  });

  final CoreVisualState coreState;
  final SkinTokens skin;
  final UiPrefs prefs;
  final VoidCallback? onTouchDown;
  final VoidCallback? onLongPressStart;
  final VoidCallback? onLongPressEnd;

  @override
  Widget build(BuildContext context) {
    final allowsMotion = !coreState.stillnessLock;
    final p = allowsMotion ? coreState.parallax : Offset.zero;
    final dx = AppMath.clamp(p.dx, -1.0, 1.0);
    final dy = AppMath.clamp(p.dy, -1.0, 1.0);

    final accent = Color.lerp(
          skin.surface,
          coreState.accent,
          coreState.accentMix.clamp(0.0, 1.0),
        ) ??
        skin.surface;

    return GestureDetector(
      behavior: HitTestBehavior.opaque,
      onTapDown: (_) => onTouchDown?.call(),
      onLongPressStart: (_) => onLongPressStart?.call(),
      onLongPressEnd: (_) => onLongPressEnd?.call(),
      child: AnimatedScale(
        duration: const Duration(milliseconds: 220),
        curve: Curves.easeOut,
        scale: coreState.coreScale,
        child: Transform(
          alignment: Alignment.center,
          transform: Matrix4.identity()
            ..setEntry(3, 2, 0.0012)
            ..translate(dx * 6, dy * 6)
            ..rotateX(dy * 0.045)
            ..rotateY(dx * -0.045),
          child: SizedBox.square(
            dimension: 220,
            child: Stack(
              fit: StackFit.expand,
              children: [
                DecoratedBox(
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    gradient: RadialGradient(
                      center: const Alignment(-0.2, -0.25),
                      radius: 0.95,
                      colors: <Color>[
                        Color.lerp(accent, Colors.white, 0.08) ?? accent,
                        accent.withOpacity(coreState.brightness),
                        Color.lerp(accent, Colors.black, 0.25) ?? accent,
                      ],
                    ),
                    border: Border.all(
                      color: coreState.accent.withOpacity(
                        AppMath.clamp(0.16 + (coreState.accentMix * 0.52), 0.1, 0.72),
                      ),
                      width: 3.5,
                    ),
                    boxShadow: [
                      BoxShadow(
                        color: coreState.accent.withOpacity(0.22),
                        blurRadius: 22,
                        spreadRadius: 1,
                      ),
                    ],
                  ),
                ),
                if (coreState.rippleEnabled)
                  CustomPaint(
                    painter: _RipplePainter(
                      color: coreState.accent,
                      amp: AppMath.clamp(
                        prefs.rippleAmplitude + (coreState.audioAmp * prefs.audioAmpToGlow),
                        0.08,
                        0.30,
                      ),
                    ),
                  ),
                if (coreState.rippleEnabled)
                  Align(
                    alignment: Alignment.bottomCenter,
                    child: SizedBox(
                      width: 170,
                      height: 48,
                      child: CustomPaint(
                        painter: WaveformPainter(
                          color: coreState.accent,
                          amplitude: AppMath.clamp(
                            0.15 + coreState.audioAmp,
                            0.15,
                            1.0,
                          ),
                        ),
                      ),
                    ),
                  ),
                Center(
                  child: Text(
                    'CORE',
                    style: TextStyle(
                      color: skin.textPrimary.withOpacity(0.86),
                      letterSpacing: 1.6,
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class _RipplePainter extends CustomPainter {
  _RipplePainter({
    required this.color,
    required this.amp,
  });

  final Color color;
  final double amp;

  @override
  void paint(Canvas canvas, Size size) {
    final center = Offset(size.width / 2, size.height / 2);
    final base = size.shortestSide * 0.40;
    final wavePaint = Paint()
      ..color = color.withOpacity(0.16)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 1.6;
    for (var i = 0; i < 3; i++) {
      final wave = math.sin(i * 0.7) * size.shortestSide * amp;
      canvas.drawCircle(center, base + (i * 9) + wave.abs(), wavePaint);
    }
  }

  @override
  bool shouldRepaint(covariant _RipplePainter oldDelegate) {
    return oldDelegate.color != color || oldDelegate.amp != amp;
  }
}

