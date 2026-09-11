"""Runtime configuration; production never inherits development credentials."""

import os
from pathlib import Path

BRAND = "patnam-pakodi"


def setting(name: str, local: str = "") -> str:
    secret_file = os.environ.get(name + "_FILE")
    if secret_file:
        return Path(secret_file).read_text(encoding="utf-8").strip()
    value = os.environ.get(name, "")
    if value:
        return value
    if os.environ.get("APP_ENV") == "production":
        if local:
            raise RuntimeError(f"Missing runtime configuration: {name}")
        return ""
    return local


def app_database_url():
    return setting(
        "COMMERCE_DATABASE_URL", "postgresql://pakodi_app:local-app-only@127.0.0.1:5434/pakodi"
    )


def origin():
    return setting("PUBLIC_ORIGIN", "http://127.0.0.1:3501").rstrip("/")


def media_root():
    return Path(
        setting("MEDIA_ROOT", str(Path(__file__).resolve().parents[3] / ".agent-workflow/media"))
    )


def validate_runtime():
    fixture_mode()
    if os.environ.get("APP_ENV") != "production":
        return
    from cryptography.fernet import Fernet

    for name in ("DATABASE_URL", "COMMERCE_DATABASE_URL", "REDIS_URL", "DATA_ENCRYPTION_KEY"):
        value = setting(name)
        if not value or "local-" in value:
            raise RuntimeError(f"Production configuration required: {name}")
    Fernet(setting("DATA_ENCRYPTION_KEY").encode())
    if not origin().startswith("https://"):
        raise RuntimeError("Production PUBLIC_ORIGIN must use HTTPS")


def fixture_mode():
    from urllib.parse import urlsplit

    mode = os.environ.get("PROVIDER_MODE", "live")
    if mode == "live":
        return False
    if mode != "fixtures":
        raise RuntimeError("Unknown provider mode")
    parsed = urlsplit(origin())
    if (
        os.environ.get("APP_ENV") not in {"test", "staging"}
        or parsed.scheme not in {"http", "https"}
        or parsed.hostname not in {"127.0.0.1", "localhost", "::1"}
        or parsed.username
        or parsed.password
        or parsed.path not in {"", "/"}
        or parsed.query
        or parsed.fragment
    ):
        raise RuntimeError("Provider fixtures require a local test or staging origin")
    return True
