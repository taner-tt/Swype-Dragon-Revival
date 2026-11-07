# Swype 'Senaste' emoji — real APK-level fix (test only)

This fixes the user-observed problem: while tapping `😊` then `👌` in
Swype's emoji **Senaste** tab, the emoji grid immediately reorders and
moves the next target under the finger.

## Verified program path

Reverse-inspected the **working** `Swype-English-Only-REKEYED(3).apk`:
- `EmojiInputController$1.onSelect` calls
  `EmojiCategoryRecents.add(...)` then
  `EmojiPagerAdapter.refreshDynamicPages()`.
- `EmojiCategoryRecents.add(Emoji, boolean)` chooses
  `RecentListManager.addPending()` **or** `RecentListManager.add()`.
  The latter immediately changes the recent list and its rendered order.
- `EmojiInputController.hideView()` already calls
  `EmojiCategoryRecents.commit()`, which replays queued clicks into
  the saved recent history.

## Minimal binary change, **not a hypothetical Java-only module**

The signed test APK built locally replaces one existing DEX
conditional in `EmojiCategoryRecents.add()`:

```
if-eqz v3, +8   # original selects immediate reorder for some taps
```

with two NOP code units. The existing
`RecentListManager.addPending()` and `return-void` then run for
every tap. `hideView()` still calls the existing `commit()`.

This means the order is frozen **for the full emoji-panel session**
and updated after closing the panel. It does **not yet** update on
switching from Senaste to another emoji category while the panel
remains open. That is a narrower, deliberately safer behavioral
choice than rewriting tab/pager control flow.

## Binary verification

- Original class DEX method code offset: `8608492`.
- Modified instruction offset: `8608508`.
- All archive entries except `classes.dex` and signing metadata are
  **byte-identical** with the working Swype APK.
- Original `classes.dex` SHA-256:
  `36e023349640501646f6bbc9ef16dca58b8e1348d8aefe92b55d7f2609231980`
- Patched `classes.dex` SHA-256:
  `7a434cb1638071c8ae2f6517f98a3989cfa242a0ad7553fe0e3aa91ca4a5a6d8`
- The DEX SHA-1 signature and Adler-32 checksum were rebuilt and
  validated, as were the ZIP contents.
- Signed using the user's **existing local private test keystore**;
  private key was not committed or uploaded to GitHub.
- JAR/APK v1 signature verifies, and the signing certificate
  fingerprint matches the working Swype APK.
- Signed test APK SHA-256:
  `fc66d1c6cbb4a244f2cdcd72db3d2e2a16739709fe6e07b004ca10734067195b`

## Constraints and tests needed

This is a **device test** and not yet confirmed on Samsung. Do not
uninstall the existing app if Android refuses an in-place install.
The patch deliberately leaves the active keyboard, all themes,
emoji glyph sources, layout, network/languages, and GIF functionality
unmodified. The test APK can be rolled back to the previous
`Swype-English-Only-REKEYED(3).apk` if Android permits an in-place
install.

To verify, open Senaste, tap `😊` and `👌` several times and
ensure the grid does **not move while the panel is open**. Close and
reopen the emoji panel: most-recent-used order should update.
Also confirm normal typing and other theme colors.

The independent test module `StableEmojiRecents.java` remains a
clean integration option for future source-level improvements, but
the APK binary patch uses Swype's **own existing** pending queue
and commit infrastructure instead of adding a second history store.
