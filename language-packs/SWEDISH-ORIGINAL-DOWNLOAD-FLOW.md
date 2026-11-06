# Swedish original download flow — source-based audit (2026-11-07)

Only the language architecture is in scope. Do not edit theme, GIF or emoji code.

## Audited source
Original Java decompilation preserved as the GitHub Actions `swype-inspection` artifact from run `42079023597`, produced from `Swype-English-Only-REKEYED.apk`. The newly added `audit_original_download_flow.py` runs **14 explicit source checks** against that artifact ZIP; all 14 passed locally. These are static checks, NOT a runnable APK verification. The user-supplied FIX47C APK still needs direct bytecode comparison for each assumed callback signature.

## Confirmed original execution chain

1. `LanguageManager.LanguageListTransaction.getList()` creates the original `list` command and a response callback.
2. On successful response, `listResponse()` reads `Response.parameters.get(MessageAPI.LANGUAGE_LIST)`. `MessageAPI.LANGUAGE_LIST` is the string `"43"`.
3. The parsed language list is committed through `languageInstallMetadata`. The original transaction also invokes `taskCompletedAcknowledgement(taskAcknowledgement)`; `onEndProcessing()` calls `finishTransaction(getName())`, `managerStartComplete()`, and `notifyLanguageListeners()`.
4. `SDKDownloadManager.InstallTask.doInBackground()` calls `new LanguageInstall(...).install(downloadPath)`.
5. On reported success, `InstallTask.onPostExecute()` calls `LanguageList.addDownloadedLanguage(langName)`, `DatabaseConfig.updateLanguage(...)`, `IMEApplication.refreshInputMethods()`, `onUpdateLanguage()`, `onPostInstallLanguage()`, and finally a language-install-completed callback.
6. `LanguageInstall.installALM()` is a different route that refreshes the database directly. Do not substitute it for the original `SDKDownloadManager` path without source proof.

## Critical patch correctness risks (not yet solved)

- The experimental GitHub list patch replaces `getList()` with a separately spawned thread and manually invokes `listResponse()`. The original full transaction lifecycle (including acknowledgment and `onEndProcessing()`) has **not** been demonstrated to run correctly when invoked this way. An apparent populated catalog is not proof of a responsive Languages menu.
- If GitHub fails or sends an empty list, the current injected Runnable merely logs or returns; the original error/transaction-completion behavior is not reproduced. A pending spinner or repeated failed retrieval is possible.
- `LanguageInstall.install()` returns `true` after `installPack()`; within `installPack()`, failed extraction/move can skip metadata creation without necessarily throwing. The original SDK then registers the language only according to its own subsequent checks. We should verify expected database files actually exist, not just trust a successful ZIP download.
- Swype's Alpha core version comes from runtime build settings. Source shows it reaches `setCoreVersionAlpha(coreVersions.get(1))`, while `ACManager.setCoreVersions()` requires `major.minor`. The native text `XT9 V11.03.07.00` does **not**, by itself, prove that catalog field `102` should be `11.03`; do not guess.
- `Swedish` (local ALM database ID `0x011D = 285`) is already embedded in FIX47C. A true download test needs a test configuration where Swedish is not already preinstalled, without deleting the user's functioning installation.

## Release gates
- Verify exact server Alpha core version and package VERSION for the candidate APK.
- Test the complete callback/transaction lifecycle for the GitHub list; ensure non-200, malformed, timeout and empty catalog have a finite, recoverable completion path.
- Make one authorized GitHub-hosted Swedish ZIP accessible by unauthenticated HTTPS; do not publish proprietary binaries without distribution authorization or embed access tokens.
- Verify the exact hosted ZIP MD5 and the catalog schema before building.
- Build and sign with owner's matching private key *without committing it*; protect user's installed version.
- On a safe test install, verify language list, download, installation, activation, Swedish prediction, removal and re-download, including failure recovery.

No APK has been built or runtime-tested by this audit.
