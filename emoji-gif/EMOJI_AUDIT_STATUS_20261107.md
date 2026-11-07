# Emoji audit status, November 7, 2026 — Samsung display versus Swype selection

User confirmed A/B-B did not change the visual positions: new emoji such as 🥰 are still at the end. **The central-registry ordering hypothesis is rejected as a sufficient fix.** The V3 stable recent-grid behavior is still confirmed working.

Read-only inspection of `Swype-Emoji-V3-AB-B-HUVUDREGISTER-TEST-signed.apk`:

- ZIP contains 201 filename entries with 'emoji', 'emoticon', or 'smiley' (category icons, tab backgrounds, emoji panel chrome, XML); it does **not** contain per-Unicode-emoji image atlases under those names.
- No `.ttf` or `.otf` entries in the APK.
- The sole `classes.dex` contains `EmojiGridCell`, `drawText`, `drawBitmap`, `hasGlyph`, and `canRenderEmoji` identifiers. These names alone do not establish which rendering path individual cells take at runtime. The absence of embedded fonts and emoji sheets is evidence of likely Android text/font fallback, but not yet a proof of OEM glyph use in every view.
- Swype controls emoji availability through `@array/emoji` and category arrays and actual `EmojiLoader` / `EmojiCategoryStandard` paths.
- Previous user-visible A/B tests established that moving 🥰 to slot 14 in both arrays did **not** place it there on Samsung.
- The last attempted category sorting is **not accepted**. Do not send another bulk-ARSC reorder as a fix until the actual post-load `EmojiCategory.getEmojiList()` and `EmojiPageView.setItems()` sequence is observed.

Next useful experiment:
1. Extract complete `EmojiCategoryStandard.loadCodePoints/loadStrings` bytecode and inspect whether the emoji list is sorted, appended, filtered or de-duplicated; inspect `EmojiLoader.getEmoji` and category XML.
2. Instrument where `EmojiPageView.setItems` receives the list and log first/last ten codepoints, and sample positions for 🥰 / 🫩 / 🤩. This distinguishes source-order versus later reordering.
3. Only build another signed APK after identified deterministic code path. Preserve V3 DEX recent-page freeze and all other theme/language/GIF assets.
