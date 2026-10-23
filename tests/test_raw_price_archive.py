import json
import unittest
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory

import pandas as pd

from raw_price_archive import archive_prices, archived_csv_sha256, load_price_archive


def sample_prices() -> pd.DataFrame:
    return pd.DataFrame({
        "date": pd.to_datetime(["2026-01-02", "2026-01-02", "2026-01-05", "2026-01-05"]),
        "ticker": ["SPY", "TLT", "SPY", "TLT"],
        "Open": [100.0, 90.0, 101.0, 91.0],
        "High": [102.0, 91.0, 103.0, 92.0],
        "Low": [99.0, 89.0, 100.0, 90.0],
        "Close": [101.0, 90.5, 102.0, 91.5],
        "Volume": [1000, 800, 1100, 850],
    })


class RawPriceArchiveTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Path(".test_tmp").mkdir(exist_ok=True)

    def test_archive_is_content_addressed_and_idempotent(self):
        with TemporaryDirectory(dir=".test_tmp") as directory:
            root = Path(directory)
            first = archive_prices(sample_prices(), root=root, retrieved_at="2026-10-22T00:00:00+00:00")
            second = archive_prices(sample_prices(), root=root, retrieved_at="2099-01-01T00:00:00+00:00")
            self.assertEqual(first, second)
            self.assertEqual(len(list(root.glob("*/prices.csv"))), 1)
            data_path = root / str(first["version_id"]) / "prices.csv"
            self.assertEqual(sha256(data_path.read_bytes()).hexdigest(), first["sha256"])
            data_path.write_bytes(data_path.read_bytes().replace(b"\n", b"\r\n"))
            self.assertEqual(archived_csv_sha256(data_path), first["sha256"])
            loaded = load_price_archive(str(first["version_id"]), root=root)
            self.assertEqual(len(loaded), 4)

    def test_loader_requires_explicit_version_and_detects_tampering(self):
        with TemporaryDirectory(dir=".test_tmp") as directory:
            root = Path(directory)
            manifest = archive_prices(sample_prices(), root=root)
            with self.assertRaisesRegex(ValueError, "explicit"):
                load_price_archive("latest", root=root)
            data_path = root / str(manifest["version_id"]) / "prices.csv"
            data_path.write_text("tampered", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "hash mismatch"):
                load_price_archive(str(manifest["version_id"]), root=root)

    def test_manifest_has_reproducibility_fields(self):
        with TemporaryDirectory(dir=".test_tmp") as directory:
            root = Path(directory)
            manifest = archive_prices(sample_prices(), root=root)
            stored = json.loads(
                (root / str(manifest["version_id"]) / "manifest.json").read_text(encoding="utf-8")
            )
            required = {"version_id", "provider", "price_adjustment", "retrieved_at_utc",
                        "sha256", "rows", "tickers", "first_date", "last_date"}
            self.assertTrue(required.issubset(stored))


if __name__ == "__main__":
    unittest.main()
