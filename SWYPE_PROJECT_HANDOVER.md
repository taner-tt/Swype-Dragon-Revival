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

### Exact install flow — VERIFIED FROM BYTECODE
Method-level DEX disassembly now establishes the downstream install path precisely.

`CatalogManager.downloadTheme(index, wrapper)` obtains the theme SKU and calls:

`ACCatalogService.downloadCatalogItem(sku, new CatalogManager$4(...))`

The success callback is:

`CatalogManager$4.downloadComplete(File downloadedFile)`

On success it calls:

`CatalogManager.installDownloadedFile(sku, downloadedFile.getAbsolutePath())`

`installDownloadedFile(sku, downloadedPath)` then:
1. calls `installPath(sku)` to calculate the destination;
2. deletes an existing destination file if present;
3. creates a `File` for the downloaded temporary file;
4. creates a `File` for the destination;
5. copies bytes with `copyFile(source, destination)`.

`installPath(sku)` delegates to `IMEApplication.getNewThemeApkPath(sku)` and creates the parent directories when missing.

`IMEApplication.getNewThemeApkPath(sku)` is now fully resolved. It constructs:

`<Context.getFilesDir()>/themes/<sku>/<sku>.apk`

This exactly matches the historical archive layout `files/themes/<theme>/<theme>.apk`. This is no longer a hypothesis.

### Exact installed_themes schema — VERIFIED
`InstalledList(Context)` opens Android SharedPreferences named exactly:

`installed_themes`

`InstalledList.loadAll()` simply loads all entries from that preference file into its map.

After a successful theme download/install, `CatalogManager$4.downloadComplete()` obtains the installed `ThemeItemSeed.sku` and writes:

`installed_themes[sku] = true`

using `SharedPreferences.Editor.putBoolean(sku, true)`, then reloads `InstalledList` and updates theme status to `THEME_INSTALLED`.

Therefore the historical `shared_prefs/installed_themes.xml` is directly explained: it is a boolean set keyed by theme SKU.

### Post-install handling — VERIFIED
After successful copy, the callback also calls `addWordListFromApk(...)` using the installed APK path, handles theme categories, sets installing percentage to 100, marks the `ThemeItemSeed` installed/not installing, updates `ThemeManager` status, notifies UI callbacks, and records completion telemetry.

This confirms that the ordinary success path does not use Android's package installer. The APK is copied into Swype private app storage and registered in Swype state.

### Theme selection/activation — VERIFIED
The theme UI methods `Themes.applyTheme(...)` and `ThemesCategory.applyTheme(...)` distinguish downloaded themes by `SwypeTheme.THEME_SOURCE.CONNECT`.

For a downloaded theme they:
1. call `UserPreferences.setActiveDownloadedTheme(sku)`;
2. resolve `IMEApplication.getThemeApkPath(sku)`;
3. store that APK path as `UserPreferences.setCurrentThemeId(path)`;
4. notify `ThemeManager.onThemeChanged(...)` / themed-resource refresh logic.

`IMEApplication.checkIfThemeLoaded()` reads `UserPreferences.getActiveDownloadedTheme()` and calls `applyDownloadedTheme(sku)`.

`IMEApplication.applyDownloadedTheme(sku)`:
1. initializes `ThemeLoader` if needed;
2. resolves `getThemeApkPath(sku)`;
3. calls `ThemeLoader.loadThemeApkFile(themedContext, apkPath)`;
4. logs `Theme loaded from APK`.

`IMEApplication.checkThemeChanged()` also directly reloads an APK through `ThemeLoader.loadThemeApkFile(...)` when the current theme points at an APK path.

This proves that download/install and apply are separate phases: successful download copies/registers the APK; selecting/current-theme lifecycle loads it.

### Theme APK loading — VERIFIED
`ThemeLoader.loadThemeApkFile(context, path)` calls `ThemeApkInfo.fromStaticApkFile(context, path)`, then hands the resulting object to `ThemeApkResourceBroker.setThemeFromApk(...)`.

`ThemeApkInfo.fromStaticApkFile(...)`:
- requires an existing path ending in `.apk`;
- calls Android `PackageManager.getPackageArchiveInfo(path, ...)`;
- obtains `Resources` for the archive application;
- sets up a private `dex` directory;
- records APK/package/resource information;
- calls `readThemeMetaDataFromFile(resources, packageName)`.

`readThemeMetaDataFromFile(...)` resolves resource `theme_metadata` of type `xml` inside the theme APK and constructs `ThemeMetaData` from it.

`ThemeMetaData` parses theme metadata including fields/tags such as `id`, `name`, `description`, `snapshot`, `version`, `date`, `author`, and optional `wordlist` entries with `type`, `version`, and `file` attributes.

`ThemeApkResourceBroker.setThemeFromApk(...)` uses a `DexClassLoader`, loads the theme package's generated `.R$styleable` class, accesses `SwypeThemeTemplate`, resolves theme styles/resources and builds a `ThemeResourceAccessor`. This is genuine dynamic external-APK resource loading, not normal Android package installation.

### Sideload path — VERIFIED
`ThemeManager.scanSideloadedThemes(...)` separately scans external storage under:

`<external-storage>/Download//themes/`

when storage permission/state allows it. This is a separate sideload discovery path and must not be confused with the normal Connect download destination in private `files/themes/...` storage.

### Confirmed CatalogService contract
The embedded Nuance catalog API exposes catalog items with SKU, title, canonical name, categories, preview URLs, thumbnail URL, price, type, installed/purchased/update flags, plus `downloadCatalogItem`, `installedCatalogItem`, `uninstallCatalogItem`, SKU-list methods and catalog callbacks.

