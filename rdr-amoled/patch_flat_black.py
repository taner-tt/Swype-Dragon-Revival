#!/usr/bin/env python3
"""Experimental visual-only Flat Black -> RDR AMOLED patch. No app code changes."""
import pathlib, sys, os
import xml.etree.ElementTree as ET

root = pathlib.Path(sys.argv[1])
styles_path = root / "res/values/styles.xml"
metadata_path = root / "res/xml/theme_metadata.xml"
assert styles_path.is_file() and metadata_path.is_file(), "Missing expected theme resources"
styles = ET.parse(styles_path)
r = styles.getroot()
theme = next((x for x in r if x.tag == "style" and x.attrib.get("name") == "SwypeDLT.FlatBlack.V3xx"), None)
assert theme is not None, "Not Flat Black v3: stop safely"
def set_value(key,value):
    matches=[x for x in theme if x.tag=="item" and x.attrib.get("name")==key]
    assert len(matches)==1, f"Missing or ambiguous theme attr: {key}"
    matches[0].text=value

# Original already uses transparent normal key faces. Remove only horizontal key-row boundaries.
for key in ("secondRowBackground","thirdRowBackground","fourthRowBackground","bottomRowBackground","bottom5RowBackground","numberRowBackground"):
    set_value(key,"@drawable/trans_background")
# Keep text styles and white glyphs; make all surrounding areas pure OLED black.
for key in ("wingLeftBackgroundColor","wingRightBackgroundColor"):
    set_value(key,"#ff000000")
for key in ("keyboardSuggestStrip","keyboardSuggestStripHandwriting","keyboardSuggestStripHandwritingVer","keyboardBackgroundHwr"):
    set_value(key,"@drawable/background_black")
# The original Flat Black theme inherits these from SwypeDLT.Colorful.
# They were the missing *normal-state* backgrounds; pressed-only changes cannot
# remove the white GIF/emoji rectangle shown by the user.
for key in (
    "keyboardPopupBackground",
    "keyboardKeyFeedbackFunctionBarBackground",
    "keyboardKeyFeedbackBackground",
    "keyboardKeyFeedbackSelectedBackground",
    "keyboardPopupBackgroundFlick",
):
    matches=[x for x in theme if x.tag=="item" and x.attrib.get("name")==key]
    if matches:
        assert len(matches)==1
        matches[0].text="@drawable/background_black"
    else:
        ET.SubElement(theme,"item",{"name":key}).text="@drawable/background_black"
# Directly traced from the compiled popup_messaging_return_key.xml:
# <KeyboardEx keyBackground="@drawable/btn_keyboard_popup_key">
# The drawable selector references ?btnKeyboardPopupKeyNormal (default) and
# ?btnKeyboardPopupKeyPressed (pressed). Both need an explicit pure-black
# override in RDR; changing keyboardPopupBackground alone is insufficient.
for key in ("btnKeyboardPopupKeyNormal","btnKeyboardPopupKeyPressed"):
    matches=[x for x in theme if x.tag=="item" and x.attrib.get("name")==key]
    if matches:
        assert len(matches)==1, f"Duplicate attr: {key}"
        matches[0].text="@drawable/background_black"
    else:
        ET.SubElement(theme,"item",{"name":key}).text="@drawable/background_black"
# Darken the theme-specific popup selector backgrounds instead of altering global app resources.
set_value("popupKeyTextColor","@color/white")
set_value("popupKeyTextColorMenu","@color/white")
set_value("btnKeyboardPopupKeyPressed","@drawable/background_black")
# RDR palette: black and white chrome; color emoji glyphs must remain untouched.
# Preserve true transparency for key faces; all visible foreground colors are white.
for key in (
    "candidateComponent","candidateOther","candidatePressed","candidateRecommended",
    "componentForegroundColor","defaultKeyTextColor","defaultStrokeCandidateColor",
    "funcKeyTextColor","funcBtmTextColor","handwritingModeDisplayColor",
    "highlightedKeyTextColor","popupKeyTextColor","popupKeyTextColorMenu",
    "popupKeyTextColorPressed","traceColor","unrecognizedWordUnderlineHighlightColor",
    "verCandidateComponent","verCandidateNormal","verCandidateOther",
    "verCandidateRecommended","verCandidateSelected","wordErrorForegroundColor",
    "emojiCatIconColorNormal","emojiCatIconColorSelected",
):
    if any(x.tag=="item" and x.attrib.get("name")==key for x in theme):
        set_value(key,"#ffffffff")
# Preserve the original emojiColor resource and color emoji glyph rendering.
for key in ("convertingStringBackgroundColor","listSelectorBackgroundTappedColor",
            "unrecognizedWordBackgroundHighlightColor","wordInlineBackgroundColor"):
    if any(x.tag=="item" and x.attrib.get("name")==key for x in theme):
        set_value(key,"#ff000000")
styles.write(styles_path,encoding="utf-8",xml_declaration=True)

# Unique Android package: do not overwrite or collide with Flat_Black_v3.
manifest_path = root / "AndroidManifest.xml"
manifest = ET.parse(manifest_path)
mroot = manifest.getroot()
old_package = "com.nuance.swype.theme.flatblack_v3xx"
new_package = os.environ.get("RDR_THEME_PACKAGE","com.nuance.swype.theme.rdr_black_amoled_v1")
assert mroot.attrib.get("package") == old_package, "Unexpected original theme package"
mroot.set("package",new_package)
android_ns = "{http://schemas.android.com/apk/res/android}"
activity = mroot.find("./application/activity")
assert activity is not None, "MainActivity missing"
old_activity = activity.get(android_ns+"name")
assert old_activity in ("MainActivity",".MainActivity",old_package+".MainActivity"), "Unexpected activity name"
activity.set(android_ns+"name",old_package+".MainActivity")
ET.register_namespace("android","http://schemas.android.com/apk/res/android")
manifest.write(manifest_path,encoding="utf-8",xml_declaration=True)

metadata=ET.parse(metadata_path)
mr=metadata.getroot()
for name,value in {"name":os.environ.get("RDR_THEME_NAME","RDR.BLACK.AMOLED.V1"),"description":"RDR AMOLED black, borderless keyboard","version":"1","author":"RDR / Swype Dragon Revival"}.items():
    node=mr.find(name)
    assert node is not None, f"Missing metadata: {name}"
    node.text=value
snapshot_node=mr.find("snapshot")
assert snapshot_node is not None, "Snapshot attribute missing"
snapshot_node.text="@drawable/rdr_amoled_keyboard_preview"
metadata.write(metadata_path,encoding="utf-8",xml_declaration=True)
print("Patched theme, assigned unique package and metadata; all original keyboard touch areas preserved")
