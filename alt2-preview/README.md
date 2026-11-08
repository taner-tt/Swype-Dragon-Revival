# Swype Alt2 emoji panel — isolated preview

This branch preserves the real Swype APK and signing key. The test app is a separate, clearly labelled **preview** with application ID `se.swyperevival.alt2preview`; it is **not Swype** and cannot replace the old emoji panel yet.

Features: black panel, six category buttons, built-in emoji samples including 🥰, text insertion into its own test field, native Android default typeface (Samsung emoji fallback where supported). No bundled emoji art or fonts.

Not implemented: integration into Swype's IME, keyboard typing, exact 568-entry CLDR 17.0 dataset, signed update for Swype. Preview APK is debug-signed with a distinct package name.

See GitHub Actions > "Alt2 emoji panel preview APK" for a downloadable debug APK artifact after a successful run.

## Cross-device glyph support (preview)

Uses Android `Paint.hasGlyph()` with `Typeface.DEFAULT` to estimate local device support for each emoji sequence. Unsupported candidates are dimmed; tapping still inserts original Unicode text (so recipients on newer devices can potentially see it). This is a heuristic and **does not guarantee** correct color glyphs or complete ZWJ rendering. No bundled cross-device fallback font yet. Full Unicode CLDR 17.0 dataset and real Swype integration are still outstanding.
