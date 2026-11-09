#!/usr/bin/env python3
"""Build Swype's native Nuance catalog from the readable, theme-style languages.json.

Unlike themes.json, native Swype does NOT parse this friendly schema.
Never advertise a language unless its real package metadata, public HTTPS asset
and redistribution authorization have explicitly been verified. No placeholders.
"""
import argparse
import json
import re
from pathlib import Path
from urllib.parse import urlparse

REQUIRED = ("id", "name", "nativeName", "version", "downloadUrl",
            "md5", "languageId", "coreVersion", "country",
            "redistributionAuthorized", "packageVerified")
HOSTS = {"github.com", "raw.githubusercontent.com", "objects.githubusercontent.com"}
MD5 = re.compile(r"^[a-fA-F0-9]{32}$")
SHA256 = re.compile(r"^[a-fA-F0-9]{64}$")


def build(source):
    entries = source.get("languages")
    if not isinstance(entries, list):
        raise ValueError("languages must be an array")
    result = []
    seen = set()
    for item in entries:
        if not isinstance(item, dict):
            raise ValueError("language entry must be an object")
        status = item.get("status")
        if status != "published":
            continue  # Builtin English and pending Swedish remain invisible for download
        name = item.get("id", "<unknown>")
        missing = [k for k in REQUIRED if k not in item]
        if missing:
            raise ValueError(f"{name}: published entry missing {missing}")
        if item["redistributionAuthorized"] is not True or item["packageVerified"] is not True:
            raise ValueError(f"{name}: public distribution and package verification must be true")
        if not all(isinstance(item[k], str) and item[k].strip()
                   for k in ("id", "name", "nativeName", "version", "coreVersion", "country")):
            raise ValueError(f"{name}: invalid language metadata")
        if not isinstance(item["languageId"], int) or isinstance(item["languageId"], bool) or item["languageId"] <= 0:
            raise ValueError(f"{name}: languageId must be a positive integer")
        if not isinstance(item["md5"], str) or not MD5.fullmatch(item["md5"]):
            raise ValueError(f"{name}: invalid MD5")
        if not isinstance(item["sha256"], str) or not SHA256.fullmatch(item["sha256"]):
            raise ValueError(f"{name}: invalid SHA256")
        url = urlparse(str(item["downloadUrl"]))
        if (url.scheme != "https" or url.hostname not in HOSTS or url.username or url.password
                or (url.hostname == "github.com" and "/releases/download/" not in url.path)):
            raise ValueError(f"{name}: requires a public GitHub direct download URL")
        if item["id"] in seen or item["languageId"] in seen:
            raise ValueError(f"{name}: duplicate language")
        seen.add(item["id"])
        seen.add(item["languageId"])
        result.append({"11": item["name"], "20": item["version"],
                       "51": item["downloadUrl"], "10": item["md5"].lower(),
                       "102": item["coreVersion"], "122": item["country"],
                       "124": item["nativeName"], "146": [item["languageId"]]})
    return {"43": result}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=Path("language-packs/languages.json"))
    parser.add_argument("--output", type=Path, default=Path("language-packs/nuance-language-list.json"))
    args = parser.parse_args()
    source = json.loads(args.source.read_text(encoding="utf-8"))
    catalog = build(source)
    args.output.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Generated {len(catalog['43'])} downloadable languages; unpublished entries excluded")


if __name__ == "__main__":
    main()
