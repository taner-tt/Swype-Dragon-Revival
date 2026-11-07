#!/usr/bin/env python3
"""Patch Swype's language-list request to use a GitHub JSON catalog.

The original download/install/uninstall code remains untouched.
Produces an unsigned experimental APK; never ship as a verified build.
"""
from pathlib import Path
import sys

# A catalog with no downloadable packs cannot complete a usable language refresh.
# Fail the release build rather than silently leaving the transaction pending.
import json
catalog = Path(__file__).with_name("nuance-language-list.json")
entries = json.loads(catalog.read_text(encoding="utf-8")).get("43")
if not isinstance(entries, list) or not entries:
    raise RuntimeError("GitHub language catalog has no verified downloadable packs; refusing to produce a misleading installable APK")
# These are the literal Nuance JSON field identifiers consumed by listResponse().
# In particular checksum 10 is MD5, not the SHA-256 used by the public manifest.
from urllib.parse import urlparse
import re
for index, entry in enumerate(entries):
    required = ("11", "20", "51", "10", "122", "124", "146")
    if not isinstance(entry, dict) or any(k not in entry for k in required):
        raise RuntimeError(f"Language entry {index} is missing required Nuance fields")
    if not any(k in entry for k in ("102", "103", "104", "105")):
        raise RuntimeError(f"Language entry {index} has no core version")
    if not isinstance(entry["146"], list) or not entry["146"] or not all(isinstance(x, int) for x in entry["146"]):
        raise RuntimeError(f"Language entry {index} has invalid language IDs")
    if not isinstance(entry["10"], str) or not re.fullmatch(r"[0-9a-fA-F]{32}", entry["10"]):
        raise RuntimeError(f"Language entry {index} requires a 32-digit MD5 checksum")
    url = urlparse(str(entry["51"]))
    if url.scheme != "https" or url.hostname not in ("github.com", "raw.githubusercontent.com", "objects.githubusercontent.com"):
        raise RuntimeError(f"Language entry {index} has an unapproved download URL")

p = Path(sys.argv[1]) / "smali/com/nuance/connect/service/manager/LanguageManager$LanguageListTransaction.smali"
s = p.read_text()
# Fail closed if the decompiled baseline does not expose the exact bridge API.
response = Path(sys.argv[1]) / "smali/com/nuance/connect/comm/Response.smali"
if not response.exists():
    raise RuntimeError("Response.smali not found; do not build an unverified patch")
