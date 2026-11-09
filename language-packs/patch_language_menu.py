#!/usr/bin/env python3
"""Restore the original Swype Download Languages preference and log Languages screen opening.

This is a narrow Android-smali patch for Swype 3722. It keeps the existing
download preference, click listener, dialog, and install handler. This does
not make an empty remote catalog contain downloadable languages.
"""
from pathlib import Path
import sys

root = Path(sys.argv[1])
p = root / "smali/com/nuance/swype/input/settings/LanguageOptions.smali"
s = p.read_text(encoding="utf-8")

start = s.index(".method protected buildLanguagePrefs()V")
end = s.index(".end method", start) + len(".end method")
part = s[start:end]
old = """    :cond_2
    iget-object v8, p0, Lcom/nuance/swype/input/settings/LanguageOptions;->screen:Landroid/preference/PreferenceScreen;

    invoke-virtual {v8, v2}, Landroid/preference/PreferenceScreen;->removePreference(Landroid/preference/Preference;)Z"""
if part.count(old) != 1:
    raise RuntimeError("Original download preference visibility contract changed; refusing patch")
part = part.replace(old, """    :cond_2
    # The obsolete Nuance Connect availability gate must not hide the existing row.
    # Preserve the original view and click listener. All download checks remain.
    nop""")
s = s[:start] + part + s[end:]

start = s.index(".method public onResume()V")
end = s.index(".end method", start) + len(".end method")
part = s[start:end]
needle = "    invoke-virtual {p0}, Lcom/nuance/swype/input/settings/LanguageOptions;->buildLanguagePrefs()V"
if part.count(needle) != 1 or ".locals 1" not in part:
    raise RuntimeError("Unexpected Languages screen onResume; refusing patch")
part = part.replace(needle, needle + """

    const-string v0, "SwypeGitHubLanguages"
    const-string v1, "Original Languages screen opened; native Download Languages preference retained"
    invoke-static {v0, v1}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I""")
part = part.replace(".locals 1", ".locals 2", 1)
s = s[:start] + part + s[end:]
p.write_text(s, encoding="utf-8")
print("PATCHED native Languages menu: download row preserved and onResume logged")
