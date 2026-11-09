#!/usr/bin/env python3
"""Compile and execute the actual KlipyGifBridge.field helper with Java test classes.

Regression: KeyboardEx.Key may inherit Android Keyboard.Key.label. A test that
only has a directly declared label would miss the phone's reported failure.
"""
from pathlib import Path
import re
import subprocess
import tempfile

root = Path(__file__).resolve().parents[2]
src = (root / "klipy/android/src/com/swyperevival/klipy/KlipyGifBridge.java").read_text(encoding="utf-8")
start = src.index("    private static Object field(Object owner, String name)")
end = src.index("\n    /**", start)
method = src[start:end]
assert "getSuperclass()" in method, "Field lookup must search parent classes"
assert "NoSuchFieldException" in method
test_source = """
import java.lang.reflect.Field;
public class InheritedPopupLabelTest {
""" + method + """
    static class AndroidKey { public CharSequence label = "GIF"; }
    static class SwypeKey extends AndroidKey {}
    static class SmileyKey extends AndroidKey { SmileyKey(){ label = "☺"; } }
    static class OwnKey { private CharSequence label = "GIF"; }
    public static void main(String[] args) throws Exception {
        if (!"GIF".equals(field(new SwypeKey(), "label"))) throw new AssertionError("Inherited GIF label lost");
        if (!"☺".equals(field(new SmileyKey(), "label"))) throw new AssertionError("Smiley label changed");
        if (!"GIF".equals(field(new OwnKey(), "label"))) throw new AssertionError("Declared label lost");
        try {
            field(new Object(), "label");
            throw new AssertionError("Missing label accepted");
        } catch (NoSuchFieldException expected) { }
        System.out.println("PASS: inherited GIF label, smiley, direct label and missing label");
    }
}
"""
with tempfile.TemporaryDirectory() as td:
    p = Path(td) / "InheritedPopupLabelTest.java"
    p.write_text(test_source, encoding="utf-8")
    subprocess.run(["javac", "-encoding", "UTF-8", str(p)], cwd=td, check=True)
    subprocess.run(["java", "-cp", td, "InheritedPopupLabelTest"], cwd=td, check=True)
