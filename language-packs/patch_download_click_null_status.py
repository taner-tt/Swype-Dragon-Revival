#!/usr/bin/env python3
"""Guard Swype 3722 Download Languages against absent legacy ConnectedStatus.

Device crash evidence: LanguageOptions.handleDownloadClick() line 473 calls
ConnectedStatus.isConnectedWifi() on null. The original UI hid the preference
when this service was unavailable; after restoring it, this guard prevents
the main-thread NullPointerException. It intentionally does NOT pretend the
GitHub language catalog or native installer is working.
"""
from pathlib import Path
import sys

p = Path(sys.argv[1]) / "smali/com/nuance/swype/input/settings/LanguageOptions.smali"
s = p.read_text(encoding="utf-8")
start = s.index(".method private handleDownloadClick()Z")
end = s.index(".end method", start) + len(".end method")
method = s[start:end]
old = """    .line 473
    iget-object v3, p0, Lcom/nuance/swype/input/settings/LanguageOptions;->connectedStatus:Lcom/nuance/swype/connect/ConnectedStatus;

    invoke-virtual {v3}, Lcom/nuance/swype/connect/ConnectedStatus;->isConnectedWifi()Z"""
new = """    # Null object is observed on actual Android when legacy Nuance
    # initialization did not provide ConnectedStatus.
    iget-object v3, p0, Lcom/nuance/swype/input/settings/LanguageOptions;->connectedStatus:Lcom/nuance/swype/connect/ConnectedStatus;
    if-nez v3, :swype_status_ready
    const-string v3, "SwypeGitHubLanguages"
    const-string v4, "Download pressed: ConnectedStatus null; download blocked instead of crashing"
    invoke-static {v3, v4}, Landroid/util/Log;->e(Ljava/lang/String;Ljava/lang/String;)I
    iget-object v3, p0, Lcom/nuance/swype/input/settings/LanguageOptions;->activity:Landroid/app/Activity;
    if-eqz v3, :swype_status_return
    const-string v4, "Språkservern är ännu inte ansluten. Ingen nedladdning är tillgänglig."
    invoke-static {v3, v4, v2}, Landroid/widget/Toast;->makeText(Landroid/content/Context;Ljava/lang/CharSequence;I)Landroid/widget/Toast;
    move-result-object v3
    invoke-virtual {v3}, Landroid/widget/Toast;->show()V
    :swype_status_return
    return v1
    :swype_status_ready
    .line 473
    iget-object v3, p0, Lcom/nuance/swype/input/settings/LanguageOptions;->connectedStatus:Lcom/nuance/swype/connect/ConnectedStatus;

    invoke-virtual {v3}, Lcom/nuance/swype/connect/ConnectedStatus;->isConnectedWifi()Z"""
if method.count(old) != 1 or ".locals 5" not in method:
    raise RuntimeError("Unexpected method/reg contract: refusing unsafe patch")
s = s[:start] + method.replace(old, new) + s[end:]
p.write_text(s, encoding="utf-8")
print("Fixed null ConnectedStatus crash in native language download click")
