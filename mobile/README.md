# Richard OS Assistant (Flutter)

Premium futuristic mobile AI-assistant shell for Richard OS.

Features (per spec):
- Splash (logo + orb) -> Onboarding ("Speak Freely. Richard Is Listening.")
- Bottom nav: Home · Chat(Voice) · Brain · Projects · Assistant
- Voice hero: animated Richard Orb (10 states) + mic + dynamic status + wake word
- Home dashboard: greeting + quick-action grid (Create Project, Analyze Image, Run Workflow, Research, Reminder, Translate, Control Home, Control Mobile)
- Brain: neural services around Richard Brain · Projects: active/completed + progress
- Assistant: Personal Assistant grid (Calendar/Email/Tasks/Notes/Finance/.../Home Assistant)
- Settings (server/wake/persona/active-mic/theme + full groups) · Knowledge/Memory · Skills · Tools/MCP · Security

Reuses the Studio 3D avatar via `widgets/avatar_webview.dart`; server calls via `api_client.dart`.
