package com.nuance.swype.input.emoji;
import java.util.*;
public final class SwypeEmojiOrderTest {
  static Emoji e(String s) { return new Emoji(s,true); }
  public static void main(String[] args) {
    Emoji a=e("😀"),b=e("😍"),c=e("😘"),d=e("🥰"),z=e("😐");
    List<Emoji> source=Arrays.asList(a,b,c,z,d);
    List<Emoji> out=SwypeEmojiOrder.order(source,Arrays.asList("😀","😍","🥰","😘","🦄"));
    assert out.equals(Arrays.asList(a,b,d,c,z)):out;
    assert out.get(2)==d && source.equals(Arrays.asList(a,b,c,z,d));
    List<Emoji> other=SwypeEmojiOrder.order(source,Arrays.asList("😘","🥰","😀"));
    assert other.get(0)==c && other.get(1)==d;
    System.out.println("PASS: real Nuance method shapes; object identity and original list preserved");
  }
}
