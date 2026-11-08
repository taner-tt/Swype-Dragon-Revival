# GIF popup background investigation — 2026-11-07

## Original development evidence

The archived ChatGPT transcript PDF (pages 358–362 of 372) records:
- The GIF button was inserted into the **existing expanded lower-right popup**, not the bottom keyboard row.
- The desired order is the original dynamic action (Search/Enter/Done), then GIF, then emoji.
- The previous developer reported building `Swype-GIF-Popup-Fix-signed.apk` and the user subsequently replied “bättre”.
- The transcript does **not** contain the XML/smali patch or exact resource IDs used in that APK.

## Binary evidence from locally available APKs

All four locally compared APKs have *byte-identical* `classes.dex`,
`resources.arsc` and `AndroidManifest.xml` (same SHA-256 per entry):

| Entry | Identical SHA-256 prefix across compared APKs |
|---|---|
| classes.dex | 36e023349640501646 |
| resources.arsc | ee0010970e86764a33 |
| AndroidManifest.xml | 671b2c34282b9c903d |

Compared: `Swype-English-Only-REKEYED(3).apk`, `Swype_Popup_Mork_TEST.apk`,
`Swype_Popup_Mork_V2_TEST.apk`, and `Swype_EmojiPanel_Svart_TEST.apk`.
The earlier popup-themed tests changed 63 and 87 archive entries respectively,
predominantly PNG/9-patch drawables and signing metadata, but did not touch code
or the Android resource table.

## Consequence

Do not keep changing random PNGs or RDR theme properties. Identify the actual
expanded popup view's construction and selection logic by decompiling the
installed APK's `classes.dex`, then trace background assignments, view
inflation and GIF/emoji child views. A comparison with the original
`Swype-GIF-Popup-Fix-signed.apk` would be valuable **if its bytes can be
recovered**; the archived PDF alone is not the original APK.

Preserve the working RDR BLACK AMOLED V1 theme and current installation
until a code-level fix is validated in an isolated APK.

## Status

Diagnosis only. No verified popup fix has been built or installed.
