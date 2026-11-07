package com.nuance.swype.input.emoji;
import java.util.*;
/** Ordered static categories only. Do not apply to Recents (V3 owns its view). */
public final class SwypeEmojiOrder {
  private SwypeEmojiOrder() {}
  public static List<Emoji> order(List<Emoji> source, List<String> codeOrder) {
    if(source == null || codeOrder == null) throw new IllegalArgumentException("source/order required");
    Map<String,Emoji> indexed = new LinkedHashMap<String,Emoji>();
    for(Emoji item:source) {
      if(item == null) continue;
      String key = item.getEmojiDisplayCode();
      if(key != null && !indexed.containsKey(key)) indexed.put(key, item);
    }
    List<Emoji> result = new ArrayList<Emoji>();
    Set<String> used = new HashSet<String>();
    for(String text:codeOrder) {
      if(text == null || !used.add(text)) continue;
      Emoji e=indexed.get(text);
      if(e==null) e=EmojiLoader.getEmoji(text);
      if(e!=null && e.isCanDisplay()) result.add(e);
    }
    for(Map.Entry<String,Emoji> old:indexed.entrySet()) {
      if(used.add(old.getKey()) && old.getValue().isCanDisplay()) result.add(old.getValue());
    }
    return Collections.unmodifiableList(result);
  }
}
