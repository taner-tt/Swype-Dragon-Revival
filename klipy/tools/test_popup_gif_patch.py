#!/usr/bin/env python3
"""Offline assertions for the popup GIF hook; no APK or Android device needed."""
from pathlib import Path
import tempfile
import sys
from patch_popup_gif_handler import patch_text, main

BASE = (
    ".class public Lcom/nuance/swype/input/SlideSelectPopupManager;\n"
    ".super Ljava/lang/Object;\n"
    ".method private sendKeyCode(Lcom/nuance/swype/input/KeyboardViewEx$OnKeyboardActionListener;"
    "Lcom/nuance/swype/input/KeyboardEx$Key;)Z\n"
    "    .registers 11\n"
    "    const/4 v0, 0x0\n"
    "    invoke-interface {p1, v0}, Lcom/nuance/swype/input/"
    "KeyboardViewEx$OnKeyboardActionListener;->onKey(I)V\n"
    "    return v0\n"
    ".end method\n"
    ".method public irrelevant()V\n"
    "    .locals 0\n"
    "    return-void\n"
    ".end method\n"
)

def check():
    fixed = patch_text(BASE)
    hook = ("invoke-static {p2}, Lcom/swyperevival/klipy/"
            "KlipyGifBridge;->notePopupKey(Ljava/lang/Object;)V")
    assert fixed.count(hook) == 1
    assert fixed.index(hook) > fixed.index(".registers 11")
    assert fixed.index(hook) < fixed.index("const/4 v0")
    assert fixed.count("invoke-interface {p1, v0}") == 1
    assert fixed.split(".method public irrelevant()V")[1] == BASE.split(".method public irrelevant()V")[1]

    try:
        patch_text(fixed)
        raise AssertionError("Duplicate hook was allowed")
    except ValueError:
        pass
    try:
        patch_text(BASE.replace("sendKeyCode", "otherMethod"))
        raise AssertionError("Wrong method name was allowed")
    except ValueError:
        pass

    with tempfile.TemporaryDirectory() as td:
        target = Path(td) / "smali" / "com" / "nuance" / "swype" / "input"
        target.mkdir(parents=True)
        p = target / "SlideSelectPopupManager.smali"
        p.write_text(BASE, encoding="utf-8")
        main(Path(td))
        assert p.read_text(encoding="utf-8") == fixed
    print("PASS: popup GIF label hook, exact target, duplicate guard and original dispatch")

if __name__ == "__main__":
    check()
