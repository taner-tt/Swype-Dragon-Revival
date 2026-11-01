# Swype Dragon Revival — Project Handover

Last updated: 2026-11-01

## Purpose
Persistent recovery/handover document for the Swype revival project. The previous ChatGPT project conversation reached its maximum length. This file is the durable project memory and must be updated from direct evidence.

Guiding rule: preserve and port Nuance/Swype's real implementation wherever possible rather than inventing a replacement architecture.

## Known baseline and regression rules
The recovered conversation identifies FIX40 as the safe working baseline. Dragon, languages, Shift behavior, and previous Settings fixes were reported working there and must not be disturbed by theme work.

FIX48 and FIX48B were failed/abandoned theme experiments, not baselines. FIX48B failed with `FIX48B: could not locate the top-level Settings XML by its original Themes entry`. Do not resume by making another guessed Settings XML patch merely to get a build through.

## Theme objective
Restore Swype's downloadable themes using the replacement GitHub distribution backend while retaining Swype's genuine theme/resource mechanism.

Desired flow:
`Swype Theme UI -> catalog -> download -> Swype-owned theme storage/registration -> Nuance theme loader -> ThemeManager -> select/apply theme`

Rejected flow:
`Settings -> independent list -> Android normal APK installer -> theme treated as an ordinary installed app`

## GitHub theme infrastructure — VERIFIED
Repository: `taner-tt/Swype-Dragon-Revival`

The repository contains theme distribution/catalog infrastructure, not the full FIX1..FIX48 source history. The `themes-v1` release contains exactly 270 expected theme ZIP assets. `tools/build_theme_catalog.py` generates `themes.json` with `id`, `filename`, `url`, `size`, and `sha256`; the workflow verifies the 270-entry catalog and hashes. The inspected workflow completed successfully. Do not repeatedly debug the GitHub catalog unless new evidence shows a backend failure.

## Historical archive evidence
Recovered old theme data contains 270 theme packages arranged like `files/themes/<theme>/<theme>.apk` and includes `installed_themes.xml` / `shared_prefs/installed_themes.xml` evidence. A real downloaded theme APK was previously reported as generation/version `5.0.1-1624448` with package names like `com.nuance.swype.theme...`.

## FIX48 / FIX48B lesson
FIX48 attacked the problem at the wrong layer by trying to locate/add a Settings theme entry and by considering a separate catalog/install flow. The GitHub/catalog URL structure itself was not the root cause.

## PRIMARY DIRECT APK EVIDENCE — FIX47C
Analyzed artifact: `Swype-ARM64-S25-FIX47C-GIF-BEFORE-SMILEY.apk`.

Direct DEX parsing confirms that FIX47C contains Nuance's external/downloadable-theme architecture. This supersedes the earlier hypothesis that the current lineage lacked the later external loader.

### Confirmed theme/resource classes
- `com.nuance.swype.plugin.ThemeApkInfo`
- `com.nuance.swype.plugin.ThemeApkResourceBroker`
- `com.nuance.swype.plugin.ThemeResourceAccessor`
- `com.nuance.swype.plugin.ThemeLoader`
- `com.nuance.swype.plugin.ThemeMetaData`
- `com.nuance.swype.input.ThemeManager`
- `com.nuance.swype.inapp.CatalogManager`
- `com.nuance.connect.api.CatalogService`
- `com.nuance.connect.internal.CategoryServiceInternal`

### Confirmed method-level inventory from DEX class data
`ThemeApkInfo` contains `fromStaticApkFile` and `readThemeMetaDataFromFile`.

`ThemeApkResourceBroker` contains `setThemeFromApk`.

`ThemeLoader` contains `loadThemeApkFile`, `applyTheme`, `buildResourceIdMap`, `openRawResourceInThemeApk`, themed color/drawable/text/dimension accessors, and resource mapping logic.

`ThemeManager` contains `scanSideloadedThemes`, `getDownloadedSwypeTheme`, `syncPurchasedOrInstalledList`, `addConnectedThemesToMap`, `getSwypeTheme`, `getSwypeThemes`, category/theme status management, and downloadable-theme enablement logic.

`CatalogManager` contains especially important lifecycle methods:
- `downloadTheme`
- `cancelDownloadTheme`
- `installDownloadedFile$14e1ec69`
- `installPath$7157d249`
- `copyFile`
- `deleteFile`
- `fileExists`
- `updateThemesListFromConnect`
- `uninstallTheme`
- `addWordListFromApk`
- `refreshOfflineCatalogItemsWhenNetworkOff`
- `getCatalogService`
- `getThemesForCategory`

This is strong evidence that the local install/register lifecycle already exists in FIX47C and that the correct patch boundary may be upstream of `installDownloadedFile`, rather than inside ThemeManager/resource loading.

### Confirmed CatalogService contract
The embedded Nuance catalog API exposes catalog items with SKU, title, canonical name, categories, preview URLs, thumbnail URL, price, type, installed/purchased/update flags, plus `downloadCatalogItem`, `installedCatalogItem`, `uninstallCatalogItem`, SKU-list methods and catalog callbacks.

