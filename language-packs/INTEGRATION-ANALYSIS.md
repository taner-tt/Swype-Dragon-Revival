# Swype language transport: verified APK analysis (2026-11-05)

Source: successful GitHub Actions run 42079023597, decompiled `Swype-English-Only-REKEYED.apk`. This report records observed code behavior, not a tested replacement APK.

## Confirmed original flow

- `com.nuance.connect.service.manager.LanguageManager.LanguageListTransaction.getList()` calls `LanguageManager.createCommand("list", CRITICAL, {all:true})`. This is **not** an HTTP GET of a standalone JSON catalog.
- `listResponse(Response)` reads a `LANGUAGE_LIST` array from a parsed Nuance `Response.parameters` object. Each language entry requires at least `LANGUAGE`, `VERSION`, `URL`, `CHECKSUM`, `COUNTRY`, `NAME_TRANSLATED`, nonempty integer `LANGUAGE_IDS`, and one of the core-version fields (`CORE_VERSION_ALPHA`, Chinese, Japanese or Korean).
- `LanguageDownloadTransaction` obtains `URL` from those properties, downloads the pack and validates `CHECKSUM`.
- `ACBuildConfig` delegates server URLs to `ACBuildConfigRuntime.URL`; server communications go through the Nuance command/response client.

## Consequence

Replacing the legacy server hostname with `raw.githubusercontent.com` **alone is not sufficient**: GitHub serves static files and does not implement Nuance's command transport or `Response` framing. The existing `language-packs/languages.json` is also missing mandatory language metadata and does not match the original `LANGUAGE_LIST` schema.

## Minimal integration direction

1. Keep original Swype Languages screen, install/uninstall logic, package validation and language registration.
2. Intercept **only** the `LanguageListTransaction.getList()` fetch/response bridge and provide a GitHub-hosted catalog transformed into the original response's expected language properties. Avoid redirecting all Nuance services.
3. Keep `LanguageDownloadTransaction` as-is where possible by providing a direct downloadable package URL and the **MD5** checksum that `EncryptUtils.md5(response.file)` checks (not SHA-256).
4. Confirm the installer accepts the candidate language ZIP structure; test on device before listing the language as available.
5. Keep English built in; do not publish proprietary Nuance language packs or signing secrets to the public repository without appropriate rights.

## Verified download behavior

`LanguageDownloadTransaction.downloadLanguagePack()` already uses `this.currentCommand.thirdPartyURL = this.url`, `method = "GET"`, and `hasBody = false`. Consequently, **the package URL can point directly to GitHub without replacing the download implementation**. The remaining bridge is the language-list transaction: it currently creates a Nuance `"list"` command and expects a `Response` with `LANGUAGE_LIST` as a JSON array. The existing GitHub `languages.json` is not yet consumable by this transaction.

A later inspection of the locally supplied `Swype-Swedish-Install-Candidate-UNTESTED.zip` confirms **three** entries: `Swedish.mdf`, `SVusUN_xt9_ALM3.ldb.mp3`, and `database_le.dat.mp3`. Both `.mp3` entries are GZIP-compressed and successfully decompress to their expected filenames. This corrects the earlier claim that `database_le.dat` was missing. `LanguageInstall.extractFiles()` explicitly decompresses `.mp3` entries, and `LanguageInstall.createMetadataFile()` writes installation metadata. These are offline format checks only: Android language registration, language ID/core compatibility, UI visibility, and actual Swedish prediction are NOT verified. Do not publish proprietary language binaries without distribution rights.

## Status

Inspection succeeded; no APK was patched, signed or device-tested by this report. Next analysis targets: `LanguageDownloadTransaction` checksum implementation, `LanguageInstall` package layout and catalog injection points.
