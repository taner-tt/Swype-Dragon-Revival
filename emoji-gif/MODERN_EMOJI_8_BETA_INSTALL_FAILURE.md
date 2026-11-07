# Installation failure in first modern-emoji beta — corrected ARSC layout

## User report

Samsung Android installer reported (Swedish) `Det gick inte att installera appen — Det finns ett problem med appfilen` for the eight-emoji APK. The download completed; it was **not** a missing-file error. Do not use `Swype-Emoji-Moderna-Ansikten-8-BETA-signed.apk` again.

## Verified root issue in our resource patcher

The global `resources.arsc` string pool has **8 styled entries**. The initial patcher:
- added 16 strings **after the styles payload**;
- did **not** move the style-section offset forward by the appended string data length.

This violates the Android binary string-pool layout: added string offsets now targeted data beyond the declared start of the styles section. That is a definite serialization bug and a plausible cause of the install failure, though there may be additional issues.

## Correction

From the untouched, working `Swype-Emoji-Senaste-Stabil-TEST-signed.apk`:
- placed 16 added strings **before** the existing styles payload;
- adjusted the stringsStart and stylesStart offsets and overall pool/chunk/package sizes;
- kept original eight style records, original strings, original emoji entries and category ordering;
- kept the intended eight appended emoji codes in both `@array/emoji` and `@array/emoji_category_smiley`.

The corrected beta was re-signed locally using the user's existing test signing certificate. Signing key and password were **not** committed or uploaded.

The local corrected file: `Swype-Emoji-Moderna-Ansikten-8-BETA-REPARERAD-signed.apk`
SHA-256: `692f63aa27d5f10ddb4c37b1a2471b12c324fa9c45923ab652b25f585bb73277`.

Verified in current container:
- ZIP CRC check passes;
- JAR signature verified;
- certificate SHA-256 matches the working Swype;
- decoded string pool and two complex arrays read back with 1,918 and 369 entries;
- only `resources.arsc` and signature metadata differ from stable-recents APK;
- `classes.dex` is **byte-identical** to stable-recents version.

## Outstanding risk

**No Samsung installation test or Android PackageManager parse test has been performed yet.** The ARSC-layout error was corrected based on binary-format and read-back evidence; it does not guarantee that a different install-time error cannot exist. If the corrected beta fails too, preserve current installation and fall back to the known working stable-recents APK rather than uninstalling the app.
