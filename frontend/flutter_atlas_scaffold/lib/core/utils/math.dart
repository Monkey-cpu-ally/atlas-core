class AppMath {
  const AppMath._();

  static double clamp(double value, double min, double max) {
    return value.clamp(min, max).toDouble();
  }

  static double lerp(double a, double b, double t) {
    return a + (b - a) * t.clamp(0.0, 1.0);
  }

  static double normalize(double value, double min, double max) {
    if (max <= min) {
      return 0;
    }
    return ((value - min) / (max - min)).clamp(0.0, 1.0).toDouble();
  }
}

