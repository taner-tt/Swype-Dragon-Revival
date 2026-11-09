#!/usr/bin/env python3
"""Fail-closed language-only APK comparison against user-supplied Swype 3722.

Reference and candidate remain local/private. This does not establish Android
runtime behavior or signing compatibility.
"""
import argparse
import hashlib
import json
import zipfile
from pathlib import Path
from audit_swype_3722_dex import audit

EXPECTED_METHODS = {
    'Lcom/nuance/connect/service/manager/LanguageManager;': {
        'requestLanguagesList': '(Ljava/lang/String;)V',
        'finishTransaction': '(Ljava/lang/String;)V',
    },
    'Lcom/nuance/connect/service/manager/LanguageManager$LanguageListTransaction;': {
        'getList': '()V', 'onEndProcessing': '()V', 'getName': '()Ljava/lang/String;',
    },
    'Lcom/nuance/connect/service/manager/AbstractCommandManager;': {
        'isTransactionActive': '(Ljava/lang/String;)Z',
        'startTransaction': '(Lcom/nuance/connect/comm/Transaction;)V',
    },
    'Lcom/nuance/connect/service/ConnectClient;': {
        'getString': '(Lcom/nuance/connect/service/configuration/ConnectConfiguration$ConfigProperty;)Ljava/lang/String;',
    },
    'Lcom/nuance/connect/internal/GenericProperty$BooleanProperty;': {
        'setValue': '(Ljava/lang/Boolean;Lcom/nuance/connect/internal/Property$Source;)V',
    },
    'Lcom/nuance/connect/comm/Transaction;': {'getName': '()Ljava/lang/String;'},
}

EXPECTED_BASE_SHA256 = "1b9a279f8a4fd859ed369c5f1290a2da34203d8ff02f952c98c37d170434d69d"

def digest(data):
    return hashlib.sha256(data).hexdigest()

def has_exact_methods(report):
    return all(signature in report['method_signatures'].get(cls, {}).get(method, [])
               for cls, members in EXPECTED_METHODS.items()
               for method, signature in members.items())

def verify(reference, candidate=None):
    baseline = audit(reference)
    report = {
        'reference': reference.name, 'reference_sha256': baseline['sha256'],
        'reference_zip_crc_ok': baseline['zip_crc_ok'],
        'reference_is_exact_3722': baseline['sha256'] == EXPECTED_BASE_SHA256,
        'reference_embedded_swedish': baseline['embedded_swedish'],
        'reference_embedded_english': baseline['embedded_english'],
        'reference_has_shared_database': baseline['shared_database'],
        'reference_has_all_exact_methods': has_exact_methods(baseline),
        'reference_dex': baseline['dex'],
        'reference_has_klipy_secondary_dex': 'classes2.dex' in baseline['dex'],
    }
    if candidate is None:
        report['candidate_validation'] = 'NOT PERFORMED — no candidate given'
        return report
    actual = audit(candidate)
    report.update({
        'candidate': candidate.name,
        'candidate_sha256': actual['sha256'],
        'candidate_crc_ok': actual['zip_crc_ok'],
        'candidate_bridge_present': any(x['github_bridge_present'] for x in actual['dex'].values()),
        'candidate_main_dex_changed': (baseline['dex'].get('classes.dex', {}).get('sha256') !=
                                       actual['dex'].get('classes.dex', {}).get('sha256')),
        'candidate_has_exact_methods': has_exact_methods(actual),
        'candidate_klipy_classes2_unchanged': (baseline['dex'].get('classes2.dex', {}).get('sha256') ==
                                               actual['dex'].get('classes2.dex', {}).get('sha256')),
    })
    with zipfile.ZipFile(reference) as original, zipfile.ZipFile(candidate) as patched:
        present = set(patched.namelist())
        protected = sorted(n for n in original.namelist()
                           if n.startswith(('assets/', 'lib/')) and not n.endswith('/'))
        report['protected_resources_checked'] = len(protected)
        report['protected_resources_missing_or_changed'] = [
            n for n in protected
            if n not in present or digest(original.read(n)) != digest(patched.read(n))]
    report['protected_resources_unchanged'] = not report['protected_resources_missing_or_changed']
    report['candidate_passes_structural_guard'] = all((
        report['reference_is_exact_3722'], report['reference_zip_crc_ok'], report['reference_has_all_exact_methods'],
        report['candidate_crc_ok'], report['candidate_bridge_present'],
        report['candidate_main_dex_changed'], report['candidate_has_exact_methods'],
        report['candidate_klipy_classes2_unchanged'], report['protected_resources_unchanged'],
    ))
    return report

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('reference', type=Path)
    parser.add_argument('--candidate', type=Path)
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    report = verify(args.reference, args.candidate)
    payload = json.dumps(report, indent=2, ensure_ascii=False) + '\n'
    if args.out:
        args.out.write_text(payload)
    print(payload)
    good = all((report['reference_is_exact_3722'], report['reference_zip_crc_ok'], report['reference_has_all_exact_methods'],
                report['reference_has_klipy_secondary_dex'],
                report['reference_embedded_english'],
                report['reference_has_shared_database'],
                not report['reference_embedded_swedish']))
    if args.candidate is not None:
        good = good and report['candidate_passes_structural_guard']
    raise SystemExit(0 if good else 1)
