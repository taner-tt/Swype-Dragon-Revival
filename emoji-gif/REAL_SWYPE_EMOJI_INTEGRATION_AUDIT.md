# Actual Swype emoji integration points — baseline APK audit

Scope: **emoji only**. Do not change GIF, theme drawing, languages, keyboard or RDR theme.

Audited installed baseline: `Swype-Emoji-Senaste-Stabil-TEST-signed.apk`. Inspected the real `classes.dex` class and method definitions, and methods' invoked code references (the call-site scan is advisory, not a control-flow decompilation).

## Confirmed from DEX

- `com.nuance.swype.input.emoji.EmojiLoader.init()` calls `android.content.res.Resources.getStringArray()`, builds the central emoji registry, and exposes `canRenderEmoji` and `getEmoji`.
- `com.nuance.swype.input.emoji.EmojiCategoryStandard.loadCodePoints()` calls `Resources.getStringArray()`, parses code points with `Integer.parseInt()`, builds Unicode sequences via `StringBuffer.appendCodePoint()` and resolves registered emojis with `EmojiLoader.getEmoji()`.
- `EmojiCategoryStandard.loadStrings()` also calls `Resources.getStringArray()` and constructs `Emoji` objects.
- `EmojiCategoryList.parseXml()` reads the XML category definitions and creates the list of categories.
- `EmojiPageView.drawCells()` and `EmojiGridCell.drawContent()` own in-keyboard emoji drawing.
- `EmojiInputController` wires the existing categories, pager, input and recent selections.
- The previously patched `EmojiCategoryRecents.add()` queues taps, and `EmojiInputController.hideView()` commits the queue (stable recents APK).

## Integration consequence

**Adding a new emoji solely to a Java source list will not put it in this APK.**
The host APK's central emoji registry, each relevant category resource array, and rendering path must be integrated together. The independent `SystemEmojiCatalog`, `AndroidEmojiSource` and `SystemEmojiPage` are building blocks but are **not** yet wired to these methods.

Safest implementation path:
1. Extract/verify the actual string-array resource IDs referenced from both `EmojiLoader.init` and `EmojiCategoryStandard`.
2. Retain original Swype registry and category lists, adding valid supported Unicode sequences instead of replacing old ones; test Samsung/Pixel OEM glyph support and ZWJ/skin-tone sequences.
3. Retain `EmojiInputController` / `EmojiPageView` so the user gets the same original keyboard and controls, and preserve the stable-recents patch.
4. Check under >=3 different existing themes, plus old Android fallback.
5. Make a separately signed beta APK only after actual resources **and** host DEX dispatch/rendering modifications are present, validate signing and unchanged nonemoji resources, then test on device.

## Status

Read-only inspection completed. **No new modern-emoji Swype APK is built or claimed in this step.** The previous history-only APK is still the last installable test build.
