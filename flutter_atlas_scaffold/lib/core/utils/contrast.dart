import 'package:flutter/material.dart';

class Contrast {
  const Contrast._();

  static Color bestOn(Color background) {
    final l = background.computeLuminance();
    return l > 0.45 ? Colors.black : Colors.white;
  }
}

