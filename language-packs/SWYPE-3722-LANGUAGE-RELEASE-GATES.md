# Swype 3722: language-only candidate release gates — 2026-11-09

## Target APK

User-supplied **`Swype-3722-KLIPY-GIF-POPUP-FIX-SIGNED-TEST(1).apk`** is the new reference. Baseline SHA-256:

`1b9a279f8a4fd859ed369c5f1290a2da34203d8ff02f952c98c37d170434d69d`

This file is local/private and must **not** be published or transferred to a GitHub release merely to facilitate compilation.

## Checks actually performed on the new APK

- ZIP CRC passed; English LDB and common database exist; no Swedish MDF/LDB embedded. This allows a meaningful future remote Swedish install test.
- One main `classes.dex` and a **second `classes2.dex` containing KLIPY code**. Keep KLIPY DEX byte-for-byte identical for a language-only integration. The reference secondary-DEX SHA-256 is:
  `925df618a0ae834e74b71404e755deb6ee294685c883091d09757adaa121c111`.
- Original DEX method names and **exact method descriptors** were inspected directly from this uploaded APK and matched the intended bridge's entrypoints: `requestLanguagesList(String):void`, `finishTransaction(String):void`, `LanguageListTransaction.getList():void`, `onEndProcessing():void`, `getName():String`, `AbstractCommandManager.startTransaction(Transaction):void`, `isTransactionActive(String):boolean`, `ConnectClient.getString(ConfigProperty):String`, `GenericProperty.BooleanProperty.setValue(Boolean,Property.Source):void`, and `Transaction.getName():String`. All present.
- The new baseline is **NOT yet patched**: neither DEX contains `GitHubLanguageCatalog`.
- Four local verification regression tests passed against the real APK: exact reference contract, explicit rejection of unpatched APK as candidate, detection of mutated shared database, and detection of mutated secondary DEX.

## Fail-closed comparison required before a user-installable language APK

Given an actual patched candidate built from this exact reference, compare:

1. `classes2.dex` SHA-256 unchanged (to preserve KLIPY integration).
2. Every original `assets/*` and `lib/*` byte-for-byte unchanged, unless a specific language-only exception is explicitly documented.
3. All necessary DEX method descriptors remain present.
4. The **new** main DEX has the `GitHubLanguageCatalog` implementation.
5. ZIP CRC succeeds.
6. Verify signing certificate on the final signed APK with `apksigner`/Android signing tooling; do not infer identical signing ability from a keystore filename alone.
7. Install into a disposable/safe test setup and verify menu refresh, offline/failure completion, download, activation, typing, removal/reinstall.

The local audit script and four-test harness in the conversation were executed and available for download; they have **not** been added to this repository because they import one another from the conversation's local files.

## Actual remaining blockers

- There is no apktool/aapt/smali Android build toolchain available in the **current local container**. Earlier GitHub Actions builds used an **older** preserved English-only APK and do not count as a successful Swype 3722 build.
- The new user-provided APK is not in an authenticated GitHub Actions artifact or release that CI can access; do not publish proprietary or user-private APKs just to remove that blocker.
- Swedish server field `102` (actual runtime configured Alpha-core version) and field `20` (authentic pack version) are not established.
- GitHub draft-release Swedish ZIP is not anonymously readable; do not assume it works as a download source or upload/provision proprietary language data without permission.

**Status: reference compatibility confirmed at DEX method signature level; NO patched/signed Swype 3722 APK, device test, or successful network download yet.**
