package com.swyperevival.klipy;
import java.net.*;
import java.util.Locale;
public final class KlipyEndpoints {
 private KlipyEndpoints(){}
 private static String enc(String v){try{return URLEncoder.encode(v,"UTF-8");}catch(Exception e){throw new IllegalArgumentException(e);}}
 private static String base(String key){if(key==null||!key.matches("[A-Za-z0-9_-]{16,256}"))throw new IllegalArgumentException("Invalid key");return "https://api.klipy.com/api/v1/"+key+"/gifs/";}
 private static String params(int page,int count,String locale){if(page<1||page>1000||count<8||count>50||locale==null||!locale.matches("[A-Za-z]{2}"))throw new IllegalArgumentException("Parameters");return "page="+page+"&per_page="+count+"&locale="+enc(locale.toLowerCase(Locale.ROOT));}
 public static String trending(String key){return base(key)+"trending?"+params(1,24,"se");}
 public static String search(String key,String query){if(query==null||query.trim().isEmpty()||query.length()>200)throw new IllegalArgumentException("Query");return base(key)+"search?"+params(1,24,"se")+"&q="+enc(query);}
 public static boolean media(String raw){try{URI u=new URI(raw);String h=u.getHost();return "https".equalsIgnoreCase(u.getScheme())&&u.getUserInfo()==null&&(u.getPort()<0||u.getPort()==443)&&("static.klipy.com".equals(h)||"static1.klipy.com".equals(h)||"static2.klipy.com".equals(h));}catch(Exception e){return false;}}
}
