"""Delivery must be serialized and backed by fresh GitHub and Git evidence."""
import argparse
from contextlib import ExitStack, nullcontext, redirect_stdout
import copy
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import agent_workflow as workflow

ROOT = Path(__file__).resolve().parents[2]
URL = "https://github.com/base/project/pull/2"
SHA = "a" * 40
PR = {"url": URL, "state": "open", "merged": False,
      "head": {"ref": "chore/task", "repo": "fork/project", "sha": SHA},
      "base": {"ref": "main", "repo": "base/project"}}


def git_value(args, *unused, **kwargs):
    if args[:2] == ["remote", "get-url"]:
        return "https://github.com/" + ("base" if args[2] == "upstream" else "fork") + "/project.git"
    return SHA


class RemoteEvidenceTests(unittest.TestCase):
    def verify(self, payload=PR, *, url=URL, require_open=False):
        with patch.object(workflow, "has_remote", return_value=True), \
             patch.object(workflow, "git", side_effect=git_value), \
             patch.object(workflow, "run", return_value=subprocess.CompletedProcess(
                 [], 0, json.dumps(payload), "")) as execute:
            result = workflow.verify_remote_pr(ROOT, "chore/task", "upstream/main", url,
                                               require_open=require_open)
        self.assertEqual(execute.call_args.args[0][:3], ["gh", "api", "repos/base/project/pulls/2"])
        self.assertEqual(execute.call_args.kwargs["timeout"], 15)
        return result

    def test_exact_open_pr_is_verified(self):
        self.assertEqual(self.verify()["head_sha"], SHA)

    def test_pr_must_match_commit_and_both_repositories_and_branches(self):
        for section, key, value in [("head", "sha", "b" * 40), ("head", "ref", "chore/other"),
                                    ("head", "repo", "other/project"), ("base", "ref", "prod"),
                                    ("base", "repo", "other/project")]:
            with self.subTest(section=section, key=key):
                payload = copy.deepcopy(PR)
                payload[section][key] = value
                with self.assertRaises(workflow.GitError):
                    self.verify(payload)

    def test_closed_unmerged_pr_is_not_delivery(self):
        with self.assertRaisesRegex(workflow.GitError, "CLOSED"):
            self.verify({**PR, "state": "closed"})

    def test_merged_exact_head_can_stop_but_cannot_finish_new_delivery(self):
        payload = {**PR, "state": "closed", "merged": True}
        self.assertEqual(self.verify(payload)["state"], "MERGED")
        with self.assertRaisesRegex(workflow.GitError, "MERGED"):
            self.verify(payload, require_open=True)

    def test_bad_cached_url_is_rejected_before_network_access(self):
        for url in (None, "https://example.com/pull/2", "https://github.com/other/project/pull/2",
                    URL + "/comments"):
            with self.subTest(url=url), patch.object(workflow, "has_remote", return_value=True), \
                 patch.object(workflow, "git", side_effect=git_value), patch.object(workflow, "run") as execute:
                with self.assertRaises(workflow.GitError):
                    workflow.verify_remote_pr(ROOT, "chore/task", "upstream/main", url)
                execute.assert_not_called()

    def test_malformed_or_incomplete_readback_is_not_delivery(self):
        for payload in (None, [], {}, {**PR, "head": None}, {**PR, "url": "https://wrong"}):
            with self.subTest(payload=payload), self.assertRaises(workflow.GitError):
                self.verify(payload)

    def test_network_failure_is_not_delivery(self):
        with patch.object(workflow, "has_remote", return_value=True), \
             patch.object(workflow, "git", side_effect=git_value), \
             patch.object(workflow, "run", side_effect=workflow.GitError("GitHub unavailable")):
            with self.assertRaisesRegex(workflow.GitError, "unavailable"):
                workflow.verify_remote_pr(ROOT, "chore/task", "upstream/main", URL)

    def test_remote_timeout_has_a_terminal_failure_result(self):
        with patch.object(workflow.subprocess, "run", side_effect=subprocess.TimeoutExpired("gh", 15)):
            result = workflow.run(["gh", "api"], timeout=15)
            self.assertEqual(result.returncode, 124)
            with self.assertRaisesRegex(workflow.GitError, "timed out"):
                workflow.run(["gh", "api"], timeout=15, check=True)

    def test_failed_git_status_or_tracking_never_looks_clean(self):
        with patch.object(workflow.subprocess, "run", return_value=subprocess.CompletedProcess([], 1, "", "git failed")), \
             patch.object(workflow, "upstream_of", return_value="origin/chore/task"):
            with self.assertRaises(workflow.GitError):
                workflow.is_dirty(ROOT)
            with self.assertRaises(workflow.GitError):
                workflow.unpushed(ROOT, "chore/task")

    def test_state_remote_failure_is_explicit_and_nonzero(self):
        state = {"branch": "chore/task", "base_ref": "upstream/main", "pr_url": URL}
        output = io.StringIO()
        with patch.object(workflow, "repo_root", return_value=ROOT), \
             patch.object(workflow, "workflow_state", return_value=state), \
             patch.object(workflow, "verify_remote_pr", side_effect=workflow.GitError("unavailable")), \
             redirect_stdout(output):
            self.assertEqual(workflow.cmd_state(argparse.Namespace(cwd=None, remote=True)), 1)
        self.assertEqual(json.loads(output.getvalue())["remote_pr"]["status"], "unverified")


