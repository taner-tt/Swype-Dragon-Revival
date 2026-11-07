package com.swypedragon.emoji;

import com.nuance.swype.input.emoji.Emoji;
import com.nuance.swype.input.emoji.EmojiLoader;
import java.util.Collection;
import java.util.List;

/**
 * Actual Nuance API integration surface, verified against Swype V3 classes.dex.
 *
 * Placement bridge for STATIC emoji categories. Never pass Senaste/Recents here:
 * Swype's existing V3 recent-grid visual freeze must remain unchanged.
 *
 * Existing emoji objects are preserved when possible. New codepoints are resolved
 * from EmojiLoader's catalog; an absent registry entry is NOT silently fabricated.
 */
public final class SwypeEmojiHostAdapter implements EmojiPageBridge.EmojiHost<Emoji> {
    @Override
    public String unicodeOf(Emoji emoji) {
        return emoji.getEmojiDisplayCode();
    }

    @Override
    public Emoji resolve(String unicode) {
        return EmojiLoader.getEmoji(unicode);
    }

    @Override
    public boolean canDisplay(Emoji emoji) {
        return emoji.isCanDisplay();
    }

    public List<Emoji> orderStaticCategory(List<String> officialOrder,
                                           Collection<Emoji> originalCategory) {
        return EmojiPageBridge.orderedPage(officialOrder, originalCategory, this);
    }
}
