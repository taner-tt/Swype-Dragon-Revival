"""Regression tests for the generated GitHub language bridge's error behavior.

Tests generated smali against a synthetic transaction API. Not a device test.
"""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

PATCHER = Path(__file__).with_name("patch_language_catalog.py")


class GitHubLanguageBridgeTest(unittest.TestCase):
    def test_catalog_fallback_does_not_clear_existing_languages(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            scripts = base / "language-packs"
            scripts.mkdir()
            shutil.copyfile(PATCHER, scripts / PATCHER.name)
            (scripts / "nuance-language-list.json").write_text(json.dumps({
                "43": [{
                    "11": "Swedish",
                    "20": "1",
                    "51": "https://github.com/example/release/releases/download/v1/swedish.zip",
                    "10": "0123456789abcdef0123456789abcdef",
                    "122": "SE",
                    "124": "Svenska",
                    "146": [285],
                    "102": "11.03",
                }]
            }), encoding="utf-8")
            dst = base / "decoded" / "smali" / "com" / "nuance" / "connect"
            manager = dst / "service" / "manager"
            comm = dst / "comm"
            manager.mkdir(parents=True)
            comm.mkdir(parents=True)
            (manager / "LanguageManager$LanguageListTransaction.smali").write_text(
                ".class public Ltest;\n"
                ".method private getList()V\n    .locals 0\n    return-void\n.end method\n"
                "# access$100(\n", encoding="utf-8")
            (manager / "LanguageManager.smali").write_text(
                ".method public requestLanguagesList(Ljava/lang/String;)V\\n"
                "    .locals 1\\n"
                "    new-instance v0, Lcom/nuance/connect/service/manager/LanguageManager$LanguageListTransaction;\\n"
                "    invoke-direct {v0, p0, p1}, Lcom/nuance/connect/service/manager/LanguageManager$LanguageListTransaction;-><init>(Lcom/nuance/connect/service/manager/LanguageManager;Ljava/lang/String;)V\\n"
                "    invoke-virtual {p0, v0}, Lcom/nuance/connect/service/manager/LanguageManager;->startTransaction(Lcom/nuance/connect/comm/Transaction;)V\\n"
                "    return-void\\n.end method\\n", encoding="utf-8")
            (comm / "Response.smali").write_text(
                ".field public status:I\n.field public parameters:Ljava/util/HashMap;\n",
                encoding="utf-8")
            subprocess.run([sys.executable, str(scripts / PATCHER.name), str(base / "decoded")],
                           check=True, capture_output=True, text=True)
            bridge = (manager / "GitHubLanguageCatalog.smali").read_text(encoding="utf-8")
            manager_code = (manager / "LanguageManager.smali").read_text(encoding="utf-8")
            request_code = manager_code.split(".method public requestLanguagesList(", 1)[1].split(".end method", 1)[0]
            self.assertNotIn("->startTransaction(", request_code)
            self.assertIn("const/high16 v5, 0x100000", bridge)
            self.assertIn("Language catalog larger than 1 MiB", bridge)
            self.assertIn("completeWithoutCatalog()V", bridge)
            self.assertIn("AtomicBoolean;->compareAndSet(ZZ)Z", bridge)
            self.assertIn("GitHubLanguageCatalog;->releaseInFlight()V", bridge)
            self.assertIn("LanguageListTransaction;->onEndProcessing()V", bridge)
            self.assertIn("invoke-virtual {v3, v0, v1}, Ljava/util/HashMap;->put(", bridge)
            fallback = bridge.split(".method private completeWithoutCatalog()V", 1)[1]
            self.assertNotIn("const-string v", fallback.split(".end method", 1)[0])
            self.assertNotIn("JSONArray", fallback.split(".end method", 1)[0])
            self.assertIn("Response;->parameters:Ljava/util/HashMap;", fallback)
            self.assertIn("LanguageListTransaction;->access$100(", fallback)
            if os.getenv("SWYPE_SMALI_ASSEMBLE") == "1":
                # Only syntax/register verification. Class references resolve at APK runtime.
                subprocess.run(
                    ["java", "-jar", "/usr/share/java/smali.jar", "assemble",
                     str(manager / "GitHubLanguageCatalog.smali"),
                     "-o", str(base / "bridge.dex")],
                    check=True, capture_output=True, text=True
                )
                self.assertGreater((base / "bridge.dex").stat().st_size, 0)


if __name__ == "__main__":
    unittest.main()
