# Swype Dragon Revival — Project Handover

Last updated: 2026-11-01

## Purpose

Persistent recovery/handover document for the Swype revival project. The previous ChatGPT project conversation reached its maximum length. This file is the durable project memory and must be updated when new evidence is recovered from chats, APKs, ZIPs, source trees, builds, or tests.

Guiding rule: preserve and port Nuance/Swype's real implementation wherever possible rather than inventing a replacement architecture.

## Known baseline and regression rules

The recovered conversation identifies FIX40 as the safe working baseline. Dragon, languages, Shift behavior, and previous Settings fixes were reported working there and must not be disturbed by theme work.

FIX48 and FIX48B were failed/abandoned theme experiments, not baselines. They stopped before APK build/install and did not change the installed phone app. FIX48B failed with:

`FIX48B: could not locate the top-level Settings XML by its original Themes entry`

Do not resume by making another guessed Settings XML patch merely to get a build through.

## Theme objective

Restore Swype's downloadable themes using the replacement GitHub distribution backend while retaining Swype's genuine theme/resource mechanism.

Desired flow:

`Swype Theme UI -> catalog -> download -> Swype-owned theme storage/registration -> Nuance theme loader -> ThemeManager -> select/apply theme`

Rejected flow:

`Settings -> independent list -> Android normal APK installer -> theme treated as an ordinary installed app`

## GitHub theme infrastructure — VERIFIED

Repository: `taner-tt/Swype-Dragon-Revival`

The repository currently contains theme distribution/catalog infrastructure, not the full FIX1..FIX48 source history. Git history here must therefore not be interpreted as the FIX history.

The `themes-v1` release contains exactly 270 expected theme ZIP assets.

`tools/build_theme_catalog.py` reads the release, paginates assets, selects ZIPs, sorts them, and writes `themes.json` entries containing `id`, `filename`, `url`, `size`, and `sha256`. It fails unless exactly 270 themes are found.

`.github/workflows/build-theme-catalog.yml` verifies 270 entries, validates the release URL prefix and 64-character SHA-256 values, and commits an updated catalog when necessary. The inspected workflow completed successfully.

Conclusion: do not repeatedly debug the GitHub catalog unless new evidence shows a catalog/backend failure.

## Historical archive evidence

Recovered old theme data contains approximately/exactly 270 theme packages arranged like:

`files/themes/<theme>/<theme>.apk`

and includes `installed_themes.xml` / `shared_prefs/installed_themes.xml` evidence.

A real downloaded theme APK was previously reported as generation/version `5.0.1-1624448` with package names like `com.nuance.swype.theme...`.

The working/ported Swype history also contained an older-version identification (`1.8.16.1081600.40345`), which originally led to the hypothesis that the external loader existed only in a later Swype generation.

That hypothesis has now been materially revised by direct inspection of FIX47C; see below.

## FIX48 / FIX48B lesson

FIX48 attacked the problem at the wrong layer by trying to locate/add a Settings theme entry and by considering a separate catalog/install flow. The original code has theme UI concepts including `SettingsLauncher.showThemes()`, `ThemesActivity`, and `ThemesCategoryActivity`. The investigated build also had `enable_in_app_purchasable_themes=false`, which helped explain why the expected Settings resource structure was absent.

The GitHub/catalog URL structure itself was not the root cause. `themes.json` and `themes-v1` were internally consistent.

## NEW DIRECT APK EVIDENCE — FIX47C

Analyzed artifact:

`Swype-ARM64-S25-FIX47C-GIF-BEFORE-SMILEY.apk`

This APK is now a primary evidence source for the theme investigation.

Direct inspection of its `classes.dex` proves that it contains Nuance external/downloadable-theme machinery. The following classes and symbols are present:

- `com.nuance.swype.plugin.ThemeApkInfo`
- `com.nuance.swype.plugin.ThemeApkResourceBroker`
- `com.nuance.swype.plugin.ThemeResourceAccessor`
- `com.nuance.swype.plugin.ThemeLoader`
- `com.nuance.swype.plugin.ThemeMetaData`
- `com.nuance.swype.input.ThemeManager`
- `com.nuance.swype.inapp.CatalogManager`

Relevant method/symbol names present include:

- `loadThemeApkFile`
- `readThemeMetaDataFromFile`
- `getThemeApkPath`
- `getNewThemeApkPath`
- `applyDownloadedTheme`
- `setThemeFromApk`
- `getDrawableFromThemeApk`
- `openRawResourceInThemeApk`
- `obtainTypedValuesFromThemeApk`
- `createPackageContext`
- `getPackageArchiveInfo`
- `downloadTheme`
- `cancelDownloadTheme`
- `applyThemeFromCurrentThemeApk`

Relevant state/storage/string evidence includes:

- `installed_themes`
- `/Download//themes/`
- `/themes/`
- `Theme loaded from APK`
- `Theme is a downloaded theme`
- `Theme is a embedded theme`
- `Loading downloadable theme`
- `Downloaded theme sku is:`
- `returning downloaded theme`
- `purchased or free downloaded themes sku:`
- `Uninstalled theme sku is:`
- `bThemeApkLoaded`
- `themeApkFile`
- `themeApkPath`
- `themeApkInfo`
- `themeApkResourceBroker`

