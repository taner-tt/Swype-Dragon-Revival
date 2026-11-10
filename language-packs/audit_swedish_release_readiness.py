#!/usr/bin/env python3
"""Offline, fail-closed Swedish-language release-readiness audit for Swype 3722.

Usage: python audit_swedish_release_readiness.py ZIP [LANGUAGES_JSON] --output REPORT.json
No language ZIP, proprietary bytes, credentials or private paths are uploaded.
"""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import sys
import zipfile

EXPECTED = {'Swedish.mdf','SVusUN_xt9_ALM3.ldb.mp3','database_le.dat.mp3'}

def audit(package: Path, catalog: Path | None) -> dict:
    raw = package.read_bytes()
    result = {
        'package_sha256': hashlib.sha256(raw).hexdigest(),
        'package_md5': hashlib.md5(raw).hexdigest(),
        'zip_size_bytes': len(raw),
        'format_checks': {},
        'package_contents': {},
        'publication': {},
        'release_ready': False,
        'blockers': [],
    }
    with zipfile.ZipFile(package) as z:
        names = set(z.namelist())
        result['format_checks']['exact_expected_members'] = names == EXPECTED
        result['format_checks']['zip_crc'] = z.testzip() is None
        lines = z.read('Swedish.mdf').decode('utf-8').splitlines() if 'Swedish.mdf' in names else []
        result['format_checks']['mdf_has_two_database_paths'] = (
            len(lines) == 2
            and lines[0].endswith('/SVusUN_xt9_ALM3.ldb')
            and lines[1].endswith('/database_le.dat')
        )
        for name in sorted(names & EXPECTED):
            entry = z.read(name)
            metadata = {'compressed_bytes_in_zip':len(entry)}
            if name.endswith('.mp3'):
                metadata['is_gzip'] = entry[:2] == b'\x1f\x8b'
                try:
                    metadata['uncompressed_bytes'] = len(gzip.decompress(entry))
                    metadata['gzip_valid'] = True
                except (gzip.BadGzipFile, EOFError, OSError):
                    metadata['gzip_valid'] = False
            result['package_contents'][name] = metadata
    if not all(result['format_checks'].values()) or any(not info.get('gzip_valid', True) for info in result['package_contents'].values()):
        result['blockers'].append('Archive structure, integrity or gzip payload did not validate')
    # Neither ZIP timestamps nor embedded engine strings constitute verified package/core versions.
    result['blockers'].append('Authentic Swype/Nuance language package version (field 20) unverified')
    result['blockers'].append('Device-configured Alpha core version (field 102) unverified')
    if catalog is not None:
        data = json.loads(catalog.read_text(encoding='utf-8'))
        langs = data.get('languages', [])
        sv = next((x for x in langs if x.get('id') == 'sv'), None)
        result['publication']['swedish_catalog_entry'] = bool(sv)
        if sv:
            result['publication']['status'] = sv.get('status')
            result['publication']['download_url_present'] = bool(sv.get('downloadUrl'))
            result['publication']['sha256_matches_local'] = sv.get('sha256') == result['package_sha256']
            if sv.get('status') != 'available' or not sv.get('downloadUrl') or not result['publication']['sha256_matches_local']:
                result['blockers'].append('No verified published Swedish release with matching public checksum')
        else:
            result['blockers'].append('Swedish entry missing from catalog')
    else:
        result['blockers'].append('Public language manifest not checked')
    result['blockers'].append('Redistribution rights and on-device installation not verified')
    return result

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('zip', type=Path)
    parser.add_argument('manifest', nargs='?', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    info = audit(args.zip, args.manifest)
    output = json.dumps(info, indent=2, ensure_ascii=False) + '\n'
    if args.output:
        args.output.write_text(output, encoding='utf-8')
    print(output)
    sys.exit(0 if info['release_ready'] else 2)
