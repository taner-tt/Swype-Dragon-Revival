#!/usr/bin/env python3
"""Prevent the verified Swype 3722 native LanguageUpdateFragment main-thread ANR.

Observed call chain: onActivityCreated -> LanguageUpdate constructor ->
ConnectedStatus -> Connect.getSDKManager -> CountDownLatch.await().
Current GitHub language catalog is empty. Until an asynchronous, validated,
installer-connected catalog UI exists, show an honest empty diagnostic row
instead of blocking the UI thread. This is not a functional language downloader.
"""
from pathlib import Path
import sys

path = Path(sys.argv[1]) / "smali/com/nuance/swype/input/settings/LanguageUpdateFragment.smali"
s = path.read_text(encoding="utf-8")

def swap_method(src, signature, replacement):
    start = src.index(signature)
    end = src.index(".end method", start) + len(".end method")
    return src[:start] + replacement + src[end:]

replacement = """.method public onActivityCreated(Landroid/os/Bundle;)V
    .locals 5
    .param p1, "savedInstanceState"    # Landroid/os/Bundle;

    invoke-super {p0, p1}, Lcom/nuance/swype/input/settings/ActionbarListFragment;->onActivityCreated(Landroid/os/Bundle;)V
    const-string v0, "SwypeGitHubLanguages"
    const-string v1, "Download page: legacy Nuance SDK init bypassed to prevent main-thread ANR; empty GitHub catalog"
    invoke-static {v0, v1}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I

    invoke-virtual {p0}, Lcom/nuance/swype/input/settings/LanguageUpdateFragment;->getActivity()Landroid/support/v4/app/FragmentActivity;
    move-result-object v0
    if-eqz v0, :swype_page_done

    new-instance v1, Landroid/widget/ArrayAdapter;
    const v2, 0x1090003
    const/4 v3, 0x1
    new-array v3, v3, [Ljava/lang/String;
    const/4 v4, 0x0
    const-string p1, "Inga språk publicerade på GitHub ännu"
    aput-object p1, v3, v4
    invoke-direct {v1, v0, v2, v3}, Landroid/widget/ArrayAdapter;-><init>(Landroid/content/Context;I[Ljava/lang/Object;)V
    invoke-virtual {p0, v1}, Lcom/nuance/swype/input/settings/LanguageUpdateFragment;->setListAdapter(Landroid/widget/ListAdapter;)V
    :swype_page_done
    return-void
.end method"""

s = swap_method(s, ".method public onActivityCreated(Landroid/os/Bundle;)V", replacement)
for signature in [
    ".method public onActivityResult(IILandroid/content/Intent;)V",
    ".method public onListItemClick(Landroid/widget/ListView;Landroid/view/View;IJ)V",
    ".method public onDestroy()V",
    ".method public onPause()V",
    ".method public onResume()V",
    ".method public onStart()V",
    ".method public onStop()V",
]:
    if signature not in s:
        continue
    start = s.index(signature)
    end = s.index(".end method", start) + len(".end method")
    method = s[start:end]
    needle = "    iget-object v0, p0, Lcom/nuance/swype/input/settings/LanguageUpdateFragment;->delegate:Lcom/nuance/swype/input/settings/LanguageUpdate;"
    if needle not in method:
        raise RuntimeError(f"Unexpected lifecycle contract: {signature}")
    method = method.replace(needle, needle + "\n    if-eqz v0, :swype_empty_delegate", 1)
    last_return = method.rfind("    return-void")
    if last_return < 0:
        raise RuntimeError(f"Missing return: {signature}")
    method = method[:last_return] + "    :swype_empty_delegate\n" + method[last_return:]
    s = s[:start] + method + s[end:]

path.write_text(s, encoding="utf-8")
print("Guarded LanguageUpdateFragment from blocking legacy Nuance SDK initialization")
