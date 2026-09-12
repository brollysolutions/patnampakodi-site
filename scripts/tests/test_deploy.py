"""Deployment orchestration regressions using only synthetic files and commands."""

import base64
import importlib.util
import io
import os
import subprocess
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

spec = importlib.util.spec_from_file_location(
    "deploy", Path(__file__).resolve().parents[1] / "deploy.py"
)
deploy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(deploy)


class DeploymentTests(unittest.TestCase):
    def test_modern_standalone_compose_is_accepted_when_plugin_is_missing(self):
        with patch.object(
            deploy,
            "run",
            side_effect=[deploy.DeploymentError("missing plugin"), "5.1.2\n"],
        ) as command:
            self.assertEqual(deploy.select_compose(), ("docker-compose",))
        self.assertEqual(
            [call.args[0] for call in command.call_args_list],
            [
                ["docker", "compose", "version", "--short"],
                ["docker-compose", "version", "--short"],
            ],
        )

    def test_runtime_check_requires_matching_restricted_roles_and_authenticated_redis(
        self,
    ):
        for roles, redis_ok, valid in (
            (
                [("pakodi_reader", False, False), ("pakodi_app", False, False)],
                True,
                True,
            ),
            ([("pakodi_owner", True, True)], True, False),
            (
                [("pakodi_reader", False, False), ("pakodi_app", False, True)],
                True,
                False,
            ),
            (
                [("pakodi_reader", False, False), ("pakodi_app", False, False)],
                False,
                False,
            ),
        ):
            config = types.ModuleType("app.config")
            config.setting = lambda key: "synthetic-" + key
            config.validate_runtime = MagicMock()
            psycopg = types.ModuleType("psycopg")
            psycopg.connect = MagicMock()
            connection = psycopg.connect.return_value.__enter__.return_value
            connection.execute.return_value.fetchone.side_effect = roles
            redis = types.ModuleType("redis")
            redis.Redis = MagicMock()
            redis.Redis.from_url.return_value.ping.return_value = redis_ok
            with patch.dict(
                "sys.modules",
                {"app.config": config, "psycopg": psycopg, "redis": redis},
            ):
                if valid:
                    deploy.check_runtime()
                    self.assertEqual(psycopg.connect.call_count, 2)
                    redis.Redis.from_url.assert_called_once()
                else:
                    with self.assertRaises(RuntimeError):
                        deploy.check_runtime()

    def test_runtime_defaults_and_existing_values_are_persisted_without_replacement(
        self,
    ):
        with (
            tempfile.TemporaryDirectory() as directory,
            patch.object(deploy, "network_inventory", return_value=([], [])),
        ):
            path = Path(directory) / "runtime.env"
            with (
                patch.object(deploy, "ROOT", Path(directory) / "repo"),
                patch.dict(
                    deploy.DEFAULTS,
                    {"PAKODI_SECRETS_DIR": (Path(directory) / "secrets").as_posix()},
                ),
            ):
                options = deploy.prepare_options(path)
                self.assertEqual(options["PAKODI_HOST"], "patnampakodi.com")
                self.assertEqual(options["PAKODI_NETWORK_PREFIX"], "10.253.91")
                original = path.read_bytes()
                self.assertEqual(deploy.prepare_options(path), options)
                self.assertEqual(path.read_bytes(), original)
                path.write_text(
                    "# Keep this comment\nPAKODI_HOST=custom.example.com\nPAKODI_NETWORK_PREFIX=10.254.91\n",
                    encoding="utf-8",
                )
                options = deploy.prepare_options(path)
                self.assertEqual(options["PAKODI_HOST"], "custom.example.com")
                self.assertEqual(options["PAKODI_NETWORK_PREFIX"], "10.254.91")
                self.assertTrue(path.read_text().startswith("# Keep this comment\n"))

    def test_runtime_rejects_shell_content_unknown_keys_and_duplicates(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "runtime.env"
            for content in (
                "PAKODI_HOST=$(id)",
                "PAKODI_HOST=`id`",
                "PASSWORD=synthetic",
                "PAKODI_HOST=a.com\nPAKODI_HOST=b.com",
                "source evil.sh",
            ):
                with self.subTest(content=content):
                    path.write_text(content, encoding="utf-8")
                    with self.assertRaises(deploy.DeploymentError):
                        deploy.read_options(path)

    def test_invalid_domain_and_inside_checkout_secrets_fail_before_inventory(self):
        with (
            tempfile.TemporaryDirectory() as directory,
            patch.object(deploy, "network_inventory") as inventory,
        ):
            path = Path(directory) / "runtime.env"
            for value in (
                "https://patnampakodi.com",
                "patnampakodi.com/path",
                "",
                "a.com:443",
            ):
                path.write_text("PAKODI_HOST=" + value, encoding="utf-8")
                with self.assertRaises(deploy.DeploymentError):
                    deploy.prepare_options(path)
            with patch.object(deploy, "ROOT", Path(directory)):
                path.write_text(
                    "PAKODI_SECRETS_DIR=" + (Path(directory) / "secrets").as_posix(),
                    encoding="utf-8",
                )
                with self.assertRaises(deploy.DeploymentError):
                    deploy.prepare_options(path)
            inventory.assert_not_called()

    def test_ambient_compose_and_domain_overrides_cannot_redirect_deployment(self):
        with patch.dict(
            os.environ,
            {
                "COMPOSE_FILE": "other.yaml",
                "COMPOSE_PROJECT_NAME": "other",
                "PAKODI_HOST": "wrong.example.com",
                "COMPOSE_ENV_FILES": "private.env",
            },
        ):
            env = deploy.environment({"PAKODI_HOST": "patnampakodi.com"})
        self.assertNotIn("COMPOSE_FILE", env)
        self.assertNotIn("COMPOSE_PROJECT_NAME", env)
        self.assertNotIn("COMPOSE_ENV_FILES", env)
        self.assertEqual(env["COMPOSE_DISABLE_ENV_FILE"], "1")
        self.assertEqual(env["PAKODI_HOST"], "patnampakodi.com")

    def network(self, name, subnet):
        return {
            "Name": name,
            "IPAM": {"Config": [{"Subnet": subnet}]},
            "Labels": {"com.docker.compose.project": "pakodi"},
        }

    def test_network_avoids_docker_and_host_routes_and_preserves_existing(self):
        networks = [
            self.network("another-app", "172.29.0.0/16"),
            {"Name": "host", "IPAM": {"Config": None}},
        ]
        routes = [{"dst": "default"}, {"dst": "10.253.0.0/16"}]
        self.assertEqual(deploy.choose_prefix(None, networks, routes), "10.254.91")
        self.assertEqual(
            deploy.choose_prefix("172.29.91", networks, routes), "10.254.91"
        )
        existing = [self.network("pakodi_private", "10.253.91.0/24")]
        self.assertEqual(deploy.choose_prefix(None, existing, routes), "10.253.91")
        with self.assertRaises(deploy.DeploymentError):
            deploy.choose_prefix("10.254.91", existing, [])
        existing[0]["Labels"] = {}
        with self.assertRaises(deploy.DeploymentError):
            deploy.choose_prefix(None, existing, [])

    def test_network_rejects_invalid_and_public_ranges(self):
        for prefix in ("999.1.1", "8.8.8", "127.0.0", "1.2", "10.2.3.4"):
            with self.subTest(prefix=prefix), self.assertRaises(deploy.DeploymentError):
                deploy.choose_prefix(prefix, [], [])

    def test_missing_secrets_with_existing_data_and_partial_directories_fail_closed(
        self,
    ):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory) / "secrets"
            with self.assertRaises(deploy.DeploymentError):
                deploy.prepare_secrets(folder, True)
            self.assertFalse(folder.exists())
            folder.mkdir()
            marker = folder / "keep"
            marker.write_text("synthetic", encoding="utf-8")
            with self.assertRaises(deploy.DeploymentError):
                deploy.prepare_secrets(folder, False)
            self.assertEqual(marker.read_text(), "synthetic")

    def test_new_secret_generation_and_retry_preserve_credentials(self):
        with (
            tempfile.TemporaryDirectory() as directory,
            patch.object(deploy.os, "chown", create=True) as chown,
        ):
            folder = Path(directory) / "secrets"
            deploy.prepare_secrets(folder, False)
            files = {
                name: (folder / name).read_bytes()
                for name in (*deploy.CORE_FILES, *deploy.PROVIDER_FILES)
            }
            self.assertEqual(
                len(base64.urlsafe_b64decode(files["api/data_encryption_key"])), 32
            )
            self.assertIn(b"@postgres:5433/pakodi", files["api/database_url"])
            self.assertIn(b"@redis:6380/0", files["api/redis_url"])
            self.assertTrue(all(files[name] == b"" for name in deploy.PROVIDER_FILES))
            self.assertNotEqual(
                files["api/database_url"], files["api/commerce_database_url"]
            )
            deploy.prepare_secrets(folder, True)
            self.assertEqual(
                files, {name: (folder / name).read_bytes() for name in files}
            )
            self.assertTrue(chown.called)
            if os.name == "posix":
                self.assertEqual(folder.stat().st_mode & 0o777, 0o700)
                self.assertEqual(
                    (folder / "api/database_url").stat().st_mode & 0o777, 0o640
                )

    def test_exclusive_file_creation_never_replaces_existing(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "existing"
            path.write_text("keep", encoding="utf-8")
            with self.assertRaises(FileExistsError):
                deploy.exclusive_write(path, "replace")
            self.assertEqual(path.read_text(), "keep")

    def flow(self, state="0|0", fail_migration=False):
        def command(options, *args, **kwargs):
            if "ON_ERROR_STOP=1" in args:
                return "1" if args[-1] == "SELECT count(*) FROM admins;" else state
            if fail_migration and args == ("run", "--rm", "--no-deps", "-T", "migrate"):
                raise deploy.DeploymentError("synthetic migration failure")
            return ""

        return command

    def test_fresh_setup_bootstraps_before_migration_and_starts_after_seed(self):
        with (
            patch.object(deploy, "compose", side_effect=self.flow()) as command,
            patch.object(deploy, "confirm_backup") as backup,
        ):
            deploy.deploy(deploy.DEFAULTS, False, False)
        backup.assert_not_called()
        calls = [call.args[1:] for call in command.call_args_list]
        bootstrap = next(
            i for i, args in enumerate(calls) if "app.bootstrap_roles" in args
        )
        migrate = calls.index(("run", "--rm", "--no-deps", "-T", "migrate"))
        seed = next(i for i, args in enumerate(calls) if "app.seed" in args)
        start = next(
            i for i, args in enumerate(calls) if args[0] == "up" and "api" in args
        )
        self.assertLess(bootstrap, migrate)
        self.assertLess(migrate, seed)
        self.assertLess(seed, start)
        self.assertTrue(
            all("--volumes" not in args and "down" not in args for args in calls)
        )

    def test_update_never_rebootstraps_and_backup_refusal_precedes_service_changes(
        self,
    ):
        with (
            patch.object(deploy, "compose", side_effect=self.flow("2|34")) as command,
            patch.object(deploy, "confirm_backup") as backup,
        ):
            deploy.deploy(deploy.DEFAULTS, True, True)
            backup.assert_called_once_with(True)
            self.assertFalse(
                any(
                    "app.bootstrap_roles" in call.args
                    for call in command.call_args_list
                )
            )
        with (
            patch.object(deploy, "compose", side_effect=self.flow()) as command,
            patch.object(
                deploy,
                "confirm_backup",
                side_effect=deploy.DeploymentError("cancelled"),
            ),
        ):
            with self.assertRaises(deploy.DeploymentError):
                deploy.deploy(deploy.DEFAULTS, True, False)
            self.assertFalse(
                any(
                    "stop" in call.args or "up" in call.args
                    for call in command.call_args_list
                )
            )

    def test_partial_roles_and_failed_migrations_never_start_application(self):
        for state, fail in (("1|0", False), ("0|5", False), ("2|34", True)):
            with (
                self.subTest(state=state),
                patch.object(
                    deploy, "compose", side_effect=self.flow(state, fail)
                ) as command,
            ):
                with self.assertRaises(deploy.DeploymentError):
                    deploy.deploy(deploy.DEFAULTS, False, False)
                self.assertFalse(
                    any(
                        call.args[1] == "up" and "api" in call.args
                        for call in command.call_args_list
                    )
                )

    def test_error_output_never_discloses_container_credentials(self):
        result = subprocess.CompletedProcess(
            ["docker"], 1, "secret-output", "postgresql://secret"
        )
        with (
            patch.object(deploy.subprocess, "run", return_value=result),
            self.assertRaises(deploy.DeploymentError) as raised,
        ):
            deploy.run(["docker", "compose"])
        self.assertNotIn("secret", str(raised.exception))

    def test_backup_confirmation_requires_explicit_operator_input(self):
        with (
            patch.object(deploy.sys, "stdin", io.StringIO("BACKUP READY")),
            self.assertRaises(deploy.DeploymentError),
        ):
            deploy.confirm_backup(False)
        deploy.confirm_backup(True)

    def test_compose_selection_prefers_supported_plugin(self):
        for version in ("v2.20.0", "2.40.3+ubuntu", "v5.1.2"):
            with (
                self.subTest(version=version),
                patch.object(deploy, "run", return_value=version) as command,
            ):
                self.assertEqual(deploy.select_compose(), ("docker", "compose"))
                command.assert_called_once_with(
                    ["docker", "compose", "version", "--short"]
                )

    def test_compose_selection_falls_back_from_unusable_plugin(self):
        for result in (FileNotFoundError(), "2.19.9", "unknown"):
            with (
                self.subTest(result=result),
                patch.object(deploy, "run", side_effect=[result, "v5.1.2"]),
            ):
                self.assertEqual(deploy.select_compose(), ("docker-compose",))

    def test_compose_selection_rejects_missing_legacy_and_malformed_versions(self):
        for result in (
            FileNotFoundError(),
            deploy.DeploymentError("failed"),
            "1.29.2",
            "2.19.9",
            "5.1",
            "5.1.2 invalid",
        ):
            with (
                self.subTest(result=result),
                patch.object(deploy, "run", side_effect=[result, result]),
                self.assertRaisesRegex(deploy.DeploymentError, "2.20.0"),
            ):
                deploy.select_compose()

    def test_preflight_selection_is_reused_with_project_and_runtime_options(self):
        for selected in (("docker", "compose"), ("docker-compose",)):
            with (
                self.subTest(selected=selected),
                patch.object(deploy, "COMPOSE_COMMAND", ("docker", "compose")),
                patch.object(deploy, "select_compose", return_value=selected) as select,
                patch.object(
                    deploy,
                    "docker",
                    side_effect=['"unix:///var/run/docker.sock"', "linux"],
                ),
                patch.object(deploy, "run", return_value="") as command,
                patch.dict(
                    os.environ, {"COMPOSE_PROJECT_NAME": "unrelated"}, clear=True
                ),
            ):
                deploy.preflight()
                for args in (
                    ("config", "--quiet"),
                    ("build",),
                    ("up", "-d", "--wait"),
                    ("exec", "api", "python"),
                ):
                    deploy.compose(deploy.DEFAULTS, *args, visible=True)
                    invocation = command.call_args
                    self.assertEqual(
                        invocation.args[0],
                        [
                            *selected,
                            "-p",
                            "pakodi",
                            "-f",
                            str(deploy.ROOT / "compose.production.yaml"),
                            "--profile",
                            "operations",
                            *args,
                        ],
                    )
                    self.assertEqual(
                        invocation.kwargs["env"]["PAKODI_HOST"], "patnampakodi.com"
                    )
                    self.assertEqual(
                        invocation.kwargs["env"]["COMPOSE_DISABLE_ENV_FILE"], "1"
                    )
                    self.assertNotIn("COMPOSE_PROJECT_NAME", invocation.kwargs["env"])
                    self.assertTrue(invocation.kwargs["visible"])
                select.assert_called_once()

    def test_preflight_rejects_missing_old_and_remote_compose(self):
        with (
            patch.object(deploy, "run", side_effect=FileNotFoundError),
            patch.dict(os.environ, {}, clear=True),
            self.assertRaisesRegex(deploy.DeploymentError, "Compose plugin"),
        ):
            deploy.preflight()
        with (
            patch.object(deploy, "run", return_value="1.29.2"),
            patch.dict(os.environ, {}, clear=True),
            self.assertRaisesRegex(deploy.DeploymentError, "2.20.0"),
        ):
            deploy.preflight()
        with (
            patch.object(deploy, "run", return_value="5.1.2"),
            patch.dict(os.environ, {"DOCKER_HOST": "ssh://remote"}, clear=True),
            self.assertRaisesRegex(deploy.DeploymentError, "local Docker socket"),
        ):
            deploy.preflight()

    def test_standalone_compose_retains_context_and_linux_engine_guards(self):
        for environment, engine, message in (
            ({"DOCKER_CONTEXT": "remote"}, "linux", "Unset DOCKER_CONTEXT"),
            ({"DOCKER_HOST": "tcp://remote:2375"}, "linux", "local Docker socket"),
            (
                {"DOCKER_HOST": "unix:///var/run/docker.sock"},
                "windows",
                "Linux Docker Engine",
            ),
        ):
            with (
                self.subTest(environment=environment, engine=engine),
                patch.dict(os.environ, environment, clear=True),
                patch.object(
                    deploy, "select_compose", return_value=("docker-compose",)
                ),
                patch.object(deploy, "docker", return_value=engine),
                self.assertRaisesRegex(deploy.DeploymentError, message),
            ):
                deploy.preflight()

    def test_overlapping_runtime_prefix_is_replaced_and_saved_for_retry(self):
        networks = [self.network("another-app", "172.29.0.0/16")]
        with (
            tempfile.TemporaryDirectory() as directory,
            patch.object(deploy, "network_inventory", return_value=(networks, [])),
            patch.dict(
                deploy.DEFAULTS,
                {
                    "PAKODI_SECRETS_DIR": Path(tempfile.gettempdir()).as_posix()
                    + "/synthetic-deploy-secrets"
                },
            ),
        ):
            path = Path(directory) / "runtime.env"
            path.write_text(
                "# retain\nPAKODI_HOST=patnampakodi.com\nPAKODI_NETWORK_PREFIX=172.29.91\n",
                encoding="utf-8",
            )
            options = deploy.prepare_options(path)
            self.assertEqual(options["PAKODI_NETWORK_PREFIX"], "10.253.91")
            self.assertIn("# retain", path.read_text())
            original = path.read_bytes()
            deploy.prepare_options(path)
            self.assertEqual(path.read_bytes(), original)

    def test_blank_runtime_prefix_is_saved_for_retry(self):
        with (
            tempfile.TemporaryDirectory() as directory,
            patch.object(deploy, "network_inventory", return_value=([], [])),
            patch.dict(
                deploy.DEFAULTS,
                {
                    "PAKODI_SECRETS_DIR": Path(tempfile.gettempdir()).as_posix()
                    + "/synthetic-deploy-secrets"
                },
            ),
        ):
            path = Path(directory) / "runtime.env"
            path.write_text(
                "PAKODI_HOST=patnampakodi.com\nPAKODI_NETWORK_PREFIX=\n",
                encoding="utf-8",
            )
            options = deploy.prepare_options(path)
            self.assertEqual(options["PAKODI_NETWORK_PREFIX"], "10.253.91")
            self.assertEqual(
                deploy.read_options(path)["PAKODI_NETWORK_PREFIX"], "10.253.91"
            )
            original = path.read_bytes()
            deploy.prepare_options(path)
            self.assertEqual(path.read_bytes(), original)

    def test_exhausted_network_candidates_fail_without_deleting_networks(self):
        networks = [
            self.network("ten-range", "10.0.0.0/8"),
            self.network("private-range", "172.16.0.0/12"),
        ]
        with self.assertRaises(deploy.DeploymentError):
            deploy.choose_prefix(None, networks, [{"dst": "192.168.0.0/16"}])

    def test_another_web_server_port_is_not_stopped(self):
        with (
            patch.object(deploy, "docker", return_value="") as docker,
            patch.object(deploy.socket, "socket") as socket,
            self.assertRaisesRegex(deploy.DeploymentError, "already in use"),
        ):
            socket.return_value.__enter__.return_value.bind.side_effect = OSError(
                "in use"
            )
            deploy.check_proxy_ports()
        self.assertEqual(docker.call_count, 1)

    def test_own_proxy_ports_are_preserved(self):
        with (
            patch.object(
                deploy,
                "docker",
                side_effect=[
                    "own-proxy",
                    '{"80/tcp":[{"HostPort":"80"}],"443/tcp":[{"HostPort":"443"}]}',
                ],
            ),
            patch.object(deploy.socket, "socket") as socket,
        ):
            deploy.check_proxy_ports()
        socket.assert_not_called()

    def test_ipv6_only_web_server_is_detected(self):
        with (
            patch.object(deploy, "docker", return_value=""),
            patch.object(deploy.socket, "has_ipv6", True),
            patch.object(deploy.socket, "socket") as socket,
            self.assertRaisesRegex(deploy.DeploymentError, "already in use"),
        ):
            socket.return_value.__enter__.return_value.bind.side_effect = [
                None,
                OSError("IPv6 in use"),
            ]
            deploy.check_proxy_ports()

    def test_first_admin_uses_existing_interactive_cli_and_never_resets_accounts(self):
        original = self.flow()

        def command(options, *args, **kwargs):
            return (
                "0"
                if args[-1] == "SELECT count(*) FROM admins;"
                else original(options, *args, **kwargs)
            )

        with (
            patch.object(deploy, "compose", side_effect=command) as compose,
            patch.object(deploy.sys.stdin, "isatty", return_value=True),
            patch("builtins.input", return_value="my.operator"),
        ):
            deploy.deploy(deploy.DEFAULTS, False, False)
        compose.assert_any_call(
            deploy.DEFAULTS,
            "exec",
            "api",
            "python",
            "-m",
            "app.admin_cli",
            "create",
            "my.operator",
            visible=True,
        )
        with (
            patch.object(deploy, "compose", side_effect=command),
            patch.object(deploy.sys.stdin, "isatty", return_value=False),
            self.assertRaisesRegex(deploy.DeploymentError, "no administrator"),
        ):
            deploy.deploy(deploy.DEFAULTS, False, False)

    @unittest.skipUnless(os.name == "posix", "POSIX symlink behavior")
    def test_symlinked_options_and_secret_directory_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            target = folder / "actual"
            target.mkdir()
            link = folder / "link"
            link.symlink_to(target, target_is_directory=True)
            with self.assertRaises(deploy.DeploymentError):
                deploy.prepare_secrets(link, False)
            with self.assertRaises(deploy.DeploymentError):
                deploy.read_options(link / "runtime.env")

    @unittest.skipUnless(
        os.name == "posix" and getattr(os, "geteuid", lambda: -1)() == 0,
        "Linux root container permission check",
    )
    def test_generated_secrets_are_readable_by_container_uid_under_restrictive_umask(
        self,
    ):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory) / "synthetic-secrets"
            previous = os.umask(0o077)
            try:
                deploy.prepare_secrets(folder, False)
            finally:
                os.umask(previous)
            for mount, filename in (
                ("api", "database_url"),
                ("owner", "migration_database_url"),
            ):
                child = os.fork()
                if child == 0:
                    try:
                        os.chroot(folder / mount)
                        os.chdir("/")
                        os.setgroups([])
                        os.setgid(10001)
                        os.setuid(10001)
                        assert Path("/" + filename).read_bytes()
                    except (OSError, AssertionError):
                        os._exit(1)
                    os._exit(0)
                _, status = os.waitpid(child, 0)
                self.assertEqual(os.waitstatus_to_exitcode(status), 0)

    @unittest.skipUnless(
        os.name == "posix" and getattr(os, "geteuid", lambda: -1)() == 0,
        "Linux deployment lock",
    )
    def test_deployment_lock_rejects_contention_and_releases_on_error(self):
        with tempfile.TemporaryDirectory() as directory:
            path = str(Path(directory) / "deploy.lock")
            with (
                deploy.deployment_lock(path),
                self.assertRaisesRegex(deploy.DeploymentError, "Another Pakodi"),
                deploy.deployment_lock(path),
            ):
                self.fail("contended lock was acquired")
            with self.assertRaises(ValueError), deploy.deployment_lock(path):
                raise ValueError("synthetic failure")
            with deploy.deployment_lock(path):
                pass


if __name__ == "__main__":
    unittest.main()
