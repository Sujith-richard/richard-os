import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:richard_os_assistant/theme.dart';

void main() {
  test('theme has expected colors', () {
    expect(RColors.lavenderDeep, const Color(0xFF7C3AED));
    expect(RColors.accent, const Color(0xFF22D3EE));
    expect(RColors.ok, const Color(0xFF10B981));
  });
}
