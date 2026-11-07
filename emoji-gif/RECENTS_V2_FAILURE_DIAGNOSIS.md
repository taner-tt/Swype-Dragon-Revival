# Samsung test: recents still moves and modern emojis remain at end

**Device result (user report, November 7, 2026): V2 failed. Do not promote as fixed.**

## Binary verification performed on the two actual signed APKs

`Swype-Emoji-9-BETA-signed.apk`: `EmojiCategoryRecents.add` branch already forced to pending mode (first four instruction bytes `00000000`).

`Swype-Emoji-9-STABLE-RECENTS-v2-TEST-signed.apk`:
- The same `EmojiCategoryRecents.add` patch is still present.
- In `EmojiInputController$1.onSelect`, invoke at +`0x96` (`refreshDynamicPages`) is NOP'd.
- In the same method, invoke at +`0x13e` (`onCategoryChanged`) is NOP'd.
- User reports the visible **Senaste** still changes immediately. This is conclusive device-feedback that those patches are insufficient, even though the binary changes are genuinely present.

## Additional still-live refresh path verified in unchanged DEX

`EmojiInputController.addEmojiInRecentCat()` calls
- `EmojiCategoryRecents.add` at instruction offset +`0x20`
- `EmojiPagerAdapter.refreshDynamicPages()` at instruction offset +`0x32`.

`EmojiInputController.onGlobalPageChanged()` and `onTabChanged()` also run during page/category transitions. Directly NOP-ing more refreshes is **not** proven safe: the pager needs legitimate updates when moving between categories. Need an actual *visible snapshot* / deferred refresh until leaving the Recents tab, with a single controlled refresh at exit. Ensure displayed list and click mapping use the same stable snapshot.

The user's words about icons remaining in the same places confirm the separate category-order defect: the 9-emoji beta **appended** all new entries to the end of `emoji_category_smiley`. That was never a proper final sorted integration.

## Required correction gates

1. Reproduce first/second tap in Senaste in runtime instrumentation, or instrument original code for selection, pending-list, adapter `setItems`, page changes and reopen.
2. Freeze *rendered* emoji list, not only MRU storage. Update MRU after leaving Senaste, and redraw once.
3. Rebuild categories from official Unicode subgroup ordering while preserving Swype's category choices, rather than appending the nine additions.
4. Expand beyond nine emojis only after safe resource serialization, glyph support and OEM fallback are verified.
5. Re-test Samsung on the signed output. Current V2 is **not fixed**.

**No new APK is produced by this diagnostic.** Keep last known functional beta until actual behavior is verified.
