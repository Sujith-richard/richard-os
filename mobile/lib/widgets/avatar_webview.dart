import 'package:flutter/material.dart';
import 'package:webview_flutter/webview_flutter.dart';

/// Embeds the existing Richard 3D neural avatar (ui/avatar.html) inside the
/// app — same premium orb as the desktop Studio.
class AvatarWebView extends StatelessWidget {
  const AvatarWebView({super.key, this.url});
  final String? url;
  @override
  Widget build(BuildContext context) {
    final target = url ?? 'http://127.0.0.1:8000/ui/avatar.html';
    return WebViewWidget(controller: WebViewController()
      ..setJavaScriptMode(JavaScriptMode.unrestricted)
      ..loadRequest(Uri.parse(target)));
  }
}
