#!/usr/bin/env python3
"""Patch Swype's language-list request to use a GitHub JSON catalog.

The original download/install/uninstall code remains untouched.
Produces an unsigned experimental APK; never ship as a verified build.
"""
from pathlib import Path
import sys

p = Path(sys.argv[1]) / "smali/com/nuance/connect/service/manager/LanguageManager$LanguageListTransaction.smali"
s = p.read_text()
# Fail closed if the decompiled baseline does not expose the exact bridge API.
response = Path(sys.argv[1]) / "smali/com/nuance/connect/comm/Response.smali"
if not response.exists():
    raise RuntimeError("Response.smali not found; do not build an unverified patch")
r = response.read_text()
required = [
    ("language-list callback", "access$100(", s),
    ("Response status", "->status:I", r),
    ("Response parameters", "->parameters:Ljava/util/HashMap;", r),
]
for label, token, source in required:
    if token not in source:
        raise RuntimeError(f"Missing {label}: {token}. Check the original smali API before patching.")
start = s.index(".method private getList()V")
end = s.index(".end method", start) + len(".end method")
replacement = """.method private getList()V
    .locals 2

    new-instance v0, Lcom/nuance/connect/service/manager/GitHubLanguageCatalog;

    invoke-direct {v0, p0}, Lcom/nuance/connect/service/manager/GitHubLanguageCatalog;-><init>(Lcom/nuance/connect/service/manager/LanguageManager$LanguageListTransaction;)V

    new-instance v1, Ljava/lang/Thread;

    invoke-direct {v1, v0}, Ljava/lang/Thread;-><init>(Ljava/lang/Runnable;)V

    invoke-virtual {v1}, Ljava/lang/Thread;->start()V

    return-void
.end method"""
p.write_text(s[:start] + replacement + s[end:])

out = p.parent / "GitHubLanguageCatalog.smali"
out.write_text(r'''.class public Lcom/nuance/connect/service/manager/GitHubLanguageCatalog;
.super Ljava/lang/Object;
.implements Ljava/lang/Runnable;

.field private final transaction:Lcom/nuance/connect/service/manager/LanguageManager$LanguageListTransaction;

.method public constructor <init>(Lcom/nuance/connect/service/manager/LanguageManager$LanguageListTransaction;)V
    .locals 0
    invoke-direct {p0}, Ljava/lang/Object;-><init>()V
    iput-object p1, p0, Lcom/nuance/connect/service/manager/GitHubLanguageCatalog;->transaction:Lcom/nuance/connect/service/manager/LanguageManager$LanguageListTransaction;
    return-void
.end method

.method public run()V
    .locals 8
    :try_start_0
    new-instance v0, Ljava/net/URL;
    const-string v1, "https://raw.githubusercontent.com/taner-tt/Swype-Dragon-Revival/main/language-packs/nuance-language-list.json"
    invoke-direct {v0, v1}, Ljava/net/URL;-><init>(Ljava/lang/String;)V
    invoke-virtual {v0}, Ljava/net/URL;->openConnection()Ljava/net/URLConnection;
    move-result-object v0
    const/16 v1, 0x2710
    invoke-virtual {v0, v1}, Ljava/net/URLConnection;->setConnectTimeout(I)V
    invoke-virtual {v0, v1}, Ljava/net/URLConnection;->setReadTimeout(I)V
    invoke-virtual {v0}, Ljava/net/URLConnection;->getInputStream()Ljava/io/InputStream;
    move-result-object v0
    new-instance v1, Ljava/io/ByteArrayOutputStream;
    invoke-direct {v1}, Ljava/io/ByteArrayOutputStream;-><init>()V
    const/16 v2, 0x1000
    new-array v2, v2, [B
    :goto_0
    invoke-virtual {v0, v2}, Ljava/io/InputStream;->read([B)I
    move-result v3
    if-ltz v3, :cond_0
    const/4 v4, 0x0
    invoke-virtual {v1, v2, v4, v3}, Ljava/io/ByteArrayOutputStream;->write([BII)V
    goto :goto_0
    :cond_0
    invoke-virtual {v0}, Ljava/io/InputStream;->close()V
    new-instance v0, Ljava/lang/String;
    invoke-virtual {v1}, Ljava/io/ByteArrayOutputStream;->toByteArray()[B
    move-result-object v1
    const-string v2, "UTF-8"
    invoke-direct {v0, v1, v2}, Ljava/lang/String;-><init>([BLjava/lang/String;)V
    new-instance v1, Lorg/json/JSONObject;
    invoke-direct {v1, v0}, Lorg/json/JSONObject;-><init>(Ljava/lang/String;)V
    const-string v0, "43"
    invoke-virtual {v1, v0}, Lorg/json/JSONObject;->getJSONArray(Ljava/lang/String;)Lorg/json/JSONArray;
    move-result-object v1
    new-instance v2, Lcom/nuance/connect/comm/Response;
    invoke-direct {v2}, Lcom/nuance/connect/comm/Response;-><init>()V
    const/4 v3, 0x1
    iput v3, v2, Lcom/nuance/connect/comm/Response;->status:I
    new-instance v3, Ljava/util/HashMap;
    invoke-direct {v3}, Ljava/util/HashMap;-><init>()V
    invoke-virtual {v3, v0, v1}, Ljava/util/HashMap;->put(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;
    iput-object v3, v2, Lcom/nuance/connect/comm/Response;->parameters:Ljava/util/HashMap;
    iget-object v0, p0, Lcom/nuance/connect/service/manager/GitHubLanguageCatalog;->transaction:Lcom/nuance/connect/service/manager/LanguageManager$LanguageListTransaction;
    invoke-static {v0, v2}, Lcom/nuance/connect/service/manager/LanguageManager$LanguageListTransaction;->access$100(Lcom/nuance/connect/service/manager/LanguageManager$LanguageListTransaction;Lcom/nuance/connect/comm/Response;)V
    :try_end_0
    .catch Ljava/lang/Exception; {:try_start_0 .. :try_end_0} :catch_0
    return-void
    :catch_0
    move-exception v0
    const-string v1, "SwypeGitHubLanguages"
    const-string v2, "Could not retrieve language catalog"
    invoke-static {v1, v2, v0}, Landroid/util/Log;->e(Ljava/lang/String;Ljava/lang/String;Ljava/lang/Throwable;)I
    return-void
.end method
''')
print("Patched", p, "and created", out)
