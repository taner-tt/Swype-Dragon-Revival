"""Regression test for numeric Nuance MessageAPI keys in the GitHub bridge.

Uses synthetic smali fixtures; it does NOT establish APK/runtime compatibility.
"""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
PATCH = HERE / "patch_language_catalog.py"


class BridgeKeyTest(unittest.TestCase):
    def test_language_list_is_stored_under_integer_43(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            work = root / "language-packs"
            work.mkdir()
            shutil.copyfile(PATCH, work / PATCH.name)
            catalog = {
                "43": [{
                    "11": "Swedish", "20": "1", "51": "https://github.com/example/test/releases/download/v1/Swedish.zip",
                    "10": "0123456789abcdef0123456789abcdef", "122": "SE", "124": "Svenska",
                    "146": [1], "102": "1"
                }]
            }
            (work / "nuance-language-list.json").write_text(json.dumps(catalog), encoding="utf-8")
            smali = root / "decoded" / "smali" / "com" / "nuance" / "connect"
            manager = smali / "service" / "manager"
            comm = smali / "comm"
            manager.mkdir(parents=True)
            comm.mkdir(parents=True)
            transaction = manager / "LanguageManager$LanguageListTransaction.smali"
            transaction.write_text(
                ".class public Ltest;\n"
                ".method private getList()V\n    .locals 0\n    return-void\n.end method\n"
                "# access$100(\n", encoding="utf-8")
            (comm / "Response.smali").write_text(
                ".field public status:I\n.field public parameters:Ljava/util/HashMap;\n",
                encoding="utf-8")
            subprocess.run(
                [sys.executable, str(work / PATCH.name), str(root / "decoded")],
                check=True, capture_output=True, text=True
            )
            bridge = (manager / "GitHubLanguageCatalog.smali").read_text(encoding="utf-8")
            self.assertIn("const/16 v4, 0x2b", bridge)
            self.assertIn("Ljava/lang/Integer;->valueOf(I)", bridge)
            self.assertIn("invoke-virtual {v3, v4, v1}, Ljava/util/HashMap;->put(", bridge)
            self.assertNotIn("invoke-virtual {v3, v0, v1}, Ljava/util/HashMap;->put(", bridge)


if __name__ == "__main__":
    unittest.main()
