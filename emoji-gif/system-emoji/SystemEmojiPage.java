package com.swypedragon.emoji;

import android.content.Context;
import android.graphics.Typeface;
import android.os.Handler;
import android.os.Looper;
import android.view.Gravity;
import android.view.View;
import android.view.ViewGroup;
import android.view.inputmethod.InputConnection;
import android.widget.BaseAdapter;
import android.widget.FrameLayout;
import android.widget.GridView;
import android.widget.TextView;
import java.util.ArrayList;
import java.util.Collection;
import java.util.Collections;
import java.util.List;

/**
 * Emoji page hosted INSIDE the keyboard's existing emoji container.
 *
 * This class deliberately does not create a second IME, change keyboard layouts,
 * theme styles, or the GIF action. It draws Unicode with Android's font fallback.
 * The Swype integration must supply its existing category list, existing
 * InputConnection, and must choose when to insert this view into its TabHost.
 *
 * NOTE: this component is not yet wired into Swype's closed-source controller.
 */
public final class SystemEmojiPage extends FrameLayout {
    private final GridView grid;
    private final EmojiAdapter adapter;
    private final Handler main = new Handler(Looper.getMainLooper());
    private volatile int generation;
    private InputConnection connection;

    public SystemEmojiPage(Context context, InputConnection connection,
                           Collection<String> originalEmoji) {
        super(context);
        this.connection = connection;
        adapter = new EmojiAdapter(context);
        adapter.replace(originalEmoji == null
                ? Collections.<String>emptyList()
                : new ArrayList<String>(originalEmoji));
        grid = new GridView(context);
        grid.setNumColumns(8);
        grid.setVerticalSpacing(dp(4));
        grid.setHorizontalSpacing(dp(4));
        grid.setStretchMode(GridView.STRETCH_COLUMN_WIDTH);
        grid.setClipToPadding(false);
        grid.setPadding(dp(4), dp(4), dp(4), dp(4));
        grid.setAdapter(adapter);
        grid.setOnItemClickListener((parent, child, position, id) -> {
            InputConnection current = this.connection;
            if (current != null) {
                String unicode = adapter.getItem(position);
                if (unicode != null && !unicode.isEmpty()) {
                    current.commitText(unicode, 1);
                }
            }
        });
        addView(grid, new FrameLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.MATCH_PARENT));
    }

    /** Call on main thread after the Swype editor changes. */
    public void setInputConnection(InputConnection connection) {
        this.connection = connection;
    }

    /**
     * Off-UI-thread discovery and device support filter.
     * Keep Swype's originals visible while detection runs.
     */
    public void appendSystemEmoji(Collection<String> originalEmoji) {
        final int request = ++generation;
        final List<String> originals = originalEmoji == null
                ? Collections.<String>emptyList()
                : new ArrayList<String>(originalEmoji);
        new Thread(() -> {
            final AndroidEmojiSource device = new AndroidEmojiSource(dp(28));
            final List<String> merged;
            try {
                merged = SystemEmojiCatalog.merge(originals, device, device);
            } catch (RuntimeException error) {
                // Never erase the old emoji panel due to an OEM ICU/font bug.
                return;
            }
            main.post(() -> {
                if (request == generation) adapter.replace(merged);
            });
        }, "SwypeSystemEmojiDiscovery").start();
    }

    /** Cancel delayed emoji updates when the host view is destroyed. */
    public void cancelLoading() {
        ++generation;
    }

    private int dp(float value) {
        return (int) (getResources().getDisplayMetrics().density * value + 0.5f);
    }

    private final class EmojiAdapter extends BaseAdapter {
        private final Context context;
        private List<String> emoji = Collections.emptyList();

        private EmojiAdapter(Context context) { this.context = context; }
        private void replace(Collection<String> next) {
            emoji = Collections.unmodifiableList(new ArrayList<String>(next));
            notifyDataSetChanged();
        }
        @Override public int getCount() { return emoji.size(); }
        @Override public String getItem(int position) { return emoji.get(position); }
        @Override public long getItemId(int position) { return position; }

        @Override public View getView(int position, View recycled, ViewGroup parent) {
            TextView cell;
            if (recycled instanceof TextView) cell = (TextView) recycled;
            else {
                cell = new TextView(context);
                cell.setGravity(Gravity.CENTER);
                cell.setTypeface(Typeface.DEFAULT);
                cell.setTextSize(27);
                cell.setMinHeight(dp(48));
                cell.setContentDescription("Emoji");
            }
            String sequence = getItem(position);
            cell.setText(sequence);
            cell.setContentDescription(sequence);
            return cell;
        }
    }
}
