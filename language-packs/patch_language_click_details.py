#!/usr/bin/env python3
"""Non-installing detail feedback for currently unverified GitHub languages.

Swype 3722's Nuance SDK is unavailable: on Android it blocks main thread.
This guards a tap on the already-working asynchronous GitHub catalog list.
Do not claim the private Swedish ZIP is publicly downloadable or supported
until authenticated version metadata and redistribution permission exist.
"""
from pathlib import Path
import sys

p = Path(sys.argv[1]) / "smali/com/nuance/swype/input/settings/LanguageUpdateFragment.smali"
s = p.read_text(encoding="utf-8")
start = s.index(".method public onListItemClick(")
end = s.index(".end method", start) + len(".end method")
method = """.method public onListItemClick(Landroid/widget/ListView;Landroid/view/View;IJ)V
    .locals 7
    .param p1, "l"    # Landroid/widget/ListView;
    .param p2, "v"    # Landroid/view/View;
    .param p3, "position"    # I
    .param p4, "id"    # J

    # Never hand unverified catalog entries to a disconnected Nuance installer.
    invoke-virtual {p0}, Lcom/nuance/swype/input/settings/LanguageUpdateFragment;->getActivity()Landroid/support/v4/app/FragmentActivity;
    move-result-object v0
    if-eqz v0, :swype_click_done
    invoke-virtual {p1, p3}, Landroid/widget/ListView;->getItemAtPosition(I)Ljava/lang/Object;
    move-result-object v1
    if-eqz v1, :swype_click_done
    invoke-virtual {v1}, Ljava/lang/Object;->toString()Ljava/lang/String;
    move-result-object v2
    const-string v3, "Svenska"
    invoke-virtual {v2, v3}, Ljava/lang/String;->startsWith(Ljava/lang/String;)Z
    move-result v3
    if-eqz v3, :swype_check_english
    const-string v2, "Svenska: ZIP verifierad lokalt, men paketversion, Alpha-version och godkänd nedladdningslänk saknas."
    goto :swype_show_notice
    :swype_check_english
    const-string v3, "English"
    invoke-virtual {v2, v3}, Ljava/lang/String;->startsWith(Ljava/lang/String;)Z
    move-result v3
    if-eqz v3, :swype_other_notice
    const-string v2, "English finns redan i Swype."
    goto :swype_show_notice
    :swype_other_notice
    const-string v2, "Ingen verifierad installerbar språkfil finns för detta språk."
    :swype_show_notice
    const-string v3, "SwypeGitHubLanguages"
    invoke-static {v3, v2}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I
    const/4 v4, 0x1
    invoke-static {v0, v2, v4}, Landroid/widget/Toast;->makeText(Landroid/content/Context;Ljava/lang/CharSequence;I)Landroid/widget/Toast;
    move-result-object v5
    invoke-virtual {v5}, Landroid/widget/Toast;->show()V
    :swype_click_done
    return-void
.end method"""
old = s[start:end]
if "delegate:Lcom/nuance/swype/input/settings/LanguageUpdate;" not in old:
    raise RuntimeError("Unexpected language fragment baseline; refusing patch")
p.write_text(s[:start] + method + s[end:], encoding="utf-8")
print("Enabled read-only language status details; no unverified install calls")
