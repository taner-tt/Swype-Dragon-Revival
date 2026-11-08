package com.swyperevival.klipy;
public final class KlipyEndpointsTest {
  private static void ok(boolean b, String msg){if(!b)throw new AssertionError(msg);}
  private static void rejects(Runnable action){try{action.run();throw new AssertionError("Expected failure");}catch(IllegalArgumentException expected){}}
  public static void main(String[] args){
    String key="abcdefghijklmnopabcdefghijklmnop";
    String s=KlipyEndpoints.search(key,"hej & då");
    ok(s.startsWith("https://api.klipy.com/api/v1/"+key+"/gifs/search?"),"HTTPS endpoint");
    ok(s.contains("q=hej+%26+d%C3%A5"),"UTF-8 query encoding");
    ok(s.contains("locale=se"),"Swedish locale");
    ok(KlipyEndpoints.trending(key).contains("/gifs/trending?"),"Trending");
    rejects(()->KlipyEndpoints.search(key," "));
    rejects(()->KlipyEndpoints.trending("invalid"));
    ok(KlipyEndpoints.media("https://static.klipy.com/gif/x.gif"),"Media host");
    ok(!KlipyEndpoints.media("http://static.klipy.com/gif/x.gif"),"Require HTTPS");
    ok(!KlipyEndpoints.media("https://static.klipy.com.evil.example/x.gif"),"Reject host spoof");
    ok(!KlipyEndpoints.media("https://user@static.klipy.com/x.gif"),"Reject URL credentials");
    System.out.println("PASS KLIPY endpoints and URL validation");
  }
}
