"""Offline tests for Swedish server metadata generator, using synthetic package bytes."""
import gzip
import hashlib
from pathlib import Path
import sys
import tempfile
import unittest
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parent))
from generate_swedish_catalog import build_entry

URL = "https://github.com/example/swype/releases/download/v1/Swedish.zip"


def make_pack(path, *, missing=False, corrupt=False):
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("Swedish.mdf", b"SVusUN_xt9_ALM3.ldb\ndatabase_le.dat\n")
        z.writestr("SVusUN_xt9_ALM3.ldb.mp3", b"not a gzip" if corrupt else gzip.compress(b"test words"))
        if not missing:
            z.writestr("database_le.dat.mp3", gzip.compress(b"test shared db"))


class CatalogTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.pack = Path(self.tmp.name) / "sv.zip"
        make_pack(self.pack)

    def test_valid_catalog_uses_original_language_id_and_actual_md5(self):
        entry = build_entry(self.pack, URL, "11.03", "1")
        self.assertEqual(entry["146"], [285])
        self.assertEqual(entry["10"], hashlib.md5(self.pack.read_bytes()).hexdigest())
        self.assertEqual(entry["102"], "11.03")
        self.assertEqual(set(entry), {"11", "20", "51", "10", "102", "122", "124", "146"})

    def test_reject_missing_database(self):
        make_pack(self.pack, missing=True)
        with self.assertRaisesRegex(ValueError, "exactly three"):
            build_entry(self.pack, URL, "11.03", "1")

    def test_reject_invalid_gzip(self):
        make_pack(self.pack, corrupt=True)
        with self.assertRaises(OSError):
            build_entry(self.pack, URL, "11.03", "1")

    def test_reject_wrong_swedish_language_id(self):
        with self.assertRaisesRegex(ValueError, "285"):
            build_entry(self.pack, URL, "11.03", "1", 286)

    def test_reject_unverified_version_format(self):
        with self.assertRaisesRegex(ValueError, "major.minor"):
            build_entry(self.pack, URL, "XT9 V11.03.07.00", "1")

    def test_reject_draft_or_unapproved_url(self):
        for url in ["https://github.com/example/project/releases/tag/v1",
                    "https://attacker.example/words.zip", "http://github.com/words.zip"]:
            with self.subTest(url=url), self.assertRaises(ValueError):
                build_entry(self.pack, url, "11.03", "1")


if __name__ == "__main__":
    unittest.main()
