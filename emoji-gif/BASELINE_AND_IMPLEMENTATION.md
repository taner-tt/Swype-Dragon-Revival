# Emoji + GIF first — independent of RDR theme

Working baseline: `Swype-English-Only-REKEYED(3).apk`.
User explicitly requested to pause all RDR theme changes and focus on emoji/GIF.
Do not use the global direct-black diagnostic APK as a basis.

## Verified against the working APK (local binary AXML inspection)

Both:
- `res/xml/popup_messaging_return_key.xml`
- `res/xml/popup_smileys_with_return.xml`

contain exactly the same three keys:

| Position | Label or icon | Android resource key code |
|---|---|---|
| left | dynamic Enter/Search/Done | `0x7f0f0041` |
| middle | `GIF` | `0x7f0f0040` |
| right | smiley icon `?0x7f0102bf` | `0x7f0f0040` |

`0x7f0f0040` is the existing **`keycode_emoticon`**.
No `keycode_gif` string is defined in `classes.dex`.
The APK bundles `GifDecoder` library classes, but that is **not**
a GIF search, panel, or send feature.

The read-only checker `tools/inspect_emoji_gif_base.py`
asserts that the three-key popup still matches this original
layout. It does not modify Android packages.

## Required implementation, in order

1. Preserve the currently working ordinary keyboard,
   existing theme selection, and per-theme popup colors.
2. Keep existing emoji key bound to `keycode_emoticon` and
   test it opens the original colorful emoji panel.
3. Define an *independent* GIF key code and dispatch handler.
   Change only the **middle** key's code in both popup variants.
   Do not bind it to the existing emoji action or Android's file picker.
4. Add a real in-keyboard GIF panel with search results and
   an explicit network data source. Implement secure image insertion
   into target apps (`InputConnection.commitContent` where supported,
   with an explicit appropriate fallback).
5. Validate open/close, Search/Enter/Done, emoji, layout width,
   keyboard typing/swiping, and 3+ unrelated themes on Samsung.
   Signing and APK build passing is not enough.
6. Only after successful user testing, revisit RDR theme.

## Status

Repository work branch: `experiment/emoji-gif-first`.
**No functional standalone GIF panel has been implemented yet.
No new Swype APK is claimed or published.** This avoids
falsely announcing a fix based only on a text label.
