# First installable modern emoji beta — eight additional faces

This is a **device-test build**, based on the user's previous
`Swype-Emoji-Senaste-Stabil-TEST-signed.apk`.
The work is scoped **exclusively to emoji resource arrays**;
no theme, language, keyboard, popup, GIF, layout or DEX code edits.

## Original facts verified by reading compiled `resources.arsc`

- `@array/emoji` (resource `0x7f0c002f`): 1,910 entries.
- `@array/emoji_category_smiley` (`0x7f0c0035`): 361 entries.
- Other emoji category arrays are unaffected.
- Several newer emojis such as 🥹, 🫠, 🫢, 🫣 and 🫨
  **already exist** in both original arrays; they were NOT duplicated.
- Exactly eight missing codes are appended to both arrays:
  `1F929 1F92A 1F92B 1F92C 1F92D 1F92E 1F92F 1FAE9`
  (🤩 🤪 🤫 🤬 🤭 🤮 🤯 🫩).
- The new catalog size is **1,918** entries and the smiley
  category is **369** entries. Existing entries preserve original
  ordering and byte values.

## Binary patch scope and verification

- The patch reconstructs only Android's compiled resource table
  `resources.arsc`: appends 16 string pool items, creates
  replacement complex-array records for two resource IDs, and
  adjusts chunk/parent lengths. All unrelated resource IDs are
  preserved.
- Subsequent read-back of the generated ARSC verified those
  list counts and all eight new emoji values.
- A separate verification script compared the base and beta APK
  member-by-member: **only `resources.arsc` and signing metadata
  differ**.
- In particular, `classes.dex` is unchanged from the previous
  stable-recents test, so the history fix was preserved.
- ZIP CRC test passed; `jarsigner -verify` passed.
- Signing certificate SHA-256 matches the existing working APK.
- New signed APK SHA-256:
  `61c6fc1b96f3664d4fef1a97905238becb86ebd3a00591d0c55620ac7bf94564`.
- Local patch, resource audit and verification scripts are packaged
  separately with the beta. The private signing key was **not**
  included in that package or uploaded to GitHub.

## Limitations

**Resource-level verification does not prove on-device rendering.**
The existing `EmojiLoader` and emoji font fallback may still
filter or fail to draw the new codepoints; these behaviors can only
be checked on Android. Some newer emojis may depend on the handset
OS version. No installed-device test or multi-brand test has yet
been completed. This is not a claim of full Unicode Emoji 17.0
coverage: a separate catalog diff identifies 199 missing
standalone-codepoint candidates, and additional ZWJ/multi-codepoint
sequences need their own analysis.

To test on Samsung: install the signed beta **over** the
previous same-certificate Swype if Android permits it; do not
uninstall first. Open the original smiley category, scroll to the
end where eight test entries have been appended, and verify
🤩 🤪 🤫 🤬 🤭 🤮 🤯 appear in color and can be typed.
Check that selecting 😊 then 👌 in **Senaste** does not move
the list while the emoji panel remains open. Verify normal
typing and a theme other than RDR.

If no new emojis appear, the next step is debugging
`EmojiLoader.canRenderEmoji()` or the view's glyph drawing
path, **not** global theme-background edits.
