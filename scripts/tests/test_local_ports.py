"""Regression coverage for the local Docker PostgreSQL connection boundary."""

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
LOCAL_POSTGRES_CONSUMERS = (
    "apps/api/app/config.py",
    "apps/api/app/db.py",
    "apps/api/tests/conftest.py",
    "apps/api/tests/test_commerce.py",
    "scripts/verify_application.py",
)


class LocalPortConfigurationTests(unittest.TestCase):
    def test_postgres_host_port_is_consistent_for_all_local_consumers(self):
        compose = (ROOT / "compose.yaml").read_text(encoding="utf-8")
        self.assertIn('"127.0.0.1:5433:5432"', compose)
        self.assertNotIn("55450", compose)
        for relative_path in LOCAL_POSTGRES_CONSUMERS:
            with self.subTest(path=relative_path):
                content = (ROOT / relative_path).read_text(encoding="utf-8")
                self.assertIn("127.0.0.1:5433", content)
                self.assertNotIn("55450", content)


if __name__ == "__main__":
    unittest.main()