Download callbacks include `downloadStarted`, `downloadPercentage`, `downloadComplete`, `downloadFailed`, and `downloadStopped`.

### Confirmed storage/state strings and endpoints
DEX strings include `installed_themes`, `/Download//themes/`, `Theme loaded from APK`, `Theme is a downloaded theme`, `Loading downloadable theme`, `Downloaded theme sku is:`, `applyThemeFromCurrentThemeApk()`, and old Swype Connect endpoints including `api-swype.swypeconnect.com`, `ccp-swype.swypeconnect.com`, and `lbs-swype.swypeconnect.com` variants.

The exact endpoint used by the theme catalog still needs call-level attribution; endpoint presence alone is not enough to assign a specific service.

### Theme UI/resources are present in FIX47C
The APK contains actual theme UI resources including `res/xml/themespreferences.xml`, `theme_main_page.xml`, `theme_item.xml`, `theme_grid_view.xml`, `theme_bundle_grid_view.xml`, `theme_category_item.xml`, preview/download layouts and theme download/check/update/stop graphics.

The old FIX48B XML-detection failure was therefore a failure of that patch's lookup assumption, not proof that FIX47C lacks theme resources.

## Current architecture model — NOW METHOD-VERIFIED DOWNSTREAM
The normal Nuance flow is now established as:

`CatalogService catalog item / SKU`
` -> CatalogManager.downloadTheme()`
` -> ACCatalogService.downloadCatalogItem(sku, callback)`
` -> callback receives temporary File`
` -> installDownloadedFile(sku, tempPath)`
` -> copy to <filesDir>/themes/<sku>/<sku>.apk`
` -> installed_themes[sku] = true`
` -> ThemeManager/UI status = THEME_INSTALLED`
` -> user selects theme`
` -> activeDownloadedTheme = sku`
` -> currentThemeId = installed APK path`
` -> IMEApplication / ThemeLoader.loadThemeApkFile()`
` -> ThemeApkInfo.fromStaticApkFile()`
` -> theme_metadata XML`
` -> ThemeApkResourceBroker.setThemeFromApk()`
` -> DexClassLoader + theme R.styleable / resources`
` -> ThemeResourceAccessor`
` -> active keyboard theme`

## Most promising patch boundary
The safest boundary is now even clearer: preserve everything from `installDownloadedFile(sku, downloadedPath)` downstream if possible.

A GitHub replacement only needs to supply a valid downloaded theme APK plus its correct SKU to the existing local install path, and supply enough catalog/UI data for the user to choose/download it. The existing Nuance code already knows how to copy, register, list, select and dynamically load the APK.

The preferred implementation target is therefore a small adapter at or immediately upstream of `CatalogManager.downloadTheme()` / `ACCatalogService.downloadCatalogItem()`, not a replacement ThemeManager or theme engine.

Important: GitHub currently publishes ZIP assets. Before patching, verify the ZIP payload structure. If each ZIP contains the expected `<sku>.apk`, the bridge must download/extract that APK and then feed the extracted APK path plus SKU into the existing install path. Do not pass the ZIP itself to `installDownloadedFile` unless artifact inspection proves the existing code expects ZIP (current bytecode strongly indicates the installed destination is an APK).

## Next technical investigation
1. Inspect one actual `themes-v1` ZIP and its contained APK against the now-known SKU/path rules.
2. Verify the theme APK contains `theme_metadata.xml`, generated `R$styleable.SwypeThemeTemplate`, expected package/resource names and any required wordlists.
3. Attribute the exact Nuance catalog endpoint/service and identify how much of CatalogService initialization is dead.
4. Map the minimum fields needed to construct/display a `ThemeItemSeed` / `ConnectDownloadableThemeWrapper` from GitHub `themes.json`.
5. Decide whether to patch `downloadTheme()` directly or insert a minimal replacement CatalogService adapter.
6. Only then create the next theme FIX build.

## Still not proven
- exact Nuance endpoint responsible for theme catalog data
- whether existing local loader works unchanged on the target Android version when given a valid historical theme APK
- exact structure of each current GitHub ZIP asset (must inspect one directly)
- whether current `themes.json` has enough UI metadata or needs extension for display/category/preview information
- any signature/package/version compatibility checks beyond those already observed in `ThemeApkInfo`

## Safety rules
1. Preserve known-good Dragon/language/Shift/Settings behavior.
2. Treat FIX48/FIX48B as discarded experiments.
3. Do not use Android's normal package installer; verified Nuance flow copies APKs into private storage.
4. Do not rewrite the theme engine while the genuine Nuance loader exists.
5. Do not modify GitHub catalog infrastructure without evidence it is the failing layer.
6. Prefer direct APK/source/build evidence over recollection.
7. Mark hypotheses as hypotheses.
8. Update this file after every major verified finding.

## Conversation continuity
The user wants to avoid another project loss caused by a ChatGPT conversation reaching its maximum length. ChatGPT does not expose an exact reliable percentage of remaining conversation context to the assistant, so an exact automatic 10%-remaining alert cannot be guaranteed. Mitigation: keep this handover current throughout the work rather than waiting for the end.

## Continuation instruction
Read this file before changing code. Continue from the now-verified FIX47C flow: `CatalogManager.downloadTheme -> downloadComplete -> installDownloadedFile(sku,tempPath) -> files/themes/<sku>/<sku>.apk -> installed_themes[sku]=true -> selection -> ThemeLoader -> ThemeApkInfo -> ThemeApkResourceBroker`. Do not return to the abandoned FIX48 Settings-XML strategy.