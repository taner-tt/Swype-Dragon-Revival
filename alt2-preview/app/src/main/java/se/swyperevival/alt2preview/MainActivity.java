package se.swyperevival.alt2preview;

import android.app.Activity;
import android.os.Bundle;
import android.graphics.Color;
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
import android.view.Gravity;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.GridLayout;
import android.widget.HorizontalScrollView;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;

public class MainActivity extends Activity {
    private static final int BLACK = Color.rgb(8, 8, 10);
    private static final int PANEL = Color.rgb(21, 22, 26);
    private static final int WHITE = Color.rgb(244, 244, 247);
    private static final int ACCENT = Color.rgb(100, 170, 255);

    // Demonstration data only. The complete 568-item CLDR 17.0 catalog is NOT
    // part of this preview. No emoji assets/fonts are bundled.
    private static final String[][] EMOJI = {
      {"😀","😃","😄","😁","😆","😅","😂","🤣","🥲","☺️","😊","😇","🙂","🙃","😉","😍","🥰","😘","😗","😚","😙","🥹","😋","😛","😜","🤪","😝","🤑","🤗","🤭","🫢","🫣","🤫","🤔","🫡","🤐","🤨","😐","😑","😶","🫥","😏","😒","🙄","😬","😮‍💨","🤥","🫨","😌","😔","😪","🤤","😴","😷","🤒","🤕","🤢","🤮","🤧","🥵","🥶","🥴","😵","😵‍💫","🤯","🤠","🥳","🥸","😎","🤓","🧐"},
      {"👋","🤚","🖐️","✋","🖖","🫱","🫲","🫳","🫴","👌","🤌","🤏","✌️","🤞","🫰","🤟","🤘","🤙","👈","👉","👆","👇","☝️","🫵","👍","👎","✊","👊","🤛","🤜","👏","🙌","🫶","👐","🤲","🤝","🙏","✍️","💅","🤳","💪","🦾","🦿","🦵","🦶","👂","🦻","👃","🧠","🫀","🫁","🦷","🦴","👀","👁️","👅","👄","🫦","👶","🧒","👦","👧","🧑","👨","👩","🧓","👴","👵"},
      {"🐶","🐱","🐭","🐹","🐰","🦊","🐻","🐼","🐻‍❄️","🐨","🐯","🦁","🐮","🐷","🐽","🐸","🐵","🙈","🙉","🙊","🐒","🐔","🐧","🐦","🐤","🐣","🐥","🦆","🦅","🦉","🦇","🐺","🐗","🐴","🦄","🐝","🪱","🐛","🦋","🐌","🐞","🐜","🪰","🪲","🪳","🦟","🦗","🕷️","🦂","🐢","🐍","🦎","🦖","🦕","🐙","🦑","🦐","🦞","🦀","🐟","🐠","🐡","🦈","🐬","🐳","🐋","🦭"},
      {"🍏","🍎","🍐","🍊","🍋","🍋‍🟩","🍌","🍉","🍇","🍓","🫐","🍈","🍒","🍑","🥭","🍍","🥥","🥝","🍅","🍆","🥑","🥦","🫛","🥬","🥒","🌶️","🫑","🌽","🥕","🫒","🧄","🧅","🥔","🍠","🥐","🥯","🍞","🥖","🥨","🧀","🥚","🍳","🧈","🥞","🧇","🥓","🥩","🍗","🍖","🦴","🌭","🍔","🍟","🍕","🫓","🥪","🥙","🧆","🌮","🌯","🫔","🥗","🥘","🫕","🥫","🍝","🍜","🍲"},
      {"🚗","🚕","🚙","🚌","🚎","🏎️","🚓","🚑","🚒","🚐","🛻","🚚","🚛","🚜","🛵","🏍️","🛺","🚲","🛴","🚏","🛣️","🛤️","⛽","🚨","🚥","🚦","🛑","🚧","⚓","⛵","🛶","🚤","🛳️","⛴️","🛥️","🚢","✈️","🛩️","🛫","🛬","🪂","💺","🚁","🚟","🚠","🚡","🛰️","🚀","🛸","🏠","🏡","🏘️","🏢","🏣","🏤","🏥","🏦","🏨","🏩","🏪","🏫","🏬","🏭","🏯","🏰","💒"},
      {"⌚","📱","📲","💻","⌨️","🖥️","🖨️","🖱️","🖲️","💽","💾","💿","📀","📷","📸","📹","🎥","📽️","🎞️","📞","☎️","📟","📠","📺","📻","🎙️","🎚️","🎛️","🧭","⏱️","⏲️","⏰","🕰️","⌛","⏳","📡","🔋","🪫","🔌","💡","🔦","🕯️","🪔","🧯","🛢️","💸","💵","💴","💶","💷","🪙","💰","💳","💎","⚖️","🪜","🧰","🪛","🔧","🔨","⚒️","🛠️","⛏️","🪚","🔩","⚙️"}
    };

