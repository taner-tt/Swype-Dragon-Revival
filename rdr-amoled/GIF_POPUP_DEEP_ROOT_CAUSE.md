# Swype GIF popup white rectangle — root cause investigation (2026-11-07)

## Verdict and scope

**The exact white-rectangle resource is not yet proved.** What *is*
proved is that it cannot be reliably fixed by blindly replacing PNGs
or by setting only a couple of theme style attributes. The most
credible remaining issue is **how the expanded popup resolves its
own selector and parent background from the main APK versus the
downloaded theme**. A separate implementation defect is that the
new GIF key duplicates the emoji key code.

Stable `RDR.BLACK.AMOLED.V1` and the installed Swype app were not
modified in this investigation.

## 1. Exact APK XML chain, extracted from actual compiled AXML

`res/xml/popup_messaging_return_key.xml`:
- one `KeyboardEx` row, three `Key` children
- root `keyBackground=@0x7f0200cb` =
  `@drawable/btn_keyboard_popup_key`
- key 1: dynamic return/search key, code `@integer/keycode_...`,
  icon `?symKeyboardReturn`
- key 2: `keyLabel="GIF"`,
  **codes=`@0x7f0f0040`**, `keyboardSettings=1024`
- key 3: icon `?emojiIconPopupMenu`,
  **codes=`@0x7f0f0040`**, `keyboardSettings=1024`

`0x7f0f0040` resolves to **`keycode_emoticon`**. The GIF key is
a copy of the emoticon action at the binary keyboard-layout level;
it is not an independent GIF action. This can affect functionality
and selection behavior, but by itself does **not prove** the source
of the white fill.

`res/xml/popup_smileys_with_return.xml` contains the same 3-key
structure; another codepath selects this resource.

`res/drawable/btn_keyboard_popup_key.xml`:
- `state_pressed=true` -> `?btnKeyboardPopupKeyPressed` (attr `0x7f010262`)
- normal state -> `?btnKeyboardPopupKeyNormal` (attr `0x7f010261`)

`res/layout/keyboard_popup_keyboard.xml`:
- parent `LinearLayout` has `background=?keyboardPopupBackground`
  (attr `0x7f01026f`)
- child `KeyboardViewEx` has `background=@android:color/transparent`,
  `keyBackground=@drawable/btn_keyboard_popup_key`,
  and `keyBorder=?keyboardPopupBorder`.

Text colors also have their own chain:
- `res/color/color_popup_text.xml` normal -> `?popupKeyTextColor`;
  pressed -> `?popupKeyTextColorPressed`
- `res/color/color_popup_text_menu.xml` normal ->
  `?popupKeyTextColorMenu`, pressed ->
  `?popupKeyTextColorPressed`.

There are **at least three independently controlled visual layers**:
the popup parent surface, normal/pressed key images, and key
text/icon state. The white area may be produced by either of the
first two, or by a drawable applied per-key.

## 2. DEX code trace confirms which layout is really used

Parsed local `classes.dex`, including method references:

- `XT9Keyboard.configureMessagingReturnKey()` and
  `XT9Keyboard.setReturnAltEmoji()` reference
  `R.xml.popup_messaging_return_key`.
- `XT9Keyboard.configureMessagingReturnKey()` also references
  `R.xml.popup_smileys_with_return`.
- `KeyboardViewEx.showPopupKeyboardHelper()` calls
  `getThemedLayoutInflater()`, `ThemeLoader.setLayoutInflaterFactory()`
  and `ThemeLoader.applyTheme()` for the expanded popup view.
- `KeyboardEx.<init>()` calls `IMEApplication.getThemedContext()`.
- `KeyboardViewEx.drawKey()` consults
  `KeyboardEx.Key.getCurrentDrawableState()`, sets the Drawable
  state and chooses between the default `mKeyBackground` and
  a per-key `Key.mKeyBackground`.
- `KeyboardEx.Key.getCurrentDrawableState()` checks `pressed`,
  `on`, `locked` and `focused` states.
- `KeyboardStyle.getDrawable()` has **two resource paths**:
  when `TypedValueWrapper.bFromThemeApk` is true it calls
  `ThemeLoader.getThemedDrawable()`; otherwise it calls
  Android `Resources.getDrawable()`.

**Interpretation, not yet proof:** a selector or parent background
may be resolved via the second (host APK) path, even when the
downloaded keyboard theme supplies black overrides. Other
possible causes are `Key.mKeyBackground` overriding the common
background or a press/focus state using a different drawable.

## 3. Failed attempted fixes were a useful negative control

Six local Swype APKs:
- `Swype-English-Only-REKEYED(3).apk`
- `Swype_Popup_Mork_TEST.apk`
- `Swype_Popup_Mork_V2_TEST.apk`
- `Swype_EmojiPanel_Svart_TEST.apk`
- `Swype_MorkEmojiPanel_NY_TEST.apk`
- `Swype_TEST.apk`

