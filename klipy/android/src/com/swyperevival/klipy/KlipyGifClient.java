package com.swyperevival.klipy;
import android.os.Handler;import android.os.Looper;import org.json.*;import java.net.*;import java.io.*;import java.util.*;import java.util.concurrent.*;
public final class KlipyGifClient {
 public interface Callback {void success(List<Gif> gifs);void failure(String msg);}
 public static final class Gif {public final String slug,title,thumbnail,animation;Gif(String s,String t,String th,String a){slug=s;title=t;thumbnail=th;animation=a;}}
 private final ExecutorService executor=Executors.newSingleThreadExecutor();
 private final Handler main=new Handler(Looper.getMainLooper());
 private final String key;
 public KlipyGifClient(String key){this.key=key;}
 public void trending(Callback cb){load(KlipyEndpoints.trending(key),cb);}
 public void search(String q,Callback cb){load(KlipyEndpoints.search(key,q),cb);}
 private static String file(JSONObject o,String size,String type){JSONObject a=o==null?null:o.optJSONObject(size);JSONObject b=a==null?null:a.optJSONObject(type);return b==null?"":b.optString("url","");}
 private static List<Gif> parse(JSONObject root)throws Exception {
  if(!root.optBoolean("result"))throw new IOException("API failure");
  JSONObject d=root.optJSONObject("data");JSONArray items=d==null?null:d.optJSONArray("data");if(items==null)throw new IOException("Unexpected schema");
  ArrayList<Gif> out=new ArrayList<>();
  for(int i=0;i<items.length();i++){JSONObject item=items.optJSONObject(i);if(item==null)throw new IOException("Invalid item");
   // Never silently drop sponsored entries: block until a provider-compliant ad renderer exists.
   if("ad".equalsIgnoreCase(item.optString("type")))throw new IOException("Sponsored results require renderer");
   JSONObject f=item.optJSONObject("file");String animation=file(f,"hd","gif");if(!KlipyEndpoints.media(animation))animation=file(f,"sm","gif");
   if(!KlipyEndpoints.media(animation))throw new IOException("Unknown media host");
   String thumb=file(f,"sm","webp");if(!KlipyEndpoints.media(thumb))thumb=file(f,"sm","gif");if(!KlipyEndpoints.media(thumb))thumb=animation;
   out.add(new Gif(item.optString("slug"),item.optString("title"),thumb,animation));
  }return out;
 }
 private void load(String endpoint,Callback cb){executor.execute(()->{
  HttpURLConnection c=null;try{
   c=(HttpURLConnection)new URL(endpoint).openConnection();c.setConnectTimeout(7000);c.setReadTimeout(12000);c.setInstanceFollowRedirects(false);c.setRequestProperty("Accept","application/json");
   if(c.getResponseCode()!=200)throw new IOException("HTTP");
   ByteArrayOutputStream bytes=new ByteArrayOutputStream();try(InputStream in=c.getInputStream()){byte[] b=new byte[8192];int n;while((n=in.read(b))!=-1){if(bytes.size()+n>2000000)throw new IOException("Too large");bytes.write(b,0,n);}}
   List<Gif> out=parse(new JSONObject(bytes.toString("UTF-8")));main.post(()->cb.success(out));
  }catch(Exception e){main.post(()->cb.failure("Kunde inte hämta GIF:ar."));}finally{if(c!=null)c.disconnect();}
 });}
 public void close(){executor.shutdownNow();}
}
