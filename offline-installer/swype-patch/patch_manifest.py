#!/usr/bin/env python3
import sys
from pathlib import Path
from xml.etree import ElementTree as ET

manifest = Path(sys.argv[1])
ET.register_namespace("android", "http://schemas.android.com/apk/res/android")
ns = "{http://schemas.android.com/apk/res/android}"
root = ET.parse(manifest).getroot()
app = root.find("application")
if app is None:
    raise ValueError("Missing application")
name = "com.swyperevival.offline.OfflineLanguageImportActivity"
if not any(a.get(ns+"name") == name for a in app.findall("activity")):
    a = ET.SubElement(app, "activity")
    a.set(ns+"name", name)
    a.set(ns+"exported", "true")
    a.set(ns+"label", "Importera Swype-språk offline")
    f = ET.SubElement(a, "intent-filter")
    ET.SubElement(f, "action", {ns+"name":"android.intent.action.MAIN"})
    ET.SubElement(f, "category", {ns+"name":"android.intent.category.LAUNCHER"})
ET.ElementTree(root).write(manifest, encoding="utf-8", xml_declaration=True)
print("Added offline import activity")
