# Full Swype emoji pipeline audit and deterministic display-order probe

**Date:** 2026-11-07. **Scope:** emoji only, no theme/language/GIF modifications.

## Confirmed from installed APK binary

Source analyzed: `Swype-Emoji-V3-AB-B-HUVUDREGISTER-TEST-signed.apk`.

### Where emoji drawings come from

- `EmojiLoader.canRenderEmoji()` calls **`android.graphics.Paint.hasGlyph`** and `measureText`.
- `EmojiGridCell.drawContent()` calls **`android.graphics.Canvas.drawText`** (fallback rendering path).
- `EmojiGridCell$TextBitmap.<init>()` calls `Bitmap.createBitmap`, then **`Canvas.drawText`** into the bitmap; `TextBitmap.draw()` later calls **`Canvas.drawBitmap`**.
- `EmojiGridCell.<init>()` references `EmojiCacheManager.from`.

**Verdict:** The panel uses Unicode text drawn with Android Paint/font fallback and caches rendered glyphs as bitmaps. It does **not** contain a bundled static image for each emoji. Thus the **glyph artwork is supplied via the phone's font system** (which can differ on Samsung, Pixel, Xiaomi etc.). The list of selectable emoji and their categories are **Swype's own**, not Samsung Keyboard's private picker. Different versions of Android/OEM may vary in emoji support and appearance.

### Data loading and visual rendering

`res/xml/emoji_category_list.xml` (compiled, decoded directly from APK):
- `categoryName=smiley` explicitly maps `categoryItems=@0x7f0c0035`, i.e. `@array/emoji_category_smiley`.
- Other items (family, nature, travel etc.) have independent array IDs.

`EmojiCategoryStandard.loadCodePoints()` calls:
- `Resources.getStringArray` to fetch category contents;
- parses Unicode code points using `String.split` and `StringBuffer.appendCodePoint`;
- resolves through `EmojiLoader.getEmoji` and filters with **`Emoji.isCanDisplay`**;
- appends accepted emoji to an `ArrayList`.

`EmojiCategoryStandard.getEmojiList()` invokes `load()`.
`EmojiPageView.setItems()` takes a list, selects a sublist, calls `EmojiGridParams.createCells()` and invalidates the view.
`EmojiGridParams.createCells()` iterates the input list using `List.get` and makes `EmojiGridCell` objects.

**Important uncertainty:** These static call traces do not establish the exact runtime state/caching, active resources or which app version is loaded. The observed Samsung last-page order still disagrees with the compiled category array.

### Why previous sort tests remain inconclusive

| Signed build | 🥰 smiley array position | 🥰 central-registry position | User screenshot |
| --- | ---: | ---: | --- |
| V3, before sort | 369 | 1918 | Last page |
| V3 sorted smiley | **14** | 1918 | Still last page |
| V3 sorted smiley + central | **14** | **14** | Still last page |

The APK byte differences were genuine, but the Android device displayed a different order. Do not presume the register is the cause; both reorder experiments failed.

## Decisive diagnostic: visible first-two swap

New built and signed APK:
`Swype-Emoji-V3-DIAG-ORDER-PROBE-signed.apk`
SHA-256: `36653c66c17378d46ebd802122e02656c33541f4e2d32e09551a51859e1dc750`.

**Exactly one logical change:** swap the first two 32-bit string references in `@array/emoji_category_smiley`:
- Existing `😀` (`1F600`) at position 0 moves to position 1.
- Existing `😁` (`1F601`) at position 1 moves to position 0.

Nothing is added/deleted. No DEX, GUI, language, GIF, theme, manifest, or XML changes. `classes.dex` byte-identical to B, retaining V3 history fix. Only `resources.arsc` and JAR signing metadata differ. CRC and JAR signature checked. Certificate SHA-256 matches established Swype certificate: `49:43:45:00:D4:91:4E:D8:73:75:A6:9F:85:2C:2F:69:E1:0E:85:E9:B8:A7:F9:85:C1:9E:F6:0A:D6:E5:05:3B`.

### Phone experiment & decision

1. Install directly over current Swype, **do not uninstall**.
2. Open **smiley category** (not Senaste), navigate to first page.
3. Look at only the first two cells:
   - **😁 then 😀** = compiled category array does govern display in the running app; investigate why particular modern emoji still end up last (filtering, duplicates, supplemental lists, runtime order).
   - **😀 then 😁** = compilation change doesn't reach displayed cells; investigate runtime resource/config source, cached page lists, package/version, alternative category load path. Do **not** modify main registry again until this is resolved.
4. Verify normal emoji selection and stable Senaste; screenshot of first page suffices.

**No on-device result yet**; this diagnostic is not a complete emoji fix. Do not overclaim.

## Next steps after discriminating test

- If swap succeeds: inspect `Emoji.isCanDisplay`, the exact full output list of `EmojiCategoryStandard.loadCodePoints` and any other category list append; detect duplicates at runtime. Build a proper Unicode/CLDR-ordered category list only after this.
- If swap fails: instrument active `Resources.getStringArray(0x7f0c0035)` and `EmojiPageView.setItems` on-device, compare active APK's SHA-256 and version, and investigate per-theme resource overlays / retained category data.
- For complete Unicode emojis, source official RGI sequences and test device glyphs; don't assume codepoint-only arrays provide all skin-tone and ZWJ sequences.

## Diagnostics locally performed
Custom read-only DEX method table/call-site tracer: `emoji_audit_current/dex_method_trace.py`.
AXML decoder: `emoji_audit_current/axml_dump.py`.
Order-probe patch script: `emoji_audit_current/build_order_probe.py` (depends on user-owned local test signing key; NEVER commit the key or password).

The user has confirmed V3 stable-recents display works; do not alter it.
