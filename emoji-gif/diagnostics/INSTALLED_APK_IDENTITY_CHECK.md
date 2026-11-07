# Diagnostic: verify the actually installed APK before more emoji edits

The user's Samsung showed 🥰 at the end after both `@array/emoji` and `@array/emoji_category_smiley` were sorted in the A/B B package. Static DEX examination found no ordering operation in `EmojiCategoryStandard.loadCodePoints`, `getEmojiList`, `EmojiPageView.setItems`, or `EmojiGridParams.createCells`.

This mismatch is **not yet explained**. The actual installed APK's identity has not been verified against the analyzed file. It is important to rule out an older APK, an installation/update discrepancy, or a split-APK setup before editing more bytecode.

`emoji-gif/diagnostics/verify_installed_swype.py` is a user-controlled optional ADB diagnostic:
- queries the installed Swype package, finds its `base.apk`, pulls only that APK (never app private data or message content);
- streams SHA-256 for installed vs user-supplied reference APK;
- prints whether they are byte-identical, then removes the temporary pulled APK;
- no uninstall, cache clearing, private-input collection or APK modification.
- requires desktop Python 3, ADB, phone-authorized USB debugging. The script has **not** been run against the user's Samsung.

`test_verify_installed_swype.py` passed three local tests: package recognition, no false positives and full-file hash streaming. These tests do not verify Swype's emoji behavior.

For a byte-identical installed APK, the next unknown is runtime state/emoji values at the category-to-pager boundary and possible cached page objects. For a mismatch, first identify the installed build. Do not claim an emoji-order fix until the discrepancy is resolved.

**V3 recents remains the last user-confirmed behavior; no new Swype APK was built here.** Themes, language, GIF untouched.
