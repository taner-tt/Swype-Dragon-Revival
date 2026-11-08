# Swedish runtime Alpha-core diagnostic — 2026-11-08

Scope: **language catalog only**; do not change themes, GIF, emoji or the original installation path.

## Source-grounded implementation

The preserved real Swype smali contains:
- `LanguageManager$LanguageListTransaction.this$0:LanguageManager`
- `AbstractCommandManager.client:ConnectClient`
- `ConnectClient.getString(ConnectConfiguration.ConfigProperty):String`
- `ConnectConfiguration.ConfigProperty.CORE_VERSION_ALPHA`

The experimental GitHub language-list patch reads that configured property **at the moment Swype requests the download catalog** and writes one tagged Android log entry:

`SwypeGitHubLanguages: Configured runtime Alpha core: <value>`

This does not change the runtime version, the native XT9 library, the remote catalog, or the original installation engine. If configuration is not ready, it logs a warning but still starts the normal GitHub list-fetch worker. The patch refuses to run against decompiled APK baselines missing any of those source signatures.

## Why this matters

The native text `XT9 V11.03.07.00` is not proof that the app registers `CORE_VERSION_ALPHA=11.03`. Earlier source analysis found that the host exposes Alpha through the `BuildSettings` slot 1. We now have a concrete way to collect the actual configured value in a **future debug device test**, instead of publishing an unverified catalog field 102.

For the user/device owner only, in an Android debugging session with USB debugging enabled and a safe test installation:

```sh
adb logcat -c
# Open Swype Settings -> Languages and request/refresh the server language list.
adb logcat -d -s SwypeGitHubLanguages:I
```

If no line appears, the list-refresh path might not have executed, logs may have been filtered, or the installed APK may not include the patched code. `null` is a diagnostic result, **not a valid numeric version**.

## Verification and limits

The GitHub CI assembles both synthetic smali and a complete APK rebuilt from the preserved English-only Swype decompilation; it is not the owner's current master APK and is not a phone test. No APK is signed/published by this workflow. The public catalog remains empty, and private draft-release ZIP files cannot be downloaded anonymously by stock Swype. Publishing any proprietary language package requires confirmed redistribution rights.

Do not guess field 102 or mark a signed APK/device-tested before actual runtime and download confirmation.
