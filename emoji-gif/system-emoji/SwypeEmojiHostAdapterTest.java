package com.swypedragon.emoji;
import com.nuance.swype.input.emoji.Emoji;
import com.nuance.swype.input.emoji.EmojiLoader;
import java.util.*;
public final class SwypeEmojiHostAdapterTest {
    public static void main(String[] args) {
        Emoji face = new Emoji("😀",true);
        Emoji love = new Emoji("🥰",true);
        Emoji cool = new Emoji("😎",true);
        Emoji old = new Emoji("😐",true);
        Emoji unsupported = new Emoji("🦄",false);
        for(Emoji x:Arrays.asList(face,love,cool,old,unsupported)) EmojiLoader.register(x);
        SwypeEmojiHostAdapter adapter=new SwypeEmojiHostAdapter();
        // Legacy order is wrong; new Unicode order should win, object identity preserved.
        List<Emoji> got=adapter.orderStaticCategory(
            Arrays.asList("😀","🥰","😎","🦄","🪿"),
            Arrays.asList(face,cool,old,love));
        List<String> actual=new ArrayList<String>();
        for(Emoji x:got) actual.add(x.getEmojiDisplayCode());
        assert actual.equals(Arrays.asList("😀","🥰","😎","😐")) : actual;
        assert got.get(0)==face && got.get(1)==love && got.get(2)==cool;
        assert adapter.resolve("🪿")==null;
        assert !adapter.canDisplay(unsupported);
        System.out.println("PASS: real Swype signatures, old object identity, sorted list, missing glyph / registry fallback");
    }
}
