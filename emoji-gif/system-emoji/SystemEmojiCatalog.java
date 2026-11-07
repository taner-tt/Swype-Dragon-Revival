package com.swypedragon.emoji;

import java.util.ArrayList;
import java.util.Collection;
import java.util.Collections;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Set;

/** Append renderable device emoji without replacing or reordering Swype's originals. */
public final class SystemEmojiCatalog {
    public interface GlyphSupport {
        boolean canDraw(String sequence);
    }
    public interface DeviceEmojiSource {
        Collection<String> getSupportedSequences();
    }
    private SystemEmojiCatalog() {}

    public static List<String> merge(Collection<String> original,
                                     DeviceEmojiSource device,
                                     GlyphSupport glyphs) {
        if (original == null || device == null || glyphs == null) {
            throw new IllegalArgumentException("Original list, device and glyph test required");
        }
        Set<String> combined = new LinkedHashSet<String>();
        for (String value : original) {
            if (isValidSequence(value)) combined.add(value);
        }
        Collection<String> candidates = device.getSupportedSequences();
        if (candidates != null) {
            for (String value : candidates) {
                if (isValidSequence(value) && glyphs.canDraw(value)) combined.add(value);
            }
        }
        return Collections.unmodifiableList(new ArrayList<String>(combined));
    }
    private static boolean isValidSequence(String value) {
        if (value == null || value.length() == 0 || value.length() > 64) return false;
        for (int i = 0; i < value.length();) {
            int cp = value.codePointAt(i);
            if (Character.isSurrogate(value.charAt(i)) && cp <= 0xFFFF) return false;
            if (Character.isISOControl(cp)) return false;
            i += Character.charCount(cp);
        }
        return true;
    }
}
