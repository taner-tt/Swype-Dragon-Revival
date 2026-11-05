#!/usr/bin/env python3
"""Validate a locally supplied Swedish Swype ZIP without uploading proprietary binaries."""
import gzip
import hashlib
import json
import sys
import zipfile
from pathlib import Path

def verify(path):
    path = Path(path)
    expected = {"Swedish.mdf", "SVusUN_xt9_ALM3.ldb.mp3", "database_le.dat.mp3"}
    report = {"file": path.name, "sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "checks": {}, "files": {}}
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        report["checks"]["zip_integrity"] = archive.testzip() is None
        report["checks"]["expected_entries"] = set(names) == expected
        report["checks"]["installer_entry_limit"] = len(names) <= 1024
        report["checks"]["safe_paths"] = all("/" not in n and "\\" not in n and ".." not in n for n in names)
        total = 0
        for name in names:
            data = archive.read(name)
            if name.endswith(".mp3"):
                data = gzip.decompress(data)
            total += len(data)
            report["files"][name] = {"uncompressed_bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}
        report["checks"]["installer_100mb_limit"] = total < 100 * 1024 * 1024
        metadata = archive.read("Swedish.mdf").decode("utf-8", errors="replace") if "Swedish.mdf" in names else ""
        report["checks"]["metadata_names_both_databases"] = all(x in metadata for x in ("SVusUN_xt9_ALM3.ldb", "database_le.dat"))
    report["checks"]["device_language_registration"] = "NOT TESTED"
    report["checks"]["android_prediction_and_swipe"] = "NOT TESTED"
    return report

if __name__ == "__main__":
    print(json.dumps(verify(sys.argv[1]), indent=2, ensure_ascii=False))
