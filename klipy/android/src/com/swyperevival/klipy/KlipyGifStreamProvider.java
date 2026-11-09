package com.swyperevival.klipy;
import android.content.ContentProvider;
import android.content.ContentValues;
import android.database.Cursor;
import android.net.Uri;
import android.os.ParcelFileDescriptor;
import java.io.InputStream;
import java.io.OutputStream;
import java.io.IOException;
import java.net.HttpURLConnection;
import java.net.URL;

/** One-time streaming bridge to receiving apps. Does not cache KLIPY media on disk. */
public final class KlipyGifStreamProvider extends ContentProvider {
    public static final String AUTHORITY = "com.nuance.swype.dtc.klipy.gif";
    public static Uri uri(String mediaUrl) {
        if (!KlipyEndpoints.media(mediaUrl)) throw new IllegalArgumentException("Untrusted media URL");
        return new Uri.Builder().scheme("content").authority(AUTHORITY).appendPath("stream")
                .appendQueryParameter("url", mediaUrl).build();
    }
    @Override public boolean onCreate(){ return true; }
    @Override public String getType(Uri uri){ return "image/gif"; }
    @Override public Cursor query(Uri uri,String[] columns,String filter,String[] args,String order){return null;}
    @Override public Uri insert(Uri uri, ContentValues vals){throw new UnsupportedOperationException();}
    @Override public int delete(Uri uri,String where,String[] args){throw new UnsupportedOperationException();}
    @Override public int update(Uri uri,ContentValues vals,String where,String[] args){throw new UnsupportedOperationException();}
    @Override public ParcelFileDescriptor openFile(Uri requested,String mode) throws java.io.FileNotFoundException {
        if (!"r".equals(mode) || requested==null || !"stream".equals(requested.getLastPathSegment())
            || !AUTHORITY.equals(requested.getAuthority()))throw new java.io.FileNotFoundException("Invalid GIF URI");
        String url=requested.getQueryParameter("url");
        if (!KlipyEndpoints.media(url))throw new java.io.FileNotFoundException("Untrusted GIF");
        try {
            ParcelFileDescriptor[] pipe=ParcelFileDescriptor.createPipe();
            new Thread(() -> {
                HttpURLConnection conn=null;
                try (OutputStream out=new ParcelFileDescriptor.AutoCloseOutputStream(pipe[1])) {
                    conn=(HttpURLConnection)new URL(url).openConnection();
                    conn.setConnectTimeout(8000);conn.setReadTimeout(15000);
                    conn.setInstanceFollowRedirects(false);
                    if (conn.getResponseCode()!=200)throw new IOException("Bad status");
                    int bytes=0;
                    try (InputStream in=conn.getInputStream()) {
                        byte[] buf=new byte[16384];
                        int n;
                        while ((n=in.read(buf))!=-1) {
                            bytes+=n;
                            if(bytes>16*1024*1024)throw new IOException("GIF too large");
                            out.write(buf,0,n);
                        }
                    }
                } catch (IOException ignored) {
                    try{pipe[1].close();}catch(IOException ignoredClose){}
                } finally {if(conn!=null)conn.disconnect();}
            },"SwypeKLIPY-GIF-Stream").start();
            return pipe[0];
        }catch(IOException e){throw new java.io.FileNotFoundException("Cannot open GIF stream");}
    }
}
