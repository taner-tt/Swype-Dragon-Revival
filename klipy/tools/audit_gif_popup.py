#!/usr/bin/env python3
"""Read-only map of possible GIF long-press popup handlers in decoded Swype.

Searches methods and resource XML for evidence; does NOT patch anything.
Candidate matches require manual review before a popup hook is attempted.
"""
from pathlib import Path
import re
import sys

root = Path(sys.argv[1])
if not root.is_dir():
    raise SystemExit("Usage: audit_gif_popup.py <apktool decoded directory>")

TOKENS = re.compile(r"(?i)(?:gif|emoji|smiley|popup|long.press|longclick|search)")
METHODS = re.compile(r"(?ms)^\s*\.method\s+([^\n]+)\n(.*?)^\s*\.end method")
interesting = []
total = 0
for path in sorted(root.glob("smali*/**/*.smali")):
    if not any(t in str(path).lower() for t in ("swype", "nuance")):
        continue
    try:
        data = path.read_text(encoding="utf-8")
    except UnicodeError:
        continue
    for match in METHODS.finditer(data):
        total += 1
        signature, body = match.groups()
        evidence = []
        for line in body.splitlines():
            stripped = line.strip()
            if TOKENS.search(stripped) and (
                "const-string" in stripped or "invoke-" in stripped
                or "sget" in stripped or "iget" in stripped
            ):
                evidence.append(stripped[:190])
                if len(evidence) == 5:
                    break
        if evidence or TOKENS.search(signature):
            score = len(evidence)
            lower = (str(path) + " " + signature).lower()
            score += 3 if "popup" in lower else 0
            score += 2 if "long" in lower or "touch" in lower else 0
            score += 2 if "gif" in lower else 0
            interesting.append((score, str(path.relative_to(root)), signature, evidence))

print("READ-ONLY GIF / POPUP HANDLER AUDIT")
print(f"Smali methods examined: {total}")
print(f"Candidate methods found: {len(interesting)}")
print("Candidates are clues, NOT verified event handlers.")
for score, path, signature, lines in sorted(interesting, reverse=True)[:100]:
    print(f"\n[{score}] {path} :: {signature}")
    for line in lines:
        print("  " + line)
print("\nResource filenames suggesting popup/emoji/GIF:")
resource_files = [
    str(p.relative_to(root))
    for p in root.glob("res/**/*")
    if p.is_file() and TOKENS.search(p.name)
]
for name in sorted(resource_files)[:100]:
    print("  " + name)
print(f"Total matching resource filenames: {len(resource_files)}")
print("\nThis program never writes decoded resources or DEX files.")
