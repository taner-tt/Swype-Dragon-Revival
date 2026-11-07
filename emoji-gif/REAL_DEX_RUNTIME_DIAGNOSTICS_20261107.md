# Real APK integration inspection — Swype already has runtime emoji diagnostics

**Status 2026-11-07: genuine read-only DEX inspection and diagnostic tooling complete. No new APK build.**

The source APK used: `Swype-Emoji-V3-AB-B-HUVUDREGISTER-TEST-signed.apk`, with `classes.dex` SHA-256 `73190634254c2bf3d67b2bbe9edacc89238636a200d49e9f5bbead026f0bcaaa`. This DEX preserves the user's Samsung-confirmed V3 recent-history freeze.

## Newly verified in original compiled instructions

1. `EmojiCategoryStandard.loadCodePoints()` (code_item `0x835c98`) **already calls** `LogManager$Log.d` with `loadCodePoints: called <category> :: added emoji :: <hex>` **after** `EmojiLoader.getEmoji` and `Emoji.isCanDisplay` and **before** `List.add`. Therefore, if these debug messages are emitted, their order is the order of accepted Emoji objects as they are inserted. It also logs its array type.
2. `EmojiCategoryStandard.getEmojiList()` (code_item `0x835e90`) logs `getEmojiList(): called` and returns `Collections.unmodifiableList(this.emojis)`; it does **not** re-sort before return.
3. `EmojiPageView.setItems()` (code_item `0x83b64c`) calls `List.subList`, creates cells, and **already logs** `setItems : called :: emojis.size() ..., cells count:: ..., pageNumber : ...`.
4. `EmojiGridParams.createCells()` sequentially calls `List.get` and constructs `EmojiGridCell`; **no list sorting** is called inside this method either.

Together these are positive evidence that `loadCodePoints()` -> `getEmojiList()` -> `setItems()` -> `createCells()` preserves the list order in the inspected methods. **This sharpens the unresolved contradiction**: in A/B B resource data 🥰 is at index 14, but the Samsung screenshot shows 🥰 at the end. Before injecting a new adapter, check the actual runtime array and whether a different category/configuration or stale app state is being displayed. The code does not establish that the APK on device loaded the intended resource entries.

## New reproducible diagnostic

`emoji-gif/diagnostics/analyze_emoji_logcat.py` extracts only Swype's internal emoji loader and page counters from a locally captured logcat file. It purposely does not print unrelated logcat lines or keyboard text. Test with `python emoji-gif/diagnostics/test_emoji_logcat.py`. GitHub Actions run `42421901170` passed all steps.

**Caution:** Production Swype logging may be disabled in `LogManager`. In that case an empty report proves nothing, and a targeted local-only instrumentation build is still required. Logs may contain private text: keep raw logcat private; only send the filtered JSON report.

On a connected test device with Android Debug Bridge authorized (only if user already uses ADB):

```sh
adb logcat -c
# Open Swype smileys, navigate near 🥰, close the panel.
adb logcat -d -v brief > swype-logcat.txt
python emoji-gif/diagnostics/analyze_emoji_logcat.py swype-logcat.txt > emoji-report.json
```

The report contains category names/counts, positions for U+1F970/U+1F929/U+1FAE9 and page-number/cell-count information, not raw typed content. Users should review the report before sharing. This is optional diagnostic material, not required for ordinary keyboard usage.

## What remains unresolved

- Whether `LogManager` actually emits verbose diagnostics in the installed release APK.
- Why the Samsung-visible last page differs from the sorted resource list.
- True in-APK injection of the Nuance Unicode ordering adapter (compilation and Java harness tests are **not equivalent** to a signed Android APK).
- Full official Unicode emoji coverage (separate from order).

No blind third reorder or risky user-data reset. V3, themes, languages, GIF and original keyboard remain unchanged.