Have identical SHA-256 hashes for:
- `classes.dex` — `36e023349640...`
- `resources.arsc` — `ee0010970e86...`
- `res/xml/popup_messaging_return_key.xml` — `213e5d5b2143...`
- `res/xml/popup_smileys_with_return.xml` — `1accbd8275ad...`
- `res/layout/keyboard_popup_keyboard.xml` — `c021521a9f28...`
- `res/drawable/btn_keyboard_popup_key.xml` — `08682c74ceb9...`

Hence all earlier local popup-dark APK experiments left both the
selector/layout and implementation code intact.

The separately published RDR POPUP TEST2 has explicit style
overrides for **both** `btnKeyboardPopupKeyNormal` and
`btnKeyboardPopupKeyPressed`, plus the popup container background,
all to `@drawable/background_black`. The user reports **the same
white rectangle**. So these style overrides alone are insufficient
on the actual Samsung device.

## 4. Other theme comparison — actual decoded resources

Compared six installed theme formats in Actions run
`42318175761`:

- `Flat_Black_v3`: `popup_background_menu_colorful` opaque pixel
  average about `#161616`; pressed resource about `#060606`
- `Colorful Black`: menu resource about `#F0F0F0`; pressed black
- `Colorful Orange`: menu resource about `#F0F0F0`; pressed orange
- `Colorful Red`: menu resource about `#F0F0F0`; pressed red
- `India Tiger Black`: has a separate
  `popup_background_menu_india_tiger` and
  `popup_background_selected_india_tiger` asset family.
- `RDR POPUP TEST2`: its style values are already black for both
  selector states, but the visible phone output is still white.

Those themes' behavior correlates with **both selector state and
different pixel data inside same-named NinePatch resources**.
This is why image files are still relevant, but random edits are not.

The host APK does include a bright
`popup_background_key_white.9.png` (~#EEEEEE opaque pixel average),
but inspection of compiled XML did not show a direct reference
to that name; its presence alone cannot prove causation.

## 5. White rectangle's actual geometry in the provided screenshot

In user screenshot `17022.jpg` (709 × 1536), the white region at
`y=1215` extends **continuously from x=518 through x=706**.
This covers **both GIF and emoji** rather than a tiny white fill
inside the emoji glyph. This supports testing a shared popup
surface or matching unpressed-key backgrounds rather than repainting
the emoji icon PNG.

## 6. Ranked hypotheses, with falsification checks

1. **Highest priority: theme resource / selector resolution mismatch.**
   The popup's layout and selector are host-APK resources. A drawable
   may fall through `KeyboardStyle.getDrawable()` to the host
   `Resources.getDrawable()`, or one of the nested `?attr`
   references may resolve outside the downloaded theme. Verify
   runtime `bFromThemeApk`, resource ID, and actual Drawable
   loaded by `KeyboardViewEx` for each popup key.
2. **Different key background override or pressed/focused state.**
   The view can use `Key.mKeyBackground` instead of
   `KeyboardViewEx.mKeyBackground`; `getCurrentDrawableState()`
   changes selection. Verify per-key backgrounds and states for
   Search, GIF, emoji while popup is visible.
3. **Parent popup surface remains light.** Inspect actual
   resolved `keyboardPopupBackground` at runtime and test it
   independently of key backgrounds.
4. **Identical GIF/emoji key code** affects selection or actions.
   Compare behavior of two `keycode_emoticon` entries; fixing
   functional independence is separate from proving fill color.

## 7. A decisive minimal diagnostic test (NOT YET EXECUTED)

In an **isolated, rollback-capable diagnostic APK only**, temporarily
set the `keyBackground` attribute in
`popup_messaging_return_key.xml` and
`popup_smileys_with_return.xml` to a literal known-black drawable,
**bypassing** `btn_keyboard_popup_key.xml` and its `?attr` chain.
Do not change GIF codes, hitboxes, or RDR theme.

- White disappears: problem is in the selector / theme resource
  path, **not** the popup parent surface.
- White remains: isolate the parent
  `keyboardPopupBackground` and per-key `mKeyBackground` next.
- The diagnostic APK would affect popup behavior under other
  themes, so **do not release it as a final solution**. A final
  patch must preserve normal themes and alter only RDR.

Alternative, stronger proof: capture per-key Drawable class, resource
name, `bFromThemeApk`, `pressed/focused`, and resolved RGB in
debug logs. No root-cause claim is final without this or an
equivalent phone-side result.

## Status

**Evidence collected and code paths mapped.** No new final APK or
theme fix was released from this investigation. Stable RDR is
unchanged.
