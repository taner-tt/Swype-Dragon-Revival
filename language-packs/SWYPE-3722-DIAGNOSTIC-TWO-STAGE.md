# Swype 3722 — safe two-stage Alpha core diagnosis

The installed original Swype 3722 is the sole target. Do **not** assume
the native XT9 version text is the Android runtime Alpha core version.

## Why the earlier release gate was circular

The public `main/language-packs/nuance-language-list.json` is `{"43":[]}`,
and the original patcher intentionally refuses an empty catalog for a
**normal downloadable-language release**. But the actual `CORE_VERSION_ALPHA`
must be measured on the device before filling the catalog field `102`.

A **diagnostic-only** switch in `patch_language_catalog.py` now permits
instrumenting that exact empty catalog **only when**:

```sh
SWYPE_LANGUAGE_DIAGNOSTIC_ONLY=1 \
  python3 language-packs/patch_language_catalog.py PATH_TO_PRIVATE_DECODED_3722
```

It rejects a nonempty catalog when in diagnostic mode and prints
`DIAGNOSTIC ONLY`. Without this explicit switch, empty catalogs still fail.
The generated bridge still requests the public empty catalog; it will not
present a downloadable Swedish language package.

**This does not make an APK itself**: `apktool`/Android build tools must first
decode and later rebuild the user's private 3722 APK. Preserve
`classes2.dex` (KLIPY) unchanged, do not alter original resources, and use
the matching private signing key only after verifying its certificate.
Do not publish any APK, keystore or proprietary language binaries.

## Two-stage device procedure

1. Build an explicitly named **DIAGNOSTIC-ONLY** language APK based on the
   exact uploaded 3722 hash. Run byte-preservation and signature guards;
   use only in a safe test installation. This branch's CI still only rebuilds
   the older preserved English-only Swype reference and **is not** a 3722 build.
2. On the device, open Swype's original Languages screen and request a list
   refresh, then capture the tag:
   `adb logcat -d -s SwypeGitHubLanguages:I`
   Expected probe text:
   `Configured runtime Alpha core: <actual value>`.
   A missing line or `null` is NOT an acceptable measured version.
3. Only with the measured version, authentic language package version,
   byte-verified Swedish ZIP and authorized anonymously downloadable GitHub
   release URL, generate the real Nuance `"43"` catalog entry.
4. Rebuild a separate production-candidate APK **without** the diagnostic
   switch. Validate URL, MD5, signature, original assets and KLIPY DEX.
   Then test list, download, install, activate, typing, remove and reinstall
   on Android. No one should claim that this stage has happened until there
   is an actual test result.

## Current verified status

- Eight local Python tests of the owner's original 3722 and DEX transplant
  preparation passed in the conversation on 2026-11-09.
- The new diagnostic-mode regression exercises: empty normal catalog fails;
  empty diagnostic catalog is explicitly labeled; nonempty diagnostic
  catalog fails.
- GitHub CI validates this patch on the **older preserved** Swype source.
- The actual 3722 diagnostic APK has **not been built or installed**.
- Public catalog is empty and draft Swedish release is not anonymously
  accessible.

This step unblocks **diagnosis design**, not a completed end-to-end download.
