import 'package:flutter/widgets.dart';

import '../ui/screens/dial_screen.dart';

class AppRoutes {
  const AppRoutes._();

  static const String dial = '/';

  static Map<String, WidgetBuilder> map = <String, WidgetBuilder>{
    dial: (_) => const DialScreen(),
  };
}

