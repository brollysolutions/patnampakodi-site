"""Local staging isolation guard regressions, without Docker mutations."""

import copy
import importlib.util
import os
import subprocess
import unittest
from pathlib import Path
from unittest.mock import patch

spec = importlib.util.spec_from_file_location(
    "staging_guard", Path(__file__).resolve().parents[1] / "staging.py"
)
staging = importlib.util.module_from_spec(spec)
spec.loader.exec_module(staging)


class StagingIsolationTests(unittest.TestCase):
    def config(self):
        return {
            "networks": {"private": {"internal": True}, "web-entry": {}},
            "services": {
                **{
                    name: {
                        "networks": {"private": {}},
                        "environment": {
                            "APP_ENV": "staging",
                            "PROVIDER_MODE": "fixtures",
                            "PUBLIC_ORIGIN": "http://127.0.0.1:3500",
                        },
                    }
                    for name in ("api", "worker", "fixture-provider")
                },
                "web": {
                    "networks": {"private": {}, "web-entry": {}},
                    "environment": {"SITE_INDEXABLE": "false"},
                    "ports": [{"host_ip": "127.0.0.1", "published": "3500", "target": 3500}],
                },
                "migrate": {"networks": {"private": {}}},
                "seed": {"networks": {"private": {}}},
            },
        }

    def test_refuses_public_network_port_indexing_or_live_provider(self):
        clean = self.config()
        staging.validate_config(clean)
        bad = copy.deepcopy(clean)
        bad["networks"]["private"]["internal"] = False
        with self.assertRaises(RuntimeError):
            staging.validate_config(bad)
        bad = copy.deepcopy(clean)
        bad["services"]["web"]["ports"][0]["host_ip"] = "0.0.0.0"
        with self.assertRaises(RuntimeError):
            staging.validate_config(bad)
        bad = copy.deepcopy(clean)
        bad["services"]["web"]["environment"]["SITE_INDEXABLE"] = "true"
        with self.assertRaises(RuntimeError):
            staging.validate_config(bad)
        for name in ("api", "worker", "fixture-provider"):
            bad = copy.deepcopy(clean)
            bad["services"][name]["environment"]["PROVIDER_MODE"] = "live"
            with self.assertRaises(RuntimeError):
                staging.validate_config(bad)

    def test_wrong_web_listener_or_published_port_is_rejected(self):
        for changes in ({"published": "3501"}, {"target": 3501}, {"protocol": "udp"}):
            with self.subTest(changes=changes):
                bad = self.config()
                bad["services"]["web"]["ports"][0].update(changes)
                with self.assertRaises(RuntimeError):
                    staging.validate_config(bad)

    def test_backend_cannot_join_entry_network_and_operations_must_exist(self):
        bad = self.config()
        bad["services"]["api"]["networks"]["web-entry"] = {}
        with self.assertRaises(RuntimeError):
            staging.validate_config(bad)
        bad = self.config()
        del bad["services"]["migrate"]
        with self.assertRaises(RuntimeError):
            staging.validate_config(bad)

    def test_ignores_ambient_compose_file_and_env_overrides(self):
        with patch.dict(
            os.environ,
            {
                "COMPOSE_FILE": "other.yaml",
                "COMPOSE_PROJECT_NAME": "other",
                "COMPOSE_PROFILES": "other",
                "COMPOSE_ENV_FILES": "private.env",
                "COMPOSE_DISABLE_ENV_FILE": "0",
            },
            clear=True,
        ):
            result = staging.environment()
        self.assertEqual(result, {"COMPOSE_DISABLE_ENV_FILE": "1"})

    def test_refuses_remote_docker_endpoints_before_compose(self):
        with (
            patch.dict(os.environ, {"DOCKER_HOST": "ssh://remote.example"}, clear=True),
            patch.object(staging.subprocess, "run") as command,
        ):
            with self.assertRaises(RuntimeError):
                staging.require_local_engine()
            command.assert_not_called()
        with (
            patch.dict(os.environ, {}, clear=True),
            patch.object(
                staging.subprocess,
                "run",
                return_value=subprocess.CompletedProcess(
                    [], 0, stdout='"tcp://remote.example:2376"'
                ),
            ),
            self.assertRaises(RuntimeError),
        ):
            staging.require_local_engine()
        with (
            patch.dict(os.environ, {}, clear=True),
            patch.object(
                staging.subprocess,
                "run",
                return_value=subprocess.CompletedProcess(
                    [], 0, stdout='"unix:///var/run/docker.sock"'
                ),
            ),
        ):
            staging.require_local_engine()
