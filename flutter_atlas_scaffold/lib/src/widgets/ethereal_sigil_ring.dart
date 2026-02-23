import 'dart:math' as math;

import 'package:flutter/material.dart';

import '../controllers/voice_core_controller.dart';
import '../models/voice_core_state.dart';
import '../models/voice_core_timing.dart';

class EtherealSigilRing extends StatefulWidget {
  const EtherealSigilRing({
    required this.sigilState,
    this.color = VoiceCoreController.ghostPurpleAccent,
    this.size = 260,
    this.fadeInDuration = VoiceCoreTiming.spec.sigilFadeInDuration,
    this.fadeOutDuration = VoiceCoreTiming.spec.sigilFadeOutDuration,
    super.key,
  });

  final CouncilSigilState sigilState;
  final Color color;
  final double size;
  final Duration fadeInDuration;
  final Duration fadeOutDuration;

  @override
  State<EtherealSigilRing> createState() => _EtherealSigilRingState();
}

class _EtherealSigilRingState extends State<EtherealSigilRing>
    with SingleTickerProviderStateMixin {
  late final AnimationController _rotationController;

  @override
  void initState() {
    super.initState();
    _rotationController = AnimationController(vsync: this);
    _syncRotationMode();
  }

  @override
  void didUpdateWidget(covariant EtherealSigilRing oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.sigilState.rotationMode != widget.sigilState.rotationMode ||
        oldWidget.sigilState.rotationPeriodSec !=
            widget.sigilState.rotationPeriodSec) {
      _syncRotationMode();
    }
  }

  @override
  void dispose() {
    _rotationController.dispose();
    super.dispose();
  }

  void _syncRotationMode() {
    if (widget.sigilState.rotationMode == SigilRotationMode.static) {
      _rotationController.stop();
      _rotationController.value = 0;
      return;
    }

    final period = widget.sigilState.rotationPeriodSec ?? 45;
    _rotationController
      ..duration = Duration(
        milliseconds: (period * 1000).round(),
      )
      ..repeat();
  }

  @override
  Widget build(BuildContext context) {
    final boundedOpacity =
        (widget.sigilState.opacityPercent.clamp(8, 15) / 100).toDouble();
    final targetOpacity = widget.sigilState.visible ? boundedOpacity : 0.0;
    final duration =
        widget.sigilState.visible ? widget.fadeInDuration : widget.fadeOutDuration;

    return SizedBox.square(
      dimension: widget.size,
      child: TweenAnimationBuilder<double>(
        tween: Tween<double>(end: targetOpacity),
        duration: duration,
        curve: Curves.easeOut,
        builder: (context, value, child) {
          return Opacity(opacity: value, child: child);
        },
        child: RotationTransition(
          turns: _rotationController,
          child: RepaintBoundary(
            child: CustomPaint(
              painter: _SigilPainter(
                color: widget.color,
              ),
            ),
          ),
        ),
      ),
    );
  }
}

class _SigilPainter extends CustomPainter {
  const _SigilPainter({
    required this.color,
  });

  final Color color;

  @override
  void paint(Canvas canvas, Size size) {
    final center = Offset(size.width / 2, size.height / 2);
    final radius = math.min(size.width, size.height) / 2;
    final base = color.withOpacity(0.18);

    final ringPaint = Paint()
      ..color = base
      ..style = PaintingStyle.stroke
      ..strokeCap = StrokeCap.round;

    final ringFractions = <double>[0.64, 0.76, 0.88];
    for (var i = 0; i < ringFractions.length; i++) {
      ringPaint.strokeWidth = i == 0 ? 1.1 : 0.8;
      canvas.drawCircle(center, radius * ringFractions[i], ringPaint);
    }

    final markerPaint = Paint()
      ..color = base.withOpacity(0.22)
      ..strokeWidth = 0.9
      ..strokeCap = StrokeCap.round;

    for (var i = 0; i < 24; i++) {
      final angle = (math.pi * 2 / 24) * i;
      final inner = Offset(
        center.dx + math.cos(angle) * radius * 0.8,
        center.dy + math.sin(angle) * radius * 0.8,
      );
      final outer = Offset(
        center.dx + math.cos(angle) * radius * 0.88,
        center.dy + math.sin(angle) * radius * 0.88,
      );
      canvas.drawLine(inner, outer, markerPaint);
    }
  }

  @override
  bool shouldRepaint(covariant _SigilPainter oldDelegate) {
    return oldDelegate.color != color;
  }
}
