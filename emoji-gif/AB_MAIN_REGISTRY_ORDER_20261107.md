# A/B test: does the main emoji registry determine screen position?

**2026-11-07.** Based on the actual user-visible failure of `Swype-Emoji-V3-RATTA-PLATSER-9-TEST-signed.apk`, which placed 🥰 at position 14 of `emoji_category_smiley` but still rendered it on the final UI page.

## A: control (previously tested on Samsung)
`Swype-Emoji-V3-RATTA-PLATSER-9-TEST-signed.apk`

- `emoji_category_smiley`: 🥰 index 14, 🤩 index 12, 🫩 index 101.
- Central `@array/emoji`: 🥰 index 1918, 🤩 index 1910, 🫩 index 1917.
- User confirms historical grid is stable (V3), **but category ordering is wrong on-screen**.

## B: new, controlled comparison APK
`Swype-Emoji-V3-AB-B-HUVUDREGISTER-TEST-signed.apk`
SHA-256: `464c9ed140b065af37ff80f2055686899bed297f387e782e6fb2449be27afa94`.

- Kept all category resource arrays **identical** to A.
- Reordered only the 1,919 string-value map entries in central `@array/emoji` to place nine previously appended codes near their existing analogs.
- 🥰 index 14 in **both** central registry and smiley category.
- 🤩 index 12 in both.
- 🫩 index 1816 in central registry (next to 🫨, which has that position in the central catalog), index 101 in smiley category. This exception tests that the central list is cross-category, not solely smiley.
- Original 1,910 central entries retain original relative order; no emoji codes were deleted, created, or duplicated.
- **DEX SHA-256 is identical** to A: `73190634254c2bf3d67b2bbe9edacc89238636a200d49e9f5bbead026f0bcaaa`. Hence V3 stable recent behavior is preserved at the binary level.
- Every APK member is identical apart from `resources.arsc` and new signature metadata.
- ZIP CRC check passed, both compiled arrays parsed after signing (1,919 and 370 entries), JAR signature verified.
- Same signing certificate SHA-256 as existing user install: `49:43:45:00:D4:91:4E:D8:73:75:A6:9F:85:2C:2F:69:E1:0E:85:E9:B8:A7:F9:85:C1:9E:F6:0A:D6:E5:05:3B`.
- The user signing key **was not uploaded or committed**.

## Decision tree from Samsung testing

1. Install B over A without uninstalling. Open the smiley tab (not Senaste) and inspect 🥰 and 🤩.
2. If 🥰/🤩 now appear near related faces, the main registry ordering (or its downstream effect) contributes to visual order. Verify 🫩 separately.
3. If 🥰/🤩 remain on the last page, registry order is not sufficient. Inspect live `EmojiCategoryStandard` / `EmojiPagerAdapter` list order and `EmojiPageView.setItems()` inputs; do not blindly patch more resource arrays.
4. In either case verify Senaste stays visually fixed after emoji taps.

**Limits:** This A/B experiment is an unsigned binary-resource hypothesis until Android validates installation and behavior. The signed output exists but the on-device result is unknown. The full modern Unicode emoji import is not yet present. GIF, languages, theme assets are unmodified.
