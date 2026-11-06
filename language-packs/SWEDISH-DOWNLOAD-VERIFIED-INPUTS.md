# Swedish GitHub language download: verified inputs and remaining gates

Analysis date: 2026-11-06. **This is not a tested download APK.** Do not publish Swype/Nuance language binaries or signing credentials without verifying distribution rights.

## Verified directly from existing decompiled Swype APK analysis artifact

Source: GitHub Actions inspection artifact (run 42079023597) of `Swype-English-Only-REKEYED.apk`.

- `decoded/res/xml/langfiles.xml`: Swedish ALM database `SVusUN_xt9_ALM3.ldb` has ID `0x0000011D` (decimal **285**); original legacy MLM database carries the same ID; common HDB `database_le.dat` has ID `0x000001FF` (decimal **511**).
- `decoded/res/values/arrays.xml`: `language_Swedish` includes `0x011d`, native name `Svenska`, and English name `Swedish`.
- `MessageAPI.LANGUAGE_LIST = "43"` is a **String**. `Response.parameters` is `HashMap<String,Object>`. **Do not replace the String key with Integer(43)**. PR #4 was corrected after this exact-source check.
- `LanguageListTransaction.listResponse()` expects `parameters.get("43")` to be a `JSONArray`, and language objects with string keys `11` (language), `20` (version), `51` (URL), `10` (MD5 checksum), `122` (country), `124` (translated name), `146` (nonempty integer list of language IDs), and a matching core-version key (Alpha = `102`).
- `LanguageDownloadTransaction.downloadLanguagePack()` uses `thirdPartyURL` and HTTP GET without a GitHub token, then verifies MD5. A private/draft release file is **not accessible** through this ordinary unauthenticated download flow.
- `SwypeCoreLibrary.getCoreVersions()` is native. The **exact matching Alpha core version string remains unverified**, so it must not be guessed from language-ID, language list, or unrelated package version.
- Core version supplied to the ACManager must have a `major.minor` numeric pattern (e.g. `digit.digit`); this pattern is not evidence of the actual Swype version.

## Verified from the locally provided FIX47C and Swedish ZIP, not from public GitHub

- FIX47C assets have `Swedish.mdf`, `SVusUN_xt9_ALM3.ldb.mp3`, and `database_le.dat.mp3`.
- The user-provided Swedish candidate ZIP contains those three files, each at the ZIP root. Archive CRC passes; the `.mp3` database entries successfully decompress as GZIP.
- The candidate ZIP's MD5 is **25cf5ca3031255362c2cc567fd59faf6** and SHA-256 is **74ba6cb3efa803be7a11886cdf4a8ae5e6cb59bf363ae1fbc8efe8b28c410f9b**. **Checksums apply only to this exact ZIP byte sequence**; rebuilding the ZIP changes them.
- FIX47C already contains Swedish locally. To prove *download via original menu*, a safe test APK should start **without Swedish preinstalled**. Keep the user's current working Swype intact.

## Remaining work before a download-test APK can be called ready

1. Confirm the target APK has the same Swedish ID mapping and determine its exact Alpha engine core version string, ideally from the running `SwypeCoreLibrary`/build initialization, rather than guessing.
2. Confirm the package VERSION value accepted by this target and the original language installation transaction, including any server-side compatibility checks.
3. Obtain authorization for distribution and provide a publicly reachable, direct HTTPS language ZIP URL on GitHub (not a draft-release asset). Do **not** embed a GitHub API token in a public APK.
4. Generate `nuance-language-list.json` using the existing `generate_swedish_catalog.py` with exact verified values, URL, and the MD5 of the byte-identical hosted ZIP. Run `validate_nuance_catalog.py`.
5. Patch only the list-fetch bridge in the chosen signed APK, verify the real smali callback and Response shape, and preserve the original install/remove workflow.
6. Build/sign with the user's private keystore **outside GitHub**, compare package name/certificate against the intended update target, then test download/activate/type/remove/re-download on Android.
7. Protect the working APK and app data. Do not uninstall it to test an unverified candidate.

## Scope

Swedish only. No changes to themes, GIF, emoji, or Dragon. No language binaries were committed to the public repository by this audit.
