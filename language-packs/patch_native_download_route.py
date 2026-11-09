#!/usr/bin/env python3
"""Route Swype 3722 Download Languages click to the native downloader screen.

This is an experimental follow-up to the verified ConnectedStatus null guard.
The old Nuance ConnectedStatus is null on the test device. Instead of
blocking with a toast, launch the existing IMEApplication.showLanguageDownloads
path, which delegates to SettingsV11Launcher / LanguageUpdateFragmentActivity.
It does not make an empty GitHub language catalog downloadable.
"""
from pathlib import Path
import sys

p = Path(sys.argv[1]) / "smali/com/nuance/swype/input/settings/LanguageOptions.smali"
s = p.read_text(encoding="utf-8")
start = s.index(".method private handleDownloadClick()Z")
end = s.index(".end method", start) + len(".end method")
method = s[start:end]
old = '''    iget-object v3, p0, Lcom/nuance/swype/input/settings/LanguageOptions;->connectedStatus:Lcom/nuance/swype/connect/ConnectedStatus;
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
    :swype_status_ready'''
new = '''    iget-object v3, p0, Lcom/nuance/swype/input/settings/LanguageOptions;->connectedStatus:Lcom/nuance/swype/connect/ConnectedStatus;
    if-nez v3, :swype_status_ready
    :swype_native_open_try_start
    const-string v3, "SwypeGitHubLanguages"
    const-string v4, "Download pressed: ConnectedStatus null; opening native language downloads"
    invoke-static {v3, v4}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I
    iget-object v3, p0, Lcom/nuance/swype/input/settings/LanguageOptions;->activity:Landroid/app/Activity;
    if-eqz v3, :swype_native_open_return
    invoke-static {v3}, Lcom/nuance/swype/input/IMEApplication;->from(Landroid/content/Context;)Lcom/nuance/swype/input/IMEApplication;
    move-result-object v3
    if-eqz v3, :swype_native_open_return
    invoke-virtual {v3}, Lcom/nuance/swype/input/IMEApplication;->showLanguageDownloads()V
    :swype_native_open_try_end
    .catch Ljava/lang/Exception; {:swype_native_open_try_start .. :swype_native_open_try_end} :swype_native_open_error
    :swype_native_open_return
    return v1
    :swype_native_open_error
    move-exception v3
    const-string v4, "SwypeGitHubLanguages"
    invoke-static {v4, v3}, Landroid/util/Log;->e(Ljava/lang/String;Ljava/lang/Throwable;)I
    return v1
    :swype_status_ready'''
if method.count(old) != 1:
    raise RuntimeError("Unexpected existing null guard; refusing unsafe patch")
p.write_text(s[:start] + method.replace(old, new) + s[end:], encoding="utf-8")
print("Routed missing ConnectedStatus to original native language downloader")
