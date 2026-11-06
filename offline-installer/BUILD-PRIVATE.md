# Build with your private language archive

The GitHub Actions build intentionally produces an **empty prototype** because the proprietary language files must not be committed to the public repository.

On a machine with Android SDK 35, Java 17 and Gradle 8.10.2:

```sh
python3 offline-installer/prepare_assets.py /path/to/Swype-104-Language-Packs-UNTESTED.zip
cd offline-installer
gradle :app:assembleDebug
```

The resulting APK is `app/build/outputs/apk/debug/app-debug.apk`. Its size may be several hundred MB. Android must be tested for installability and extraction performance.

**Functional limitation:** This APK currently selects and exports language ZIP files. It does **not** install them inside Swype. A receiving import component must be implemented in the modified Swype APK, then the installer must be changed to call it. Do not describe this prototype as a finished language installer.

No signing keystore or private language files should be committed.
