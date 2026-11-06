# Swype Language Installer (offline prototype)

Android project for selecting bundled language ZIP files and exporting them. **Does not install into Swype.** A secure import receiver must first be added to the modified Swype app.

Build via GitHub Actions workflow `offline-language-installer.yml`. Its APK artifact is a **prototype only** unless private language assets are supplied. Never publish proprietary language assets or signing keys.

To build locally with packages, put original-format `.zip` language packs under `app/src/main/assets/packs/` and run `gradle :app:assembleDebug`. GitHub Actions builds a source-only APK with an empty language list unless assets are supplied through a private workflow mechanism. The APK is debug-signed, not signed with the user's Swype key.
