package com.swypedragon.emoji;

import java.util.ArrayList;
import java.util.Collection;
import java.util.Collections;
import java.util.LinkedHashSet;
import java.util.List;

/**
 * Keeps the visible Recent Emoji grid in a stable order during interaction.
 * Usage updates are queued and applied only after leaving the Recent tab.
 * This class owns no Android UI: the host must call leaveRecents() on tab exit.
 */
public final class StableEmojiRecents {
    private final int capacity;
    private final List<String> visible = new ArrayList<String>();
    private final List<String> pendingClicks = new ArrayList<String>();
    private boolean inRecents;

    public StableEmojiRecents(int capacity, Collection<String> initial) {
        if (capacity < 1) throw new IllegalArgumentException("capacity must be positive");
        this.capacity = capacity;
        if (initial != null) {
            for (String emoji : initial) {
                if (emoji != null && !emoji.isEmpty() && !visible.contains(emoji)) {
                    visible.add(emoji);
                    if (visible.size() == capacity) break;
                }
            }
        }
    }

    /** Call when the user navigates to the 'Senaste' emoji category. */
    public void enterRecents() {
        inRecents = true;
    }

    /** Copy for the adapter. Never changes while inRecents is true. */
    public List<String> displayed() {
        return Collections.unmodifiableList(new ArrayList<String>(visible));
    }

    /**
     * Called on every emoji insertion, including when another category is open.
     * Recent-tab selections are queued; other-category selections are applied
     * immediately so the next visit to Recent sees those newly used emojis.
     */
    public void recordUse(String emoji) {
        if (emoji == null || emoji.isEmpty()) return;
        if (inRecents) pendingClicks.add(emoji);
        else promote(emoji);
    }

    /**
     * Flush queued clicks after the user has left the tab (NOT after each tap).
     * Reverse replay gives the last-used emoji first, as expected for MRU.
     */
    public void leaveRecents() {
        if (!inRecents) return;
        inRecents = false;
        for (String emoji : pendingClicks) promote(emoji);
        pendingClicks.clear();
    }

    public boolean isInRecents() {
        return inRecents;
    }

    private void promote(String emoji) {
        visible.remove(emoji);
        visible.add(0, emoji);
        while (visible.size() > capacity) visible.remove(visible.size() - 1);
    }
}
