#!/usr/bin/env python3
"""Trace Nuance Alpha core-version provenance in the saved original Swype APK.

This is STATIC evidence; it never guesses a runtime value. No APK is edited.
Usage: python3 audit_core_version_chain.py swype-inspection-source.zip
"""
import json
import re
import sys
import zipfile
from pathlib import Path

ROOT = "java-src/sources/"
SOURCES = {
    "host": "com/nuance/swypeconnect/ac/ACManager.java",
    "service": "com/nuance/connect/internal/ConnectServiceManagerInternal.java",
    "message": "com/nuance/connect/internal/ConfigServiceInternal.java",
    "client": "com/nuance/connect/service/manager/ConfigurationManager.java",
    "native": "com/nuance/input/swypecorelib/SwypeCoreLibrary.java",
}

def audit(archive):
    with zipfile.ZipFile(archive) as z:
        src = {name: z.read(ROOT + path).decode("utf-8") for name, path in SOURCES.items()}
        java = [(n, z.read(n).decode("utf-8", "replace")) for n in z.namelist()
                if n.startswith(ROOT) and n.endswith(".java")]
    checks = {
        "host_build_settings_uses_alpha_slot_1":
            'this.coreVersions.put(1, str)' in src["host"],
        "service_receives_alpha_from_host":
            '.setCoreVersionAlpha(coreVersions.get(1))' in src["service"],
        "message_reads_alpha_slot_1":
            'bundle.putString(Strings.PROP_CORE_ALPHA, coreVersions.get(1))' in src["message"],
        "client_registers_alpha_from_host":
            'setProperty(ConnectConfiguration.ConfigProperty.CORE_VERSION_ALPHA, message.getData().getString(Strings.PROP_CORE_ALPHA))' in src["client"],
        "native_xt9_version_is_separate":
            'String coreVersions = getCoreVersions();' in src["native"],
    }
    # Search actual invocation syntax rather than merely text matching the method
    # declaration. Decompilation may miss reflection/indirect calls.
    setter_calls = [n.removeprefix(ROOT) for n, source in java
                    if ".setCoreVersions(" in source]
    external_setter_calls = [name for name in setter_calls
                             if name != SOURCES["host"]]
    report = {
        "reference": Path(archive).name,
        "checks": checks,
        "static_core_version_forwarding_call_sites": setter_calls,
        "setter_invocations_outside_ACManager": external_setter_calls,
        "core_setting_proven_at_runtime": False,
        "alpha_core_catalog_value_102": "NOT DETERMINED FROM STATIC SOURCES",
        "native_XT9_version_equals_server_core": "NOT ESTABLISHED",
        "interpretation": "Alpha version is retrieved through host BuildSettings (slot 1). "
                          "A compiled native library version text does not establish the "
                          "actual value supplied at runtime by the host.",
    }
    return report

if __name__ == "__main__":
    report = audit(Path(sys.argv[1]))
    print(json.dumps(report, indent=2))
    if not all(report["checks"].values()):
        sys.exit("Original version chain changed: inspect before building a live catalog")
