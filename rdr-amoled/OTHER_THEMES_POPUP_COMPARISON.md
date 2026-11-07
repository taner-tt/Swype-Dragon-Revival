# Popup comparison — six actual Swype theme APKs (2026-11-07)

## Sources compared

Original release assets: `Flat_Black_v3.zip`, `nuance.theme.colorful_black.zip`,
`nuance.theme.colorful_orange.zip`, `nuance.theme.colorful_red.zip`,
`nuance.theme.india_tigerblack.zip`, plus `RDR.BLACK.AMOLED.V1.POPUP.TEST2.zip`.
All were downloaded and Apktool-decoded in GitHub Actions run 42318175761.

## What really varies across themes

All Colorful variants inherit normal popup settings from `SwypeDLT.Colorful`:
`btnKeyboardPopupKeyNormal=@drawable/trans_key`;
`keyboardKeyFeedbackBackground=@drawable/popup_background_key_colorful`;
`keyboardKeyFeedbackFunctionBarBackground=@drawable/popup_background_menu_colorful`;
`keyboardPopupBackground=@drawable/popup_background_menu_colorful`.

But the **same-named NinePatch files have different actual pixel contents**:

| Theme | `popup_background_menu_colorful` center/opaque average | `popup_background_pressed_colorful_color` opaque average |
| --- | --- | --- |
| Flat_Black_v3 | dark ~#161616 | dark ~#060606 |
| Colorful Black | light ~#F0F0F0 | black ~#000000 |
| Colorful Orange | light ~#F0F0F0 | orange ~#E87D0A |
| Colorful Red | light ~#F0F0F0 | red ~#B11A1A |

TigerBlack uses a distinct drawable family:
`popup_background_menu_india_tiger`, `popup_background_selected_india_tiger`,
`popup_background_key_india_tiger`.

The normal/pressed styles in RDR TEST2 were already explicitly `@drawable/background_black`,
yet the user's phone still displayed a white rectangle behind the emoji button.

## Relevant compiled APK mapping (directly inspected locally)

`res/xml/popup_messaging_return_key.xml` defines three keys:
dynamic return action (`?symKeyboardReturn`), `GIF`, emoji (`?emojiIconPopupMenu`).
Its `keyBackground` is `@drawable/btn_keyboard_popup_key` (0x7f0200cb).

`res/drawable/btn_keyboard_popup_key.xml` is a selector:
- pressed -> `?btnKeyboardPopupKeyPressed` (0x7f010262)
- normal -> `?btnKeyboardPopupKeyNormal` (0x7f010261)

## Interpretation

Themes can recolor the same view by supplying different named PNGs and style
references. But RDR TEST2 proves merely changing popup style refs does not
remove the white emoji block. Possible reasons (unproven): themed resource
resolution does not apply to the expanded popup, another drawable/selected
state is on top, or the white comes from the emoji icon asset itself.

**Next investigative target:** inspect `?emojiIconPopupMenu` (0x7f0102bf)
and its actual drawable under multiple themes, and the popup manager's
highlight/selection overlays. Do not ship a new APK or theme until that
dependency is identified. Preserve the stable RDR theme and app.
