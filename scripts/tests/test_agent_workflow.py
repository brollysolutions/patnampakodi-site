#!/usr/bin/env python3
"""Self-tests for the agent workflow engine.

Hermetic: no Git repository, no network, no `gh`. The git layer is stubbed so
the guards themselves are what gets tested. Run directly:

    uv run --no-project python scripts/tests/test_agent_workflow.py
"""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import agent_workflow as aw  # noqa: E402

ROOT = Path("/repo")


class SkillSourceParityTests(unittest.TestCase):
    def test_generated_bytecode_is_ignored_but_source_changes_are_visible(self):
        with tempfile.TemporaryDirectory(prefix="skill-parity-test-") as directory:
            root = Path(directory)
            left, right = root / "agents", root / "claude"
            for tree in (left, right):
                (tree / "skill/scripts").mkdir(parents=True)
                (tree / "skill/SKILL.md").write_text("same instructions", encoding="utf-8")
                (tree / "skill/scripts/helper.py").write_text("print(1)", encoding="utf-8")
            cache = left / "skill/scripts/__pycache__"
            cache.mkdir()
            (cache / "helper.cpython-312.pyc").write_bytes(b"generated")
            (left / "skill/scripts/legacy.pyc").write_bytes(b"generated")
            self.assertEqual(aw._tree_files(left), aw._tree_files(right))
            (right / "skill/scripts/helper.py").write_text("print(2)", encoding="utf-8")
            self.assertNotEqual(aw._tree_files(left), aw._tree_files(right))


class SensitivePathTests(unittest.TestCase):
    def test_sensitive(self) -> None:
        for path in (
            ".env",
            ".env.local",
            "apps/api/.env.production",
            r"apps\web\.env",
            "secrets/token.txt",
            "deploy/secrets/db.json",
            "config/.npmrc",
            "~/.pypirc",
            "gcp/service-account.json",
            "a/credentials.json",
            "keys/id_rsa",
            "keys/id_ed25519",
            "certs/server.pem",
            "certs/tls.key",
            "certs/bundle.p12",
            "certs/bundle.pfx",
            "java/app.keystore",
            "backups/nightly.dump",
            "backups/nightly.backup",
        ):
            with self.subTest(path=path):
                self.assertTrue(aw.is_sensitive_path(path))

    def test_not_sensitive(self) -> None:
        for path in (
            "",
            "README.md",
            "apps/api/app/main.py",
            ".env.example",
            ".env.production.example",
            "secrets.md",
            "docs/secrets-policy.md",
            "certs/server.pem.example",
        ):
            with self.subTest(path=path):
                self.assertFalse(aw.is_sensitive_path(path))


