# Full Swype emoji audit (2026-11-07) — seven APKs, 89 classes inventoried

The user requested a **deep technical audit of everything emoji-related** rather than another blind APK patch. This is a read-only analysis: **no new APK and no changes to themes, GIF, language or the confirmed V3 recent-page freeze.**

## Definitive observations from real compiled binaries

- Seven APKs were ZIP-tested and their `classes.dex` / `resources.arsc` compared: original, Recent V1, Emoji 9, Recent V2, Recent V3, V3 sorted category, V3 sorted main registry.
- The emoji package `com.nuance.swype.input.emoji` has **89 classes including inner classes**. Their methods were indexed; critical loader/render/pager/history chains were traced. Not every method was formally control-flow verified.
- `EmojiGridCell.drawContent` and `EmojiGridCell$TextBitmap` render text through Android `Canvas.drawText`. The latter produces a **bitmap cache of drawn text**, not an embedded Samsung emoji image. `EmojiLoader.canRenderEmoji` uses Android `Paint.hasGlyph`. There are **no APK-bundled TTF/OTF emoji font files**. System/OEM glyph rendering is therefore strongly supported, though the exact font on Samsung was not runtime-instrumented.
- `EmojiCategoryStandard.loadCodePoints` reads `Resources.getStringArray`, resolves Unicode and `EmojiLoader.getEmoji`, filters `Emoji.isCanDisplay` and appends accepted emojis with `List.add`. **No direct sort call found in that method.**
- `res/xml/emoji_category_list.xml` explicitly references `@0x7f0c0035` for smiley, matching the updated `@array/emoji_category_smiley`. All nine emoji resource arrays in the current APK have a single decoded configuration.
- A/B B provably has 🥰 at index **14 in both** main registry (1,919 entries) and smiley list (370 entries); its `classes.dex` is identical to V3. The Samsung screenshot **still shows it on the last page**. Merely reordering either or both resource arrays **does not solve the observed behavior**. We do **not** claim to know why without live `EmojiPageView.setItems` list evidence.
- V3's stable `Senaste` grid is **user-confirmed working**; freeze code must remain untouched.
- Resource counts in A/B B: main 1919; smiley 370; family 340; nature 301; objects 521; transportation 128; flags 256; emoticons 17; GIF-preview 1.

## Next justified experiment (not built yet)

Instrument in a private diagnostic APK:
1. `EmojiCategoryStandard.loadCodePoints()`: actual array resource ID, count, first/last ten and index of 🥰, 🤩, 🫩 after filtering.
2. `EmojiCategoryStandard.getEmojiList()`: same snapshot.
3. `EmojiPageView.setItems()`: actual visible page list, category ID, selected page, count.
4. `EmojiLoader.getEmoji/isCanDisplay`: filtering decision for those targets.

Keep logs **local only** and never log user-typed text. Only a targeted, runtime-confirmed change should precede any bulk Unicode/CLDR import.

The latest official Unicode Emoji specification is **v18.0** as of November 2026: https://www.unicode.org/reports/tr51/ and https://www.unicode.org/emoji/charts/ . The phone may support fewer emojis; Unicode data and device glyph filtering must be used together.

The companion full Swedish report, machine-readable comparative results, method-call inventory, and scripts were generated as conversation files in the current container (`Swype_Emoji_Full_Djupkontroll_20261107.zip`). They are **not** committed to GitHub because the connector supports UTF-8 files, and the full bundle contains generated data; the link must be obtained from the specific conversation attachment.
