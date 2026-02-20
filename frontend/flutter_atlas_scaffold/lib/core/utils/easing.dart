import 'package:flutter/animation.dart';

class AppEasing {
  const AppEasing._();

  static const Curve smooth = Curves.easeOutCubic;
  static const Curve settle = Curves.easeOut;
  static const Curve softInOut = Curves.easeInOutCubic;
}

