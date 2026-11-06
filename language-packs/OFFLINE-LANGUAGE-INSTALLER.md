# Swype Language Installer — offline APK

## Separate project; GitHub integration remains the main plan

Keep the existing GitHub-as-only-language-server work unchanged. This is an alternative, offline installer.

## User experience

1. Install one separate Android APK containing the available Swype language files and their human-readable names.
2. Open the installer and view all available languages.
3. Select one or more languages with checkboxes.
4. Tap **Install selected languages**.
5. Open Swype Dragon Revival and enable the newly installed languages from Swype's existing language settings.

No Nuance server or GitHub connection is required for the offline installer.

## Android implementation constraint

A separately installed APK cannot write to another app's private data directory under Android's normal sandbox rules. Implement a secure, explicitly authorized receiver/import pathway **inside the modified Swype APK** (for example, a signature-protected ContentProvider or explicit import Activity). The offline installer then sends selected packs through that pathway; Swype itself performs extraction, validation, registration, and activation. Do not depend on root access, accessibility automation, or shared-user-ID assumptions.

## Inputs and validation

- Source archive: user's private `lang(2).zip` (104 MDF entries, based on previous audit).
- Swedish candidate: `Swype-Swedish-Install-Candidate-UNTESTED.zip` includes compressed language assets and shared `database_le.dat`.
- Confirm each MDF's dependencies and ensure any shared database file is compatible before bundling; do not infer that one shared file works for all languages.
- Preserve original language IDs and native installer metadata; do not invent metadata.
- Never commit proprietary language binaries or private signing keys to a public repository.

## Acceptance tests

- All included language names appear with checkboxes.
- Multi-select imports each chosen pack; invalid packs fail independently with actionable errors.
- Swype shows and can activate imported languages without network access.
- Reinstall, duplicate import, and uninstall behavior tested on Android.
- Produce actual signed APK(s) and validate on a device before declaring completion.

## Status

Requirements captured. Installer APK and Swype import bridge are **not yet implemented or tested**.
