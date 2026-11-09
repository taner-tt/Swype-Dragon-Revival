#!/usr/bin/env python3
"""Patch the popup's exact sendKeyCode(listener, Key) method, not generic typing.

The selected KeyboardEx.Key has a label ("GIF") even though the existing
GIF and smiley keys share their key-code resource. The KLIPY bridge records
this label and lets the original onKey dispatch proceed. When Swype next
activates its emoji controller, the bridge opens KLIPY for the GIF choice.

Fail closed on layout surprises, duplicate hooks, or wrong method signatures.
"""
from pathlib import Path
import re
import sys


def patch_text(s):
    owner = "Lcom/nuance/swype/input/KeyboardEx$Key;"
    listener = "Lcom/nuance/swype/input/KeyboardViewEx$OnKeyboardActionListener;"
    signature = f"sendKeyCode({listener}{owner})Z"
    target = re.compile(r"(?m)^\s*\.method\b[^\n]*" + re.escape(signature) + r"[ \t]*$")
    matches = list(target.finditer(s))
    if len(matches) != 1:
        raise ValueError(f"Expected one exact popup sendKeyCode method, found {len(matches)}")
    if "Lcom/swyperevival/klipy/KlipyGifBridge;->notePopupKey" in s:
        raise ValueError("Popup GIF hook already present")
    start = matches[0].end()
    end = s.find(".end method", start)
    if end < 0:
        raise ValueError("Missing end of popup method")
    body = s[start:end]
    declaration = re.search(r"(?m)^[ \t]*\.(registers|locals)[ \t]+(\d+)[ \t]*$", body)
    if not declaration:
        raise ValueError("Missing method register declaration")
    # p2 is already an argument register, so the hook needs NO scratch locals.
    # Inject before first executable opcode, outside metadata and annotations.
    opcode = re.search(
        r"(?m)^[ \t]+(?:const(?:/[a-z0-9]+)?|move(?:/[a-z0-9]+)?|iget[\w/-]*|"
        r"sget[\w/-]*|invoke-[\w/-]+|new-instance|return[\w/-]*|"
        r"check-cast|if-[\w/-]+|goto[\w/-]*|monitor-enter|"
        r"move-object[\w/-]*)\s+", body
    )
    if not opcode or opcode.start() <= declaration.end():
        raise ValueError("No safe insertion point")
    hook = (
        "    # KLIPY popup label probe; original sendKeyCode remains unchanged.\n"
        "    invoke-static {p2}, Lcom/swyperevival/klipy/KlipyGifBridge;->notePopupKey(Ljava/lang/Object;)V\n"
    )
    patched = body[:opcode.start()] + hook + body[opcode.start():]
    out = s[:start] + patched + s[end:]
    if out.count("->notePopupKey(Ljava/lang/Object;)V") != 1:
        raise ValueError("Unexpected popup hook count")
    return out


def main(root):
    paths = list(root.glob("smali*/com/nuance/swype/input/SlideSelectPopupManager.smali"))
    if len(paths) != 1:
        raise SystemExit(f"Expected exactly one popup manager; found {len(paths)}")
    path = paths[0]
    content = path.read_text(encoding="utf-8")
    patched = patch_text(content)
    path.write_text(patched, encoding="utf-8")
    print("Patched only SlideSelectPopupManager.sendKeyCode; emoji handlers preserved")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: patch_popup_gif_handler.py <decoded-apk-dir>")
    main(Path(sys.argv[1]))
