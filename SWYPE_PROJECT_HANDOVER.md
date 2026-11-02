# Swype Dragon Revival — Project Handover

Last updated: 2026-11-02

## Purpose
Durable recovery/handover document for the Swype revival project. Preserve Nuance/Swype's real implementation wherever possible and replace dead server boundaries rather than inventing parallel theme/language systems.

## Non-negotiable working rule
Study original architecture first. Compare alternatives and prefer the smallest robust solution closest to original Swype. Do not churn builds or apply symptom fixes. Compile success is not runtime success; a build becomes a working baseline only after device confirmation.

## Stable behavior that must not regress
Known working lineage preserves keyboard typing, Swedish default, Dragon, Shift and Settings. FIX49L was a recovery baseline. Theme work must not disturb these functions.

## Theme objective
Replace Nuance's dead theme distribution backend with GitHub while retaining Swype's genuine downstream theme engine.

Target architecture:
`Swype -> GitHub catalog/download -> extracted theme APK -> original Swype private theme storage -> ThemeLoader -> ThemeApkInfo -> ThemeApkResourceBroker -> keyboard`

Do not use Android's normal APK installer.

## Original Nuance architecture — VERIFIED FROM FIX47C
Analyzed original artifact: `Swype-ARM64-S25-FIX47C-GIF-BEFORE-SMILEY.apk`.

Verified classes include `ThemeApkInfo`, `ThemeApkResourceBroker`, `ThemeResourceAccessor`, `ThemeLoader`, `ThemeMetaData`, `ThemeManager`, `CatalogManager`, `CatalogService` and `CategoryServiceInternal`.

Verified normal downstream flow:
`CatalogManager.downloadTheme()` -> `ACCatalogService.downloadCatalogItem()` -> callback receives temporary file -> `installDownloadedFile(sku,tempPath)` -> copy to `<filesDir>/themes/<sku>/<sku>.apk` -> `installed_themes[sku]=true` -> ThemeManager/UI -> user selection -> `IMEApplication.applyDownloadedTheme(sku)` -> `ThemeLoader.loadThemeApkFile()` -> `ThemeApkInfo.fromStaticApkFile()` -> `theme_metadata.xml` -> `ThemeApkResourceBroker.setThemeFromApk()` -> DexClassLoader/resources -> active keyboard theme.

`installed_themes` is an Android SharedPreferences boolean set keyed by SKU. `scanSideloadedThemes` under external `/Download//themes/` is a separate path and must not be confused with normal private theme storage.

## GitHub backend — VERIFIED
Repository: `taner-tt/Swype-Dragon-Revival`.

Release `themes-v1` contains 270 theme ZIP assets. Current `themes.json` is schema 2 with count 270 and per-theme `id`, human-readable `name`, `filename`, download `url`, preview URL, size and SHA-256. Generated preview images live under `theme-previews/`.

A verified example is `btm.theme.garfield_bestfriends.zip`, SHA-256 `ab60bf9d7c6a74f2117640ef4d761ea37fc0c824ef5727f4cfc1eb1dcc89d329`. It contains a real theme APK with package `com.nuance.swype.theme.garfield_bestfriends`, `theme_metadata.xml`, generated R classes and `SwypeThemeTemplate` resources.

## FIX49–FIX50 findings
FIX49O/Q established a working GitHub-backed FÅ TEMA surface. FIX49T proved ZIP download/extract/install could reach Swype's private theme install path. FIX49U crashed because incomplete synthetic `ConnectDownloadableThemeWrapper` objects violated original invariants. FIX49V introduced safer custom theme objects.

FIX49W added a direct-apply bypass for `GitHubSwypeTheme` because the original preview click path crashed on the custom object. This made downloaded themes activate immediately on tap. It was useful diagnostically but not acceptable final UX.

FIX49X scraped GitHub release HTML and only exposed 99 links; this was rejected. Catalog data must come from `themes.json`, not release-page DOM.

FIX50D deletion is runtime-confirmed: downloaded theme removal updates MINA TEMAN immediately.

FIX50E–H attempted local image extraction/display hacks and failed. Do not return to those symptom fixes.

## FIX51 backend/catalog work
GitHub catalog generation was upgraded to schema 2 and generated preview images. This produced real theme images rather than placeholder cards.

FIX51A incorrectly navigated the WebView directly to `themes.json`, causing raw JSON to be displayed. Rejected.

FIX51B changed FÅ TEMA to an internal HTML catalog that fetches `themes.json`. Installed GitHub themes subsequently showed real preview imagery in MINA TEMAN.

## FIX51C — RUNTIME CONFIRMED
FIX51C is the current runtime-confirmed theme baseline.

User-confirmed behavior:
`FÅ TEMA -> download -> MINA TEMAN -> tap downloaded theme -> preview dialog -> AVBRYT / TILLÄMPA -> theme changes only after TILLÄMPA`.

This fixes the unwanted FIX49W behavior where tapping a downloaded theme immediately activated it. Preserve this preview/apply behavior.

Artifact SHA-256: `46276788f46a6585da5d97403cdf0183e3cd73345ea1c7e8bf91bbea73ce753b`.

## FIX51D — BUILT, NOT YET RUNTIME CONFIRMED
FIX51D is a catalog quality pass built from FIX51C; do not call it stable until device-tested.

Changes:
- adds a small JavaScript bridge used only by the GitHub catalog to query Swype's real local installed state;
- installed state requires both `installed_themes[sku]=true` and the expected private theme APK to exist;
- FÅ TEMA marks already installed cards `INSTALLERAD`;
- tapping an installed catalog card does not redownload it;
- `GitHubThemeInstaller` independently checks installed state before opening the network connection, so duplicate downloads are prevented even if UI interception is bypassed;
- catalog remains driven by all entries returned by schema-2 `themes.json` and continues using its name/preview/download URL fields;
- FIX51C preview/apply and existing downstream install/theme engine are otherwise left intact.

FIX51D artifact SHA-256: `5911a07f528a4cbb6b39858f0e9cd2938265741980113bdbd8016b574d5deb89`.
Permanent signing certificate SHA-256: `5D:B9:3A:51:FF:5F:85:9D:C5:FA:9F:B7:9D:00:02:92:39:1F:9F:16:A3:D1:49:6E:DA:F0:0C:AE:30:4F:64:6F`.

## Current custom compatibility layer
`GitHubSwypeTheme` still exists and reports EMBEDDED to avoid unsafe legacy CONNECT casts. This is an architectural compromise. Do not remove it casually while FIX51C behavior depends on it. Long-term, the preferred endpoint is an original-compatible catalog object model, but only after exact `ThemeItemSeed` / `ConnectDownloadableThemeWrapper` invariants are understood. Previous synthetic objects crashed.

## Next test / next investigation
First runtime-test FIX51D:
1. Open FÅ TEMA and verify the catalog reports 270 themes and displays names/images.
2. Verify an already installed theme is visibly marked `INSTALLERAD`.
3. Verify tapping that installed card does not download/install it again.
4. Download one not-installed theme and verify it appears in MINA TEMAN.
5. Tap it and verify FIX51C behavior remains: preview first; AVBRYT leaves current theme unchanged; TILLÄMPA activates it.
6. Verify deletion still updates MINA TEMAN immediately.

Only after that should the next architectural cleanup be considered.

## Safety / continuity
Never create a new signing key. Never commit the private signing key or its password. Verify APK existence, successful build, signature and SHA-256 before handing it over. Preserve runtime-confirmed behavior and update this handover after major verified findings.