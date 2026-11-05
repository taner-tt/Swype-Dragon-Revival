#!/usr/bin/env python3
"""Audit the language metadata in a private local Swype lang ZIP.

Does not publish or extract any proprietary language database.
"""
import argparse
import csv
import json
import os
import zipfile
from pathlib import Path

def audit(source, output):
    with zipfile.ZipFile(source) as z:
        files = {os.path.basename(n): n for n in z.namelist() if n.startswith("lang/files/") and not n.endswith("/")}
        rows = []
        for name, path in sorted(files.items()):
            if not name.endswith(".mdf"):
                continue
            refs = [os.path.basename(x.strip()) for x in z.read(path).decode("utf-8", "replace").splitlines() if x.strip()]
            missing = [x for x in refs if x not in files]
            rows.append({"language": name[:-4], "metadata": name, "databases": "; ".join(refs),
                         "missing": "; ".join(missing), "complete_in_archive": not missing})
    with open(output, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    summary = {"languages_with_mdf": len(rows), "complete_in_archive": sum(r["complete_in_archive"] for r in rows),
               "missing_dependencies": sum(not r["complete_in_archive"] for r in rows),
               "missing_file_names": sorted({n for r in rows for n in r["missing"].split("; ") if n})}
    print(json.dumps(summary, indent=2))

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("archive", type=Path)
    p.add_argument("--output", type=Path, default=Path("language-audit.csv"))
    args = p.parse_args()
    audit(args.archive, args.output)
