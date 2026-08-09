import 'dart:async';
import 'package:flutter/material.dart';
import 'api_client.dart';
import 'theme.dart';
import 'screens/splash.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await RichardApi.loadBase();
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
