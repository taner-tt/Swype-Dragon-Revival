#!/usr/bin/env python3
"""Regression checks for exact Swype IME -> KLIPY sender bind hook."""
from pathlib import Path
import tempfile
from patch_swype_ime_gif_sender import patch_text, main

BASE = (
    ".class public Lcom/nuance/swype/input/IME;\n"
    ".super Landroid/inputmethodservice/InputMethodService;\n"
    ".method public onStartInputView(Landroid/view/inputmethod/EditorInfo;Z)V\n"
    "    .locals 1\n"
    "    const/4 v0, 0x0\n"
    "    invoke-super {p0, p1, p2}, Landroid/inputmethodservice/InputMethodService;"
    "->onStartInputView(Landroid/view/inputmethod/EditorInfo;Z)V\n"
    "    return-void\n"
    ".end method\n"
    ".method public untouched()V\n"
    "    .locals 0\n"
    "    return-void\n"
    ".end method\n"
)

def test():
    patch = patch_text(BASE)
    target = "->bindService(Landroid/inputmethodservice/InputMethodService;)V"
    assert patch.count(target) == 1
    assert patch.index(target) < patch.index("const/4 v0")
    assert patch.split(".method public untouched()V")[1] == BASE.split(".method public untouched()V")[1]
    for bad in (patch, BASE.replace("onStartInputView", "missingMethod")):
        try:
            patch_text(bad)
            raise AssertionError("Rejected input accepted")
        except ValueError:
            pass
    with tempfile.TemporaryDirectory() as tmp:
        dest = Path(tmp)/"smali/com/nuance/swype/input"
        dest.mkdir(parents=True)
        (dest/"IME.smali").write_text(BASE,encoding="utf-8")
        main(Path(tmp))
        assert (dest/"IME.smali").read_text(encoding="utf-8")==patch
    print("PASS: IME binder exact method, original code retained, duplicate blocked")

if __name__ == "__main__":
    test()
