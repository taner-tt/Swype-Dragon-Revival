#!/usr/bin/env python3
"""Offline Swedish reference/package audit; no uploads, APK modification or signing."""
import argparse
import gzip
import hashlib
import json
import re
import zipfile
from pathlib import Path

EXPECTED = ("Swedish.mdf", "SVusUN_xt9_ALM3.ldb.mp3", "database_le.dat.mp3")

def audit(apk_path: Path, package_path: Path):
    package_data = package_path.read_bytes()
    checks = {}
    observations = {}
    with zipfile.ZipFile(apk_path) as apk, zipfile.ZipFile(package_path) as pack:
        checks["package_zip_crc"] = pack.testzip() is None
        checks["expected_files"] = set(pack.namelist()) == set(EXPECTED)
        checks["reference_has_files"] = all("assets/" + name in apk.namelist() for name in EXPECTED)
        checks["matches_reference_bytes"] = checks["reference_has_files"] and all(
            pack.read(name) == apk.read("assets/" + name) for name in EXPECTED)
        metadata = pack.read("Swedish.mdf").decode("utf-8", "replace") if "Swedish.mdf" in pack.namelist() else ""
        checks["metadata_names_databases"] = all(name in metadata for name in ("SVusUN_xt9_ALM3.ldb", "database_le.dat"))
        checks["database_gzip_valid"] = True
        for name in EXPECTED[1:]:
            try:
                gzip.decompress(pack.read(name))
            except (OSError, KeyError, EOFError):
                checks["database_gzip_valid"] = False
        native = apk.read("lib/armeabi/libSwypeCoreDTC.so")
        observations["native_xt9_version_strings"] = sorted({
            value.decode("ascii") for value in re.findall(rb"XT9 V\d+(?:\.\d+){3}", native)
        })
    return {
        "md5": hashlib.md5(package_data).hexdigest(),
        "sha256": hashlib.sha256(package_data).hexdigest(),
        "checks": checks,
        "observations": observations,
        "server_alpha_core_version_102": "UNVERIFIED - native version is not a proven catalog value",
        "swype_download_and_device_test": "NOT TESTED",
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("reference_apk", type=Path)
    parser.add_argument("swedish_zip", type=Path)
    args = parser.parse_args()
    print(json.dumps(audit(args.reference_apk, args.swedish_zip), ensure_ascii=False, indent=2))
