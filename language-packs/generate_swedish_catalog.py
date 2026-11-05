#!/usr/bin/env python3
"""Generate a Nuance-compatible Swedish catalog entry for a legally hosted pack.

Never upload the package or signing key. A draft release URL will NOT work with
Swype's unauthenticated download transaction.
"""
import argparse
import hashlib
import json
from pathlib import Path
from urllib.parse import urlparse

def main():
    p = argparse.ArgumentParser()
    p.add_argument("package", type=Path)
    p.add_argument("--url", required=True, help="Public HTTPS direct-download URL, only when distribution is authorized")
    p.add_argument("--language-id", required=True, type=int, help="ID verified against target APK; do not guess")
    p.add_argument("--core-version", required=True, help="Alpha core version verified against target APK")
    p.add_argument("--version", required=True, help="Package version verified against target APK")
    p.add_argument("--country", default="SE")
    p.add_argument("--out", type=Path, default=Path("nuance-language-list.json"))
    args = p.parse_args()
    u = urlparse(args.url)
    if u.scheme != "https" or u.hostname not in ("github.com", "raw.githubusercontent.com", "objects.githubusercontent.com"):
        p.error("Only approved GitHub HTTPS download URLs are accepted by the current APK patch")
    if "/releases/download/" not in u.path and u.hostname == "github.com":
        p.error("A draft release or release page is not a direct download URL")
    if not args.package.is_file():
        p.error("Language ZIP not found")
    md5 = hashlib.md5(args.package.read_bytes()).hexdigest()
    entry = {"11":"Swedish","20":args.version,"51":args.url,"10":md5,
             "102":args.core_version,"122":args.country,"124":"Svenska",
             "146":[args.language_id]}
    args.out.write_text(json.dumps({"43":[entry]},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("Catalog written:",args.out,"MD5:",md5)

if __name__ == "__main__":
    main()
