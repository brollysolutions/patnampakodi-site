"""Regression tests from the workflow audit; fixtures contain no real secrets."""
from contextlib import nullcontext, redirect_stderr
import io
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import agent_workflow as workflow
from setup_workflow import find_bash


class GuardRegressionTests(unittest.TestCase):
    def test_force_push_variants_are_denied_on_task_branches(self):
        for command in ("git push --force origin feat/x", "git push -f origin feat/x",
                        "git push --force-with-lease origin feat/x",
                        "git push origin +HEAD:feat/x"):
            with self.subTest(command=command):
                self.assertIsNotNone(workflow.command_is_blocked(command, "feat/x"))

    def test_explicit_sensitive_path_with_spaces_is_denied(self):
        self.assertEqual(workflow.sensitive_tool_input({"file_path": "my project/.env"}),
                         "my project/.env")

    def test_patch_headers_cannot_edit_or_move_to_sensitive_paths(self):
        for header in ("*** Add File: .env", "*** Update File: my project/.env",
                       "*** Delete File: .env", "*** Move to: secrets/token.txt"):
            with self.subTest(header=header), patch.object(workflow, "current_branch", return_value="fix/test"):
                decision = workflow.handle_pre_tool_use(Path.cwd(), {
                    "tool_name": "apply_patch",
                    "tool_input": {"command": "*** Begin Patch\n" + header + "\n+fixture\n*** End Patch"},
                }, "codex")
                self.assertEqual(decision.get("hookSpecificOutput", {}).get("permissionDecision"), "deny")

    def test_patch_prose_mentioning_env_is_allowed(self):
        with patch.object(workflow, "current_branch", return_value="fix/test"):
            self.assertEqual(workflow.handle_pre_tool_use(Path.cwd(), {
                "tool_name": "apply_patch", "tool_input": {"command":
                    "*** Begin Patch\n*** Add File: README.md\n+Document .env setup\n*** End Patch"},
            }, "codex"), {})


class GitPathRegressionTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.git("init", "--initial-branch=fix/test")
        self.git("config", "user.name", "Workflow Test")
        self.git("config", "user.email", "workflow@example.invalid")
        (self.root / "README.md").write_text("fixture", encoding="utf-8")
        self.git("add", "README.md")
        self.git("commit", "-m", "test: base")
        self.base = self.git("rev-parse", "HEAD").stdout.strip()

    def git(self, *args):
        return subprocess.run(["git", *args], cwd=self.root, check=True,
                              capture_output=True, text=True, encoding="utf-8")

    def test_status_paths_preserve_unicode_spaces_and_rename_sources(self):
        (self.root / "café").mkdir()
        (self.root / "café/.env").write_text("dummy test fixture", encoding="utf-8")
        self.git("mv", "README.md", "renamed notes.md")
        self.assertEqual(set(workflow.working_tree_paths(self.root)),
                         {"café/.env", "README.md", "renamed notes.md"})

    def test_failed_diff_is_an_error_not_an_empty_safe_diff(self):
        with self.assertRaises(workflow.GitError):
            workflow.changed_paths(self.root, ["missing-ref...HEAD"])

    def test_history_check_detects_removed_sensitive_fixture(self):
        fixture = self.root / ".env"
        fixture.write_text("dummy test fixture", encoding="utf-8")
        self.git("add", ".env")
        self.git("commit", "-m", "test: add fixture")
        fixture.unlink()
        self.git("add", ".env")
        self.git("commit", "-m", "test: remove fixture")
        self.assertEqual(workflow.changed_paths(self.root, [f"{self.base}...HEAD"]), [])
        self.assertIn(".env", workflow.committed_paths(self.root, self.base))


class DeliverySelectionTests(unittest.TestCase):
    def exercise(self, selected, staged=(), history=(), failed_command=None):
        commands = []
        def execute(args, **kwargs):
            commands.append(args)
            rc = 1 if args[:2] == failed_command else 0
            return subprocess.CompletedProcess(args, rc, "", "fixture failure" if rc else "")
        from contextlib import ExitStack
        with ExitStack() as stack:
            for name, value in {"repo_root": Path.cwd(), "ensure_hooks_path": None,
                "current_branch": "fix/test", "working_tree_paths": ["README.md", "user notes.md"],
                "changed_paths": list(staged), "committed_paths": list(history),
                "base_ref": "origin/main", "commits_ahead": 1, "git": "fixture"}.items():
                stack.enter_context(patch.object(workflow, name, return_value=value))
            stack.enter_context(patch.object(workflow, "run", side_effect=execute))
            stack.enter_context(patch.object(workflow, "delivery_lock", return_value=nullcontext()))
            stack.enter_context(redirect_stderr(io.StringIO()))
            args = argparse.Namespace(cwd=None, title="fix: fixture", commit_message="fix: fixture",
                                      paths=selected, body_file=None, verification="tests", security="reviewed")
            self.assertEqual(workflow.cmd_finish(args), 1)
        return commands

    def test_missing_selection_does_not_stage_commit_or_push(self):
        commands = self.exercise(None)
        self.assertFalse(any("add" in command or "commit" in command or "push" in command for command in commands))

    def test_unrelated_staged_file_is_preserved(self):
        commands = self.exercise(["README.md"], staged=["user notes.md"])
        self.assertFalse(any("add" in command or "commit" in command or "push" in command for command in commands))

    def test_only_explicit_files_are_staged(self):
        commands = self.exercise(["README.md"], failed_command=["git", "commit"])
        add = next(command for command in commands if "add" in command)
        self.assertEqual(add, ["git", "--literal-pathspecs", "add", "--", "README.md"])

    def test_sensitive_history_blocks_push(self):
        commands = self.exercise(["README.md"], history=[".env"])
        self.assertFalse(any(command[:2] == ["git", "push"] for command in commands))


class HookEntrypointTests(unittest.TestCase):
    def test_configured_codex_hook_works_from_subdirectory(self):
        root = Path(__file__).resolve().parents[2]
        config = json.loads((root / ".codex/hooks.json").read_text(encoding="utf-8"))
        hook = config["hooks"]["PreToolUse"][0]["hooks"][0]
        payload = json.dumps({"cwd": str(root), "hook_event_name": "PreToolUse",
            "tool_name": "Bash", "tool_input": {"command": "git push --force origin fix/test"}})
        shells = [[find_bash(), "-c", hook["command"]]]
        if os.name == "nt":
            shells.append(["powershell", "-NoProfile", "-Command", hook["commandWindows"]])
        for shell in shells:
            with self.subTest(shell=shell[0]):
                result = subprocess.run(shell, cwd=root / "scripts", input=payload,
                    capture_output=True, text=True, encoding="utf-8", timeout=30)
                self.assertEqual(result.returncode, 0, result.stderr)
                decision = json.loads(result.stdout)
                self.assertEqual(decision.get("hookSpecificOutput", {}).get("permissionDecision"), "deny", result.stderr)


if __name__ == "__main__":
    unittest.main()
