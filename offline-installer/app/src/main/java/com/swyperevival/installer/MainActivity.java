package com.swyperevival.installer;

import android.app.Activity;
import android.os.Bundle;
import android.content.Intent;
import android.net.Uri;
import android.widget.*;
import java.io.*;
import java.util.*;
import java.util.zip.*;

/** Offline selection UI. Exports selected language packs through Android's document picker.
 * Direct import into Swype needs a receiving component in the modified Swype app. */
public class MainActivity extends Activity {
    private final ArrayList<String> selected = new ArrayList<>();
    private final ArrayList<String> languages = new ArrayList<>();
    private TextView status;
    private static final int SAVE = 42;
    @Override public void onCreate(Bundle b) {
        super.onCreate(b);
        LinearLayout root = new LinearLayout(this); root.setOrientation(LinearLayout.VERTICAL);root.setPadding(20,20,20,20);
        TextView title=new TextView(this);title.setText("Swype Language Installer — offline");title.setTextSize(22);root.addView(title);
        TextView note=new TextView(this);note.setText("Välj språk. Exportera valda paket till en ZIP-fil. Direkt installation i Swype kräver att Swype-appen får en importfunktion.");root.addView(note);
        status=new TextView(this);root.addView(status);
        Button all=new Button(this);all.setText("Markera alla / avmarkera alla");root.addView(all);
        ScrollView scroll=new ScrollView(this); LinearLayout choices=new LinearLayout(this);choices.setOrientation(LinearLayout.VERTICAL);scroll.addView(choices);
        root.addView(scroll,new LinearLayout.LayoutParams(-1,0,1));
        try { for(String f:getAssets().list("packs")) if(f.endsWith(".zip"))languages.add(f.substring(0,f.length()-4));Collections.sort(languages); }
        catch(IOException e){status.setText("Kunde inte läsa språk: "+e.getMessage());}
        ArrayList<CheckBox> boxes=new ArrayList<>();
        for(String lang:languages){CheckBox cb=new CheckBox(this);cb.setText(lang);choices.addView(cb);boxes.add(cb);cb.setOnCheckedChangeListener((v,checked)->{if(checked&&!selected.contains(lang))selected.add(lang);if(!checked)selected.remove(lang);refresh();});}
        all.setOnClickListener(v->{boolean check=selected.size()!=languages.size();for(CheckBox cb:boxes)cb.setChecked(check);});
        Button export=new Button(this);export.setText("Exportera valda språk");root.addView(export);
        export.setOnClickListener(v->{if(selected.isEmpty()){Toast.makeText(this,"Välj minst ett språk",Toast.LENGTH_SHORT).show();return;}Intent i=new Intent(Intent.ACTION_CREATE_DOCUMENT);i.addCategory(Intent.CATEGORY_OPENABLE);i.setType("application/zip");i.putExtra(Intent.EXTRA_TITLE,"Swype-valda-sprak.zip");startActivityForResult(i,SAVE);});
        setContentView(root);refresh();
    }
    private void refresh(){if(status!=null)status.setText("Valda: "+selected.size()+" / "+languages.size());}
    @Override protected void onActivityResult(int request,int result,Intent data){super.onActivityResult(request,result,data);if(request!=SAVE||result!=RESULT_OK||data==null)return;
        Uri uri=data.getData();if(uri==null)return;ArrayList<String> snapshot=new ArrayList<>(selected);
        status.setText("Exporterar "+snapshot.size()+" språk ...");
        new Thread(()->{String message;try(OutputStream output=getContentResolver().openOutputStream(uri);ZipOutputStream zip=new ZipOutputStream(new BufferedOutputStream(output))){
            byte[] buffer=new byte[65536];for(String name:snapshot){String file=name+".zip";zip.putNextEntry(new ZipEntry(file));try(InputStream in=getAssets().open("packs/"+file)){int n;while((n=in.read(buffer))!=-1)zip.write(buffer,0,n);}zip.closeEntry();}message="Exporterat "+snapshot.size()+" språkpaket. Direkt import i Swype är ännu inte implementerad.";
        }catch(Exception e){message="Export misslyckades: "+e.getMessage();}final String m=message;runOnUiThread(()->status.setText(m));}).start();
    }
}
