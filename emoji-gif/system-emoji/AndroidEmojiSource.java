package com.swypedragon.emoji;

import android.graphics.Paint;
import android.graphics.Typeface;
import android.os.Build;
import android.icu.lang.UCharacter;
import android.icu.lang.UProperty;
import android.icu.text.UnicodeSet;
import android.icu.text.UnicodeSetIterator;
import java.util.ArrayList;
import java.util.Collection;
import java.util.Collections;
import java.util.List;

/** Android ICU + system font; must run off UI thread and cache results. */
public final class AndroidEmojiSource implements SystemEmojiCatalog.DeviceEmojiSource,
        SystemEmojiCatalog.GlyphSupport {
    private final Paint paint;
    private volatile List<String> cache;

    public AndroidEmojiSource(float textSizePixels) {
        paint = new Paint(Paint.ANTI_ALIAS_FLAG);
        paint.setTypeface(Typeface.DEFAULT);
        paint.setTextSize(textSizePixels);
    }

    @Override public boolean canDraw(String sequence) {
        return Build.VERSION.SDK_INT >= 23 && paint.hasGlyph(sequence);
    }

    @Override public Collection<String> getSupportedSequences() {
        if (cache != null) return cache;
        List<String> result = new ArrayList<String>();
        if (Build.VERSION.SDK_INT >= 34) {
            try {
                UnicodeSet set = new UnicodeSet("[\\p{RGI_Emoji}]");
                UnicodeSetIterator it = new UnicodeSetIterator(set);
                while (it.next()) {
                    String value = it.codepoint == UnicodeSetIterator.IS_STRING
                            ? it.string : new String(Character.toChars(it.codepoint));
                    if (canDraw(value)) result.add(value);
                }
            } catch (IllegalArgumentException ex) {
                // Some OEM ICU builds cannot resolve the sequence property.
            }
        }
        if (result.isEmpty() && Build.VERSION.SDK_INT >= 28) {
            for (int cp = 0x2000; cp <= 0x1FAFF; cp++) {
                if (!Character.isValidCodePoint(cp) ||
                    (cp >= 0xD800 && cp <= 0xDFFF)) continue;
                if (!UCharacter.hasBinaryProperty(cp, UProperty.EMOJI_PRESENTATION)) continue;
                String value = new String(Character.toChars(cp));
                if (canDraw(value)) result.add(value);
            }
        }
        cache = Collections.unmodifiableList(result);
        return cache;
    }
}
