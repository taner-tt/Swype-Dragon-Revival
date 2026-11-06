import io
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import prepare_assets

class TestPrepareAssets(unittest.TestCase):
    def test_archive_with_manifest_files(self):
        inner = io.BytesIO()
        with zipfile.ZipFile(inner, "w") as z:
            z.writestr("Swedish.mdf", "metadata")
            z.writestr("SVusUN_xt9_ALM3.ldb.mp3", "test")
        with tempfile.TemporaryDirectory() as tmp:
            outer = Path(tmp) / "packs.zip"
            with zipfile.ZipFile(outer, "w") as z:
                z.writestr("Swedish.zip", inner.getvalue())
                z.writestr("manifest.csv", "name\nSwedish")
                z.writestr("manifest.json", "[]")
            out = Path(tmp) / "assets"
            with patch.object(sys, "argv", ["prepare_assets.py", str(outer), "--output", str(out)]):
                prepare_assets.main()
            self.assertEqual((out / "Swedish.zip").read_bytes(), inner.getvalue())
            self.assertIn("Swedish", (out / "manifest.json").read_text())

    def test_rejects_zip_slip(self):
        inner = io.BytesIO()
        with zipfile.ZipFile(inner, "w") as z:
            z.writestr("Swedish.mdf", "metadata")
            z.writestr("../bad.ldb", "test")
        with tempfile.TemporaryDirectory() as tmp:
            outer = Path(tmp) / "packs.zip"
            with zipfile.ZipFile(outer, "w") as z:
                z.writestr("Swedish.zip", inner.getvalue())
            with patch.object(sys, "argv", ["prepare_assets.py", str(outer), "--output", str(Path(tmp) / "assets")]):
                with self.assertRaises(ValueError):
                    prepare_assets.main()

if __name__ == "__main__":
    unittest.main()
