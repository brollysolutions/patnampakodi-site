"""A linked-worktree push hook must not redirect fixture Git writes to its caller."""
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from setup_workflow import find_bash

ROOT = Path(__file__).resolve().parents[2]


class HookEnvironmentTests(unittest.TestCase):
    def test_foreign_repository_writes_preserve_the_calling_worktree(self):
        # Even the regression's setup must be safe when invoked by an unfixed hook.
        clean = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            source, linked, foreign = (base / name for name in ("source", "linked", "foreign"))

            def git(cwd, *args):
                return subprocess.run(["git", *args], cwd=cwd, env=clean, check=True,
                                      capture_output=True, text=True).stdout.strip()

            for repository in (source, foreign):
                repository.mkdir()
                git(repository, "init", "--initial-branch=fix/fixture")
                git(repository, "config", "user.name", "Fixture Owner")
                git(repository, "config", "user.email", "fixture@example.invalid")
                (repository / "README.md").write_text("preserve me\n", encoding="utf-8")
                git(repository, "add", "README.md")
                git(repository, "commit", "-m", "test: fixture")
            git(source, "worktree", "add", "-b", "fix/linked", str(linked))
            before = git(linked, "rev-parse", "HEAD")
            original = (linked / "README.md").read_bytes()
            probe = base / "probe.py"
            probe.write_text('''import os, subprocess, sys
from pathlib import Path
assert sys.stdin.read() == "", "Verification consumed the push reference stream"
target = Path(os.environ["FIXTURE_TARGET"]).resolve()
def git(*args):
    return subprocess.run(["git", *args], cwd=target, check=True,
                          capture_output=True, text=True).stdout.strip()
assert Path(git("rev-parse", "--show-toplevel")).resolve() == target, "Fixture Git inherited the caller's repository"
assert git("config", "--get", "user.name") == "Fixture Owner", "Fixture inherited command-scoped configuration"
(target / "README.md").write_text("verified foreign write\\n", encoding="utf-8")
if git("status", "--porcelain"):
    git("add", "README.md")
    git("commit", "-m", "test: isolated foreign write")
''', encoding="utf-8")
            binary = base / "bin"
            binary.mkdir()
            shim = binary / "uv"
            shim.write_text('#!/usr/bin/env bash\nexec "$FIXTURE_PYTHON" "$FIXTURE_PROBE"\n',
                            encoding="utf-8", newline="\n")
            shim.chmod(0o755)
            environment = {
                **clean, "PATH": str(binary) + os.pathsep + clean.get("PATH", ""),
                "FIXTURE_PYTHON": sys.executable, "FIXTURE_PROBE": str(probe),
                "FIXTURE_TARGET": str(foreign),
                "GIT_DIR": git(linked, "rev-parse", "--absolute-git-dir"),
                "GIT_WORK_TREE": str(linked),
                "GIT_COMMON_DIR": git(source, "rev-parse", "--absolute-git-dir"),
                "GIT_INDEX_FILE": git(linked, "rev-parse", "--path-format=absolute", "--git-path", "index"),
                "GIT_PREFIX": "fixture-prefix/",
                "GIT_CONFIG_COUNT": "1", "GIT_CONFIG_KEY_0": "user.name",
                "GIT_CONFIG_VALUE_0": "Leaked fixture identity",
            }
            for remote, expected in (("refs/heads/fix/linked", 0), ("refs/heads/main", 1)):
                result = subprocess.run([find_bash(), str(ROOT / ".githooks/pre-push")],
                    cwd=linked, env=environment, input=f"refs/heads/fix/linked {before} {remote} {'0' * 40}\n",
                    capture_output=True, text=True, timeout=30)
                self.assertEqual(result.returncode, expected, result.stderr)
                if expected:
                    self.assertIn("direct pushes to protected ref", result.stderr)
                self.assertEqual(git(linked, "rev-parse", "HEAD"), before)
                self.assertEqual((linked / "README.md").read_bytes(), original)
                self.assertEqual(git(linked, "status", "--porcelain"), "")
                self.assertEqual(git(linked, "config", "user.name"), "Fixture Owner")
            self.assertEqual((foreign / "README.md").read_text(), "verified foreign write\n")
