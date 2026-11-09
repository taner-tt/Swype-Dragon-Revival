#!/usr/bin/env python3
"""Read-only extraction of popup/emoji-flow methods from decoded TEST3.

This diagnostic writes only a report. It never changes any APK resource.
The report includes method bytecode, not user information or credentials.
"""
from pathlib import Path
import re
import sys

if len(sys.argv) != 3:
    raise SystemExit("usage: audit_popup_flow.py <decoded-apk-dir> <report-path>")
root = Path(sys.argv[1])
report = Path(sys.argv[2])
targets = {
    "SlideSelectPopupManager": ("onUp(", "sendKeyCode(", "setCurrentKey("),
    "EmojiInputController": ("onTabChanged(", "createView(", "initCategoryTabs("),
    "IME": ("onKey(", "onStartInputView(", "showEmoji", "emoji"),
    "InputView": ("onKey(", "showEmoji", "emoji"),
}
all_methods = []
for klass, needles in targets.items():
    matches = list(root.glob("smali*/com/nuance/swype/input/**/" + klass + ".smali"))
    if len(matches) != 1:
        all_methods.append("MISSING/AMBIGUOUS " + klass + ": " + str(len(matches)))
        continue
    s = matches[0].read_text(encoding="utf-8")
    all_methods.append("CLASS " + str(matches[0].relative_to(root)))
    for m in re.finditer(r"(?ms)^\.method\s+([^\n]+)\n.*?^\.end method", s):
        sig = m.group(1)
        if any(t.lower() in sig.lower() for t in needles):
            text = m.group(0)
            all_methods.append("---- " + sig + " ----\n" + text[:18000])
            if len(text) > 18000:
                all_methods.append("TRUNCATED METHOD")
report.parent.mkdir(parents=True, exist_ok=True)
report.write_text("\n\n".join(all_methods), encoding="utf-8")
print("READ ONLY popup-flow report:", report, "bytes:", report.stat().st_size)
