# Private Swedish language test (draft-release safe)

## Important: do not use a GitHub draft asset as an unauthenticated Swype download URL

The Swedish candidate ZIP is stored in a **draft release** pending distribution-rights review. A draft asset requires an authenticated GitHub API request; the stock Swype `LanguageDownloadTransaction` performs a plain third-party HTTP GET and does not send the owner's GitHub authentication token. A draft asset URL is therefore **not** a working language download URL in the original Swype Languages UI. Never embed a GitHub token in an APK or expose Nuance language databases in a public repository.

## Viable private test approach

1. Keep the draft release unpublished; do not commit the language ZIP or the signing keystore to this public repository.
2. Use the owner's locally supplied Swedish candidate ZIP as a private build input. Its three entries are `Swedish.mdf`, `SVusUN_xt9_ALM3.ldb.mp3`, and `database_le.dat.mp3`. The two .mp3 files are GZIP streams, as expected by the original `LanguageInstall.extractFiles()`.
3. Implement a **local package** install/registration path in the APK, or bundle the package inside a private APK and route the original language installation logic to that local asset. The existing GitHub language-list patch alone is not sufficient.
4. Verify the installed language's language IDs and core version against the exact APK build, and test Swedish word prediction and swipe typing on Android.
5. Build from `Swype-English-Only-REKEYED(2).apk` and sign with the matching owner-provided keystore **locally**. Never upload signing credentials to a public release.

## Current limitations

No completed local-package registration patch or Android device test is present in the repository. Do not label any existing experimental APK as a working Swedish-language release. An unauthenticated HTTPS download can be enabled later only if a legally distributable Swedish pack is available at a compatible public endpoint.
