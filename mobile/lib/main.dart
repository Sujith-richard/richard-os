import 'dart:async';
import 'dart:async';
import 'package:flutter/material.dart';
import 'theme.dart';
import 'screens/splash.dart';

void main() {
  runZonedGuarded(() => runApp(const RichardApp()), (e, st) {
    // crash guard: print to console + show in UI (debug surface)
    debugPrint('RICHARD OS ERROR: $e\n$st');
  });
}

class RichardApp extends StatelessWidget {
  const RichardApp({super.key});
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Richard OS Assistant',
      debugShowCheckedModeBanner: false,
      theme: RTheme.light(),
      darkTheme: RTheme.dark(),
      home: const SplashScreen(),
    );
  }
}
