# Swype Dragon Revival — Project Handover

Last reconstructed: 2026-11-01

## Purpose of this file

This is the persistent handover / recovery document for the Swype revival project. It exists because the previous ChatGPT project conversation reached its maximum length before a full handover could be generated. This document records everything currently recovered and verified so a future conversation can resume without guessing.

This document MUST be updated as additional history is recovered from the old ChatGPT export or from APK/ZIP/source artifacts.

## Project goal

Revive the old Swype keyboard on modern Android while preserving the original Swype implementation and behavior as far as possible. The guiding rule established during development is to patch/port the original implementation rather than reimplement Swype unnecessarily.

The project includes compatibility work already performed around areas such as Dragon, languages, Shift behavior, Settings, and themes. The exact history of all FIX revisions has not yet been recovered; do not infer missing revisions from this document.

## Known working baseline

The recovered conversation identifies FIX40 as the safe working baseline.

Important rule: preserve the parts already working in FIX40. In particular, the recovered discussion says Dragon, languages, Shift, and previous Settings fixes were working and should not be disturbed by the theme work.

FIX48 and FIX48B are NOT baselines. They were experimental theme-integration attempts and are considered discarded. Both stopped before APK build/installation, so according to the recovered conversation they did not modify the Swype installation on the phone.

## Current theme objective

Restore the old downloadable Swype themes using a replacement distribution backend hosted in this GitHub repository while retaining Swype's real theme handling mechanism.

Desired conceptual flow:

Settings -> original Theme UI -> catalog -> download theme -> Swype internal theme storage/registration -> original theme/resource manager -> select theme

The rejected conceptual flow was:

Settings -> new independent list -> Android package installer -> install theme APK as if it were a normal application

The latter is considered architecturally wrong for these theme resources and potentially problematic on modern Android.

## GitHub theme infrastructure — VERIFIED

Repository: taner-tt/Swype-Dragon-Revival

The current repository does not contain the FIX40/FIX48 Swype source tree or decompiled APK. It currently contains the theme distribution/catalog infrastructure. Therefore Git history in this repository must NOT be treated as the history of FIX1..FIX48.

The repository currently has a `themes-v1` release containing the theme archives.

There are exactly 270 expected theme ZIP assets.

`tools/build_theme_catalog.py`:

- reads the GitHub release tagged `themes-v1`
- paginates through release assets
- selects `.zip` assets
- sorts them by filename
- writes `themes.json`
- records `id`, `filename`, download `url`, `size`, and `sha256`
- fails if the result is not exactly 270 themes

`.github/workflows/build-theme-catalog.yml` verifies:

- `themes.json` count is 270
- there are exactly 270 theme entries
- every download URL starts with the repository's `releases/download/themes-v1/` path
- every SHA-256 value is 64 characters

The latest inspected catalog workflow completed successfully. Therefore the GitHub catalog/distribution layer is currently considered working unless new evidence shows otherwise.

## Recovered theme investigation

FIX48 initially attempted to add/find a Settings entry and integrate a new catalog activity. This led to build-time detection failures such as:

`FIX48B: could not locate the top-level Settings XML by its original Themes entry`

The recovered investigation concluded that this was the wrong level to patch.

Important findings from that investigation:

1. The GitHub/catalog address was not duplicated across multiple relevant FIX48 locations in a way that explained the failure.

2. The `themes.json` -> `themes-v1` links were internally consistent.

3. Attempting to locate/add a Settings XML theme row was based on an incorrect assumption about this Swype build.

4. The original code path includes classes/methods discussed as `SettingsLauncher.showThemes()`, `ThemesActivity`, and `ThemesCategoryActivity`.

5. The investigated Swype build had `enable_in_app_purchasable_themes` set to false, which helped explain why the assumed Settings/theme resources did not have the expected form.

6. The approximately 270 historical themes were found in an old archive in a layout resembling:

`files/themes/<theme>/<theme>.apk`

There was also a `shared_prefs/installed_themes.xml` file.

This is strong evidence that the historical theme packages were managed as Swype-owned downloaded theme resources rather than simply launched through Android's normal APK installer.

7. A recovered investigation of the old code found that `PurchasedList` used the preference file `tme`. Therefore `installed_themes.xml` should NOT automatically be assumed to be identical to the old Google-IAP purchased-theme registry.

## Critical version mismatch

A major finding in the recovered conversation is a version mismatch between the Swype base being ported and the downloaded theme packages.

The decompiled Swype code used for the working project reportedly identifies itself as:

`1.8.16.1081600.40345`

A real downloaded theme APK inspected during the old conversation reportedly identifies with Swype/theme generation:

`5.0.1-1624448`

and package names of the form:

`com.nuance.swype.theme...`

