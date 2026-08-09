# Richard OS — Release Artifacts (v9.0.0)

## Windows
- Richard OS_0.1.0_x64-setup.exe   (installer)
- Richard OS_0.1.0_x64_en-US.msi

## Android (Richard OS Assistant)
- build/app/outputs/flutter-apk/app-release.apk (49.5 MB release, signed, installable)
  - install on phone (allow unknown sources)
  - Settings → Server URL → http://<pc-lan-ip>:8000
  - Home/Brain/Voice/Assistant all talk to the Richard server

## Linux
- Tauri .deb/.rpm/.AppImage (src-tauri/target)
- one-command installer: curl install.sh | bash

## Keycloak
- running at http://127.0.0.1:8081 (admin/admin)
