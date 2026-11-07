package com.swypedragon.emoji;

import java.util.Arrays;
import java.util.List;

/** Run with javac/java -ea; no Android SDK required. */
public final class SystemEmojiCatalogTest {
    public static void main(String[] args) {
        List<String> original = Arrays.asList("😀", "😂", "❤️", "😀");
        SystemEmojiCatalog.DeviceEmojiSource source =
                () -> Arrays.asList("😀", "🫠", "🦄", "\ud800", "");
        SystemEmojiCatalog.GlyphSupport fakeDevice = value -> !value.equals("🦄");
        List<String> actual = SystemEmojiCatalog.merge(original, source, fakeDevice);
        assert actual.equals(Arrays.asList("😀", "😂", "❤️", "🫠")) : actual;
        try {
            actual.add("💡");
            throw new AssertionError("List must be immutable");
        } catch (UnsupportedOperationException expected) {}
        List<String> olderDevice = SystemEmojiCatalog.merge(
                original, () -> Arrays.asList(), x -> true);
        assert olderDevice.equals(Arrays.asList("😀", "😂", "❤️")) : olderDevice;
        System.out.println("PASS: originals preserved; unsupported filtered; duplicates removed");
    }
}