class BlockedCommandTests(unittest.TestCase):
    def assertBlocked(self, command: str, branch: str | None = "feat/x") -> None:
        self.assertIsNotNone(
            aw.command_is_blocked(command, branch), f"expected block: {command!r} on {branch!r}"
        )

    def assertAllowed(self, command: str, branch: str | None = "feat/x") -> None:
        reason = aw.command_is_blocked(command, branch)
        self.assertIsNone(reason, f"expected allow: {command!r} on {branch!r} -> {reason}")

    def test_1_pr_merge_and_close(self) -> None:
        self.assertBlocked("gh pr merge 12 --squash")
        self.assertBlocked("gh pr close 12")
        self.assertAllowed("gh pr create --title x --body y")
        self.assertAllowed("gh pr view 12")

    def test_2_destructive_to_user_work(self) -> None:
        self.assertBlocked("git reset --hard HEAD~1")
        self.assertBlocked("git clean -fd")
        self.assertBlocked("git clean -f")
        self.assertBlocked("git checkout -- apps/api/app/main.py")
        self.assertBlocked("git restore apps/api/app/main.py")
        self.assertAllowed("git reset HEAD~1")
        self.assertAllowed("git checkout feat/other")

    def test_3_reading_a_secret(self) -> None:
        self.assertBlocked("cat .env")
        self.assertBlocked("head -5 apps/api/.env.local")
        self.assertBlocked("Get-Content .env")
        self.assertBlocked("Select-String token secrets/creds.txt")
        self.assertAllowed("cat .env.example")
        self.assertAllowed("cat README.md")

    def test_4_writing_a_secret(self) -> None:
        self.assertBlocked("rm -rf secrets/")
        self.assertBlocked("cp .env .env.bak")
        self.assertBlocked("sed -i 's/a/b/' apps/api/.env")
        self.assertBlocked("git add .env")
        self.assertBlocked("Set-Content .env 'x'")
        self.assertAllowed("git add apps/api/app/main.py")

    def test_5_pushing_to_a_protected_ref(self) -> None:
        self.assertBlocked("git push origin main")
        self.assertBlocked("git push origin HEAD:refs/heads/main")
        self.assertBlocked("git push --force origin feat/x:master")
        self.assertBlocked("git push", branch="main")
        self.assertBlocked("git push origin prod")
        self.assertAllowed("git push --set-upstream origin feat/x")

    def test_6_mutation_on_a_protected_branch(self) -> None:
        for command in (
            "git add .",
            "git commit -m 'x'",
            "git merge feat/x",
            "git rebase main",
            "git cherry-pick abc123",
            "git tag v1",
            "mkdir apps",
            "touch a.txt",
            "rm a.txt",
            "cp a b",
            "mv a b",
            "sed -i 's/a/b/' a.txt",
            "New-Item a.txt",
            "Set-Content a.txt 'x'",
        ):
            with self.subTest(command=command):
                self.assertBlocked(command, branch="main")

    def test_6_allowed_on_a_task_branch(self) -> None:
        for command in ("git add .", "git commit -m 'x'", "mkdir apps", "touch a.txt"):
            with self.subTest(command=command):
                self.assertAllowed(command, branch="feat/x")

    def test_read_only_commands_always_allowed(self) -> None:
        for command in ("ls -la", "git status", "git log --oneline", "grep -r foo .", "pwd"):
            with self.subTest(command=command):
                self.assertAllowed(command, branch="main")

    def test_compound_commands_are_inspected_per_segment(self) -> None:
        self.assertBlocked("echo hi && cat .env")
        self.assertBlocked("ls; git reset --hard")
        self.assertBlocked("cat .env | grep TOKEN")
        self.assertAllowed("echo hi && ls -la", branch="feat/x")

    def test_empty_command(self) -> None:
        self.assertAllowed("")
        self.assertAllowed("   ")


class NamingTests(unittest.TestCase):
    def test_conventional_title(self) -> None:
        for title in (
            "feat: add x",
            "fix(api): correct y",
            "security(auth): tighten z",
            "refactor(apps/web)!: drop q",
            "chore: bump deps",
        ):
            self.assertTrue(aw.conventional_ok(title), title)
        for title in ("add x", "Feat: add x", "feat add x", "feat:", "", "wip"):
            self.assertFalse(aw.conventional_ok(title), title)

    def test_slugify(self) -> None:
        self.assertEqual(aw.slugify("Add a Widget!"), "add-a-widget")
        self.assertEqual(aw.slugify("   "), "task")
        self.assertLessEqual(len(aw.slugify("x" * 200)), 48)
        self.assertFalse(aw.slugify("x" * 200).endswith("-"))

    def test_branch_name(self) -> None:
        name = aw.branch_name("claude", "Add a widget")
        self.assertRegex(name, r"^claude/\d{8}-\d{6}-add-a-widget$")
        self.assertRegex(aw.branch_name("codex", "fix"), r"^codex/")
        # An unknown agent must still produce an approved prefix.
        self.assertRegex(aw.branch_name("other", "fix"), r"^claude/")

    def test_branch_name_matches_ci_policy(self) -> None:
        import re

        policy = re.compile(
            r"(?:codex|claude|feat|fix|security|docs|refactor|test|chore|perf|build|ci|dependabot)"
            r"/[a-z0-9][a-z0-9._/-]*"
        )
        self.assertTrue(policy.fullmatch(aw.branch_name("claude", "Add a widget")))

    def test_remote_slug(self) -> None:
        self.assertEqual(aw.remote_slug("https://github.com/o/r.git"), "o/r")
        self.assertEqual(aw.remote_slug("git@github.com:o/r.git"), "o/r")
        self.assertEqual(aw.remote_slug("https://github.com/o/r"), "o/r")
        self.assertIsNone(aw.remote_slug(""))


