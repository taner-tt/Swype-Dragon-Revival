# V3 emoji category placement — first signed test APK

**Built against the exact working-on-Samsung V3 diagnostic**, not a new keyboard or an unrelated fork:
`Swype-Emoji-9-STABLE-RECENTS-v3-DIAG-signed.apk`.

Output: `Swype-Emoji-V3-RATTA-PLATSER-9-TEST-signed.apk`
SHA-256: `1c951de01ae70cacd24ddbe0056c9391853c8ec3eef2edf8dade2798f0cde04f`.

This test preserves the V3 DEX **byte for byte** (SHA-256 `73190634254c2bf3d67b2bbe9edacc89238636a200d49e9f5bbead026f0bcaaa`).
Only `resources.arsc` and APK signature metadata differ.
The APK uses the user's existing local signing key, verified with `jarsigner -verify`. The private signing key is **not on GitHub**.

## Actual array changes

`emoji_category_smiley`: still **370 entries**. Nine already-present new emojis are moved beside similar original faces, while the 361 original entries retain precisely their relative order.

| Emoji | Zero-based new position | Nearby original |
| --- | ---: | --- |
| 🤩 | 12 | 😍 |
| 🥰 | 14 | 😘 |
| 🤭 | 21 | 🤗 |
| 🤫 | 32 | 🤐 |
| 🤪 | 40 | 😛 |
| 🤯 | 51 | 😲 |
| 🤬 | 70 | 😡 |
| 🤮 | 80 | 🤢 |
| 🫩 | 101 | 🫨 |

All seven other extracted emoji-related arrays (the central registry and other category arrays) compare byte-value for byte-value identical with V3.
No added string pool entries, no Unicode glyph overrides, no new class or theme changes.

Validation assertions:
- all 370 smiley entries remain; no duplicates or missing entries;
- the original 361 items are a subsequence in unchanged relative order;
- all nine added emojis moved from the tail into the body;
- unrelated category arrays untouched;
- DEX identical to V3;
- ZIP CRC passes; JAR signature verifies.

**Limits:** This is an intermediate test of placement for nine emojis, **not a claim that all Android system emojis have been imported**. The full Unicode RGI/skin-tone/ZWJ catalog remains unimplemented; shipping all at once would risk corrupting the APK and undoing the working V3 recent-history fix. The placement in this test is curated proximity within Swype's existing ordering, not exact CLDR sorting. Device install/display still needs testing. GIF, theme and language work untouched.