r = response.read_text()
required = [
    ("language-list callback", "access$100(", s),
    ("Response status", ".field public status:I", r),
    ("Response parameters", ".field public parameters:Ljava/util/HashMap;", r),
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

# The old queue sees currentCommand == null and ends this transaction before
# the GitHub worker has finished. Avoid enqueueing this list-only transaction.
# The bridge itself calls listResponse() and onEndProcessing() once it finishes.
# Other transactions (download/install/uninstall) still use original Swype logic.
manager = Path(sys.argv[1]) / "smali/com/nuance/connect/service/manager/LanguageManager.smali"
if not manager.exists():
    raise RuntimeError("LanguageManager.smali missing; cannot isolate list transaction from legacy queue")
manager_smali = manager.read_text()
request_start = manager_smali.index(".method public requestLanguagesList(Ljava/lang/String;)V")
request_end = manager_smali.index(".end method", request_start) + len(".end method")
request = manager_smali[request_start:request_end]
old_queue_call = "    invoke-virtual {p0, v0}, Lcom/nuance/connect/service/manager/LanguageManager;->startTransaction(Lcom/nuance/connect/comm/Transaction;)V"
if request.count(old_queue_call) != 1:
    raise RuntimeError("Unexpected requestLanguagesList queue path; stopping patch")
manager_smali = manager_smali[:request_start] + request.replace(old_queue_call, "    # GitHub worker completes this list transaction; no Nuance command queue.") + manager_smali[request_end:]
manager.write_text(manager_smali)

out = p.parent / "GitHubLanguageCatalog.smali"
out.write_text(r'''.class public Lcom/nuance/connect/service/manager/GitHubLanguageCatalog;
.super Ljava/lang/Object;
.implements Ljava/lang/Runnable;

.field private final transaction:Lcom/nuance/connect/service/manager/LanguageManager$LanguageListTransaction;
.field private static final inFlight:Ljava/util/concurrent/atomic/AtomicBoolean;

.method static constructor <clinit>()V
    .locals 1
    new-instance v0, Ljava/util/concurrent/atomic/AtomicBoolean;
    invoke-direct {v0}, Ljava/util/concurrent/atomic/AtomicBoolean;-><init>()V
    sput-object v0, Lcom/nuance/connect/service/manager/GitHubLanguageCatalog;->inFlight:Ljava/util/concurrent/atomic/AtomicBoolean;
    return-void
.end method

.method public constructor <init>(Lcom/nuance/connect/service/manager/LanguageManager$LanguageListTransaction;)V
    .locals 0
    invoke-direct {p0}, Ljava/lang/Object;-><init>()V
    iput-object p1, p0, Lcom/nuance/connect/service/manager/GitHubLanguageCatalog;->transaction:Lcom/nuance/connect/service/manager/LanguageManager$LanguageListTransaction;
    return-void
.end method

.method public run()V
    .locals 8
    # Allow only one remote refresh at a time; duplicate requests acknowledge
    # without disturbing cached language metadata.
    sget-object v6, Lcom/nuance/connect/service/manager/GitHubLanguageCatalog;->inFlight:Ljava/util/concurrent/atomic/AtomicBoolean;
    const/4 v7, 0x0
    const/4 v5, 0x1
    invoke-virtual {v6, v7, v5}, Ljava/util/concurrent/atomic/AtomicBoolean;->compareAndSet(ZZ)Z
    move-result v6
    if-nez v6, :start_request
    invoke-direct {p0}, Lcom/nuance/connect/service/manager/GitHubLanguageCatalog;->completeWithoutCatalog()V
    return-void
    :start_request
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
    invoke-virtual {v1}, Ljava/io/ByteArrayOutputStream;->size()I
    move-result v4
    const/high16 v5, 0x100000
    if-le v4, v5, :goto_0
    new-instance v4, Ljava/io/IOException;
    const-string v5, "Language catalog larger than 1 MiB"
    invoke-direct {v4, v5}, Ljava/io/IOException;-><init>(Ljava/lang/String;)V
    throw v4
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
    # Reject empty catalogs: original listResponse marks them as no-download state.
    invoke-virtual {v1}, Lorg/json/JSONArray;->length()I
    move-result v4
    if-lez v4, :cond_empty_catalog
    # Reject malformed/incomplete packages before listResponse() starts a
    # metadata transaction. A malformed list must not partially replace state.
    invoke-static {v1}, Lcom/nuance/connect/service/manager/GitHubLanguageCatalog;->isCatalogValid(Lorg/json/JSONArray;)Z
    move-result v4
    if-eqz v4, :cond_empty_catalog
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
    :cond_empty_catalog
    # Only a nonempty catalog can update downloadable-language metadata.
    # An empty response leaves the previous catalog untouched.
    if-lez v4, :fallback
    iget-object v0, p0, Lcom/nuance/connect/service/manager/GitHubLanguageCatalog;->transaction:Lcom/nuance/connect/service/manager/LanguageManager$LanguageListTransaction;
    invoke-virtual {v0}, Lcom/nuance/connect/service/manager/LanguageManager$LanguageListTransaction;->onEndProcessing()V
    :try_end_0
    .catch Ljava/lang/Exception; {:try_start_0 .. :try_end_0} :catch_0
    invoke-static {}, Lcom/nuance/connect/service/manager/GitHubLanguageCatalog;->releaseInFlight()V
    return-void
    :fallback
    :try_start_fallback
    invoke-direct {p0}, Lcom/nuance/connect/service/manager/GitHubLanguageCatalog;->completeWithoutCatalog()V
    :try_end_fallback
    .catch Ljava/lang/Exception; {:try_start_fallback .. :try_end_fallback} :catch_1
    invoke-static {}, Lcom/nuance/connect/service/manager/GitHubLanguageCatalog;->releaseInFlight()V
    return-void
    :catch_0
    move-exception v0
    const-string v1, "SwypeGitHubLanguages"
    const-string v2, "Could not retrieve language catalog"
    invoke-static {v1, v2, v0}, Landroid/util/Log;->e(Ljava/lang/String;Ljava/lang/String;Ljava/lang/Throwable;)I
    :try_start_error
    invoke-direct {p0}, Lcom/nuance/connect/service/manager/GitHubLanguageCatalog;->completeWithoutCatalog()V
    :try_end_error
    .catch Ljava/lang/Exception; {:try_start_error .. :try_end_error} :catch_1
    invoke-static {}, Lcom/nuance/connect/service/manager/GitHubLanguageCatalog;->releaseInFlight()V
    return-void
    :catch_1
    move-exception v0
    const-string v1, "SwypeGitHubLanguages"
    const-string v2, "Language transaction fallback failed"
    invoke-static {v1, v2, v0}, Landroid/util/Log;->e(Ljava/lang/String;Ljava/lang/String;Ljava/lang/Throwable;)I
    invoke-static {}, Lcom/nuance/connect/service/manager/GitHubLanguageCatalog;->releaseInFlight()V
    return-void
.end method

.method private static releaseInFlight()V
    .locals 2
    sget-object v0, Lcom/nuance/connect/service/manager/GitHubLanguageCatalog;->inFlight:Ljava/util/concurrent/atomic/AtomicBoolean;
    const/4 v1, 0x0
    invoke-virtual {v0, v1}, Ljava/util/concurrent/atomic/AtomicBoolean;->set(Z)V
    return-void
.end method

# Guard the entire list before handing it to Swype's transactional parser.
# The original parser commits metadata even if individual entries throw JSON
# exceptions; preflight prevents partial registrations from a bad JSON catalog.
.method private static isCatalogValid(Lorg/json/JSONArray;)Z
    .locals 8
    const/4 v0, 0x0
    invoke-virtual {p0}, Lorg/json/JSONArray;->length()I
    move-result v1
    if-lez v1, :invalid_catalog
    :each_language
    if-ge v0, v1, :valid_catalog
    invoke-virtual {p0, v0}, Lorg/json/JSONArray;->getJSONObject(I)Lorg/json/JSONObject;
    move-result-object v2
    const-string v3, "11"
    invoke-virtual {v2, v3}, Lorg/json/JSONObject;->getString(Ljava/lang/String;)Ljava/lang/String;
    move-result-object v4
    invoke-virtual {v4}, Ljava/lang/String;->length()I
    move-result v5
    if-lez v5, :invalid_catalog
    const-string v3, "20"
    invoke-virtual {v2, v3}, Lorg/json/JSONObject;->getString(Ljava/lang/String;)Ljava/lang/String;
    move-result-object v4
    invoke-virtual {v4}, Ljava/lang/String;->length()I
    move-result v5
    if-lez v5, :invalid_catalog
    const-string v3, "122"
    invoke-virtual {v2, v3}, Lorg/json/JSONObject;->getString(Ljava/lang/String;)Ljava/lang/String;
    move-result-object v4
    invoke-virtual {v4}, Ljava/lang/String;->length()I
    move-result v5
    if-lez v5, :invalid_catalog
    const-string v3, "124"
    invoke-virtual {v2, v3}, Lorg/json/JSONObject;->getString(Ljava/lang/String;)Ljava/lang/String;
    move-result-object v4
    invoke-virtual {v4}, Ljava/lang/String;->length()I
    move-result v5
    if-lez v5, :invalid_catalog

    const-string v3, "10"
    invoke-virtual {v2, v3}, Lorg/json/JSONObject;->getString(Ljava/lang/String;)Ljava/lang/String;
    move-result-object v4
    const-string v5, "[0-9a-fA-F]{32}"
    invoke-virtual {v4, v5}, Ljava/lang/String;->matches(Ljava/lang/String;)Z
    move-result v5
    if-eqz v5, :invalid_catalog

    const-string v3, "51"
    invoke-virtual {v2, v3}, Lorg/json/JSONObject;->getString(Ljava/lang/String;)Ljava/lang/String;
    move-result-object v4
    const-string v5, "https://github.com/"
    invoke-virtual {v4, v5}, Ljava/lang/String;->startsWith(Ljava/lang/String;)Z
    move-result v6
    if-nez v6, :check_github_release
    const-string v5, "https://raw.githubusercontent.com/"
    invoke-virtual {v4, v5}, Ljava/lang/String;->startsWith(Ljava/lang/String;)Z
    move-result v6
    if-nez v6, :url_valid
    const-string v5, "https://objects.githubusercontent.com/"
    invoke-virtual {v4, v5}, Ljava/lang/String;->startsWith(Ljava/lang/String;)Z
    move-result v6
    if-eqz v6, :invalid_catalog
    goto :url_valid
    :check_github_release
    const-string v5, "/releases/download/"
    invoke-virtual {v4, v5}, Ljava/lang/String;->contains(Ljava/lang/CharSequence;)Z
    move-result v6
    if-eqz v6, :invalid_catalog
    :url_valid

    # Exactly one recognized engine-version field is needed by Swype.
    const-string v3, "102"
    invoke-virtual {v2, v3}, Lorg/json/JSONObject;->has(Ljava/lang/String;)Z
    move-result v6
    if-nez v6, :check_core_value
    const-string v3, "103"
    invoke-virtual {v2, v3}, Lorg/json/JSONObject;->has(Ljava/lang/String;)Z
    move-result v6
    if-nez v6, :check_core_value
    const-string v3, "104"
    invoke-virtual {v2, v3}, Lorg/json/JSONObject;->has(Ljava/lang/String;)Z
    move-result v6
    if-nez v6, :check_core_value
    const-string v3, "105"
    invoke-virtual {v2, v3}, Lorg/json/JSONObject;->has(Ljava/lang/String;)Z
    move-result v6
    if-eqz v6, :invalid_catalog
    :check_core_value
    invoke-virtual {v2, v3}, Lorg/json/JSONObject;->getString(Ljava/lang/String;)Ljava/lang/String;
    move-result-object v4
    const-string v5, "[0-9]+[.][0-9]+"
    invoke-virtual {v4, v5}, Ljava/lang/String;->matches(Ljava/lang/String;)Z
    move-result v6
    if-eqz v6, :invalid_catalog

    const-string v3, "146"
    invoke-virtual {v2, v3}, Lorg/json/JSONObject;->getJSONArray(Ljava/lang/String;)Lorg/json/JSONArray;
    move-result-object v4
    invoke-virtual {v4}, Lorg/json/JSONArray;->length()I
    move-result v5
    if-lez v5, :invalid_catalog
    const/4 v6, 0x0
    :check_ids
    if-ge v6, v5, :next_language
    invoke-virtual {v4, v6}, Lorg/json/JSONArray;->getInt(I)I
    move-result v7
    if-lez v7, :invalid_catalog
    add-int/lit8 v6, v6, 0x1
    goto :check_ids
    :next_language
    add-int/lit8 v0, v0, 0x1
    goto :each_language
    :valid_catalog
    const/4 v0, 0x1
    return v0
    :invalid_catalog
    const/4 v0, 0x0
    return v0
.end method

# Do not synthesize an empty "43" array: the stock Swype transaction
# interprets that as no languages available and can overwrite saved state.
# Instead, a successful response without the catalog key preserves the
# previous list while acknowledging and completing this transaction.
.method private completeWithoutCatalog()V
    .locals 3
    new-instance v0, Lcom/nuance/connect/comm/Response;
    invoke-direct {v0}, Lcom/nuance/connect/comm/Response;-><init>()V
    const/4 v1, 0x1
    iput v1, v0, Lcom/nuance/connect/comm/Response;->status:I
    new-instance v1, Ljava/util/HashMap;
    invoke-direct {v1}, Ljava/util/HashMap;-><init>()V
    iput-object v1, v0, Lcom/nuance/connect/comm/Response;->parameters:Ljava/util/HashMap;
    iget-object v2, p0, Lcom/nuance/connect/service/manager/GitHubLanguageCatalog;->transaction:Lcom/nuance/connect/service/manager/LanguageManager$LanguageListTransaction;
    invoke-static {v2, v0}, Lcom/nuance/connect/service/manager/LanguageManager$LanguageListTransaction;->access$100(Lcom/nuance/connect/service/manager/LanguageManager$LanguageListTransaction;Lcom/nuance/connect/comm/Response;)V
    invoke-virtual {v2}, Lcom/nuance/connect/service/manager/LanguageManager$LanguageListTransaction;->onEndProcessing()V
    return-void
.end method
''')
print("Patched", p, "and created", out)
