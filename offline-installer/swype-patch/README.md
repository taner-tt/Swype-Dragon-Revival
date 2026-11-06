# Swype-side offline import receiver

`OfflineLanguageImportActivity` runs **inside Swype** and lets the user select an exported ZIP using Android's system document picker. It invokes Swype's existing `LanguageInstall` class for each nested language pack. This avoids violating Android application sandboxing.

The import UI is a separate launcher entry in the patched Swype app. This is **not yet a verified build** and now calls `LanguageList.addDownloadedLanguage`, `DatabaseConfig.updateLanguage` and `IMEApplication.refreshInputMethods` after deployment; the original Swype installer and language menu may still require additional integration. Device testing is required.

The four compile-time stubs (`LanguageInstall`, `LanguageList`, `DatabaseConfig`, `IMEApplication`) are only for compiling the new activity. **None** may be included in the patched APK. The build now compiles against all four and removes their compiled classes before DEX conversion. These stubs are assumptions, not proof of the exact signatures in the FIX47C reference APK; inspect the real classes before declaring runtime compatibility.

Security: document picker grants access to a user-selected file only; each nested ZIP is size-limited, names are validated, and temporary files are deleted. This is not a guarantee that the proprietary language data is compatible.
