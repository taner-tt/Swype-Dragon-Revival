package com.nuance.swype.input.emoji;
import java.util.*;
/** TEST-ONLY registry stub. Actual APK contains its own EmojiLoader. */
public final class EmojiLoader {
    private static final Map<String,Emoji> registry = new HashMap<String,Emoji>();
    public static Emoji getEmoji(String unicode) { return registry.get(unicode); }
    public static void register(Emoji e) { registry.put(e.getEmojiDisplayCode(),e); }
}
