"""Exercise shared SEO source and local plugin preparation without network access."""

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / ".agents/skills/seo-ai-optimization/scripts"))
from test_audit_html import HtmlInventoryTests  # noqa: E402,F401; include the seven behavior tests


def load_source(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


configure = load_source("seo_configure", ROOT / "tools/seo-audit-tools/configure.py")
runner = load_source("seo_lighthouse_runner", ROOT / "tools/seo-audit-tools/scripts/run_lighthouse.py")


class PluginPreparationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="seo-plugin-test-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.node, self.chrome = self.root / "node executable", self.root / "chrome executable"
        self.node.touch()
        self.chrome.touch()
        self.packages = self.root / "packages"
        for name, version in configure.VERSIONS.items():
            folder = self.packages / "node_modules" / name
            folder.mkdir(parents=True)
            (folder / "package.json").write_text(json.dumps({"version": version}), encoding="utf-8")
            entry = folder / configure.ENTRIES[name]
            entry.parent.mkdir(parents=True)
            entry.touch()
        self.output = self.root / "local plugins/seo-audit-tools"

    def build(self):
        return configure.build_plugin(self.node, self.chrome, self.packages, self.output)

    def test_prepares_isolated_mcp_without_changing_inputs(self):
        self.build()
        config = json.loads((self.output / ".mcp.json").read_text())
        server = config["mcpServers"]["chrome-devtools-seo"]
        self.assertEqual(server["command"], str(self.node.resolve()))
        self.assertIn(f"--executable-path={self.chrome.resolve()}", server["args"])
        self.assertIn("--isolated", server["args"])
        self.assertIn("--no-usage-statistics", server["args"])
        self.assertIn("--no-performance-crux", server["args"])
        self.assertIn("--redact-network-headers", server["args"])
        self.assertEqual(server["env"]["CHROME_DEVTOOLS_MCP_NO_UPDATE_CHECKS"], "1")
        self.assertTrue((self.output / ".codex-plugin/plugin.json").is_file())
        self.assertTrue((self.output / "scripts/close_chrome.mjs").is_file())
        self.assertEqual(self.node.read_bytes(), b"")

    def test_existing_output_is_preserved(self):
        self.output.mkdir(parents=True)
        marker = self.output / "user-file.txt"
        marker.write_text("preserve me", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "never overwritten"):
            self.build()
        self.assertEqual(marker.read_text(), "preserve me")
        self.assertEqual(list(self.output.iterdir()), [marker])

    def test_wrong_package_version_creates_no_output(self):
        metadata = self.packages / "node_modules/lighthouse/package.json"
        metadata.write_text('{"version":"0.0.0"}', encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Expected installed lighthouse"):
            self.build()
        self.assertFalse(self.output.exists())

    def test_missing_entrypoint_creates_no_output(self):
        (self.packages / "node_modules/lighthouse" / configure.ENTRIES["lighthouse"]).unlink()
        with self.assertRaisesRegex(ValueError, "entrypoint is missing"):
            self.build()
        self.assertFalse(self.output.exists())

    def test_missing_executable_creates_no_output(self):
        self.chrome.unlink()
        with self.assertRaisesRegex(ValueError, "Chrome executable"):
            self.build()
        self.assertFalse(self.output.exists())

    def test_profile_cleanup_refuses_other_directory(self):
        sentinel = self.root / "user-data.txt"
        sentinel.write_text("keep", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Refusing cleanup"):
            runner.clean_owned_profile(self.root)
        self.assertEqual(sentinel.read_text(), "keep")


if __name__ == "__main__":
    unittest.main()
