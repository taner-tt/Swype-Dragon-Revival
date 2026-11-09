#!/usr/bin/env python3
"""Read-only DEX method signature and APK structure audit. No APK modifications."""
import argparse
import hashlib
import json
import struct
import zipfile
from pathlib import Path

TARGETS = {
    'Lcom/nuance/connect/service/manager/LanguageManager;': ['requestLanguagesList', 'finishTransaction'],
    'Lcom/nuance/connect/service/manager/LanguageManager$LanguageListTransaction;': ['getList', 'onEndProcessing', 'getName'],
    'Lcom/nuance/connect/service/manager/AbstractCommandManager;': ['isTransactionActive', 'startTransaction'],
    'Lcom/nuance/connect/service/ConnectClient;': ['getString'],
    'Lcom/nuance/connect/internal/GenericProperty$BooleanProperty;': ['setValue'],
    'Lcom/nuance/connect/comm/Transaction;': ['getName'],
}

def uleb(data, offset):
    value = 0
    for i in range(5):
        byte = data[offset + i]
        value |= (byte & 0x7f) << (7 * i)
        if not byte & 0x80:
            return value, offset + i + 1
    raise ValueError("Invalid ULEB128")

def inspect_dex(data):
    if data[:3] != b'dex' or data[7] != 0:
        raise ValueError("Invalid DEX header")
    read_u32 = lambda offset: struct.unpack_from('<I', data, offset)[0]
    strings_count, strings_offset = read_u32(56), read_u32(60)
    types_count, types_offset = read_u32(64), read_u32(68)
    prototypes_offset = read_u32(76)
    methods_count, methods_offset = read_u32(88), read_u32(92)
    if strings_count > 1_000_000 or types_count > 1_000_000:
        raise ValueError("Unexpectedly large DEX section")
    strings = []
    for i in range(strings_count):
        offset = read_u32(strings_offset + i * 4)
        _, pos = uleb(data, offset)
        end = data.index(b'\x00', pos)
        strings.append(data[pos:end].decode('utf-8', 'replace'))
    types = [strings[read_u32(types_offset + i * 4)] for i in range(types_count)]
    methods = {}
    for i in range(methods_count):
        class_index, prototype_index, name_index = struct.unpack_from('<HHI', data, methods_offset + i * 8)
        class_descriptor, method = types[class_index], strings[name_index]
        if class_descriptor not in TARGETS or method not in TARGETS[class_descriptor]:
            continue
        _, return_type_index, params_offset = struct.unpack_from('<III', data, prototypes_offset + prototype_index * 12)
        params = []
        if params_offset:
            count = read_u32(params_offset)
            params = [types[struct.unpack_from('<H', data, params_offset + 4 + j * 2)[0]] for j in range(count)]
        descriptor = '(' + ''.join(params) + ')' + types[return_type_index]
        methods.setdefault(class_descriptor, {}).setdefault(method, []).append(descriptor)
    return methods

def audit(apk):
    result = {'apk_filename': apk.name, 'bytes': apk.stat().st_size,
              'sha256': hashlib.sha256(apk.read_bytes()).hexdigest(),
              'zip_crc_ok': False, 'dex': {}, 'method_signatures': {},
              'missing': [], 'embedded_swedish': False}
    with zipfile.ZipFile(apk) as archive:
        result['zip_crc_ok'] = archive.testzip() is None
        names = set(archive.namelist())
        result['embedded_swedish'] = any(name.startswith('assets/') and
            ('Swedish.mdf' in name or 'SVusUN_xt9' in name) for name in names)
        result['embedded_english'] = 'assets/ENubUN_xt9_ALM3.ldb.mp3' in names
        result['shared_database'] = 'assets/database_le.dat.mp3' in names
        all_methods = {}
        for name in sorted(n for n in names if n.startswith('classes') and n.endswith('.dex')):
            blob = archive.read(name)
            result['dex'][name] = {
                'size': len(blob), 'sha256': hashlib.sha256(blob).hexdigest(),
                'github_bridge_present': b'GitHubLanguageCatalog' in blob
            }
            for cls, methods in inspect_dex(blob).items():
                for method, descriptors in methods.items():
                    all_methods.setdefault(cls, {}).setdefault(method, []).extend(descriptors)
        result['method_signatures'] = all_methods
        for cls, methods in TARGETS.items():
            for method in methods:
                if method not in all_methods.get(cls, {}):
                    result['missing'].append(cls + '->' + method)
    return result

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('apk', type=Path)
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    result = audit(args.apk)
    if args.out:
        args.out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n')
    print(json.dumps(result, indent=2, ensure_ascii=False))
