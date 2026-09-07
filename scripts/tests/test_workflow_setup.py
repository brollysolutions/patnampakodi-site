"""Regression checks for per-clone setup and truthful verification results."""
import argparse
from contextlib import ExitStack, redirect_stderr
import io
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import setup_workflow as setup
import verify_workflow as verify
import agent_workflow as workflow


class SetupTests(unittest.TestCase):
    def test_modified_first_path_keeps_first_character(self):
        with patch.object(workflow, "run", return_value=subprocess.CompletedProcess(
            [], 0, " M .env.local\n M README.md\n", ""
        )):
            paths = workflow.working_tree_paths(Path.cwd())
        self.assertEqual(paths, [".env.local", "README.md"])
        self.assertTrue(workflow.is_sensitive_path(paths[0]))

    def test_existing_private_notes_survive_repeated_setup(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            templates = root / "docs/workflow-templates"
            (templates / "private").mkdir(parents=True)
            (templates / "CLAUDE.local.md").write_text("local instructions", encoding="utf-8")
            (templates / "private/DESIGN.md").write_text("initial design", encoding="utf-8")
            setup.initialize_private_notes(root)
            notes = root / ".agent-workflow/DESIGN.md"
            notes.write_text("partner's decisions", encoding="utf-8")
            setup.initialize_private_notes(root)
            self.assertEqual(notes.read_text(encoding="utf-8"), "partner's decisions")
            self.assertEqual((root / "CLAUDE.local.md").read_text(encoding="utf-8"), "local instructions")

    def test_failed_setup_command_raises(self):
        with patch.object(setup.subprocess, "run", side_effect=subprocess.CalledProcessError(7, "git")):
            with self.assertRaises(subprocess.CalledProcessError):
                setup.run("git", "config", "--local", "core.hooksPath", ".githooks")

    def test_verification_stops_after_failed_test(self):
        with patch.object(sys, "argv", ["verify_workflow.py", "--ci"]), patch.object(
            verify.subprocess, "run", return_value=subprocess.CompletedProcess([], 7)
        ) as execute:
            self.assertEqual(verify.main(), 7)
            self.assertEqual(execute.call_count, 1)

    def test_unknown_mode_fails(self):
        with patch.object(sys, "argv", ["verify_workflow.py", "typo"]), patch.object(
            verify.subprocess, "run"
        ) as execute:
            self.assertEqual(verify.main(), 2)
            execute.assert_not_called()


class DeliveryFailureTests(unittest.TestCase):
    def exercise_failure(self, pending, failed_prefix):
        commands = []

        def execute(args, **kwargs):
            commands.append(list(args))
            failed = list(args[:len(failed_prefix)]) == failed_prefix
            return subprocess.CompletedProcess(args, 7 if failed else 0, "", "test failure" if failed else "")

        args = argparse.Namespace(cwd=None, title="chore: test delivery",
                                  commit_message="chore: test delivery",
                                  body_file=None, verification="tests", security="reviewed")
        with ExitStack() as stack:
            values = {"repo_root": Path.cwd(), "ensure_hooks_path": None,
                      "current_branch": "chore/test", "working_tree_paths": pending,
                      "base_ref": "upstream/main", "commits_ahead": 1,
                      "changed_paths": [], "has_remote": True,
                      "git": "https://github.com/example/project.git"}
            for name, value in values.items():
                stack.enter_context(patch.object(workflow, name, return_value=value))
            stack.enter_context(patch.object(workflow, "run", side_effect=execute))
            stack.enter_context(redirect_stderr(io.StringIO()))
            self.assertEqual(workflow.cmd_finish(args), 1)
        return commands

    def test_staging_failure_never_commits_or_pushes(self):
        commands = self.exercise_failure(["README.md"], ["git", "add"])
        self.assertFalse(any(command[:2] in (["git", "commit"], ["git", "push"]) for command in commands))

    def test_pr_lookup_failure_never_creates_duplicate(self):
        commands = self.exercise_failure([], ["gh", "pr", "list"])
        self.assertTrue(any(command[:2] == ["git", "push"] for command in commands))
        self.assertFalse(any(command[:3] == ["gh", "pr", "create"] for command in commands))


if __name__ == "__main__":
    unittest.main()
