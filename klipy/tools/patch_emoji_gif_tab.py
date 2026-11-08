#!/usr/bin/env python3
"""Patch only TEST3's EmojiInputController.onTabChanged() entry.

The inserted bridge call handles the "GIF" tab and returns early.
All other tabs continue into the original method. Strict assertions prevent
silently shipping a no-op or double-patched APK.
"""
import pathlib
import re
import sys

root = pathlib.Path(sys.argv[1])
files = list(root.glob("smali*/com/nuance/swype/input/emoji/EmojiInputController.smali"))
if len(files) != 1:
    raise SystemExit(f"Expected exactly one EmojiInputController.smali; found {len(files)}")
path = files[0]
s = path.read_text(encoding="utf-8")
if "Lcom/swyperevival/klipy/KlipyGifBridge;->intercept" in s:
    raise SystemExit("Bridge already installed; refusing duplicate patch")

start = re.search(r"(?m)^[ \t]*\.method\b[^\n]*\bonTabChanged\(Ljava/lang/String;\)V\s*$", s)
if not start:
    raise SystemExit("Exact onTabChanged(String):void method missing")
end = s.find(".end method", start.end())
if end < 0:
    raise SystemExit("Method end not found")
body = s[start.end():end]
registers = re.search(r"(?m)^[ \t]*\.(registers|locals)\s+(\d+)\s*$", body)
if not registers:
    raise SystemExit("No register declaration")
if registers.group(1) == "registers" and int(registers.group(2)) < 3:
    raise SystemExit("Unexpected register count")
if registers.group(1) == "locals" and int(registers.group(2)) < 1:
    raise SystemExit("No spare local register")
# Inject immediately before the first executable opcode (not into .annotation,
# .param, debugging metadata, or .catch directives).
opcode = re.search(
    r"(?m)^[ \t]+(?:const(?:/[a-z0-9]+)?|move(?:/[a-z0-9]+)?|iget[\w/-]*|"
    r"sget[\w/-]*|invoke-[\w/-]+|new-instance|return[\w/-]*|"
    r"check-cast|if-[\w/-]+|goto[\w/-]*|monitor-enter|"
    r"move-object[\w/-]*)\s+",
    body,
)
if not opcode:
    raise SystemExit("Cannot find first instruction safely")
hook = (
    "    # KLIPY Revival GIF tab hook. Other categories run original code.\n"
    "    invoke-static {p0, p1}, Lcom/swyperevival/klipy/KlipyGifBridge;->intercept(Ljava/lang/Object;Ljava/lang/String;)Z\n"
    "    move-result v0\n"
    "    if-eqz v0, :revival_klipy_original_tab\n"
    "    return-void\n"
    "    :revival_klipy_original_tab\n\n"
)
patched = body[:opcode.start()] + hook + body[opcode.start():]
out = s[:start.end()] + patched + s[end:]
assert out.count("Lcom/swyperevival/klipy/KlipyGifBridge;->intercept") == 1
path.write_text(out, encoding="utf-8")
print(f"Patched {path} at onTabChanged(String); existing logic retained")
