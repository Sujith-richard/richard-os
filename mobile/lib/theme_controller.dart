import 'package:flutter/material.dart';
import 'theme.dart';

class ThemeController extends ChangeNotifier {
  static final ThemeController I = ThemeController._();
  ThemeController._();
  bool _dark = false;
  bool get dark => _dark;
  void setDark(bool v) { _dark = v; notifyListeners(); }
}