class ToolInputTests(unittest.TestCase):
    def test_finds_nested_paths(self) -> None:
        self.assertEqual(aw.sensitive_tool_input({"file_path": ".env"}), ".env")
        self.assertEqual(
            aw.sensitive_tool_input({"edits": [{"file_path": "apps/api/.env.local"}]}),
            "apps/api/.env.local",
        )

    def test_prose_is_not_a_path(self) -> None:
        self.assertIsNone(aw.sensitive_tool_input({"prompt": "explain the .env file layout"}))
        self.assertIsNone(aw.sensitive_tool_input({"file_path": ".env.example"}))
        self.assertIsNone(aw.sensitive_tool_input({}))


class PreToolUseTests(unittest.TestCase):
    def call(self, payload: dict, branch: str = "feat/x") -> dict:
        with mock.patch.object(aw, "current_branch", return_value=branch):
            return aw.handle_pre_tool_use(ROOT, payload, "claude")

    def assertDenied(self, decision: dict) -> None:
        self.assertEqual(
            decision.get("hookSpecificOutput", {}).get("permissionDecision"), "deny", decision
        )

    def test_denies_sensitive_read(self) -> None:
        self.assertDenied(self.call({"tool_name": "Read", "tool_input": {"file_path": ".env"}}))

    def test_denies_browser_code_execution(self) -> None:
        for tool in ("mcp__playwright__browser_evaluate", "mcp__playwright__browser_run_code_unsafe"):
            self.assertDenied(self.call({"tool_name": tool, "tool_input": {}}))

    def test_denies_mutating_tool_on_protected_branch(self) -> None:
        for tool in sorted(aw.MUTATING_TOOLS):
            self.assertDenied(
                self.call({"tool_name": tool, "tool_input": {"file_path": "a.py"}}, branch="main")
            )

    def test_allows_mutating_tool_on_task_branch(self) -> None:
        self.assertEqual(
            self.call({"tool_name": "Write", "tool_input": {"file_path": "a.py"}}), {}
        )

    def test_denies_blocked_bash(self) -> None:
        self.assertDenied(
            self.call({"tool_name": "Bash", "tool_input": {"command": "git reset --hard"}})
        )

    def test_allows_ordinary_bash(self) -> None:
        self.assertEqual(
            self.call({"tool_name": "Bash", "tool_input": {"command": "ls -la"}}), {}
        )

    def test_allows_read_on_protected_branch(self) -> None:
        self.assertEqual(
            self.call({"tool_name": "Read", "tool_input": {"file_path": "a.py"}}, branch="main"), {}
        )


class UserPromptSubmitTests(unittest.TestCase):
    def call(self, branch, dirty=False, checkout_rc=0):
        checkout = mock.Mock(return_value=mock.Mock(returncode=checkout_rc, stdout="", stderr="boom"))
        with mock.patch.object(aw, "current_branch", return_value=branch), \
             mock.patch.object(aw, "is_dirty", return_value=dirty), \
             mock.patch.object(aw, "run", checkout):
            return aw.handle_user_prompt_submit(ROOT, {"prompt": "add a widget"}, "claude"), checkout

    def test_detached_head_blocks(self) -> None:
        decision, checkout = self.call(None)
        self.assertEqual(decision.get("decision"), "block")
        checkout.assert_not_called()

    def test_dirty_protected_branch_blocks_and_touches_nothing(self) -> None:
        decision, checkout = self.call("main", dirty=True)
        self.assertEqual(decision.get("decision"), "block")
        self.assertIn("user's work", decision["reason"])
        checkout.assert_not_called()

    def test_clean_protected_branch_creates_a_task_branch(self) -> None:
        decision, checkout = self.call("main", dirty=False)
        args = checkout.call_args.args[0]
        self.assertEqual(args[:3], ["git", "checkout", "-b"])
        self.assertRegex(args[3], r"^claude/\d{8}-\d{6}-add-a-widget$")
        self.assertIn("additionalContext", decision["hookSpecificOutput"])

    def test_failed_checkout_blocks(self) -> None:
        decision, _ = self.call("main", checkout_rc=1)
        self.assertEqual(decision.get("decision"), "block")

    def test_task_branch_injects_router_context(self) -> None:
        decision, checkout = self.call("feat/x")
        context = decision["hookSpecificOutput"]["additionalContext"]
        self.assertIn("feat/x", context)
        self.assertIn("$work-feature", context)
        checkout.assert_not_called()


