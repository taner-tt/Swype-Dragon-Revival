package com.swyperevival.klipy;
import android.content.Context;
import android.content.ContextWrapper;
import android.content.ClipDescription;
import android.content.ClipData;
import android.content.Intent;
import android.inputmethodservice.InputMethodService;
import android.os.Build;
import android.view.inputmethod.EditorInfo;
import android.view.inputmethod.InputConnection;
import android.view.inputmethod.InputContentInfo;
import android.widget.Toast;
import java.lang.ref.WeakReference;
import java.net.HttpURLConnection;
import java.net.URL;

/** Sends GIF content URIs with the Android IME grant flag on supported receivers. */
public final class KlipyGifSender {
    private static volatile WeakReference<InputMethodService> activeIme = new WeakReference<>(null);
    private KlipyGifSender(){}
    /** Called from the actual Swype IME lifecycle, not from the themed GIF view context. */
    public static void bindService(InputMethodService ime) {
        if (ime != null) activeIme = new WeakReference<>(ime);
    }
    private static InputMethodService service(Context ctx) {
        InputMethodService bound = activeIme.get();
        if (bound != null) return bound;
        for (int i=0;i<12 && ctx!=null;i++) {
            if(ctx instanceof InputMethodService)return (InputMethodService)ctx;
            if(!(ctx instanceof ContextWrapper))break;
            Context next=((ContextWrapper)ctx).getBaseContext();
            if(next==ctx)break;
            ctx=next;
        }
        return null;
    }
    private static boolean supportsGif(EditorInfo editor) {
        if(editor==null || editor.contentMimeTypes==null)return false;
        for(String m : editor.contentMimeTypes) {
            if(m!=null && ClipDescription.compareMimeTypes(m,"image/gif"))return true;
        }
        return false;
    }
    /** Open Android's share chooser when the receiving editor cannot accept rich IME content. */
    private static boolean chooser(Context context, KlipyGifClient.Gif gif) {
        try {
            android.net.Uri uri = KlipyGifStreamProvider.uri(gif.animation);
            Intent send = new Intent(Intent.ACTION_SEND);
            send.setType("image/gif");
            send.putExtra(Intent.EXTRA_STREAM, uri);
            send.setClipData(ClipData.newRawUri("KLIPY GIF", uri));
            send.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION);
            Intent chooser = Intent.createChooser(send, "Dela GIF");
            chooser.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_GRANT_READ_URI_PERMISSION);
            context.startActivity(chooser);
            return true;
        } catch (Exception e) {
            Toast.makeText(context, "Kan inte öppna Androids GIF-delning", Toast.LENGTH_LONG).show();
            return false;
        }
    }

    public static boolean send(Context context,KlipyGifClient.Gif gif, String key) {
        if (gif == null || !KlipyEndpoints.media(gif.animation)) return false;
        if (Build.VERSION.SDK_INT < 25) {
            Toast.makeText(context, "Öppnar Androids delning för denna app", Toast.LENGTH_SHORT).show();
            return chooser(context, gif);
        }

        InputMethodService ime = service(context);
        InputConnection connection = ime == null ? null : ime.getCurrentInputConnection();
        EditorInfo info = ime == null ? null : ime.getCurrentInputEditorInfo();
        if (connection == null || !supportsGif(info)) {
            // Some chat editors support sharing GIF files but do not advertise
            // support for InputConnection.commitContent. Never claim success.
            Toast.makeText(context, "GIF direkt stöds inte här – välj app i Dela", Toast.LENGTH_SHORT).show();
            return chooser(context, gif);
        }
        try {
            android.net.Uri uri = KlipyGifStreamProvider.uri(gif.animation);
            InputContentInfo content = new InputContentInfo(
                    uri, new ClipDescription("KLIPY GIF", new String[]{"image/gif"}), null);
            boolean sent = connection.commitContent(
                    content, InputConnection.INPUT_CONTENT_GRANT_READ_URI_PERMISSION, null);
            if (sent) {
                share(key, gif.slug);
                return true;
            }
            Toast.makeText(context, "Appen tog inte emot GIF direkt – välj Dela", Toast.LENGTH_SHORT).show();
            return chooser(context, gif);
        } catch (Exception e) {
            Toast.makeText(context, "Direkt GIF-skickning misslyckades – välj Dela", Toast.LENGTH_SHORT).show();
            return chooser(context, gif);
        }
    }
    private static void share(String key,String slug) {
        if(key==null || !key.matches("[A-Za-z0-9_-]{16,256}")||slug==null||!slug.matches("[A-Za-z0-9_-]{1,200}"))return;
        new Thread(() -> {
            HttpURLConnection conn=null;
            try {
                conn=(HttpURLConnection)new URL("https://api.klipy.com/api/v1/"+key+"/gifs/share/"+slug).openConnection();
                conn.setRequestMethod("POST");
                conn.setConnectTimeout(5000);conn.setReadTimeout(5000);conn.setInstanceFollowRedirects(false);
                conn.getResponseCode();
            } catch(Exception ignored) {} finally {if(conn!=null)conn.disconnect();}
        },"SwypeKLIPY-Share").start();
    }
}
