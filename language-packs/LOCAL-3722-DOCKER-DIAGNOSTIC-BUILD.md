# Local Docker build for Swype 3722 (2026-11-09)

The private owner-provided 3722 APK is NOT uploaded to GitHub. Recent Actions attempts did not create jobs, so no new 3722 APK has been built there.

A local, private Docker toolkit was created in the conversation as `Swype_3722_Docker_Diagnostik_Byggpaket.zip`. It contains a Dockerfile installing apktool, apksigner and zipalign, plus `run-diagnostic.sh`, the existing Python 3722 build/verification scripts, and a `.dockerignore` excluding private APKs and keystores from image build context.

On a computer with Docker and internet, extract the toolkit and place the exact owner-supplied `Swype-3722-KLIPY-GIF-POPUP-FIX-SIGNED-TEST(1).apk` alongside scripts. Run `sh run-diagnostic.sh` for an unsigned diagnostic; for a signed test, provide the owner's private `swype-revival-test.jks` locally and run `sh run-diagnostic.sh --sign` with password entered only on that machine. Build uses a pinned GitHub patch commit and `--network none` when processing private files. Signing and the final APK's DEX/assets/lib/KLIPY integrity are checked before output is delivered.

The diagnostic uses an intentionally empty language catalog and cannot download Swedish; it is only to measure true runtime `CORE_VERSION_ALPHA` from Android logcat. No signed APK or actual device test has been done in this chat. Locally 22 of 22 Python regression tests passed; Docker itself is absent in the chat environment and network resolution fails. Do not claim a successful build without running it.
