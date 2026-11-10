#!/usr/bin/env python3
"""Defensive Swype 3722 LanguageInstall smali patch.

Corrects existing failure-reporting defects but is NOT a complete transactional
installer. The legacy install() still removes old language files before installing
new ones, so DO NOT enable downloads or merge into a release without rollback.
"""
from pathlib import Path
import sys

p = Path(sys.argv[1]) / "smali/com/nuance/swype/connect/LanguageInstall.smali"
s = p.read_text(encoding="utf-8")

def edit(signature, needle, replacement):
    global s
    a=s.index(signature)
    b=s.index(".end method", a)+len(".end method")
    body=s[a:b]
    if body.count(needle)!=1:
        raise RuntimeError(f"Unexpected original installer layout: {signature}")
    s=s[:a]+body.replace(needle,replacement)+s[b:]

edit(".method private moveExtractedFiles()Z",
     "    or-int/2addr v6, v8\n\n    .line 278\n    if-eqz v6, :cond_81",
     "    move v6, v8\n\n    .line 278\n    if-eqz v6, :cond_81")
edit(".method public installPack(Ljava/lang/String;)V",
     "    if-eqz v0, :cond_27",
     "    if-eqz v0, :swype_installer_failure")
a=s.index(".method public installPack(Ljava/lang/String;)V")
b=s.index(".end method",a)+len(".end method")
body=s[a:b]
if body.count("    if-eqz v1, :cond_24")!=2:
    raise RuntimeError("Expected two installer failure paths")
body=body.replace("    if-eqz v1, :cond_24","    if-eqz v1, :swype_installer_failure")
s=s[:a]+body+s[b:]
edit(".method public installPack(Ljava/lang/String;)V",
     "    invoke-virtual {p0}, Lcom/nuance/swype/connect/LanguageInstall;->createMetadataFile()Z\n\n    .line 220",
     "    invoke-virtual {p0}, Lcom/nuance/swype/connect/LanguageInstall;->createMetadataFile()Z\n    move-result v1\n    if-eqz v1, :swype_installer_failure\n\n    .line 220")
edit(".method public installPack(Ljava/lang/String;)V",
     '    .line 210\n    .end local v0    # "stagingFolderReady":Z\n    :cond_28',
     '    :swype_installer_failure\n    new-instance v1, Ljava/io/IOException;\n    const-string v0, "Language package staging/move/metadata failed"\n    invoke-direct {v1, v0}, Ljava/io/IOException;-><init>(Ljava/lang/String;)V\n    throw v1\n\n    .line 210\n    .end local v0    # "stagingFolderReady":Z\n    :cond_28')
p.write_text(s,encoding="utf-8")
print("Fail-closed error reporting patch applied; existing destructive replacement still requires rollback")
