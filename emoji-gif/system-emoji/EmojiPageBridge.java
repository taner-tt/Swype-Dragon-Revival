package com.swypedragon.emoji;
import java.util.*;
/** Converts ordered Unicode sequences into the host Swype Emoji objects.
 * Integrate at category-to-pager boundary, NOT in Senaste; V3 owns recents. */
public final class EmojiPageBridge {
  public interface EmojiHost<T> {
    String unicodeOf(T emoji);
    T resolve(String unicode);
    boolean canDisplay(T emoji);
  }
  private EmojiPageBridge(){}
  public static <T> List<T> orderedPage(List<String> orderedUnicode,
      Collection<T> legacyObjects, EmojiHost<T> host) {
    if(orderedUnicode==null||legacyObjects==null||host==null)
      throw new IllegalArgumentException("missing input");
    Map<String,T> existing=new LinkedHashMap<String,T>();
    for(T emoji:legacyObjects) {
      if(emoji==null)continue;
      String key=host.unicodeOf(emoji);
      if(key!=null&&!existing.containsKey(key))existing.put(key,emoji);
    }
    Map<String,T> visible=new LinkedHashMap<String,T>();
    for(String unicode:orderedUnicode) {
      if(unicode==null||unicode.length()==0||visible.containsKey(unicode))continue;
      T e=existing.containsKey(unicode)?existing.get(unicode):host.resolve(unicode);
      if(e!=null&&host.canDisplay(e))visible.put(unicode,e);
    }
    for(Map.Entry<String,T> old:existing.entrySet())
      if(!visible.containsKey(old.getKey())&&host.canDisplay(old.getValue()))
        visible.put(old.getKey(),old.getValue());
    return Collections.unmodifiableList(new ArrayList<T>(visible.values()));
  }
}
