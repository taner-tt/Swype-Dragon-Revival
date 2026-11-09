package com.swyperevival.klipy;

import android.content.Context;
import android.graphics.Color;
import android.view.Gravity;
import android.view.View;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.TextView;

/**
 * Search input controlled inside the IME itself. An Android EditText hosted in
 * an input method attempts to summon another IME / edits the receiving editor.
 * These button presses edit only the search query, never the conversation.
 */
public final class KlipySearchKeyboard extends LinearLayout {
    private final TextView queryView;
    private final LinearLayout keys;
    private final StringBuilder query = new StringBuilder();
    private final Runnable onSearch;
    private final int px;

    public KlipySearchKeyboard(Context context, Runnable onSearch) {
        super(context);
        this.onSearch = onSearch;
        px = Math.max(1, (int) (context.getResources().getDisplayMetrics().density + .5f));
        setOrientation(VERTICAL);
        setBackgroundColor(0xff121212);

        LinearLayout bar = new LinearLayout(context);
        bar.setGravity(Gravity.CENTER_VERTICAL);
        queryView = new TextView(context);
        queryView.setTextColor(Color.WHITE);
        queryView.setHintTextColor(0xffbbbbbb);
        queryView.setHint("Search KLIPY – tryck för att skriva");
        queryView.setTextSize(16f);
        queryView.setGravity(Gravity.CENTER_VERTICAL);
        queryView.setPadding(10 * px, 0, 6 * px, 0);
        queryView.setBackgroundColor(0xff292929);
        bar.addView(queryView, new LayoutParams(0, 46 * px, 1f));
        Button go = button(context, "Sök");
        bar.addView(go, new LayoutParams(70 * px, 46 * px));
        addView(bar, new LayoutParams(LayoutParams.MATCH_PARENT, LayoutParams.WRAP_CONTENT));
        keys = new LinearLayout(context);
        keys.setOrientation(VERTICAL);
        keys.setVisibility(View.GONE);
        addView(keys);
        addRow(context, "qwertyuiop");
        addRow(context, "asdfghjkl");
        addRow(context, "zxcvbnmåäö");
        LinearLayout controls = new LinearLayout(context);
        controls.addView(action(context, "Mellanslag", () -> append(" ")), new LayoutParams(0, 42 * px, 3f));
        controls.addView(action(context, "⌫", this::backspace), new LayoutParams(0, 42 * px, 1f));
        controls.addView(action(context, "Rensa", this::clear), new LayoutParams(0, 42 * px, 1.5f));
        keys.addView(controls);
        queryView.setOnClickListener(v -> keys.setVisibility(keys.getVisibility() == View.VISIBLE ? View.GONE : View.VISIBLE));
        go.setOnClickListener(v -> submit());
        update();
    }

    private Button button(Context c, String label) {
        Button b = new Button(c);
        b.setAllCaps(false);
        b.setText(label);
        b.setTextSize(13f);
        b.setMinHeight(0);
        b.setMinimumHeight(0);
        b.setPadding(0, 0, 0, 0);
        return b;
    }

    private Button action(Context c, String title, Runnable run) {
        Button b = button(c, title);
        b.setOnClickListener(v -> run.run());
        return b;
    }

    private void addRow(Context context, String letters) {
        LinearLayout row = new LinearLayout(context);
        for (int i = 0; i < letters.length(); i++) {
            final String letter = String.valueOf(letters.charAt(i));
            row.addView(action(context, letter, () -> append(letter)),
                    new LayoutParams(0, 42 * px, 1f));
        }
        keys.addView(row);
    }

    private void append(String text) {
        if (query.length() >= 200) return;
        query.append(text);
        update();
    }

    private void backspace() {
        if (query.length() > 0) query.deleteCharAt(query.length() - 1);
        update();
    }

    private void clear() {
        query.setLength(0);
        update();
    }

    private void update() {
        queryView.setText(query.toString());
        queryView.setHint("Search KLIPY – tryck för att skriva");
    }

    private void submit() {
        keys.setVisibility(View.GONE);
        if (onSearch != null) onSearch.run();
    }

    public String getQuery() {
        return query.toString().trim();
    }
}
