# Emoji: stable recents V2 and correct category ordering

## User-reported issue
During emoji selection, the `Senaste` history still updates and changes while the emoji panel remains open. The first stable-recents patch was insufficient.

## Confirmed original APK code path
- `EmojiCategoryRecents.add()`: queues pending clicks, previous beta patched.
- `EmojiInputController$1.onSelect()` **also calls** `EmojiPagerAdapter.refreshDynamicPages()` after adding an emoji. It can also call `EmojiPagerAdapter.onCategoryChanged()` when the recent page count changes.
- `EmojiInputController.hideView()` already commits Swype's queued history. This preserves the delayed update.

## New local test APK (not device-verified)
`Swype-Emoji-9-STABLE-RECENTS-v2-TEST-signed.apk`
SHA-256: `acb5620cab9184b92164264808dbc28a6f2e4cd602ebf3744d12849c2cd37391`.

The patch NOPs only the two live pager invalidation invocations in `EmojiInputController$1.onSelect`:
- method code at `0x837bf0`, instruction +`0x96`: `refreshDynamicPages`
- instruction +`0x13e`: `onCategoryChanged`

The existing `EmojiCategoryRecents.addPending()`, `commit()`, and `hideView()` calls are retained.
New DEX SHA-256: `331859746eb90e95e74a70cd47a5e52a5f48987f686406b51a68f33c3b590e0e`.
Only `classes.dex` differs from the signed nine-emoji beta (apart from signature metadata). The emoji resources, themes, layout, GIF and languages are unchanged. ZIP integrity and JAR signature verification passed. Certificate SHA-256 remains `49:43:45:00:D4:91:4E:D8:73:75:A6:9F:85:2C:2F:69:E1:0E:85:E9:B8:A7:F9:85:C1:9E:F6:0A:D6:E5:05:3B`.

**Device test is still required:** repeated emoji selection in Senaste, closing/reopening panel, emoji chosen from another tab, and normal editor input. If selecting an emoji actually switches tabs, verify the tab change separately. Do not uninstall the working APK.

## All modern emojis in the correct places
The user explicitly does **not** want all missing Unicode entries appended to the end.

Unicode Emoji 18.0 is the latest official 2026 release:
- https://www.unicode.org/reports/tr51/
- https://www.unicode.org/Public/emoji/latest/emoji-test.txt

The initial `emoji-gif/plan_unicode_emoji_categories.py` script groups fully-qualified RGI emoji sequences using Unicode group/subgroup order. Crucially, it checks **actual original Swype categories** and preserves the existing membership first. For new entries, a clear majority of existing Swype category entries for the Unicode subgroup determines the target; ambiguous groups are marked for manual review. It handles multi-codepoint sequences, not just the earlier 199 single-codepoint candidate list.

This is a **plan**, not automatic complete integration. Every candidate must pass the real Android OEM glyph check, and the final APK must update both `@array/emoji` and the correct category array in `resources.arsc` without corrupting the styled string pool. Render and on-device regression tests remain necessary.