The old theme archive contains approximately 270 such APK-based themes.

The recovered investigation searched the older Swype code for mechanisms associated with dynamic external APK/resource loading, including concepts such as `addAssetPath`, `createPackageContext`, `getPackageArchiveInfo`, `installed_themes`, and external theme installation. According to that investigation, the required later-generation external theme loader was not found in this older codebase.

The older `ThemeManager` was described as building its available themes from internal `svgSwype.*` resources plus old Google-IAP-related logic.

Working hypothesis, requiring verification against actual APKs:

The 270 downloaded theme APKs belong to a later Swype generation than the Swype base currently being ported. The later Nuance external-theme loader may therefore need to be ported from a compatible later Swype APK into the FIX40 baseline.

Do NOT treat this hypothesis as proven until the relevant APKs are available and compared directly.

## Why FIX48 / FIX48B were abandoned

FIX48 treated the theme problem too much like a new Android application-install flow and also attempted a Settings integration based on resource assumptions that were not valid for the base APK.

FIX48B still relied on locating a top-level Settings XML via an assumed original Themes entry and stopped with the error noted above.

Rather than making a FIX48C that merely compiles, the decision was made to stop and identify the real Nuance theme loading architecture first.

This is important: DO NOT resume by making another guessed Settings XML search or by simply sending the downloaded theme APKs to Android's normal package installer.

## Evidence still missing

The previous ChatGPT conversation contained much more project history than has currently been recovered. The following must still be obtained where possible:

- ChatGPT account data export containing the old Swype conversation
- FIX40 APK and/or its decompiled source tree
- original/base Swype APK used to produce FIX40
- later FIX APKs/source trees if retained
- old `themes.zip`
- old `files.zip`
- later Swype 5.x APK (or preferably the exact Swype APK under which the 270 downloaded themes originally worked)
- any build scripts/logs/artifacts from FIX1..FIX48 not stored in this repository

## Next technical step

Do NOT modify FIX40 merely to make a new theme build compile.

First obtain the later Swype APK associated with the 5.x theme packages.

Then compare the old FIX40/base Swype implementation with that later Swype generation and locate Nuance's actual external-theme mechanism. Investigation should include, but not be limited to:

- discovery of external theme packages
- package/resource loading
- AssetManager/resource-path manipulation
- package context creation
- parsing/registration of downloaded themes
- `files/themes` handling
- `installed_themes.xml`
- theme metadata
- interaction with `ThemeManager`
- selection and activation of a downloaded theme
- any signature/package validation
- download/update/deletion lifecycle

Only after the real mechanism is understood should the dead Nuance server/backend portion be replaced by the already working GitHub catalog.

## Current architecture model

Known/desired backend:

GitHub `themes-v1` release
  -> 270 ZIP assets
  -> generated `themes.json`
  -> URL + size + SHA-256 metadata

Missing client bridge:

Swype Theme UI
  -> fetch/read replacement catalog
  -> download chosen theme
  -> unpack/store package correctly
  -> register/discover theme using Nuance mechanism
  -> load external theme resources
  -> expose through ThemeManager
  -> activate theme

The missing client bridge is the main theme-engineering problem.

## Safety / regression rules for future work

1. FIX40 remains the baseline until evidence establishes a better known-good baseline.
2. Preserve known working Dragon, language, Shift, and Settings behavior.
3. FIX48 and FIX48B are discarded experiments, not foundations.
4. Do not invent a replacement theme architecture before examining Nuance's later implementation.
5. Do not assume Android's ordinary APK installer is the correct way to install these theme APK resources.
6. Do not repeatedly debug the GitHub catalog unless evidence indicates it is broken; the catalog generation and validation have already been verified.
7. Separate VERIFIED facts from hypotheses reconstructed from the truncated conversation.
8. Update this handover whenever additional old-chat history or source artifacts are recovered.

## Recovery status

What is currently backed up outside the lost/full conversation:

- the GitHub theme release and catalog infrastructure
- this handover file
- recovered late-stage conversation describing FIX48/FIX48B and the theme architecture investigation

What is NOT yet safely reconstructed:

- complete FIX1..FIX40 history
- exact changes that produced FIX40
- full chronology after FIX40
- all compatibility findings around modern Android
- all earlier Dragon/language/Shift/Settings reasoning
- complete inventory of APKs/files previously supplied in the old conversation

The ChatGPT data export should be used to reconstruct these missing sections when available.

## Continuation instruction for a future assistant

Before changing code, read this entire file and inspect the actual available APK/source artifacts. If a ChatGPT export of the old conversation is available, extract the complete Swype conversation and merge its confirmed technical history into this document. Clearly mark contradictions and prefer evidence from actual APK/source/build artifacts over recollection.
