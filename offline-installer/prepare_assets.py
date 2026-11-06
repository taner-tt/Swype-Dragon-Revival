#!/usr/bin/env python3
"""Load private Swype packs into the Android app without committing proprietary files.

Usage:
  python3 offline-installer/prepare_assets.py /path/to/Swype-104-Language-Packs-UNTESTED.zip

The outer archive contains one <language>.zip per entry. This script validates
the archive and extracts nested packs into app/src/main/assets/packs/.
"""
import argparse
import hashlib
import io
import json
from pathlib import Path
import re
import sys
import zipfile

MAX_PACKS = 150
MAX_TOTAL = 1024 * 1024 * 1024
NAME = re.compile(r"^[A-Za-z][A-Za-z0-9_-]{0,80}\.zip$")

def main():
    p = argparse.ArgumentParser()
    p.add_argument("archive", type=Path)
    p.add_argument("--output", type=Path, default=Path(__file__).parent / "app/src/main/assets/packs")
    args = p.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    manifest = []
    total = 0
    with zipfile.ZipFile(args.archive) as outer:
        entries = [x for x in outer.infolist() if not x.is_dir()]
        if len(entries) > MAX_PACKS:
            raise ValueError("Too many entries in outer archive")
        for info in entries:
            name = Path(info.filename).name
            if info.filename != name or not NAME.fullmatch(name):
                raise ValueError("Invalid language filename: " + info.filename)
            if info.file_size > MAX_TOTAL or total + info.file_size > MAX_TOTAL:
                raise ValueError("Language data exceeds size limit")
            data = outer.read(info)
            total += len(data)
            with zipfile.ZipFile(io.BytesIO(data)) as inner:
                inner_entries = inner.namelist()
                if not any(n.endswith(".mdf") for n in inner_entries):
                    raise ValueError(name + ": missing MDF metadata")
                if any(n.startswith("/") or ".." in Path(n).parts for n in inner_entries):
                    raise ValueError(name + ": unsafe ZIP path")
                if inner.testzip() is not None:
                    raise ValueError(name + ": corrupt ZIP member")
            target = args.output / name
            target.write_bytes(data)
            manifest.append({"name": name[:-4], "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()})
    (args.output / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Prepared {len(manifest)} private packs ({total} bytes) in {args.output}")
    print("Do not commit the generated language assets to a public repository.")

if __name__ == "__main__":
    main()
