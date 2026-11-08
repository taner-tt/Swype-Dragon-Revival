# KLIPY / Swype Dragon Revival — status

## Confirmed working baseline
- `Swype-3722-EmojiStrip-CODE-FIX-TEST3.apk`: user-tested Swype with 3,722 emojis and correct dark candidate/emoji strip.
- Release: `swype-gif-test` with this exact asset.
- SHA-256: `22080f447de71f5f1b9dd1d8ca191a6b4db64510fbdff38000235742aed05d23`.
- The APK must be preserved as the stable fallback. Do not uninstall or clear app data on the phone.

## KLIPY
- Test key was live-tested on the user's Windows machine: both search and trending returned 8 GIF objects with media URLs.
- The test key was previously exposed in repository history. Revoke/rotate it before distribution. Never add any API key, signing key, or private token to source files, commits, logs or release assets.
- Sources: `klipy/android/src/com/swyperevival/klipy/`.
- Pure-Java URL tests: `klipy/android/tests/com/swyperevival/klipy/KlipyEndpointsTest.java`.
- `.github/workflows/klipy-android-dex.yml`: compiles standalone DEX, **not** a usable Swype APK.
- `.github/workflows/swype-klipy-prelink.yml`: pulls verified TEST3 asset, builds KLIPY DEX, appends it as `classes2.dex` to a **strictly unsigned, not-installable diagnostic prelink artifact**, and checks base APK contents are preserved.
- A green prelink build does NOT mean the GIF function works: **there is no link yet to `com.nuance.swype.input.emoji.EmojiInputController`**.

## Next real engineering steps
1. Verify latest GitHub prelink workflow and review logs/artifact.
2. Inspect decoded `EmojiInputController` + GIF category handlers to create a narrow on-tab-selection hook.
3. Keep emoji/tab layout and original typing behavior unchanged; add correct Android network permission as needed.
4. Test trending/search, attribution, sponsored result handling, search cancellation and GIF playback on device.
5. Design and verify provider-compliant GIF transfer/URI grants. Existing code only delegates selection to a callback; does **not** send GIFs yet.
6. Sign final development APK with matching original signing identity **outside public repo**, compare signing certificate, install by `adb install -r`, and test without clearing data.
7. For a distributable APK, API credentials bundled client-side are extractable. Use KLIPY-approved architecture and rotate test credential.

## Never assume
- Green GitHub workflow means Java/DEX compilation, not device runtime validation.
- The GUI is not fully functional simply because `classes2.dex` has been appended.
- Do not publish an unsigned diagnostic artifact as a test-ready APK.

## 2026-11-08: Experimental real GIF tab hook added
- New `klipy/android/src/com/swyperevival/klipy/KlipyGifBridge.java` provides GIF-only handling, fallback to original tab behavior and an on-device test-key entry. No secrets embedded in public source.
- New `klipy/tools/patch_emoji_gif_tab.py` adds a guarded single call at the start of TEST3 `EmojiInputController.onTabChanged(String)`.
- New workflow `.github/workflows/swype-klipy-integration.yml` compiles the KLIPY classes, patches the original DEX, and assembles **UNSIGNED / DO NOT INSTALL** output while checking emoji/theme resources are byte-identical.
- Build success and runtime behavior are **not yet verified**. No signed installable GIF APK yet.
- The GIF tab bridge routes only a tab whose category name is exactly `GIF` ignoring case; actual on-device tab name and layout behavior require testing.
- GIF sending is intentionally not wired yet. Selection currently only shows a message.
