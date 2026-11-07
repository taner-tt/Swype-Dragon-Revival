#!/usr/bin/env python3
"""Generate a strict Swype/Nuance Swedish catalog from a verified local ZIP.

Does not upload assets or modify a public catalog. A public URL must be authorized
and accessible without credentials for the original Swype downloader.
"""
import argparse
import gzip
import hashlib
import json
import re
import zipfile
from pathlib import Path
from urllib.parse import urlparse

SWEDISH_LANGUAGE_ID = 285  # Original Swype res/xml/langfiles.xml, 0x011D.
REQUIRED_FILES = {"Swedish.mdf", "SVusUN_xt9_ALM3.ldb.mp3", "database_le.dat.mp3"}
ALLOWED_HOSTS = {"github.com", "raw.githubusercontent.com", "objects.githubusercontent.com"}


def check_url(value):
    u = urlparse(value)
    if u.scheme != "https" or u.hostname not in ALLOWED_HOSTS or u.username or u.password or u.fragment:
        raise ValueError("Use an approved, unauthenticated HTTPS GitHub download URL")
    if u.hostname == "github.com" and "/releases/download/" not in u.path:
        raise ValueError("GitHub page or draft asset URL is not a public direct-download URL")
    if not u.path or u.path.endswith("/"):
        raise ValueError("The package URL must name a file")
    return value


def package_checks(path):
    with zipfile.ZipFile(path) as z:
        names = z.namelist()
        if len(names) != len(REQUIRED_FILES) or set(names) != REQUIRED_FILES:
            raise ValueError("Swedish ZIP must contain exactly three original-format files at ZIP root")
        failed = z.testzip()
        if failed:
            raise ValueError(f"ZIP CRC failed: {failed}")
        meta = z.read("Swedish.mdf")
        if not all(n in meta for n in (b"SVusUN_xt9_ALM3.ldb", b"database_le.dat")):
            raise ValueError("Swedish.mdf does not reference both expected databases")
        for filename in REQUIRED_FILES:
            if filename.endswith(".mp3"):
                gzip.decompress(z.read(filename))


def build_entry(path, url, core_version, package_version, language_id=SWEDISH_LANGUAGE_ID):
    if language_id != SWEDISH_LANGUAGE_ID:
        raise ValueError("Swedish ID must be 285 (0x011D) from original Swype")
    if not re.fullmatch(r"\d+\.\d+", core_version):
        raise ValueError("Alpha core version must use original major.minor syntax (not a guess)")
    if not package_version or not package_version.strip():
        raise ValueError("Language package VERSION must be nonempty")
    check_url(url)
    package_checks(path)
    digest = hashlib.md5()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return {"11": "Swedish", "20": package_version, "51": url,
            "10": digest.hexdigest(), "102": core_version,
            "122": "SE", "124": "Svenska", "146": [SWEDISH_LANGUAGE_ID]}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("package", type=Path)
    p.add_argument("--url", required=True, help="Authorized publicly downloadable GitHub ZIP URL")
    p.add_argument("--language-id", type=int, default=SWEDISH_LANGUAGE_ID,
                   help="Swedish original ID; must be 285")
    p.add_argument("--core-version", required=True,
                   help="Exact Alpha core version verified on target APK; never guess")
    p.add_argument("--version", required=True,
                   help="Exact language package version; never guess")
    p.add_argument("--out", type=Path, default=Path("nuance-language-list.json"))
    args = p.parse_args()
    try:
        entry = build_entry(args.package, args.url, args.core_version, args.version, args.language_id)
    except (ValueError, OSError, zipfile.BadZipFile, EOFError) as exc:
        p.error(str(exc))
    args.out.write_text(json.dumps({"43": [entry]}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("Catalog written:", args.out, "MD5:", entry["10"])


if __name__ == "__main__":
    main()