class StopTests(unittest.TestCase):
    def call(self, *, branch="feat/x", dirty=False, ahead=0, unpushed=False, pr_url="https://pr", remote_error=None):
        with mock.patch.object(aw, "current_branch", return_value=branch), \
             mock.patch.object(aw, "is_dirty", return_value=dirty), \
             mock.patch.object(aw, "base_ref", return_value="upstream/main"), \
             mock.patch.object(aw, "commits_ahead", return_value=ahead), \
             mock.patch.object(aw, "unpushed", return_value=unpushed), \
             mock.patch.object(aw, "pr_url_for", return_value=pr_url), \
             mock.patch.object(aw, "verify_remote_pr", side_effect=remote_error):
            return aw.handle_stop(ROOT, {}, "claude")

    def test_respects_stop_hook_active(self) -> None:
        self.assertEqual(aw.handle_stop(ROOT, {"stop_hook_active": True}, "claude"), {})

    def test_dirty_branch_reenters_the_turn(self) -> None:
        decision = self.call(dirty=True)
        self.assertEqual(decision.get("decision"), "block")
        self.assertIn("ship", decision["reason"])

    def test_unpushed_commits_reenter_the_turn(self) -> None:
        self.assertEqual(self.call(ahead=2, unpushed=True).get("decision"), "block")

    def test_missing_pr_reenters_the_turn(self) -> None:
        self.assertEqual(self.call(ahead=2, unpushed=False, pr_url=None).get("decision"), "block")

    def test_shipped_branch_ends_the_turn(self) -> None:
        self.assertEqual(self.call(ahead=2, unpushed=False, pr_url="https://pr"), {})

    def test_cached_url_does_not_hide_failed_remote_verification(self) -> None:
        decision = self.call(ahead=2, remote_error=aw.GitError("Remote PR head SHA differs"))
        self.assertEqual(decision.get("decision"), "block")
        self.assertIn("unverified", decision["reason"])

    def test_nothing_to_ship_ends_the_turn(self) -> None:
        self.assertEqual(self.call(ahead=0), {})

    def test_protected_and_detached_are_left_alone(self) -> None:
        self.assertEqual(self.call(branch="main", dirty=True), {})
        self.assertEqual(self.call(branch=None, dirty=True), {})


class ResolveRootTests(unittest.TestCase):
    """An unresolvable payload cwd must fall back, never fail open."""

    def test_prefers_the_payload_cwd(self) -> None:
        with mock.patch.object(aw, "repo_root", side_effect=[ROOT]) as root:
            self.assertEqual(aw.resolve_root({"cwd": "/from/payload"}), ROOT)
        self.assertEqual(root.call_args.args[0], Path("/from/payload"))

    def test_falls_back_to_the_process_cwd(self) -> None:
        with mock.patch.object(aw, "repo_root", side_effect=[aw.GitError("no"), ROOT]) as root:
            self.assertEqual(aw.resolve_root({"cwd": "/bogus"}), ROOT)
        self.assertEqual(root.call_count, 2)

    def test_raises_when_neither_resolves(self) -> None:
        with mock.patch.object(aw, "repo_root", side_effect=aw.GitError("no")):
            with self.assertRaises(aw.GitError):
                aw.resolve_root({"cwd": "/bogus"})


class DispatchTests(unittest.TestCase):
    def test_unknown_event_allows(self) -> None:
        self.assertEqual(aw.dispatch_hook({"hook_event_name": "Nope"}, "claude", ROOT), {})
        self.assertEqual(aw.dispatch_hook({}, "claude", ROOT), {})

    def test_every_registered_event_has_a_handler(self) -> None:
        self.assertEqual(
            set(aw.HANDLERS), {"SessionStart", "UserPromptSubmit", "PreToolUse", "Stop"}
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
