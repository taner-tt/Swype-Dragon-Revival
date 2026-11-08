package com.swyperevival.klipy;
import android.content.Context;import android.graphics.Color;import android.view.*;import android.view.inputmethod.EditorInfo;import android.webkit.*;import android.widget.*;import java.util.*;
public final class KlipyGifPanel extends LinearLayout {
 public interface OnSelect {void selected(KlipyGifClient.Gif gif);}
 private final KlipyGifClient client;private final EditText search;private final TextView status;private final WebView web;private final OnSelect callback;
 private List<KlipyGifClient.Gif> visible=new ArrayList<>();private int generation=0;private boolean closed=false;
 public KlipyGifPanel(Context context,String key,OnSelect callback){super(context);this.callback=callback;client=new KlipyGifClient(key);
  setOrientation(VERTICAL);setPadding(8,8,8,8);setBackgroundColor(0xff121212);
  LinearLayout header=new LinearLayout(context);search=new EditText(context);search.setSingleLine(true);search.setTextColor(Color.WHITE);search.setHintTextColor(0xffaaaaaa);search.setHint("Search KLIPY");search.setImeOptions(EditorInfo.IME_ACTION_SEARCH);
  header.addView(search,new LayoutParams(0,50,1));Button go=new Button(context);go.setText("Sök");header.addView(go,new LayoutParams(75,50));addView(header);
  status=new TextView(context);status.setTextColor(Color.WHITE);addView(status);
  web=new WebView(context);web.setBackgroundColor(0xff121212);web.getSettings().setJavaScriptEnabled(false);web.getSettings().setAllowFileAccess(false);web.getSettings().setAllowContentAccess(false);web.getSettings().setCacheMode(WebSettings.LOAD_NO_CACHE);
  web.setWebViewClient(new WebViewClient(){@Override public boolean shouldOverrideUrlLoading(WebView v,String u){return clicked(u);}@Override public boolean shouldOverrideUrlLoading(WebView v,WebResourceRequest r){return clicked(r.getUrl().toString());}});
  addView(web,new LayoutParams(-1,0,1));TextView attribution=new TextView(context);attribution.setGravity(Gravity.CENTER);attribution.setTextColor(Color.WHITE);attribution.setText("Powered by KLIPY");addView(attribution);
  go.setOnClickListener(v->find());search.setOnEditorActionListener((v,a,e)->{if(a==EditorInfo.IME_ACTION_SEARCH){find();return true;}return false;});trending();
 }
 public void trending(){int token=++generation;status.setText("Laddar GIF:ar...");client.trending(new KlipyGifClient.Callback(){public void success(List<KlipyGifClient.Gif> g){display(token,g);}public void failure(String e){error(token,e);}});}
 private void find(){String q=search.getText().toString().trim();if(q.isEmpty()){trending();return;}int token=++generation;status.setText("Söker...");client.search(q,new KlipyGifClient.Callback(){public void success(List<KlipyGifClient.Gif> g){display(token,g);}public void failure(String e){error(token,e);}});}
 private void error(int token,String e){if(closed||token!=generation)return;status.setText(e);visible.clear();web.loadDataWithBaseURL("https://api.klipy.com/","<html><body style='background:#121212'></body></html>","text/html","UTF-8",null);}
 private static String escape(String s){if(s==null)return "";return s.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;").replace("'","&#39;").replace("\"","&quot;");}
 private void display(int token,List<KlipyGifClient.Gif> gifs){if(closed||token!=generation)return;visible=new ArrayList<>(gifs);status.setText(gifs.size()+" GIF:ar");
  StringBuilder b=new StringBuilder("<html><head><meta name='viewport' content='width=device-width,initial-scale=1'><meta http-equiv='Content-Security-Policy' content=\"default-src 'none'; img-src https://static.klipy.com https://static1.klipy.com https://static2.klipy.com; style-src 'unsafe-inline'\"><style>body{background:#121212;margin:0}.g{display:grid;grid-template-columns:repeat(2,1fr);gap:6px}img{width:100%;height:110px;object-fit:cover}</style></head><body><div class='g'>");
  for(int i=0;i<gifs.size();i++)b.append("<a href='swypegif://item/").append(i).append("'><img src='").append(escape(gifs.get(i).thumbnail)).append("'></a>");
  b.append("</div></body></html>");web.loadDataWithBaseURL("https://api.klipy.com/",b.toString(),"text/html","UTF-8",null);
 }
 private boolean clicked(String url){if(url==null||!url.startsWith("swypegif://item/"))return true;try{int i=Integer.parseInt(url.substring(16));if(!closed&&i>=0&&i<visible.size()&&callback!=null)callback.selected(visible.get(i));}catch(Exception ignored){}return true;}
 public void close(){closed=true;++generation;client.close();web.stopLoading();web.destroy();}
}
