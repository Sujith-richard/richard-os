import 'package:flutter/material.dart';
import 'theme.dart';
import 'screens/splash.dart';
import 'screens/home_shell.dart';

void main() => runApp(const RichardApp());

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