This is a major correction to the earlier working hypothesis. We no longer need to assume that FIX47C lacks the later Nuance external theme loader. At least substantial portions of the genuine loader are demonstrably present in FIX47C.

## Current architectural model from FIX47C evidence

The symbols strongly support this Nuance-owned chain:

`download/catalog SKU`
` -> downloaded theme file/APK`
` -> ThemeApkInfo / metadata parsing`
` -> ThemeApkResourceBroker / ThemeResourceAccessor / ThemeLoader`
` -> ThemeManager`
` -> resource lookup from theme APK`
` -> applyDownloadedTheme / setThemeFromApk`
` -> active keyboard theme`

The exact control flow, storage path construction, validation rules, metadata format, and registration semantics still require method-level decompilation/disassembly before patching.

## Important distinction: what is proven vs not yet proven

PROVEN from FIX47C DEX strings/class descriptors:

- external/downloadable theme classes exist
- APK/resource broker classes exist
- package/archive APIs are referenced
- methods for loading/applying a theme APK exist
- `installed_themes` exists
- downloaded-theme state/SKU handling exists
- theme resource access methods exist

NOT YET PROVEN:

- which exact method owns each full call sequence
- the exact on-disk path expected on current Android
- whether the theme APK must be extracted from the GitHub ZIP first and to what final filename/path
- the exact XML/preferences schema of `installed_themes`
- whether signatures/package names/version metadata are validated
- whether old Nuance server dependencies block the loader before local loading begins
- whether FIX47C's existing loader is already fully functional and only its catalog/download backend is dead
- which minimum patch is required to bridge GitHub `themes.json` to the existing loader

Do not turn inferred architecture into code until these are resolved from actual bytecode/decompiled source and tests.

## Revised next technical step

Do NOT build FIX48C by guessing.

Use FIX47C as the primary client-side reference and map the real Nuance theme pipeline method-by-method, concentrating on:

1. `ThemeManager`
2. `ThemeApkInfo`
3. `ThemeApkResourceBroker`
4. `ThemeResourceAccessor`
5. `ThemeLoader`
6. `ThemeMetaData`
7. `CatalogManager`
8. calls to `createPackageContext` / `getPackageArchiveInfo`
9. `installed_themes` reads/writes
10. theme APK path construction and file movement
11. `downloadTheme` -> install/register -> `applyDownloadedTheme`
12. resource lookup from the external APK
13. signature/package/SKU/version checks
14. deletion/update lifecycle

Then identify the smallest dead-network boundary that can be replaced by the already working GitHub catalog while leaving Nuance's downstream loader intact.

## Preferred patch strategy if evidence confirms the model

The likely safest strategy is NOT to port a new theme engine. It is to retain FIX47C/FIX40-compatible Nuance classes and replace only the unavailable catalog/download source so that a selected GitHub theme is delivered in exactly the file/layout/metadata form expected by the existing loader.

This remains a hypothesis until method-level analysis confirms the entry point and expected file lifecycle.

## Files/evidence still needed when available

- ChatGPT account data export containing the full old Swype conversation
- FIX40 APK and/or decompiled FIX40 tree
- original/base APK used for FIX40
- any retained FIX41..FIX48 source/build scripts/logs
- old `themes.zip`
- old `files.zip`
- if available, a known historical Swype APK from the exact period when the 270 themes worked, for comparison against FIX47C

A later original APK is now useful as a comparison/reference, but FIX47C itself already proves that the external theme architecture exists in the current project lineage.

## Safety rules

1. Preserve the known-good working baseline and working Dragon/language/Shift/Settings behavior.
2. Treat FIX48/FIX48B as discarded experiments.
3. Do not use Android's normal package installer unless Nuance's bytecode proves that is part of the real flow.
4. Do not rewrite the theme engine while the genuine Nuance loader exists in FIX47C.
5. Do not modify GitHub catalog infrastructure without evidence it is the failing layer.
6. Prefer evidence from actual APK/source/build artifacts over recollection from the truncated chat.
7. Mark hypotheses as hypotheses.
8. Update this file after every major verified finding so a future chat can resume safely.

## Conversation continuity

The user specifically wants to avoid another project loss caused by a ChatGPT conversation reaching its maximum length. ChatGPT does not expose an exact reliable percentage of remaining conversation context to the assistant, so an exact automatic 10%-remaining alert cannot be guaranteed. The mitigation is to keep this handover current throughout the work rather than waiting for the end of the chat.

## Continuation instruction for a future assistant

Read this file before changing code. Inspect the actual APK/source artifacts. Continue from the FIX47C external-theme-loader investigation, not from the abandoned FIX48 Settings-XML strategy. If a full ChatGPT export becomes available, merge confirmed historical FIX chronology into this file and resolve contradictions in favor of direct artifact evidence.