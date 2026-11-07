# Samsung test: sorted nine ARSC entries ≠ displayed last page

**User screenshot (2026-11-07):** last page of smiley category still shows two emojis, 🫩 and 🥰. They confirm the **V3 Senaste visual-freeze still works**. This issue is independent of history.

## Reproduction from real APK files

Parsed both APKs' compiled `resources.arsc` in the local sandbox:

| Emoji | V3 original smiley entry index | "Sorted 9" smiley entry index | "Sorted 9" central-registry entry |
|---|---:|---:|---|
| 🥰 `1F970` | 369 | **14** | remains at the tail |
| 🫩 `1FAE9` | 368 | **101** | remains at the tail |
| 🤩 `1F929` | 361 | 12 | remains at the tail |
| 🤪 `1F92A` | 362 | 40 | remains at the tail |

The end of the sorted smiley array is now the **original** list tail
(`... 1F4AD, 1F573`), not the nine appended codes.
This confirms the ARSC edit did occur as intended; it **does not**
explain why the running Swype UI displays 🫩 and 🥰 on the last page.

## Important new distinction

Swype has a second emoji sequence in the **central `@array/emoji` registry** (`2016ˣ|emoji|<hex>` items). The sorted-nine beta preserved this registry in its original append-only order while moving nine entries in `@array/emoji_category_smiley` only.

Possible (unproved) mechanisms:
- `EmojiLoader` / `EmojiCategoryStandard` may merge, filter, or re-order by registry order after reading category arrays.
- Last-page content could reflect display filtering or a stale pager/category cache.
- Some emojis might appear in a separate dynamic list or duplicated source.

**Do not claim that moving entries in one ARSC array fixes UI placement.** Next must trace real list construction and pager `setItems` order in DEX, instrument both resource and runtime list order, and test the main registry order hypothesis in a separately labeled A/B APK. Preserve V3 history DEX exactly. Do not change themes, GIF or languages.

## Status

The sorted-nine placement beta is **not accepted** as a successful category-order fix. The confirmed good behavior is only stable recent-panel display from V3. No further APK built in this note.
