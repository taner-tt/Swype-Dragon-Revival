"""Run locally with SWYPE_3722_REFERENCE_APK pointing to the private original APK."""
import os
from pathlib import Path
import sys
import tempfile
import unittest
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parent))
from verify_3722_language_candidate import verify

SOURCE = Path(os.environ["SWYPE_3722_REFERENCE_APK"])

class GuardTests(unittest.TestCase):
    def test_reference_contract(self):
        result = verify(SOURCE)
        self.assertTrue(result["reference_has_all_exact_methods"])
        self.assertTrue(result["reference_has_klipy_secondary_dex"])
        self.assertFalse(result["reference_embedded_swedish"])
        self.assertTrue(result["reference_embedded_english"])

    def test_unmodified_apk_does_not_pass_as_patched_candidate(self):
        result = verify(SOURCE, SOURCE)
        self.assertFalse(result["candidate_bridge_present"])
        self.assertFalse(result["candidate_passes_structural_guard"])
        self.assertTrue(result["candidate_klipy_classes2_unchanged"])

    def test_detects_modified_shared_database(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / "changed.apk"
            with zipfile.ZipFile(SOURCE) as source, zipfile.ZipFile(target, "w") as altered:
                for item in source.infolist():
                    data = source.read(item.filename)
                    if item.filename == "assets/database_le.dat.mp3":
                        data = b"INVALID" + data
                    altered.writestr(item, data)
            result = verify(SOURCE, target)
            self.assertFalse(result["protected_resources_unchanged"])
            self.assertIn("assets/database_le.dat.mp3", result["protected_resources_missing_or_changed"])
            self.assertFalse(result["candidate_passes_structural_guard"])

    def test_detects_modified_klipy_secondary_dex(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / "changed.apk"
            with zipfile.ZipFile(SOURCE) as source, zipfile.ZipFile(target, "w") as altered:
                for item in source.infolist():
                    data = source.read(item.filename)
                    if item.filename == "classes2.dex":
                        data = data[:-1] + bytes([data[-1] ^ 1])
                    altered.writestr(item, data)
            result = verify(SOURCE, target)
            self.assertFalse(result["candidate_klipy_classes2_unchanged"])
            self.assertFalse(result["candidate_passes_structural_guard"])

if __name__ == "__main__":
    unittest.main()
