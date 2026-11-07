package com.swypedragon.emoji;
import java.util.Arrays;
import java.util.List;

public final class StableEmojiRecentsTest {
    private static void eq(List<String> expected, List<String> got) {
        if (!expected.equals(got)) throw new AssertionError("Expected "+expected+" got "+got);
    }
    public static void main(String[] args) {
        StableEmojiRecents recent = new StableEmojiRecents(4, Arrays.asList("👌", "😊", "❤️", "😂"));
        recent.enterRecents();
        List<String> before = recent.displayed();
        recent.recordUse("😊");
        eq(before, recent.displayed()); // NO JUMP after first tap!
        recent.recordUse("👌");
        eq(before, recent.displayed()); // NO JUMP after second tap!
        recent.recordUse("😊");
        eq(before, recent.displayed()); // repeated tap cannot reorder either
        recent.leaveRecents();
        eq(Arrays.asList("😊", "👌", "❤️", "😂"), recent.displayed());
        recent.enterRecents();
        recent.recordUse("🤩");
        eq(Arrays.asList("😊", "👌", "❤️", "😂"), recent.displayed());
        recent.leaveRecents();
        eq(Arrays.asList("🤩", "😊", "👌", "❤️"), recent.displayed());
        recent.recordUse("👍"); // usage in a different category updates next visit
        eq(Arrays.asList("👍", "🤩", "😊", "👌"), recent.displayed());
        recent.enterRecents();
        eq(Arrays.asList("👍", "🤩", "😊", "👌"), recent.displayed());
        System.out.println("PASS: no live reorder during emoji taps; MRU flushed after category exit");
    }
}
