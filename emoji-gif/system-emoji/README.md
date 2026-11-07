# Emoji first: Android system-native rendering

This is **tested core source**, not an integrated or installable Swype APK.

- Preserve old Swype emoji registry and list order.
- Use system ICU RGI_Emoji sequences (API 34+) and Paint.hasGlyph to append emojis supported by the device.
- Single-codepoint emoji fallback on API 28–33.
- Use Android's font fallback (OEM appearance); no fixed Samsung images.
- Leave GIF, the ordinary keyboard, popup, and all themes untouched.
- Pure-Java merge tests have passed locally. Android API bridge and real Samsung/Pixel output are **not yet device-tested**.

Run pure Java test:

```sh
javac -d classes emoji-gif/system-emoji/SystemEmojiCatalog.java emoji-gif/system-emoji/SystemEmojiCatalogTest.java
java -ea -cp classes com.swypedragon.emoji.SystemEmojiCatalogTest
```

Next integrate the candidate list into Swype's `EmojiCategoryList` and the glyph drawing path in `EmojiPageView`, then build and test a signed APK. This code alone **does not** change any APK or guarantee complete Emoji 17.0 coverage.
