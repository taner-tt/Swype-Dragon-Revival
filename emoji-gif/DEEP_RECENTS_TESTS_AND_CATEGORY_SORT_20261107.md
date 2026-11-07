# Deep Swype emoji audit — 2026-11-07

Samsung user feedback: **stable-recents V2 FAILED**, and all nine added emoji still sit at the end of the smiley category.

## Actual binary verification (not speculation)

Inspected `classes.dex` and `resources.arsc` in four real APKs:
- `Swype-English-Only-REKEYED(3).apk`
- `Swype-Emoji-Senaste-Stabil-TEST-signed.apk`
- `Swype-Emoji-9-BETA-signed.apk`
- `Swype-Emoji-9-STABLE-RECENTS-v2-TEST-signed.apk`

| Condition | Original | V1 | Emoji 9 | V2 |
| --- | --- | --- | --- | --- |
| `EmojiCategoryRecents.add()` forced to pending | No | Yes | Yes | Yes |
| `onSelect()` direct refresh NOP'd | No | No | No | Yes |
| `onSelect()` onCategoryChanged NOP'd | No | No | No | Yes |
| `onGlobalPageChanged()` invokes commit | Yes | Yes | Yes | Yes |
| `addEmojiInRecentCat()` invokes refresh | Yes | Yes | Yes | Yes |
| Smileys count | 361 | 361 | 370 | 370 |

### Important missing path

`EmojiCategoryRecents.commit()` is called from **two** places:
1. `EmojiInputController.hideView()` at `+0x1a`.
2. `EmojiInputController.onGlobalPageChanged()` at `+0xca`.

The second invocation occurs conditionally on changing category group, so it may be correct during real navigation. It is nevertheless a possible cause of **premature recent-list updates** if the selection event results in a page/category transition. This causal chain is **not proven on Samsung yet**. `RecentListManager.getAll()` returns the committed list, while `addPending()` records in a separate pending list. `EmojiPagerAdapter.refreshDynamicPages()` ultimately calls `EmojiPageView.setItems()`.

### Independent model tests

All four simulations executed and their stated assertions passed:
- A: two taps with no page event → visible list stays put.
- B: tap, premature page-change commit, tap → visible order **changes too early**; hypothesis of the device bug.
- C: two taps then leave → visible list updates only on exit, as desired.
- D: same as B but no premature commit → stable order.

**These tests are simulations of call-order consequences, not Android instrumentation or proof that the device triggered B.** Do not ship further blind NOP patches. Record active category and timestamps around `onSelect`, `onGlobalPageChanged`, `commit`, `refreshDynamicPages` and `setItems` first, then implement a snapshot of the visible recent list until the tab is left.

### Emoji placement

Parsed original `emoji_category_smiley` (361 entries) and nine-emoji beta (370 entries). All nine new codes `1F929 1F92A 1F92B 1F92C 1F92D 1F92E 1F92F 1FAE9 1F970` were appended at indices 361–369.

A separate tested **curated preview**, not yet an APK, inserts them near related Swype smileys:

| Emoji | Adjacent old emoji | New index (0-based) |
|---|---|---:|
| 🤩 | 😍 | 12 |
| 🥰 | 😘 | 14 |
| 🤭 | 🤗 | 21 |
| 🤫 | 🤐 | 32 |
| 🤪 | 😛 | 40 |
| 🤯 | 😲 | 51 |
| 🤬 | 😡 | 70 |
| 🤮 | 🤢 | 80 |
| 🫩 | 🫨 | 101 |

Checks passed: nine are unique, all 361 original entries retain their relative order, none are lost, none of the new nine are appended at the end. This is a **human-friendly Swype-specific preview**, not the exact CLDR sort order. Whole-catalog Unicode Emoji 18.0 plus RGI sequences and per-device glyph support needs a separate verified integration.

**Outcome:** V2 remains unapproved. No new signed APK has been built in this research round. Main priority: runtime diagnosis of premature commit and visible-list freeze. Second priority: comprehensive ordered, platform-aware emoji category import. GIF and theme code untouched.
