# GitHub language bridge hardening: 2026-11-07

Scope: Swype language catalog transport only. **No final APK was built or device-tested.**

## Root cause in original Swype

Original `CommandQueue.processTransaction()` obtains `getNextCommand()`; if null, it removes the transaction and calls `onEndProcessing()`. Earlier `GitHubLanguageCatalog` launched a thread from the `LanguageListTransaction` constructor without putting a command into `currentCommand`, while `requestLanguagesList()` still submitted the transaction to Nuance's queue. This could cause the original queue to finish the transaction before the GitHub network fetch completed. It was an architecture bug, not a server-hostname typo.

## Hardening applied

- Patch `LanguageManager.requestLanguagesList()` only to avoid submitting this **list-only** transaction to Nuance's queue. Its constructor starts the GitHub worker instead; the worker now explicitly invokes the original `listResponse()` and `onEndProcessing()`. The rest of Swype's language download/install/remove transactions remain untouched.
- Keep `MessageAPI.LANGUAGE_LIST` as the original **String** key `"43"`, verified against actual decompiled Java/smali.
- Use 10 s connect and read timeouts and reject catalog bodies larger than 1 MiB.
- On malformed JSON, empty list or network exception, send a response with status=1 but **without** key `"43"`; the original `listResponse()` will acknowledge/notify without overwriting cached download-list state. This is a compatibility fallback, not a genuine successful remote refresh; the UI may still show cached data.
- Serialize remote language catalog fetches with an `AtomicBoolean` and release the guard on success/failure. Duplicate requests receive a non-destructive acknowledgement.

## Automated verification

The GitHub Actions run `42318456930` succeeded: synthetic smali fixtures, regression assertions and a standalone assembler test for `GitHubLanguageCatalog.smali`. This is stronger than text checks but **does not** resolve references against FIX47C's real classes or prove installability.

An earlier CI attempt could not download a draft GitHub release APK using the default Actions token (HTTP 403). This is an access-control issue, **not evidence of either successful or failed APK assembly**. The corrected CI test does not fetch, publish, or require private APKs, language binaries or signing secrets.

## Remaining release blockers

1. Runtime validation against the **exact target APK** with complete smali class signature matching and APK build/signature checks.
2. Functional tests of on-device startup, menu loading, refresh, offline/timeout, malformed JSON, and repeated requests. The fallback currently does not expose a distinct user-facing error; consider UX/logging after runtime tests.
3. Swedish package `102` Alpha-core version and `20` package version must be verified, not inferred from the native XT9 version string.
4. Authorized GitHub-hosted **publicly readable** direct HTTPS Swedish ZIP and matching MD5. Draft release URLs cannot be fetched by unauthenticated Swype.
5. Test Swedish download, activation, prediction, uninstall, and re-download without risking the functioning installed app.

No theme/GIF/emoji files changed. Do not merge the experimental branch as a production-ready language server.


## 2026-11-07: full catalog preflight before Swype metadata commit

The bridge now validates every catalog entry before calling original `listResponse()`: nonempty language/version/country/display name, a 32-hex MD5, a GitHub HTTPS URL, a numeric major.minor core version, and nonempty positive language IDs. An invalid list triggers the non-destructive fallback rather than letting Swype partially register entries before a later malformed object. This is relevant because the original `listResponse()` catches per-entry JSONException and still commits metadata.

**CI:** https://github.com/taner-tt/Swype-Dragon-Revival/actions/runs/42319827942 — smali regression and actual preserved Swype APK assembly both passed. No APK was published or device-tested. The correct Swedish server Alpha core/package version still needs verification, and public hosting is gated by distribution rights.
