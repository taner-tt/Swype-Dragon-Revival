#!/usr/bin/env python3
"""Validate GitHub language-list JSON before building a Swype APK.

Uses the numeric MessageAPI keys consumed by the original LanguageManager.
Does not upload any language packs.
"""
import argparse
import json
import re
from urllib.parse import urlparse
from pathlib import Path

REQUIRED = ("11", "20", "51", "10", "122", "124", "146")
CORE_VERSIONS = ("102", "103", "104", "105")
ALLOWED_HOSTS = {"github.com", "raw.githubusercontent.com", "objects.githubusercontent.com"}

def validate(data):
    errors = []
    entries = data.get("43")
    if not isinstance(entries, list) or not entries:
        return ["43 (LANGUAGE_LIST) must contain at least one downloadable language"]
    for i, entry in enumerate(entries):
        prefix = f"language[{i}]"
        if not isinstance(entry, dict):
            errors.append(f"{prefix}: entry must be an object")
            continue
        for key in REQUIRED:
            if key not in entry:
                errors.append(f"{prefix}: missing field {key}")
        if not any(key in entry for key in CORE_VERSIONS):
            errors.append(f"{prefix}: missing core version")
        if not isinstance(entry.get("146"), list) or not entry["146"] or any(type(v) is not int for v in entry["146"]):
            errors.append(f"{prefix}: 146 must be nonempty integer language IDs")
        if not isinstance(entry.get("10"), str) or not re.fullmatch("[0-9a-fA-F]{32}", entry["10"]):
            errors.append(f"{prefix}: 10 must be MD5 checksum")
        url = urlparse(str(entry.get("51", "")))
        if url.scheme != "https" or url.hostname not in ALLOWED_HOSTS:
            errors.append(f"{prefix}: 51 must be approved GitHub HTTPS URL")
        elif url.hostname == "github.com" and "/releases/download/" not in url.path:
            errors.append(f"{prefix}: GitHub release page/draft asset is not a direct public download URL")
        for key in ("11", "20", "122", "124"):
            if not isinstance(entry.get(key), str) or not entry[key].strip():
                errors.append(f"{prefix}: {key} must be nonempty string")
    return errors

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("catalog", type=Path)
    args = parser.parse_args()
    errors = validate(json.loads(args.catalog.read_text(encoding="utf-8")))
    if errors:
        print("\n".join("ERROR: " + e for e in errors))
        raise SystemExit(1)
    print("Valid Nuance LANGUAGE_LIST catalog schema")