class DeliveryLockTests(unittest.TestCase):
    def child(self, path, code):
        return subprocess.run([sys.executable, "-c",
            "import sys; sys.path.insert(0, sys.argv[1]); from pathlib import Path; "
            "import agent_workflow as w; " + code,
            str(ROOT / "scripts"), str(path)], capture_output=True, text=True, timeout=15)

    def test_second_process_is_blocked_and_lock_releases_after_exit(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "finish.lock"
            code = "\nwith w.exclusive_delivery_lock(Path(sys.argv[2])): pass"
            with workflow.exclusive_delivery_lock(path):
                blocked = self.child(path, code)
                self.assertNotEqual(blocked.returncode, 0)
                self.assertIn("Another delivery is running", blocked.stderr)
            self.assertEqual(self.child(path, code).returncode, 0)

    def test_process_crash_does_not_leave_stale_lock(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "finish.lock"
            result = self.child(path, "import os\nwith w.exclusive_delivery_lock(Path(sys.argv[2])): os._exit(7)")
            self.assertEqual(result.returncode, 7)
            with workflow.exclusive_delivery_lock(path):
                pass

    def test_worktrees_use_common_git_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            common = Path(directory)
            with patch.object(workflow, "git", return_value=str(common)) as git:
                with workflow.delivery_lock(ROOT):
                    with self.assertRaises(workflow.GitError):
                        with workflow.delivery_lock(ROOT / "other-worktree"):
                            self.fail("Concurrent worktree delivery was allowed")
            self.assertEqual(git.call_args.args[0], ["rev-parse", "--git-common-dir"])


class FinishEvidenceTests(unittest.TestCase):
    def finish(self, *, remote_error=None, dirty=False, tracking="origin/chore/task", locked=False):
        output = io.StringIO()
        args = argparse.Namespace(cwd=None, title="chore: task", commit_message="chore: task",
                                  body_file=None, verification="passed", security="reviewed")
        commands = []

        def run(command, **kwargs):
            commands.append(command)
            result = json.dumps([{"number": 2, "url": URL}]) if command[:2] == ["gh", "api"] else ""
            return subprocess.CompletedProcess(command, 0, result, "")

        with ExitStack() as stack:
            values = {"repo_root": ROOT, "ensure_hooks_path": None, "current_branch": "chore/task",
                      "working_tree_paths": [], "base_ref": "upstream/main", "commits_ahead": 1,
                      "changed_paths": [], "has_remote": True, "is_dirty": dirty,
                      "upstream_of": tracking, "unpushed": False}
            for name, value in values.items():
                stack.enter_context(patch.object(workflow, name, return_value=value))
            stack.enter_context(patch.object(workflow, "git", side_effect=git_value))
            stack.enter_context(patch.object(workflow, "run", side_effect=run))
            lock = stack.enter_context(patch.object(workflow, "delivery_lock", return_value=nullcontext(),
                side_effect=workflow.GitError("Another delivery is running") if locked else None))
            remote = stack.enter_context(patch.object(workflow, "verify_remote_pr", side_effect=remote_error,
                                                      return_value={"status": "verified", "head_sha": SHA}))
            cache = stack.enter_context(patch.object(workflow, "set_pr_url"))
            stack.enter_context(redirect_stdout(output))
            result = workflow.cmd_finish(args)
        return result, commands, remote, cache, output.getvalue()

    def test_success_requires_fresh_open_pr_before_caching(self):
        result, commands, remote, cache, output = self.finish()
        self.assertEqual(result, 0)
        remote.assert_called_once_with(ROOT, "chore/task", "upstream/main", URL, require_open=True)
        cache.assert_called_once_with(ROOT, "chore/task", URL)
        self.assertEqual(json.loads(output)["remote_pr"]["head_sha"], SHA)

    def test_failed_readback_after_update_does_not_claim_success_or_cache(self):
        result, commands, _, cache, output = self.finish(remote_error=workflow.GitError("stale PR"))
        self.assertEqual(result, 1)
        self.assertTrue(any(command[:3] == ["gh", "pr", "edit"] for command in commands))
        cache.assert_not_called()
        self.assertEqual(output, "")

    def test_dirty_or_wrong_tracking_cannot_report_delivery(self):
        for changes in ({"dirty": True}, {"tracking": "upstream/main"}):
            with self.subTest(changes=changes):
                result, _, _, cache, _ = self.finish(**changes)
                self.assertEqual(result, 1)
                cache.assert_not_called()

    def test_competing_finish_does_not_stage_commit_push_or_call_github(self):
        result, commands, remote, cache, _ = self.finish(locked=True)
        self.assertEqual(result, 1)
        self.assertEqual(commands, [])
        remote.assert_not_called()
        cache.assert_not_called()


if __name__ == "__main__":
    unittest.main()
