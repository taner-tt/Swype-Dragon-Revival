#!/usr/bin/env python3
"""Fail closed when a Swype APK no longer matches the bridge's DEX contract.

Inspects decompiled, private APK smali in place. Never uploads/repackages it.
"""
from pathlib import Path
import argparse
import json
import sys

SOURCES = {
    "manager": "com/nuance/connect/service/manager/AbstractCommandManager.smali",
    "lang": "com/nuance/connect/service/manager/LanguageManager.smali",
    "list": "com/nuance/connect/service/manager/LanguageManager$LanguageListTransaction.smali",
    "property": "com/nuance/connect/internal/GenericProperty$BooleanProperty.smali",
    "enum": "com/nuance/connect/internal/Property$Source.smali",
    "transaction": "com/nuance/connect/comm/Transaction.smali",
    "response": "com/nuance/connect/comm/Response.smali",
}
REQUIRED = {
    "manager": [
        ".field protected final activeTransactions:Ljava/util/Map;",
        ".field private final idleProperty:Lcom/nuance/connect/internal/GenericProperty$BooleanProperty;",
        ".method protected isTransactionActive(Ljava/lang/String;)Z",
        ".method protected finishTransaction(Ljava/lang/String;)V",
        "Ljava/util/concurrent/ConcurrentHashMap;",
    ],
    "lang": [
        ".method public requestLanguagesList(Ljava/lang/String;)V",
        "LanguageManager;->startTransaction(Lcom/nuance/connect/comm/Transaction;)V",
    ],
    "list": [
        ".field final synthetic this$0:Lcom/nuance/connect/service/manager/LanguageManager;",
        ".method private getList()V",
        ".method public getName()Ljava/lang/String;",
        ".method public onEndProcessing()V",
        "LanguageManager;->finishTransaction(Ljava/lang/String;)V",
        "LanguageManager;->managerStartComplete()V",
    ],
    "property": [".method public setValue(Ljava/lang/Boolean;Lcom/nuance/connect/internal/Property$Source;)V"],
    "enum": [".field public static final enum DEFAULT:Lcom/nuance/connect/internal/Property$Source;"],
    "transaction": [".method public abstract getName()Ljava/lang/String;"],
    "response": [".field public parameters:Ljava/util/HashMap;"],
}


def check(decoded):
    smali = Path(decoded) / "smali"
    findings = {}
    for name, rel in SOURCES.items():
        path = smali / rel
        if not path.is_file():
            findings[name] = {"file": rel, "missing": ["FILE MISSING"]}
            continue
        src = path.read_text(encoding="utf-8")
        findings[name] = {"file": rel, "missing": [x for x in REQUIRED[name] if x not in src]}
    return {"compatible": all(not x["missing"] for x in findings.values()),
            "checks": findings, "note": "Static DEX contract only: Android runtime not tested"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("decoded", type=Path)
    arguments = parser.parse_args()
    result = check(arguments.decoded)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    sys.exit(0 if result["compatible"] else 1)
