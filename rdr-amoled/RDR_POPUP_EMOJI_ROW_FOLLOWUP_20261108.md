# RDR popup + emoji row: evidence-based follow-up (2026-11-08)

## Phone result
The user downloaded the replacement RDR.BLACK.AMOLED.V1 ZIP through Swype's own FÅ TEMA catalog. The screenshot shows an unchanged light emoji row and white backgrounds on Search and emoji popup keys. GIF is on black. This is a runtime failure, not an installer problem.

## Confirmed local binary observations
Analyzed local `RDR-BLACK-AMOLED-V1-DIRECT-STYLE-TEST4.apk` versus `btm.theme.garfield_lasagna.apk`. Both carry light and dark assets. HDPI pixel values:

| Resource | RDR | Garfield |
|---|---|---|
| `emoji_background_light.9.png` | #ECEFF1 | #ECEFF1 |
| `emoji_background_dark.9.png` | #1F1F1F | #263238 |
| `emoji_category_background_light.9.png` | ~#F6F7F8 | ~#F6F7F8 |
| `emoji_category_background_dark.9.png` | ~#252525 | ~#313C42 |
| `popup_background_menu_white.9.png` | white | white |
| `popup_background_menu_black.9.png` | black | black |
| `popup_background_key_white.9.png` | white | white |
| `popup_background_key_black.9.png` | black | black |

These binary colors prove **available resource alternatives only**; presence of a resource does NOT prove that the live popup selects it. RDR's WCL/suggestion horizontal background is already #060606. Thus the white emoji row is a separate visual surface from the black suggestion row.

## Verified prior code trace
See `rdr-amoled/GIF_POPUP_DEEP_ROOT_CAUSE.md`: host Swype XML uses `btn_keyboard_popup_key.xml` (selector over `?btnKeyboardPopupKeyNormal` / `?btnKeyboardPopupKeyPressed`). Expanded popup is rendered by `KeyboardViewEx`, which can select a per-key `Key.mKeyBackground` rather than the common keyboard background. `KeyboardStyle.getDrawable` can resolve from the theme or from the host APK.

## What failed, and why not to repeat
TEST4 added ten overrides to `SwypeDLT.FlatBlack.V3xx`. The newly uploaded theme ZIP bundled that same TEST4 payload. On-device the white strip and white Search/emoji keys remained. Therefore changing those ten mappings was demonstrably insufficient. No evidence establishes that the host actually uses the themed values for those specific surfaces.

## Next discriminating investigation (not completed)
1. Inspect the *running host APK*'s `KeyboardViewEx.drawKey` and key background selector to identify active per-key drawables for Search/GIF/emoji. Distinguish host fallback from theme resource.
2. Inspect the actual emoji-strip view/resource lookup, **not** WCL suggestion strip, and record whether it resolves light/dark theme resources or host fallback.
3. Only after identifying both lookups, patch RDR-specific resources and test through GitHub theme ZIP. Avoid global changes to Swype: a prior direct host popup patch broke other themes.
4. Validate downloaded-theme replacement versus cached installed theme; verify the installed private theme APK's SHA-256 after re-download if possible.

**Status:** diagnosis narrowed, NOT a verified fix. No production APK, theme ZIP or catalog changed by this report.
