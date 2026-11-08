#!/usr/bin/env python3
"""Extract bounded, useful information about Swype's emoji/GIF smali hooks.
No credentials and no proprietary full smali source copied into repository.
Designed for apktool-decoded TEST3 in GitHub Actions.
"""
from pathlib import Path
import re
import sys

root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("decoded")
dst = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("build/emoji-hook-audit.txt")
dst.parent.mkdir(parents=True, exist_ok=True)

targets = ("EmojiInputController.smali", "EmojiCategory.smali", "EmojiCategoryList.smali")
matches = [p for p in root.glob("smali*/**/*.smali") if p.name in targets]
report = ["Swype TEST3 GIF tab hook audit", f"root={root}", f"files={len(matches)}"]
if not matches:
    report.append("FAIL: No emoji controller smali located")
    dst.write_text("\n".join(report) + "\n", encoding="utf-8")
    sys.exit(2)
for path in sorted(matches):
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    report += ["", f"FILE {path} ({len(lines)} lines)"]
    if path.name != "EmojiInputController.smali":
        report += [f"  methods={sum('.method ' in ln for ln in lines)}"]
        continue
    found = []
    for i, line in enumerate(lines):
        if re.match(r"^\.method\b.*\b(onTabChanged|initCategoryTabs|setTab|createView|createGrid|showView)\(", line):
            found.append((i, line.strip()))
    for i, name in found:
        end = next((j for j in range(i + 1, len(lines)) if lines[j].strip() == ".end method"), len(lines) - 1)
        # Emit selected method headers and only relevant invocation names; no full decompiled proprietary code.
        report.append(f"METHOD {name}  lines {i+1}-{end+1}")
        for j in range(i, end + 1):
            ln = lines[j].strip()
            if any(tok in ln for tok in (
                "invoke-", "const-string", "packed-switch", "sparse-switch",
                "getTab", "category", "Category", "setContent", "addView", "showView"
            )):
                if "const-string" in ln:
                    # Do not dump arbitrary user strings or secrets from an APK.
                    report.append(f"  {j+1}: [const-string instruction]")
                else:
                    report.append(f"  {j+1}: {ln[:260]}")
                if len(report) > 1200:
                    report.append("[TRUNCATED]")
                    break
    report.append(f"TARGET METHODS FOUND: {[x[1].split('(')[0] for x in found]}")
dst.write_text("\n".join(report) + "\n", encoding="utf-8")
print(f"Wrote {dst} ({dst.stat().st_size} bytes)")
if not any("onTabChanged" in name for _, name in found):
    sys.exit("FAIL: onTabChanged not found")
