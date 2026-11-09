#!/usr/bin/env python3
"""Bind KLIPY GIF sender to the real Swype IME (readied per input session).

The GIF panel's Context is a themed view context and must not be treated as
InputMethodService. Patch one known IME lifecycle method, keeping all existing
Swype instructions. Fail if method signatures change.
"""
from pathlib import Path
import re
import sys

MARKER = "Lcom/swyperevival/klipy/KlipyGifSender;->bindService"

def patch_text(src):
    if MARKER in src:
        raise ValueError("Duplicate IME service binding")
    # Verified method exists in original TEST3 IME DEX.
    pat = re.compile(r"(?m)^[ \t]*\.method[^\n]*\bonStartInputView\(Landroid/view/inputmethod/EditorInfo;Z\)V[ \t]*$")
    matches = list(pat.finditer(src))
    if len(matches) != 1:
        raise ValueError("Expected one IME.onStartInputView(EditorInfo,boolean), got %d" % len(matches))
    begin = matches[0].end()
    end = src.find(".end method", begin)
    if end < 0:
        raise ValueError("Missing end method")
    body = src[begin:end]
    decl = re.search(r"(?m)^[ \t]*\.(?:registers|locals)[ \t]+\d+[ \t]*$", body)
    if not decl:
        raise ValueError("Missing register declaration")
    op = re.search(
        r"(?m)^[ \t]+(?:const(?:/[a-z0-9]+)?|move(?:/[a-z0-9]+)?|iget[\w/-]*|"
        r"sget[\w/-]*|invoke-[\w/-]+|new-instance|return[\w/-]*|"
        r"check-cast|if-[\w/-]+|goto[\w/-]*|monitor-enter)\s+", body)
    if not op or op.start() <= decl.end():
        raise ValueError("Unable to insert service binder")
    hook = (
        "    # KLIPY: connect GIF sending to the actual keyboard service.\n"
        "    invoke-static {p0}, Lcom/swyperevival/klipy/KlipyGifSender;->bindService(Landroid/inputmethodservice/InputMethodService;)V\n"
    )
    patched = src[:begin] + body[:op.start()] + hook + body[op.start():] + src[end:]
    if patched.count(MARKER) != 1:
        raise ValueError("Wrong bind count")
    return patched

def main(root):
    paths = list(root.glob("smali*/com/nuance/swype/input/IME.smali"))
    if len(paths) != 1:
        raise SystemExit("Expected exactly one Swype IME smali; found %d" % len(paths))
    path = paths[0]
    raw = path.read_text(encoding="utf-8")
    if ".super Landroid/inputmethodservice/InputMethodService;" not in raw:
        raise SystemExit("Swype IME superclass differs; no patch")
    path.write_text(patch_text(raw), encoding="utf-8")
    print("Bound GIF sender to real Swype InputMethodService during onStartInputView")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: patch_swype_ime_gif_sender.py decoded-dir")
    main(Path(sys.argv[1]))
