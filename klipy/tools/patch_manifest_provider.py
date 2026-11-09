#!/usr/bin/env python3
"""Add private, URI-grantable GIF stream provider to decoded Swype manifest."""
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

manifest=Path(sys.argv[1])
raw=manifest.read_bytes()
if not raw.lstrip().startswith(b'<'):
    raise SystemExit("Expected apktool-decoded text AndroidManifest.xml")
uri="http://schemas.android.com/apk/res/android"
ET.register_namespace("android",uri)
tree=ET.parse(manifest)
root=tree.getroot()
app=root.find("application")
if app is None:raise SystemExit("No application in manifest")
name="{"+uri+"}name"
auth="{"+uri+"}authorities"
if any(e.get(auth)=="com.nuance.swype.dtc.klipy.gif" for e in app.findall("provider")):
    raise SystemExit("Already installed")
provider=ET.SubElement(app,"provider")
provider.set(name,"com.swyperevival.klipy.KlipyGifStreamProvider")
provider.set(auth,"com.nuance.swype.dtc.klipy.gif")
provider.set("{"+uri+"}exported","false")
provider.set("{"+uri+"}grantUriPermissions","true")
tree.write(manifest,encoding="utf-8",xml_declaration=True)
parsed=ET.parse(manifest).getroot()
assert any(e.get(auth)=="com.nuance.swype.dtc.klipy.gif" for e in parsed.find("application").findall("provider"))
print("PASS: private KLIPY streaming provider registered with URI grants")
