package com.swyperevival.klipy;

import android.content.Context;
import android.graphics.Color;
import android.graphics.Typeface;
import android.view.Gravity;
import android.view.View;
import android.widget.LinearLayout;
import android.widget.TextView;

/**
 * Compact dark search UI within the keyboard. It never injects a search query
 * into the currently focused chat editor and never starts another IME.
 *
 * The search layout deliberately resembles the existing black Swype theme:
 * white glyphs directly on black, no light rounded keycaps. It does not
 * replace or modify the user's ordinary Swype keyboard or theme resources.
 */
public final class KlipySearchKeyboard extends LinearLayout {
    private static final int BACKGROUND = Color.BLACK;
    private static final int SEARCH_BACKGROUND = 0xff191919;
    private final TextView queryView;
    private final LinearLayout keys;
    private final StringBuilder query = new StringBuilder();
    private final Runnable onSearch;
    private final int dp;

    public KlipySearchKeyboard(Context context, Runnable onSearch) {
        super(context);
        this.onSearch = onSearch;
        dp = Math.max(1, (int)(context.getResources().getDisplayMetrics().density + 0.5f));
        setOrientation(VERTICAL);
        setBackgroundColor(BACKGROUND);

        LinearLayout header = new LinearLayout(context);
        header.setGravity(Gravity.CENTER_VERTICAL);
        queryView = new TextView(context);
        queryView.setTextColor(Color.WHITE);
        queryView.setHintTextColor(0xffaaaaaa);
        queryView.setTextSize(15f);
        queryView.setSingleLine(true);
        queryView.setGravity(Gravity.CENTER_VERTICAL);
        queryView.setPadding(10 * dp, 0, 6 * dp, 0);
        queryView.setBackgroundColor(SEARCH_BACKGROUND);
        header.addView(queryView, new LayoutParams(0, 38 * dp, 1f));
        header.addView(key(context, "Sök", 14, this::submit), new LayoutParams(56 * dp, 38 * dp));
        header.addView(key(context, "×", 22, () -> keys.setVisibility(View.GONE)),
                new LayoutParams(34 * dp, 38 * dp));
        addView(header, new LayoutParams(LayoutParams.MATCH_PARENT, LayoutParams.WRAP_CONTENT));

        keys = new LinearLayout(context);
        keys.setOrientation(VERTICAL);
        keys.setVisibility(View.GONE);
        keys.setBackgroundColor(BACKGROUND);
        addView(keys);
        addRow(context, "qwertyuiop");
        addRow(context, "asdfghjkl");
        addRow(context, "zxcvbnmåäö");

        LinearLayout controls = new LinearLayout(context);
        controls.addView(key(context, "Mellanslag", 13, () -> append(" ")),
                new LayoutParams(0, 34 * dp, 3f));
        controls.addView(key(context, "⌫", 19, this::backspace), new LayoutParams(0, 34 * dp, 1f));
        controls.addView(key(context, "Rensa", 13, this::clear), new LayoutParams(0, 34 * dp, 1.2f));
        keys.addView(controls);
        queryView.setOnClickListener(v ->
                keys.setVisibility(keys.getVisibility() == View.VISIBLE ? View.GONE : View.VISIBLE));
        update();
    }

    private TextView key(Context context, String label, int textSize, Runnable action) {
        TextView key = new TextView(context);
        key.setText(label);
        key.setTextColor(Color.WHITE);
        key.setTextSize(textSize);
        key.setGravity(Gravity.CENTER);
        key.setTypeface(Typeface.DEFAULT, Typeface.NORMAL);
        key.setBackgroundColor(BACKGROUND);
        key.setClickable(true);
        key.setOnClickListener(v -> action.run());
        return key;
    }

    private void addRow(Context context, String letters) {
        LinearLayout row = new LinearLayout(context);
        for (int i = 0; i < letters.length(); i++) {
            final String letter = String.valueOf(letters.charAt(i));
            row.addView(key(context, letter, 20, () -> append(letter)),
                    new LayoutParams(0, 36 * dp, 1f));
        }
        keys.addView(row);
    }

    private void append(String text) {
        if (query.length() + text.length() > 200) return;
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
        queryView.setHint("Search KLIPY");
    }

    private void submit() {
        keys.setVisibility(View.GONE);
        if (onSearch != null) onSearch.run();
    }

    public String getQuery() {
        return query.toString().trim();
    }
}
