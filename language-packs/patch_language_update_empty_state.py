#!/usr/bin/env python3
"""Diagnostic guard for Swype 3722 native Download Languages screen.

When the original Nuance service has no language list, show Swype's original
no_languages view instead of indefinitely displaying a spinner and waiting for
the obsolete 30-second timeout. Do not create fake packages, bypass package
validation, or claim that an empty GitHub catalog supports downloads.
"""
from pathlib import Path
import sys

root = Path(sys.argv[1])
path = root / "smali/com/nuance/swype/input/settings/LanguageUpdate.smali"
source = path.read_text(encoding="utf-8")
start = source.index(".method onResume()V")
end = source.index(".end method", start) + len(".end method")
body = source[start:end]
needle = """    invoke-virtual {v2}, Lcom/nuance/swype/connect/SDKDownloadManager;->isLanguageListAvailable()Z

    move-result v2

    if-nez v2, :cond_1"""
replacement = """    invoke-virtual {v2}, Lcom/nuance/swype/connect/SDKDownloadManager;->isLanguageListAvailable()Z

    move-result v2

    if-nez v2, :cond_1

    const-string v2, "SwypeGitHubLanguages"
    const-string v3, "Native download screen opened: no language list; show empty state without legacy 30s timeout"
    invoke-static {v2, v3}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I

    goto :cond_2"""
if body.count(needle) != 1:
    raise RuntimeError("Unexpected Swype 3722 LanguageUpdate onResume; refusing patch")
if ".locals 8" not in body or ":cond_2" not in body:
    raise RuntimeError("Missing required original register/empty-state contract")
body = body.replace(needle, replacement)
source = source[:start] + body + source[end:]
path.write_text(source, encoding="utf-8")
print("Native LanguageUpdate empty-state guard applied")
