# Nuance Swype bridge integration — verified actual method boundary

**Date:** 7 November 2026. **Purpose:** progress from generic Java bridge to a bridge using the names and descriptors confirmed inside the user's actual Swype `classes.dex`.

## Confirmed from real V3 APK bytecode

- `EmojiCategoryStandard.loadCodePoints()` uses `Resources.getStringArray()`, `EmojiLoader.getEmoji(String)`, `Emoji.isCanDisplay()`, then `List.add()`. No `sort` is invoked in this method.
- `EmojiCategoryStandard.getEmojiList()` returns `Collections.unmodifiableList(this.emojis)` after lazy initialization.
- `EmojiPageView.setItems(List, EmojiCategory, int)` uses `List.subList(from,to)` to split into pages; no `sort` invocation in its inspected code.
- `Emoji.getEmojiDisplayCode()`, `EmojiLoader.getEmoji(String)`, and `Emoji.isCanDisplay()` have been found at the exact referenced DEX method descriptors.

## Actual code produced

`emoji-gif/nuance-integration/SwypeEmojiOrder.java` is in the **real Nuance package** `com.nuance.swype.input.emoji`, not a generic interface. It accepts genuine `List<Emoji>` and desired ordered Unicode strings; it preserves the original objects when possible, uses `EmojiLoader.getEmoji` for supported newly registered entries, prevents duplicate codes, and preserves legacy fallback.

Test-only `NuanceEmojiStubs.java` mimics these confirmed DEX method signatures. **Never package the stubs inside a release APK.**

GitHub Actions run `42413982901` finished **successfully**, including:
- existing catalog and history tests;
- compile + run the new Nuance-specific bridge test;
- compile Android ICU/font bridge against a real Android SDK;
- ensure no APK/theme resources were altered in CI.

## Remaining actual APK blocker

The original Swype binary is closed and we do not have editable source or a working DEX assembler in the current environment. Merely compiling this Nuance-targeted source **does not install the class into the user's APK**, and the original control flow still does not invoke it.

A safe APK integration will require a DEX code injection/rebuild with a call at the **static-category list → pager** boundary, excluding `EmojiCategoryRecents`, plus an actual official Unicode order provider and device-side instrumented validation. The user-confirmed V3 recents view freeze must not be changed.

Crucially, the current Samsung observation (🥰 at the end despite index 14 in both resource arrays) means the **runtime category state and actual `setItems` input still need to be captured** before blaming either registry or list sorting. We must not announce a fixed user-installed emoji layout from these compile tests.

**Status:** genuine integration shim implemented and CI-tested; no new installed APK. GIF, language and theme components unchanged.
