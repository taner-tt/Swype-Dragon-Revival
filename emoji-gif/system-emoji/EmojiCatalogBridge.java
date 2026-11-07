package com.swypedragon.emoji;
import java.util.*;
/** New Unicode category order independent from legacy Swype registry ordering. */
public final class EmojiCatalogBridge {
  public enum Category { SMILEYS, PEOPLE, NATURE, OBJECTS, TRANSPORT, FLAGS }
  public interface GlyphSupport { boolean canDisplay(String unicode); }
  public static final class Entry {
    public final String unicode;
    public final Category category;
    public final int sortOrder;
    public Entry(String unicode, Category category, int sortOrder) {
      this.unicode=unicode; this.category=category; this.sortOrder=sortOrder;
    }
  }
  private final Map<Category,List<String>> pages;
  private EmojiCatalogBridge(Map<Category,List<String>> pages) { this.pages=pages; }
  public List<String> list(Category category) { return pages.get(category); }
  public static EmojiCatalogBridge create(Collection<Entry> imported,
      Map<Category,? extends Collection<String>> original, GlyphSupport font) {
    if(imported==null||original==null||font==null) throw new IllegalArgumentException();
    ArrayList<Entry> sorted=new ArrayList<Entry>(imported);
    Collections.sort(sorted,(a,b)->Integer.compare(a.sortOrder,b.sortOrder));
    EnumMap<Category,LinkedHashSet<String>> output=new EnumMap<>(Category.class);
    for(Category c:Category.values()) output.put(c,new LinkedHashSet<String>());
    for(Entry e:sorted) {
      if(e!=null && e.category!=null && valid(e.unicode) && font.canDisplay(e.unicode))
        output.get(e.category).add(e.unicode);
    }
    for(Category c:Category.values()) {
      Collection<String> old=original.get(c);
      if(old!=null) for(String s:old)
        if(valid(s) && font.canDisplay(s)) output.get(c).add(s);
    }
    EnumMap<Category,List<String>> result=new EnumMap<>(Category.class);
    for(Category c:Category.values())
      result.put(c,Collections.unmodifiableList(new ArrayList<String>(output.get(c))));
    return new EmojiCatalogBridge(Collections.unmodifiableMap(result));
  }
  private static boolean valid(String s) {
    if(s==null||s.isEmpty()||s.length()>96)return false;
    for(int i=0;i<s.length();) {
      char ch=s.charAt(i);
      if(Character.isLowSurrogate(ch))return false;
      int cp=s.codePointAt(i);
      if(Character.isHighSurrogate(ch)&&cp<=0xffff)return false;
      if(Character.isISOControl(cp))return false;
      i+=Character.charCount(cp);
    }
    return true;
  }
}
