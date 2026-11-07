# Emoji Senaste V3 — test that freezes *visible* recent cells

**Status:** Signed diagnostic APK built; passed structural checks but **NOT yet Samsung-tested**.

APK (local conversation attachment): `Swype-Emoji-9-STABLE-RECENTS-v3-DIAG-signed.apk`
SHA256: `eafedf7d19f7ccffab2535eea260a9aae9b0398e3d761c361e024e2ce3181b69`
Source baseline: `Swype-Emoji-9-STABLE-RECENTS-v2-TEST-signed.apk`.

## Why V1/V2 did not settle the problem

V1 queued selection calls in `EmojiCategoryRecents.add()` and V2 disabled two repaint triggers in `EmojiInputController$1.onSelect`. Other routes to a recent-page update remained live, including `EmojiInputController.addEmojiInRecentCat()` and `EmojiPagerAdapter.onCategoryChanged()`, both of which can invoke `EmojiPagerAdapter.refreshDynamicPages()`. Thus disabling isolated call sites does not reliably freeze the visual grid.

## New actual APK patch

Replace **one DEX method body** in `EmojiPagerAdapter.refreshDynamicPages()` (at `0x83bd64`) with a compact equivalent:
1. Iterate preexisting `views` set of `EmojiPageView`.
2. Read each view's `PageInfo.cat`.
3. Only process instances of `EmojiCategoryRecents` (other categories were not dynamic in the original setup).
4. Query existing Android `View.isShown()`.
5. **If the recent page is shown, leave its cells untouched.**
6. Otherwise refresh items from `EmojiCategory.getEmojiList()`, retaining the original page index, so the history can be updated when not shown.

No new classes, resources, or dependencies. The replacement uses exactly **47 16-bit DEX code units**, the same size as the original; existing method offsets and APK manifest remain unchanged. Previous pending-queue and V2 code remain.

## Automated structural verification

- DEX SHA1 + Adler32 valid.
- Every DEX branch target is an instruction boundary; complete method disassembly covers 47 code units with no unsupported opcodes.
- Only one method's instructions changed, plus DEX checksums.
- Only `classes.dex` changed inside APK (other than signature files).
- ZIP CRC valid, JAR signature verifies, same signing certificate as user's existing Swype.
- Current GIF, language, theme and keyboard assets are byte-identical with V2.
- Nine new emojis including 🥰 are still present, in their **previous, not-yet-corrected placements**.

## Actual phone tests still needed

1. Open **Senaste**, tap 😊 then 👌 and repeated emojis without switching tabs. The emoji tiles should not change position until you leave.
2. Switch to another emoji category then back to **Senaste**. Check if most-recent usage is reflected.
3. Close the emoji panel, reopen; check that recent history updates.
4. Confirm emoji insertion, keyboard typing, scrolling, and different themes.

**Technical caution:** `View.isShown()` checks view/ancestor visibility, not whether a cached ViewPager page is entirely on-screen. Depending on ViewPager caching on the device, an offscreen recents page might still report shown and remain stale when revisiting. This is a diagnostic test of the visual-update hypothesis, **not proof of the required final behavior**. If this happens, the next version needs exact active-category state or explicit stable snapshot on category enter/exit.

**Do not call V3 a fix before Samsung validation. Do not uninstall the currently working Swype to test it.**
