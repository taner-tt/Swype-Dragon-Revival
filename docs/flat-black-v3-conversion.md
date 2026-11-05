# Flat Black v3 — conversion notes (work in progress)

## Source and target
- Source: `Swype_EN_WVGA_3.6.84.26668_flat_black_v3_signed.apk` (legacy full Swype APK).
- Source keyboard bitmaps: `assets/keyboards/SwypeRef_PT_*_VGA.png` (480×320) and `assets/keyboards/SwypeRef_LS_*_WVGA.png` (800×240), plus supporting keyboard graphics.
- Reference: existing standalone theme APKs such as `nuance.theme.colorful_black.apk`, wrapped as one APK per downloadable theme ZIP.
- Distribution: release `themes-v1` -> `tools/build_theme_catalog.py` -> `themes.json` and `theme-previews/`.

## Critical compatibility finding
The source's SwypeRef images depict **complete keyboard layouts**. They are not drop-in replacements for theme drawables. Simply copying them into a newer theme APK would risk drawing key legends twice or distorting layout. A theme APK must retain its valid manifest, resource identifiers, density variants and drawable mappings.

## Non-regression requirements
1. Keep the working Swype application APK and keyboard code unchanged.
2. Preserve all 270 existing downloadable theme assets and their hashes.
3. Build the new theme independently; do not replace an existing theme ID.
4. Verify APK structure, decode with pinned Apktool 3.0.3, render its preview, and verify the final ZIP contains exactly one theme APK.
5. Only after successful packaging add the asset to the release and regenerate the catalog. A successful build is not proof of runtime compatibility; confirm install/preview/apply on device.

## Status
Catalog count validation has been prepared on this branch. **No compatible Flat Black theme APK has yet been built or published.** This note documents the conversion constraints; it does not claim successful installation.
