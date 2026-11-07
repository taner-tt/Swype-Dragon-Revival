# Verified Nuance-host emoji adapter — 2026-11-07

The user asked to proceed from the 370-item synthetic-object bridge to real Swype compatibility.

## What has been implemented

`emoji-gif/system-emoji/SwypeEmojiHostAdapter.java` implements
`EmojiPageBridge.EmojiHost<com.nuance.swype.input.emoji.Emoji>`
with **actual method signatures extracted directly from the V3 `classes.dex`**:

- `Emoji.getEmojiDisplayCode(): String`
- `Emoji.isCanDisplay(): boolean`
- `EmojiLoader.getEmoji(String): Emoji`

Its `orderStaticCategory(officialOrder, originalCategory)` produces a stable Unicode-sorted `List<Emoji>`, retaining original Emoji instances and checking their existing display flags. If an unregistered Unicode sequence is requested, the existing loader returns null and no fake `Emoji` is created. **The full modern Unicode import requires a safe registration/creation path; that is not solved by this adapter alone.**

Actual handoff methods identified from the APK:

- `EmojiCategoryStandard.getEmojiList(): List` — lazy loads `emojis`, returns `Collections.unmodifiableList`.
- `EmojiCategoryStandard.loadCodePoints(): void` — reads Android resource string array, resolves through `EmojiLoader.getEmoji`, checks `isCanDisplay`, then calls `List.add`.
- `EmojiPageView.setItems(List, EmojiCategory, int): void` — creates a page view using `List.subList` and `EmojiGridParams.createCells` with that same list. It is not a sorting method.
- `EmojiPagerAdapter.refreshDynamicPages()` feeds the category list into `setItems`, with the user's successful V3 recent-page freeze.

These DEX details support injecting the ordered static-category list at the **category/pager boundary**, while exempting `EmojiCategoryRecents`. But the confirmed user's 🥰-last-screen report still contradicts the order in both edited resource arrays. **The precise live input must be observed before claiming a fix.**

## Regression test performed

To compile without requiring Nuance's proprietary library, two **test-only stubs** with matching extracted APIs live under `emoji-gif/system-emoji/stubs/com/nuance/swype/input/emoji/`. These stubs must **never be included in a Swype build**: the APK already has real versions.

`SwypeEmojiHostAdapterTest` confirms:
- Existing objects are returned by identity, in the official requested order even when the original list is sorted wrongly.
- Unsupported glyphs are omitted and missing registry entries are not fabricated.
- Original emojis outside the modern catalog survive.
- EmojiPageBridge + typed host compiles against matching Nuance interfaces.

GitHub Actions run 42402146237: **all steps passed** (Java regressions, real Android SDK compilation, no APK/theme mutations).

## Honest remaining blocker

This is a real **typed adapter source implementation**, not yet injected into `classes.dex`. To make an installable Swype test APK we still need to:
1. Inject new DEX classes and redirect `EmojiCategoryStandard.getEmojiList` (or the pager's list handoff), taking care of DEX method references and multidex.
2. Supply sorted Unicode/CLDR category data and support new Emojis in `EmojiLoader` while respecting `Paint.hasGlyph`.
3. Exempt Senaste, keep V3 freeze, test startup, view/page ordering, and send Unicode sequence on Samsung.
4. Sign and run valid Android parse/install checks; do not publish a shell APK masquerading as an integration.

The confirmed-good V3 APK's `classes.dex` SHA-256 is `73190634254c2bf3d67b2bbe9edacc89238636a200d49e9f5bbead026f0bcaaa`, not modified in this step. GIF, theme and language work remain out of scope.
