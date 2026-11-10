#!/usr/bin/env python3
"""Show local XT9 engine version on tap of Swedish in Swype 3722.

Apply AFTER patch_language_click_details.py to a decoded Swype 3722 tree.
Reads IMEApplication's existing SwypeCoreLibrary.getXT9CoreVersion;
avoids Nuance Connect.getSDKManager, which ANRs on the test device.
XT9 raw version is a diagnostic, NOT automatic proof of the server's
CORE_VERSION_ALPHA major.minor value. No install is enabled.
"""
from pathlib import Path
import sys

p = Path(sys.argv[1]) / "smali/com/nuance/swype/input/settings/LanguageUpdateFragment.smali"
s = p.read_text(encoding="utf-8")
a = s.index(".method public onListItemClick(")
b = s.index(".end method", a) + len(".end method")
part = s[a:b]
old = '''    const-string v2, "Svenska: ZIP verifierad lokalt, men paketversion, Alpha-version och godkänd nedladdningslänk saknas."
    goto :swype_show_notice'''
new = '''    :swype_xt9_try_start
    invoke-static {v0}, Lcom/nuance/swype/input/IMEApplication;->from(Landroid/content/Context;)Lcom/nuance/swype/input/IMEApplication;
    move-result-object v3
    if-eqz v3, :swype_xt9_missing
    invoke-virtual {v3}, Lcom/nuance/swype/input/IMEApplication;->getSwypeCoreLibMgr()Lcom/nuance/swype/input/corelibmgr/SwypeCoreLibManager;
    move-result-object v3
    if-eqz v3, :swype_xt9_missing
    invoke-virtual {v3}, Lcom/nuance/swype/input/corelibmgr/SwypeCoreLibManager;->getSwypeCoreLibInstance()Lcom/nuance/input/swypecorelib/SwypeCoreLibrary;
    move-result-object v3
    if-eqz v3, :swype_xt9_missing
    invoke-virtual {v3}, Lcom/nuance/input/swypecorelib/SwypeCoreLibrary;->getXT9CoreVersion()Ljava/lang/String;
    move-result-object v3
    if-eqz v3, :swype_xt9_missing
    new-instance v4, Ljava/lang/StringBuilder;
    invoke-direct {v4}, Ljava/lang/StringBuilder;-><init>()V
    const-string v5, "XT9-kärnversion från telefonen: "
    invoke-virtual {v4, v5}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual {v4, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    const-string v5, ". Svenskt paket: versions- och distributionskontroll återstår."
    invoke-virtual {v4, v5}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual {v4}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object v2
    :swype_xt9_try_end
    .catch Ljava/lang/Throwable; {:swype_xt9_try_start .. :swype_xt9_try_end} :swype_xt9_error
    goto :swype_show_notice
    :swype_xt9_missing
    const-string v2, "XT9-version kunde inte läsas; svenskt paket är fortfarande ej verifierat."
    goto :swype_show_notice
    :swype_xt9_error
    move-exception v3
    const-string v4, "SwypeGitHubLanguages"
    const-string v5, "Read-only XT9 version lookup failed"
    invoke-static {v4, v5, v3}, Landroid/util/Log;->w(Ljava/lang/String;Ljava/lang/String;Ljava/lang/Throwable;)I
    const-string v2, "XT9-version kunde inte läsas; svenskt paket är fortfarande ej verifierat."
    goto :swype_show_notice'''
if part.count(old) != 1 or ".locals 7" not in part:
    raise RuntimeError("Unexpected read-only language-details click contract")
p.write_text(s[:a] + part.replace(old, new) + s[b:], encoding="utf-8")
print("Read-only local XT9 core diagnostic enabled, Nuance installer still blocked")
