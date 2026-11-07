package com.swypedragon.emoji;
import java.util.*;
public final class EmojiCatalogBridgeTest {
  public static void main(String[] args) {
    EmojiCatalogBridge.Category s=EmojiCatalogBridge.Category.SMILEYS;
    Map<EmojiCatalogBridge.Category,List<String>> old=new EnumMap<>(EmojiCatalogBridge.Category.class);
    old.put(s,Arrays.asList("😀","😍","😘","🥰"));
    List<EmojiCatalogBridge.Entry> modern=Arrays.asList(
      new EmojiCatalogBridge.Entry("😀",s,1),
      new EmojiCatalogBridge.Entry("😍",s,2),
      new EmojiCatalogBridge.Entry("🥰",s,3),
      new EmojiCatalogBridge.Entry("😘",s,4),
      new EmojiCatalogBridge.Entry("🫠",s,5));
    EmojiCatalogBridge result=EmojiCatalogBridge.create(modern,old,x->!"🫠".equals(x));
    assert result.list(s).equals(Arrays.asList("😀","😍","🥰","😘")):result.list(s);
    System.out.println("PASS: Unicode order independent from old registry, no duplicates");
  }
}
