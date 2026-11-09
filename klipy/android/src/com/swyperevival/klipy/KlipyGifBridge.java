package com.swyperevival.klipy;

import android.content.Context;
import android.content.SharedPreferences;
import android.os.SystemClock;
import android.text.InputType;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.TextView;
import java.lang.reflect.Field;
import java.util.WeakHashMap;

/**
 * Experimental tab bridge. Called at the beginning of EmojiInputController.onTabChanged.
 * The original method is preserved for all ordinary emoji categories.
 *
 * Deliberately does not embed credentials or implement GIF sharing.
 */
public final class KlipyGifBridge {
    private static final WeakHashMap<Object, Session> SESSIONS = new WeakHashMap<>();
    private static final String PREFS = "swype_revival_klipy";
    private static final String PREF_KEY = "development_api_key";
    private static volatile long popupGifUntil;

    private KlipyGifBridge() {}

    private static Object field(Object owner, String name) throws Exception {
        // KeyboardEx.Key inherits Android Keyboard.Key.label on some builds.
        // getDeclaredField() on the concrete class alone misses inherited fields.
        for (Class<?> type = owner.getClass(); type != null; type = type.getSuperclass()) {
            try {
                Field f = type.getDeclaredField(name);
                f.setAccessible(true);
                return f.get(owner);
            } catch (NoSuchFieldException ignored) {
                // Continue through parent types; do not swallow other failures.
            }
        }
        throw new NoSuchFieldException(name);
    }

    /**
     * The existing GIF and smiley popup cells have the SAME key code.
     * Only the actual popup key label distinguishes them. Never put credentials here.
     * Called before the original popup handler dispatches the key.
     */
    public static void notePopupKey(Object popupKey) {
        try {
            Object label = popupKey == null ? null : field(popupKey, "label");
            if (label != null && "GIF".equalsIgnoreCase(label.toString().trim())) {
                popupGifUntil = SystemClock.uptimeMillis() + 3000L;
            } else {
                popupGifUntil = 0L;
            }
        } catch (Exception ignored) {
            popupGifUntil = 0L;
        }
    }

    private static final class Session {
        View originalPager;
        ViewGroup parent;
        View shown;
        KlipyGifPanel panel;
    }

    private static void detach(Session s) {
        if (s == null) return;
        if (s.shown != null && s.parent != null) {
            try { s.parent.removeView(s.shown); } catch (Exception ignored) {}
        }
        if (s.panel != null) {
            s.panel.close();
            s.panel = null;
        }
        if (s.originalPager != null) s.originalPager.setVisibility(View.VISIBLE);
        s.shown = null;
    }

    private static void showGallery(Session s, Context context, String key) {
        // A TEST key is entered on the device, never checked into GitHub.
        if (key == null || !key.matches("[A-Za-z0-9_-]{16,256}")) return;
        if (s.shown != null) {
            try { s.parent.removeView(s.shown); } catch (Exception ignored) {}
        }
        if (s.panel != null) s.panel.close();
        KlipyGifPanel view = new KlipyGifPanel(context, key, gif ->
                KlipyGifSender.send(context, gif, key));
        s.panel = view;
        s.shown = view;
        s.parent.addView(view, Math.min(s.parent.getChildCount(), s.parent.indexOfChild(s.originalPager) + 1),
                new ViewGroup.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT));
    }

    private static View buildKeyEntry(final Session s, final Context context) {
        LinearLayout entry = new LinearLayout(context);
        entry.setOrientation(LinearLayout.VERTICAL);
        entry.setPadding(20, 12, 20, 12);
        entry.setBackgroundColor(0xff121212);

        TextView title = new TextView(context);
        title.setText("KLIPY GIF — testnyckel behövs");
        title.setTextColor(0xffffffff);
        entry.addView(title);

        EditText key = new EditText(context);
        key.setSingleLine(true);
        key.setHint("Klistra in KLIPY-testnyckeln");
        key.setInputType(InputType.TYPE_CLASS_TEXT | InputType.TYPE_TEXT_VARIATION_PASSWORD);
        key.setTextColor(0xffffffff);
        key.setHintTextColor(0xffaaaaaa);
        entry.addView(key);
        Button activate = new Button(context);
        activate.setText("Aktivera GIF-sökning");
        entry.addView(activate);
        activate.setOnClickListener(v -> {
            String value = key.getText().toString().trim();
            if (value.isEmpty()) {
                key.setError("Klistra in din KLIPY-testnyckel först");
                return;
            }
            if (!value.matches("[A-Za-z0-9_-]{16,256}")) {
                key.setError("Kontrollera nyckelns format (16–256 tecken). KLIPY har inte kontaktats.");
                return;
            }
            context.getSharedPreferences(PREFS, Context.MODE_PRIVATE)
                    .edit().putString(PREF_KEY, value).apply();
            showGallery(s, context, value);
        });
        return entry;
    }

    /**
     * @return true iff the GIF category was handled. For other tabs the
     *         caller must continue with original Swype onTabChanged().
     */
    public static boolean intercept(Object controller, String tab) {
        if (controller == null) return false;
        synchronized (SESSIONS) {
            Session old = SESSIONS.get(controller);
            boolean isGifTab = tab != null && ("gif".equalsIgnoreCase(tab.trim()) || "gifs".equalsIgnoreCase(tab.trim()));
            boolean requestedByPopup = popupGifUntil > SystemClock.uptimeMillis();
            if (!isGifTab && !requestedByPopup) {
                if (old != null) {
                    detach(old);
                    SESSIONS.remove(controller);
                }
                return false;
            }
            if (old != null && old.shown != null) {
                // A stale/detached page can survive an emoji view recreation.
                // Never claim that GIF is visible unless it belongs to the live pager.
                try {
                    View currentPager = (View) field(controller, "pager");
                    ViewGroup liveParent = (ViewGroup) currentPager.getParent();
                    if (liveParent != null && old.originalPager == currentPager
                            && old.parent == liveParent && old.shown.getParent() == liveParent) {
                        currentPager.setVisibility(View.GONE);
                        old.shown.setVisibility(View.VISIBLE);
                        old.shown.bringToFront();
                        if (requestedByPopup) popupGifUntil = 0L;
                        return true;
                    }
                } catch (Exception ignored) {
                    // Discard the invalid session and rebuild the panel.
                }
                detach(old);
                SESSIONS.remove(controller);
            }
            try {
                View pager = (View) field(controller, "pager");
                ViewGroup parent = (ViewGroup) pager.getParent();
                if (parent == null) return false;
                Context context = pager.getContext();

                Session session = new Session();
                session.originalPager = pager;
                session.parent = parent;
                SESSIONS.put(controller, session);
                pager.setVisibility(View.GONE);

                SharedPreferences prefs = context.getSharedPreferences(PREFS, Context.MODE_PRIVATE);
                String key = prefs.getString(PREF_KEY, "");
                if (key != null && key.matches("[A-Za-z0-9_-]{16,256}")) {
                    showGallery(session, context, key);
                } else {
                    session.shown = buildKeyEntry(session, context);
                    int index = parent.indexOfChild(pager);
                    parent.addView(session.shown, Math.max(0, index + 1),
                            new ViewGroup.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,
                                                       ViewGroup.LayoutParams.MATCH_PARENT));
                }
                if (requestedByPopup) popupGifUntil = 0L;
                return true;
            } catch (Exception ex) {
                Session failed = SESSIONS.remove(controller);
                detach(failed);
                return false;
            }
        }
    }
}
