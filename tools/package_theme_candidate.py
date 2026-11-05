#!/usr/bin/env python3
"""Validate and package a Swype theme APK; never modify the source APK.

Usage: python3 tools/package_theme_candidate.py path/to/theme.apk output/theme.zip
Requires a previously built, compatible standalone theme APK.
"""
import argparse
import hashlib
import json
from pathlib import Path
import zipfile

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("apk",type=Path)
    p.add_argument("output",type=Path)
    a=p.parse_args()
    if a.apk.resolve()==a.output.resolve():
        p.error("output must differ from input")
    with zipfile.ZipFile(a.apk) as src:
        names=set(src.namelist())
        required={"AndroidManifest.xml","resources.arsc","res/xml/theme_metadata.xml"}
        missing=required-names
        if missing: p.error("Not a compatible Swype standalone theme candidate; missing: "+", ".join(sorted(missing)))
        if not any(n.startswith("res/drawable") and "keyboard_background" in n for n in names):
            p.error("Missing keyboard background resources")
        if src.testzip() is not None: p.error("Corrupt APK ZIP entries")
    a.output.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(a.output,"w",compression=zipfile.ZIP_DEFLATED) as dst:
        dst.write(a.apk,a.apk.name)
    with zipfile.ZipFile(a.output) as z:
        apks=[n for n in z.namelist() if n.lower().endswith(".apk")]
        assert apks==[a.apk.name],apks
    sha=hashlib.sha256(a.output.read_bytes()).hexdigest()
    print(json.dumps({"zip":str(a.output),"inner_apk":a.apk.name,"bytes":a.output.stat().st_size,"sha256":sha},indent=2))
    print("STRUCTURE ONLY: runtime compatibility and signing are NOT verified.")

if __name__=="__main__":
    main()