Download callbacks include `downloadStarted`, `downloadPercentage`, `downloadComplete`, `downloadFailed`, and `downloadStopped`.

This provides a concrete model for the data/events the GitHub replacement may need to emulate or bypass.

### Confirmed storage/state strings and endpoints
DEX strings include:
- `installed_themes`
- `/Download//themes/`
- `Theme loaded from APK`
- `Theme is a downloaded theme`
- `Loading downloadable theme`
- `Downloaded theme sku is:`
- `applyThemeFromCurrentThemeApk()`
- `https://api-swype.swypeconnect.com/`
- `https://ccp-swype.swypeconnect.com/`
- `https://lbs-swype.swypeconnect.com/`
- older `https://api.swypeconnect.com/` and `https://lbs.swypeconnect.com/` references

The exact endpoint used by the theme catalog still needs call-level attribution; endpoint presence alone is not enough to assign a specific service.

### Theme UI/resources are also present in FIX47C
The APK contains actual theme UI resources including:
- `res/xml/themespreferences.xml` and density/device variants
- `res/layout/theme_main_page.xml`
- `theme_item.xml`
- `theme_grid_view.xml`
- `theme_bundle_grid_view.xml`
- `theme_category_item.xml`
- preview/download layouts
- theme download/check/update/stop graphics

This means the theme feature is not represented only by dormant class strings; substantial UI/resources are packaged in FIX47C too. The old FIX48B XML-detection failure must therefore be treated as a failure of that patch's lookup assumption, not proof that FIX47C has no theme preference resources.

## Current architecture model
Evidence now supports:

`Nuance CatalogService / Connect catalog`
` -> CatalogManager.downloadTheme()`
` -> download callback`
` -> CatalogManager.installDownloadedFile(...)`
` -> install path / copy / registration`
` -> ThemeApkInfo metadata`
` -> ThemeApkResourceBroker / ThemeLoader`
` -> ThemeManager downloaded theme`
` -> external APK resource lookup`
` -> active keyboard theme`

The exact bytecode call edges still need full disassembly/decompilation, but the method inventory narrows the likely replacement boundary substantially.

## Most promising patch boundary
Do NOT replace ThemeManager or build a new theme engine.

First determine whether GitHub can replace only the dead Nuance catalog/download source while feeding the result into existing `CatalogManager.installDownloadedFile(...)` and the downstream Nuance loader. If yes, that is preferred because it preserves original installation, metadata parsing, registration, APK resource loading, selection, update and uninstall semantics.

A second possible path, if CatalogService is too tightly coupled to dead Connect infrastructure, is to create a minimal adapter that maps `themes.json` entries to the data required immediately before `installDownloadedFile(...)`. This is still preferable to replacing the downstream theme engine.

## Next technical investigation
1. Disassemble/decompile `CatalogManager.downloadTheme`, callback `CatalogManager$4.downloadComplete`, `installDownloadedFile`, and `installPath`.
2. Establish the exact downloaded temporary filename/path and final `files/themes/...` layout.
3. Determine how SKU and installed state are written to `installed_themes`.
4. Trace `ThemeManager.scanSideloadedThemes` and `syncPurchasedOrInstalledList`.
5. Trace `ThemeApkInfo.readThemeMetaDataFromFile` to document required manifest/meta-data keys.
6. Trace `ThemeApkResourceBroker.setThemeFromApk` and `ThemeLoader.loadThemeApkFile` to establish package/resource loading and validation.
7. Attribute the dead Nuance endpoint actually used by the catalog.
8. Compare one historical theme APK against those exact metadata/resource requirements.
9. Only then implement the smallest GitHub bridge.

## Still not proven
- exact final on-disk path construction on current Android
- exact `installed_themes` preference schema
- exact manifest/meta-data fields required in theme APKs
- signature/package/version validation rules
- exact network endpoint/service responsible for catalog data
- whether existing local loader works unchanged on the target Android version
- whether GitHub ZIPs already contain exactly the payload expected by `installDownloadedFile`

## Safety rules
1. Preserve known-good Dragon/language/Shift/Settings behavior.
2. Treat FIX48/FIX48B as discarded experiments.
3. Do not use Android's normal APK installer unless Nuance bytecode proves it belongs in the flow.
4. Do not rewrite the theme engine while the genuine Nuance loader exists.
5. Do not modify GitHub catalog infrastructure without evidence it is the failing layer.
6. Prefer direct APK/source/build evidence over recollection.
7. Mark hypotheses as hypotheses.
8. Update this file after every major verified finding.

## Conversation continuity
The user wants to avoid another project loss caused by a ChatGPT conversation reaching its maximum length. ChatGPT does not expose an exact reliable percentage of remaining conversation context to the assistant, so an exact automatic 10%-remaining alert cannot be guaranteed. Mitigation: keep this handover current throughout the work rather than waiting for the end.

## Continuation instruction
Read this file before changing code. Continue from the FIX47C `CatalogManager -> installDownloadedFile -> ThemeApkInfo/ThemeLoader -> ThemeManager` investigation, not from the abandoned FIX48 Settings-XML strategy. If full old-chat history becomes available, merge confirmed FIX chronology and resolve contradictions in favor of direct artifact evidence.