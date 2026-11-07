package com.nuance.swype.input.emoji;
/** Test-only shape of Nuance DEX methods; do not bundle into the real APK. */
class Emoji {
  private final String text;private final boolean display;
  Emoji(String t,boolean display){this.text=t;this.display=display;}
  public String getEmojiDisplayCode(){return text;}
  public boolean isCanDisplay(){return display;}
}
class EmojiLoader {
  public static Emoji getEmoji(String text){return null;}
}
