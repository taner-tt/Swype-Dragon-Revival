package com.swypedragon.emoji;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

/**
 * Pure Java regression checks using simulated glyph support, not physical device tests.
 * The 3722 PUA values below are unique placeholders, not the real Swype emoji catalog.
 */
public final class AndroidBrandCompatibilityTest {
    private static void check(boolean condition, String message) {
        if (!condition) throw new AssertionError(message);
    }

    public static void main(String[] args) {
        List<String> original = new ArrayList<String>();
        for (int cp = 0xE000; original.size() < 3722; cp++) {
            original.add(new String(Character.toChars(cp)));
        }
        List<String> snapshot = new ArrayList<String>(original);
        String recent = "🥰";
        String zwj = "👩‍💻";
        String newer = "🫩";
        List<String> candidates = Arrays.asList(newer, zwj, recent, newer, "\ud800", "");
        Set<String> wellSupported = new HashSet<String>(Arrays.asList(newer, zwj, recent));
        Set<String> olderSupported = new HashSet<String>(Collections.singletonList(recent));

        List<String> modern = SystemEmojiCatalog.merge(original,
                () -> candidates, wellSupported::contains);
        List<String> older = SystemEmojiCatalog.merge(original,
                () -> candidates, olderSupported::contains);
        List<String> legacy = SystemEmojiCatalog.merge(original,
                Collections::emptyList, value -> false);

        check(original.equals(snapshot), "original registry was mutated");
        check(modern.size() == 3725, "modern device candidate filter/dedup incorrect");
        check(older.size() == 3723, "older device fallback incorrect");
        check(legacy.equals(snapshot), "legacy phone must keep original list intact");
        check(modern.subList(0, 3722).equals(snapshot), "old emoji order must not shift");
        check(modern.get(3722).equals(newer) && modern.get(3723).equals(zwj),
                "new emoji and ZWJ order changed");
        check(new HashSet<String>(modern).size() == modern.size(), "duplicates present");
        check(!modern.contains("\ud800"), "unpaired surrogate allowed");
        try {
            modern.clear();
            throw new AssertionError("output is mutable");
        } catch (UnsupportedOperationException expected) { }
        System.out.println("PASS: simulated OEM support levels, 3722 originals preserved, ZWJ, ordering, deduplication, immutability");
    }
}
