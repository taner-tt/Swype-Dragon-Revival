package com.swypedragon.emoji;
import java.util.*;
public final class EmojiPageBridgeTest {
  static final class E {
    final String code; final boolean supported;
    E(String s, boolean yes){code=s;supported=yes;}
  }
  static class Host implements EmojiPageBridge.EmojiHost<E> {
    int newItems;
    public String unicodeOf(E e){return e.code;}
    public E resolve(String s){newItems++;return new E(s,!"🪿".equals(s));}
    public boolean canDisplay(E e){return e.supported;}
  }
  public static void main(String[] args){
    E face=new E("😀",true), love=new E("🥰",true), old=new E("😐",true);
    Host host=new Host();
    List<E> result=EmojiPageBridge.orderedPage(
      Arrays.asList("😀","🥰","🪿","🧑🏽‍🚀","🥰"),
      Arrays.asList(face,old,love),host);
    List<String> texts=new ArrayList<>();
    for(E e:result)texts.add(e.code);
    assert texts.equals(Arrays.asList("😀","🥰","🧑🏽‍🚀","😐")):texts;
    assert result.get(0)==face && result.get(1)==love;
    assert host.newItems==2;
    try{result.clear();throw new AssertionError("mutable");}
    catch(UnsupportedOperationException expected){}
    System.out.println("PASS: ordered objects, identity, ZWJ, fallback and font gate");
  }
}
