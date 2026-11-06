#!/usr/bin/env python3
"""Audit real decompiled Swype language flow from a private Actions inspection ZIP.

This does not build APKs, publish binaries or prove Android runtime behavior.
Use: python3 language-packs/audit_original_download_flow.py swype-inspection-source.zip
"""
import argparse
import json
import re
import zipfile
from pathlib import Path

FILES = {
    "manager": "java-src/sources/com/nuance/connect/service/manager/LanguageManager.java",
    "protocol": "java-src/sources/com/nuance/connect/comm/MessageAPI.java",
    "installer": "java-src/sources/com/nuance/swype/connect/LanguageInstall.java",
    "sdk": "java-src/sources/com/nuance/swype/connect/SDKDownloadManager.java",
    "core": "java-src/sources/com/nuance/input/swypecorelib/SwypeCoreLibrary.java",
    "settings": "java-src/sources/com/nuance/swypeconnect/ac/ACManager.java",
    "config": "java-src/sources/com/nuance/connect/internal/ConnectServiceManagerInternal.java",
}

def audit(path):
    with zipfile.ZipFile(path) as z:
        src = {key: z.read(name).decode("utf-8", "replace") for key, name in FILES.items()}
    checks = {
        "language_list_key_is_string_43": bool(re.search(r'LANGUAGE_LIST\s*=\s*"43"', src["protocol"])),
        "list_response_reads_json_array": 'response.parameters.get(MessageAPI.LANGUAGE_LIST)' in src["manager"],
        "list_transaction_commits_metadata": 'languageInstallMetadata.commitTransaction()' in src["manager"],
        "list_transaction_acknowledges": 'taskCompletedAcknowledgement(this.taskAcknowledgement)' in src["manager"],
        "list_transaction_finishes_processing": 'finishTransaction(getName())' in src["manager"],
        "sdk_uses_original_install": 'langInstaller.install(installLanguagePath)' in src["sdk"],
        "sdk_adds_downloaded_language": 'list.addDownloadedLanguage(langName)' in src["sdk"],
        "sdk_updates_language_db": 'DatabaseConfig.updateLanguage(this.context, langName)' in src["sdk"],
        "sdk_refreshes_input_methods": 'imeApp.refreshInputMethods()' in src["sdk"],
        "sdk_signals_completion": 'languageInstallCompleted(this.languageId.intValue())' in src["sdk"],
        "installer_has_different_alm_path": 'boolean installALM(String tempPath)' in src["installer"],
        "engine_reads_native_core_versions": 'getCoreVersions()' in src["core"],
        "connect_alpha_uses_build_core": '.setCoreVersionAlpha(coreVersions.get(1))' in src["config"],
        "server_core_requires_major_minor": 'Alpha does not match major.minor version pattern' in src["settings"],
    }
    # This cannot determine the exact runtime core-version string or download success.
    return {
        "source": Path(path).name,
        "checks": checks,
        "all_static_checks_pass": all(checks.values()),
        "server_alpha_version_102": "NOT ESTABLISHED",
        "language_download_runtime": "NOT TESTED",
        "note": "Does not establish whether an injected callback triggers all transaction lifecycle events.",
    }

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("decompiled_inspection_zip", type=Path)
    a = p.parse_args()
    result = audit(a.decompiled_inspection_zip)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result["all_static_checks_pass"] else 1)
