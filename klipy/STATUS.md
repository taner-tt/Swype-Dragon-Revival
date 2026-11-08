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

## Build verification PR
A draft PR is used to make GitHub Actions run IDs and logs available for debugging. Do not merge unverified builds.

## 2026-11-08: Signed GIF-sharing TEST APK produced locally (not publicly published)

- GitHub Actions pull-request build 42520730630 **succeeded**, artifact ID 13632329475.
- This build contains `KlipyGifBridge`, `KlipyGifPanel`, `KlipyGifSender`, `KlipyGifStreamProvider`, and a private manifest provider `com.nuance.swype.dtc.klipy.gif` with URI grants.
- Sends `image/gif` via `InputConnection.commitContent` on Android >= 7.1 *when the receiving editor advertises GIF support*. For other apps, a message indicates unsupported content; there is no text URL fallback.
- The provider pipes KLIPY media over HTTPS to the receiving app. No persistent media file is stored in this APK implementation. GIF share analytics POST implemented as best-effort.
- Downloaded unsigned GitHub artifact, locally signed with the user's **matching** private Swype test signing certificate. **No signing key was committed/uploaded**.
- Signed file created in the conversation: `Swype-3722-RDR-KLIPY-GIF-SHARING-SIGNED-TEST.apk`.
- Signed SHA-256: `4a1cec462e0cb4e8602e00c76f3b715a293b5805447e9366bab262be5e442723`.
- Signing certificate SHA-256 matches original TEST3: `49434500d4914ed87375a69f852c2f69e10e85e9b8a7f985c19ef60ad6e5053b`.
- All original non-code APK entries, including all 3722-emoji data and RDR theme files, verified identical; only `classes.dex`, `AndroidManifest.xml`, and signature differ, plus `classes2.dex`.
- APK ZIP integrity and `jarsigner -verify` passed.
- **Not yet tested on user's Samsung device.** Both GIF entry points, emoji/theme regression, network key entry, GIF rendering and sending need on-device testing.
- Key must be rotated; previously leaked test key must be revoked. The user can enter the new test key privately in the keyboard; it is not in code.
- The code is on **draft pull request #11**, branch `klipy/build-verification-nov8`, intentionally unmerged until device validation.


## 2026-11-08: Popup GIF root cause and build verified

- Decoded the actual TEST3-derived `res/xml/popup_messaging_return_key.xml` and `popup_smileys_with_return.xml`: the center GIF key and right-hand smiley key both have `codes` pointing at the same resource ID `0x7f0f0040`. The GIF cell has `keyLabel="GIF"`. Thus the original handler cannot distinguish them solely by code.
- DEX method table confirms `SlideSelectPopupManager.sendKeyCode(OnKeyboardActionListener, KeyboardEx.Key):boolean`; the selected key has a `label` field. `sendKeyCode` forwards to the original `OnKeyboardActionListener.onKey`.
- Added a narrow `notePopupKey` hook that examines the popup key's actual label before preserving original key dispatch; a temporary GIF request is consumed by `EmojiInputController.onTabChanged` when it creates the KLIPY view. This approach requires runtime verification for the keyboard's precise event ordering.
- Added `klipy/tools/patch_popup_gif_handler.py` with a strict method signature and duplicate guard; added an offline synthetic smali test.
- GitHub Actions run **42529544603**: all build steps completed successfully, including URL tests, popup patch test, Java compilation, DEX generation, TEST3 checksum verification, both smali patches, packaging and artifact upload.
- Artifact **13637080995**: `Swype-KLIPY-INTEGRATION-UNSIGNED-DO-NOT-INSTALL.apk`, SHA-256 `6678e11aab8c63f14a87b49893acdd71c00ec4520408e9ee7eecfedeab5186ca`.
- Local ZIP check: 4,273 entries, CRC PASS, only `classes.dex` and `classes2.dex` differ from earlier unsigned KLIPY build; all original non-code resources and manifest are unchanged. New `notePopupKey` is present in the patched DEX and KLIPY DEX; corrected key-error text is present in KLIPY DEX.
- **NOT INSTALLABLE**: this artifact is unsigned. The matching original TEST3 signing key is not available in this session. Do not replace a working installation with a different signing identity.
- **NOT DEVICE-VERIFIED**: need Samsung check for popup GIF opening KLIPY, regular smiley unaffected, key activation, trending/search and sending; then emulator/other Android coverage before universal compatibility claims.