    private LinearLayout categories;
    private GridLayout grid;
    private EditText typed;
    private int active = 0;

    private int dp(float value) { return (int)(getResources().getDisplayMetrics().density * value + 0.5f); }
    private GradientDrawable surface(int color, int radius) {
        GradientDrawable d = new GradientDrawable();
        d.setColor(color); d.setCornerRadius(dp(radius)); return d;
    }

    @Override public void onCreate(Bundle saved) {
        super.onCreate(saved);
        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL); root.setBackgroundColor(BLACK);
        root.setPadding(dp(8), dp(14), dp(8), dp(8));

        TextView label = new TextView(this);
        label.setText("Swype Alt2 · emoji-paneltest");
        label.setTextColor(WHITE); label.setTextSize(16);
        label.setPadding(dp(10), dp(6), 0, dp(10)); root.addView(label);

        TextView warning = new TextView(this);
        warning.setText("FRISTÅENDE FÖRHANDSVISNING — inte integrerad i Swype ännu");
        warning.setTextColor(ACCENT); warning.setTextSize(11);
        warning.setPadding(dp(10), 0, 0, dp(8)); root.addView(warning);

        typed = new EditText(this);
        typed.setHint("Tryck på emoji för att prova …");
        typed.setHintTextColor(0xff9999a3); typed.setTextColor(WHITE);
        typed.setTextSize(18); typed.setMinHeight(dp(65));
        typed.setBackground(surface(PANEL, 12));
        typed.setPadding(dp(14), dp(10), dp(14), dp(10));
        root.addView(typed, new LinearLayout.LayoutParams(-1, -2));

        HorizontalScrollView strip = new HorizontalScrollView(this);
        strip.setHorizontalScrollBarEnabled(false);
        categories = new LinearLayout(this); categories.setOrientation(LinearLayout.HORIZONTAL);
        strip.addView(categories); root.addView(strip);

        ScrollView scroll = new ScrollView(this);
        scroll.setFillViewport(true); scroll.setBackground(surface(PANEL, 12));
        grid = new GridLayout(this); grid.setColumnCount(7);
        grid.setPadding(dp(5), dp(8), dp(5), dp(8));
        scroll.addView(grid);
        root.addView(scroll, new LinearLayout.LayoutParams(-1, 0, 1));
        setContentView(root);
        render(0);
    }

    private void render(int index) {
        active = index;
        categories.removeAllViews();
        String[] names = {"☺","👋","🐱","🍕","🚗","💡"};
        for (int i=0; i<names.length; i++) {
            final int next=i;
            Button tab=new Button(this);
            tab.setText(names[i]); tab.setTextSize(21); tab.setAllCaps(false);
            tab.setTextColor(i==active ? ACCENT : WHITE);
            tab.setBackground(surface(i==active ? 0xff303b4a : BLACK, 10));
            LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(dp(54),dp(51));
            lp.setMargins(dp(2),dp(8),dp(2),dp(8));
            categories.addView(tab,lp);
            tab.setOnClickListener(v->render(next));
        }
        grid.removeAllViews();
        for (String emoji : EMOJI[index]) {
            TextView item=new TextView(this);
            item.setText(emoji); item.setTextSize(28); item.setTextColor(WHITE);
            item.setTypeface(Typeface.DEFAULT);
            item.setGravity(Gravity.CENTER); item.setMinHeight(dp(53));
            GridLayout.LayoutParams p=new GridLayout.LayoutParams();
            p.width=0; p.height=dp(55); p.columnSpec=GridLayout.spec(GridLayout.UNDEFINED,1f);
            grid.addView(item,p);
            item.setOnClickListener(v->{
                int pos=Math.max(0,typed.getSelectionStart());
                typed.getText().insert(pos,emoji);
            });
        }
    }
}
