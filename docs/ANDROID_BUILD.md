# Richard OS — Android device agent (AccessibilityService)

## What it is
A small Android app (`android/`) exposing the phone as a Richard **device node**:
- reads the UI tree (screen understanding)
- performs gestures: tap / swipe / scroll / back (via `dispatchGesture`)
- the design doc: Observe → Act → Observe → Verify; permissions L0–L4

## Build (Android Studio)
1. Open `android/` in Android Studio.
2. Build → APK → install on your phone.
3. Enable **Accessibility** → "Richard OS" service.
4. Point it at your office: set the Richard server base URL (e.g. `http://<pc>:8000`)
   and it will POST to `/api/v1/mobile/command` when you speak.

## Flow (matches the voice/mobile proof)
"hey richard open youtube on my phone" → voice_engine (PC) → device_registry finds this node →
`_device_call("mobile", …)` POSTs to the phone's URL → service taps Type→Open → verifies → replies.

## Status
Scaffold (buildable): manifest + service (tap/swipe/label) + activity. Real network sync:
add an HTTP POST to `reportOnline()` with your server URL + auth token.
