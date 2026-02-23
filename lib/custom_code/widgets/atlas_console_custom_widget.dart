import 'package:flutter/material.dart';

import '../atlas_console/atlas_console_widget.dart';

/// FlutterFlow Custom Widget wrapper for the Atlas console.
///
/// This keeps the HUD/console implementation in
/// `lib/custom_code/atlas_console/atlas_console_widget.dart` while providing a
/// Custom Widget entry point FlutterFlow can register/use.
class AtlasConsoleCustomWidget extends StatelessWidget {
  const AtlasConsoleCustomWidget({
    super.key,
    this.width,
    this.height,
  });

  final double? width;
  final double? height;

  @override
  Widget build(BuildContext context) {
    final child = const AtlasConsoleWidget();
    if (width == null && height == null) {
      return child;
    }
    return SizedBox(
      width: width,
      height: height,
      child: child,
    );
  }
}

