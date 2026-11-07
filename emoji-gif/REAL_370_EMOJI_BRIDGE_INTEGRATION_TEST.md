# Real Swype emoji bridge integration test — 370 actual APK entries

## Result (2026-11-07)

**PASS** in a JVM integration harness loaded with the **370 real `emoji_category_smiley` strings** extracted from the signed `Swype-Emoji-V3-AB-B-HUVUDREGISTER-TEST-signed.apk`.

The harness calls the actual `EmojiPageBridge.orderedPage()` (not a reimplementation), using 370 synthetic wrapper objects representing the actual Unicode strings. All checks passed:

- Output length: 370 (same as input).
- Output sequence equals expected curated order at every index.
- All original 370 wrapper **object identities** are preserved (no loss/re-creation).
- No duplicate codes.
- Nine tested additions are adjacent to related original faces rather than at end.
- The source APK was **read only**; `classes.dex` SHA-256 `73190634254c2bf3d67b2bbe9edacc89238636a200d49e9f5bbead026f0bcaaa` is retained in source.
- The working V3 Senaste visual freeze is not modified.

Reproducible test bundle exported to conversation:
`Swype-Emoji-Verkliga-370-Integrationstest.zip` containing real source list, expected list, `EmojiPageBridge.java`, `RealSwypeBridgeTest.java`, and test output.

## What this DOES NOT prove

**This is still a host-JVM test, NOT an Android Swype integration.** The wrappers are deliberately stand-ins for Nuance's actual `com.nuance.swype.input.emoji.Emoji` objects. The existing APK has not been patched to call `EmojiPageBridge`.

To create a genuine on-phone test, the remaining *actual implementation work* is:
1. Implement a concrete `EmojiPageBridge.EmojiHost<Emoji>`, using the real `Emoji` Unicode getter, `EmojiLoader.getEmoji`, object construction/registration for new sequences and existing visibility rules.
2. Invoke the adapter for **static category lists only** in the actual controller/pager code, not for `EmojiCategoryRecents`.
3. Ensure page count/page objects are rebuilt from the same ordered list before `EmojiPageView.setItems()`; changing the list in the resource table alone previously failed on Samsung.
4. Include Unicode official group/subgroup data rather than a nine-entry curated fixture; verify available glyphs by Android and support multi-codepoint sequences.
5. Build and sign a private-test APK, verify that V3 DEX behavior and unrelated resources are unchanged, then test installation and `🥰` on actual Samsung.

**No APK was published or claimed fixed at this point.** GIF, themes, language, and ordinary keyboard remain untouched.
