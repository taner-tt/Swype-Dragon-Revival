package com.swyperevival.klipy;
import android.content.Context;
import android.content.ContextWrapper;
import android.content.ClipDescription;
import android.inputmethodservice.InputMethodService;
import android.os.Build;
import android.view.inputmethod.EditorInfo;
import android.view.inputmethod.InputConnection;
import android.view.inputmethod.InputContentInfo;
import android.widget.Toast;
import java.util.Locale;
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
            if(m!=null && (m.equalsIgnoreCase("image/gif") || m.equalsIgnoreCase("image/*") || m.equals("*/*")))return true;
        }
        return false;
    }
    public static boolean send(Context context,KlipyGifClient.Gif gif, String key) {
        if (gif==null || !KlipyEndpoints.media(gif.animation)) return false;
        if(Build.VERSION.SDK_INT<25) {
            Toast.makeText(context,"GIF-skickning kräver Android 7.1 eller senare",Toast.LENGTH_LONG).show();return false;
        }
        InputMethodService ime=service(context);
        if(ime==null) {
            Toast.makeText(context,"Kan inte nå tangentbordets inmatning",Toast.LENGTH_LONG).show();return false;
        }
        InputConnection connection=ime.getCurrentInputConnection();
        EditorInfo info=ime.getCurrentInputEditorInfo();
        if(connection==null || !supportsGif(info)) {
            Toast.makeText(context,"Den här appen stöder inte GIF från tangentbordet",Toast.LENGTH_LONG).show();return false;
        }
        try {
            android.net.Uri uri=KlipyGifStreamProvider.uri(gif.animation);
            InputContentInfo content=new InputContentInfo(uri,new ClipDescription("KLIPY GIF",new String[]{"image/gif"}),null);
            boolean sent=connection.commitContent(content,InputConnection.INPUT_CONTENT_GRANT_READ_URI_PERMISSION,null);
            if(sent) {
                share(key,gif.slug);
            } else Toast.makeText(context,"Appen tog inte emot GIF-filen",Toast.LENGTH_SHORT).show();
            return sent;
        } catch(Exception e) {
            Toast.makeText(context,"Kunde inte skicka GIF",Toast.LENGTH_LONG).show();
            return false;
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
