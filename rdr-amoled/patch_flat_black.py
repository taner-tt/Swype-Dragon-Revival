#!/usr/bin/env python3
"""Experimental visual-only Flat Black -> RDR AMOLED patch. No app code changes."""
import pathlib, sys
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
# Darken the theme-specific popup selector backgrounds instead of altering global app resources.
set_value("popupKeyTextColor","@color/white")
set_value("popupKeyTextColorMenu","@color/white")
set_value("btnKeyboardPopupKeyPressed","@drawable/background_black")
styles.write(styles_path,encoding="utf-8",xml_declaration=True)

metadata=ET.parse(metadata_path)
mr=metadata.getroot()
for name,value in {"name":"RDR.BLACK.AMOLED.V1","description":"RDR AMOLED black, borderless keyboard","version":"1","author":"RDR / Swype Dragon Revival"}.items():
    node=mr.find(name)
    assert node is not None, f"Missing metadata: {name}"
    node.text=value
metadata.write(metadata_path,encoding="utf-8",xml_declaration=True)
print("Patched 13 FlatBlack theme-specific colors / drawables and metadata; normal key touch areas untouched")
