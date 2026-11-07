package com.nuance.swype.input.emoji;
/** TEST-ONLY stub matching selected methods from the actual Swype DEX. Never package this in the app. */
public final class Emoji {
    private final String unicode;
    private final boolean canDisplay;
    public Emoji(String unicode, boolean canDisplay) { this.unicode=unicode; this.canDisplay=canDisplay; }
    public String getEmojiDisplayCode() { return unicode; }
    public boolean isCanDisplay() { return canDisplay; }
}
