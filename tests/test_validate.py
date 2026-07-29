import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class RepositoryValidationTests(unittest.TestCase):
    def test_current_repository_is_valid(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "validate.py")],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_manifest_is_schema_version_one(self):
        manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["schemaVersion"], 1)
        self.assertIsInstance(manifest["profiles"], list)


if __name__ == "__main__":
    unittest.main()
