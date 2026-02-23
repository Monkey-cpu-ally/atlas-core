import 'package:flutter/foundation.dart';

import '../../core/state/appearance_lab_state.dart';

class AppearanceLabController extends ChangeNotifier {
  AppearanceLabState _state = const AppearanceLabState();

  AppearanceLabState get state => _state;

  void enter() {
    _state = _state.copyWith(active: true, overlayVisible: true);
    notifyListeners();
  }

  void exit() {
    _state = _state.copyWith(active: false, overlayVisible: false);
    notifyListeners();
  }
}

