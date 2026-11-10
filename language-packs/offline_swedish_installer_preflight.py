#!/usr/bin/env python3
"""Offline, read-only Swype Swedish installation preflight (never installs).
Usage: python offline_swedish_installer_preflight.py APK SWEDISH_ZIP
Does not publish language bytes or sign APKs.
"""
import gzip,hashlib,json,sys,zipfile,xml.etree.ElementTree as ET
from pathlib import Path

apk,pack=map(Path,sys.argv[1:3])
with zipfile.ZipFile(apk) as a:
    supported=ET.fromstring(a.read("assets/languagelist_supported.xml").decode("utf-16"))
    enabled=ET.fromstring(a.read("assets/languagelist.xml").decode("utf-16"))
    result={
        "supported_language_count":len(supported.findall("Language")),
        "swedish_supported":any(x.get("language")=="Swedish" for x in supported.findall("Language")),
        "swedish_enabled":any(x.get("language")=="Swedish" for x in enabled.findall("Language")),
    }
with zipfile.ZipFile(pack) as z:
    expected={"Swedish.mdf","SVusUN_xt9_ALM3.ldb.mp3","database_le.dat.mp3"}
    result["exact_expected_members"]=set(z.namelist())==expected and len(z.namelist())==3
    result["zip_crc_valid"]=z.testzip() is None
    metadata=z.read("Swedish.mdf").decode("utf-8").splitlines()
    result["mdf_targets_match"]=metadata==[
        "/data/user/0/com.nuance.swype.dtc/files/SVusUN_xt9_ALM3.ldb",
        "/data/user/0/com.nuance.swype.dtc/files/database_le.dat",
    ]
    result["gzip_payload_sizes"]={name:len(gzip.decompress(z.read(name))) for name in sorted(expected) if name.endswith(".mp3")}
    result["package_sha256"]=hashlib.sha256(pack.read_bytes()).hexdigest()
    result["package_md5"]=hashlib.md5(pack.read_bytes()).hexdigest()
result["runtime_xt9_version_from_phone"]="XT9 V11.03.07.00"
result["package_version_20_verified"]=False
result["alpha_core_version_102_verified"]=False
result["authorized_public_zip_url_verified"]=False
result["installation_and_rollback_device_tested"]=False
result["release_ready"]=False
result["warning"]="LanguageInstall.install deletes previous files before replacement; do not trigger without backup and valid activation path."
print(json.dumps(result,indent=2,ensure_ascii=False))
sys.exit(0 if result["release_ready"] else 2)
