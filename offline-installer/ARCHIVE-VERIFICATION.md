# Offline language archive verification

Verified locally against the supplied `Swype-104-Language-Packs-UNTESTED.zip` on 2026-11-06.

- Nested language ZIP files: **104**
- Nested ZIP bytes: **394,936,852**
- Each nested ZIP opens and passes Python `ZipFile.testzip()` CRC check: **104/104**
- Each nested ZIP contains at least one `.mdf` file: **104/104**
- Outer non-ZIP entries: `manifest.csv`, `manifest.json`
- Names pass the importer filename policy: **104/104**

This verifies archive structure and integrity only. It does not verify language compatibility, Android APK build success, import into Swype, or runtime activation.

The proprietary language archive was **not** uploaded to this repository. For local packaging see [BUILD-PRIVATE.md](BUILD-PRIVATE.md).
