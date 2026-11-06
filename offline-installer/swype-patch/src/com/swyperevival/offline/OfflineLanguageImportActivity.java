package com.swyperevival.offline;

import android.app.Activity;
import android.content.Intent;
import android.net.Uri;
import android.os.Bundle;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.TextView;
import com.nuance.swype.connect.LanguageInstall;
import com.nuance.swype.input.LanguageList;
import com.nuance.swype.input.DatabaseConfig;
import com.nuance.swype.input.IMEApplication;
import java.io.*;
import java.util.zip.*;

/**
 * Runs inside the modified Swype package and therefore has access to Swype's
 * private files. User explicitly selects a ZIP exported by the companion app.
 */
public final class OfflineLanguageImportActivity extends Activity {
    private static final int PICK_ZIP = 901;
    private static final long MAX_PACK = 100L * 1024 * 1024;
    private static final long MAX_TOTAL = 1024L * 1024 * 1024;
    private TextView status;

    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setPadding(24,24,24,24);
        status = new TextView(this);
        status.setText("Importera språk som exporterats från Swype Language Installer. Välj ZIP-filen.");
        root.addView(status);
        Button pick = new Button(this);
        pick.setText("Välj språkfil och installera");
        root.addView(pick);
        pick.setOnClickListener(v -> {
            Intent intent = new Intent(Intent.ACTION_OPEN_DOCUMENT);
            intent.setType("application/zip");
            intent.addCategory(Intent.CATEGORY_OPENABLE);
            startActivityForResult(intent, PICK_ZIP);
        });
        setContentView(root);
    }

    @Override protected void onActivityResult(int request, int result, Intent data) {
        super.onActivityResult(request, result, data);
        if (request != PICK_ZIP || result != RESULT_OK || data == null || data.getData() == null) return;
        Uri uri = data.getData();
        status.setText("Installerar språk ...");
        new Thread(() -> {
            String resultText;
            try { resultText = importArchive(uri); }
            catch (Exception ex) { resultText = "Import misslyckades: " + ex.getMessage(); }
            final String message = resultText;
            runOnUiThread(() -> status.setText(message));
        }).start();
    }

    private String importArchive(Uri uri) throws Exception {
        int count = 0;
        long total = 0;
        byte[] buffer = new byte[65536];
        try (InputStream source = getContentResolver().openInputStream(uri);
             ZipInputStream zip = new ZipInputStream(new BufferedInputStream(source))) {
            ZipEntry entry;
            while ((entry = zip.getNextEntry()) != null) {
                if (entry.isDirectory()) continue;
                String name = entry.getName();
                if (!name.matches("[A-Za-z][A-Za-z0-9_-]{0,80}\\.zip")) throw new IOException("Ogiltigt paketnamn: " + name);
                if (++count > 150) throw new IOException("För många språkpaket");
                String language = name.substring(0, name.length() - 4);
                File temp = File.createTempFile("swype-offline-", ".zip", getCacheDir());
                try {
                    long size = 0;
                    try (FileOutputStream out = new FileOutputStream(temp)) {
                        int n;
                        while ((n = zip.read(buffer)) != -1) {
                            size += n;
                            total += n;
                            if (size > MAX_PACK || total > MAX_TOTAL) throw new IOException("Paket för stort");
                            out.write(buffer, 0, n);
                        }
                    }
                    // Check inner ZIP structure before handing it to Swype's own installer.
                    boolean metadata = false;
                    try (ZipFile inner = new ZipFile(temp)) {
                        for (java.util.Enumeration<? extends ZipEntry> e = inner.entries(); e.hasMoreElements();) {
                            ZipEntry item = e.nextElement();
                            String part = item.getName();
                            if (part.startsWith("/") || part.contains("..") || part.contains("\\")) throw new IOException("Ogiltig sökväg");
                            if (part.equals(language + ".mdf")) metadata = true;
                        }
                    }
                    if (!metadata) throw new IOException("Saknar " + language + ".mdf");
                    // Existing Swype installation routine; its compatibility still requires device testing.
                    boolean installed = new LanguageInstall(language, this).install(temp.getAbsolutePath());
                    if (!installed || !new File(getFilesDir(), language + ".mdf").isFile()) throw new IOException("Swype installer did not deploy metadata for " + language);
                    new LanguageList(this).addDownloadedLanguage(language);
                    DatabaseConfig.updateLanguage(this, language);
                    IMEApplication.from(this).refreshInputMethods();
                } finally { temp.delete(); }
            }
        }
        if (count == 0) throw new IOException("Inga språkpaket i ZIP-filen");
        return "Installerade " + count + " språk. Kontrollera och aktivera dem i Swypes språkmeny.";
    }
}
