# Offline Swedish installer rollback test: scope and results

The full executable script is distributed in the 2026-11-10 test ZIP produced locally. This document records the test protocol without private language databases or keys.

## Scope

A sandbox-only Python simulation uses the Swedish ZIP after checking exact filenames, ZIP CRC, and Swype MDF target paths. It decompresses both payloads into staging, checks SHA-256, backs up target files, swaps staged files, and attempts byte-exact rollback on injected exceptions.

Run a matrix of 3 initial states (both targets present, one present, neither present) by 4 outcomes (success, exception before first swap, after first swap, after second swap). An unrelated file is kept in each sandbox to detect accidental modifications.

**Observed 2026-11-10: 12/12 simulations passed.** For every failed transaction, all preexisting files were restored byte-for-byte; unrelated data was unchanged. This is not native Android Swype LanguageInstall verification.

The current signed runtime diagnostic APK's signature was rechecked with apksigner (certificate SHA-256 49434500d4914ed87375a69f852c2f69e10e85e9b8a7f985c19ef60ad6e5053b). Comparing with the original 3722 KLIPY APK showed four modified entries: classes.dex and three META-INF signature files, with no added or deleted entries.

## Release blockers (unchanged)

- Genuine Nuance language-package version (field 20) unavailable.
- Device Nuance Alpha-core major/minor (field 102) not verified; XT9 V11.03.07.00 does not automatically establish it.
- Authorization to redistribute the proprietary ZIP and a verified public HTTPS URL unavailable.
- Native install, registration, activation and rollback not validated on Android.

**Do not ship/install the proprietary Swedish language pack or put private ZIPs/signing material in the public repository.** This test intentionally does not alter the existing phone installation.
