"""Password-only administrator authentication against the isolated SQL/Redis fixture."""

import psycopg
import pytest
from conftest import OWNER
from redis.exceptions import ConnectionError as RedisConnectionError
from test_commerce import api, run, staff  # noqa: F401

from app import commerce_api, security
from app.admin_cli import provision

PASSWORD = "a-strong-fixture-password"
LOGIN = {"username": "fixture-admin", "password": PASSWORD}


@pytest.mark.parametrize("failure", ["wrong-password", "unknown-user", "disabled"])
def test_invalid_credentials_never_create_a_session(api, failure):  # noqa: F811
    run(provision(LOGIN["username"], PASSWORD))
    payload = dict(LOGIN)
    if failure == "wrong-password":
        payload["password"] = "another-wrong-password"
    elif failure == "unknown-user":
        payload["username"] = "unknown-admin"
    else:
        with psycopg.connect(OWNER) as conn:
            conn.execute("UPDATE admins SET enabled=false")
    response = api.post("/v1/admin/login", json=payload)
    assert response.status_code == 401
    assert response.json() == {"detail": "Sign-in details were not accepted"}
    assert not response.cookies
    with psycopg.connect(OWNER) as conn:
        assert conn.execute("SELECT count(*) FROM sessions").fetchone()[0] == 0


def test_login_throttle_cannot_be_evaded_by_username_case(api):  # noqa: F811
    run(provision(LOGIN["username"], PASSWORD))
    for username in [
        "fixture-admin",
        "FIXTURE-ADMIN",
        "Fixture-Admin",
        "fixture-admin",
        "FIXTURE-admin",
    ]:
        response = api.post(
            "/v1/admin/login", json={"username": username, "password": "a-wrong-fixture-password"}
        )
        assert response.status_code == 401
    assert api.post("/v1/admin/login", json=LOGIN).status_code == 429


def test_login_fails_closed_when_rate_store_is_unavailable(api, monkeypatch):  # noqa: F811
    run(provision(LOGIN["username"], PASSWORD))

    async def unavailable(*args, **kwargs):
        raise RedisConnectionError("Synthetic fixture outage")

    monkeypatch.setattr(security.Redis, "eval", unavailable)
    response = api.post("/v1/admin/login", json=LOGIN)
    assert response.status_code == 503
    assert not response.cookies


def test_login_keeps_account_locked_until_its_session_is_committed(api, monkeypatch):  # noqa: F811
    run(provision(LOGIN["username"], PASSWORD))
    verify_password = commerce_api.password_valid
    checked = []

    def verify_while_reset_attempts_lock(encoded, password):
        # An operator reset takes this same row lock before revoking sessions.
        # Without it, a login can verify an old hash then create a post-reset session.
        with psycopg.connect(OWNER) as conn:
            with pytest.raises(psycopg.errors.LockNotAvailable):
                conn.execute("SELECT id FROM admins FOR UPDATE NOWAIT")
            conn.rollback()
        checked.append(True)
        return verify_password(encoded, password)

    monkeypatch.setattr(commerce_api, "password_valid", verify_while_reset_attempts_lock)
    assert api.post("/v1/admin/login", json=LOGIN).status_code == 200
    assert checked == [True]
    run(provision(LOGIN["username"], "a-replaced-fixture-password", recover=True))
    assert api.get("/v1/admin/session").status_code == 401


def test_login_origin_logout_and_disabled_session(staff):  # noqa: F811
    response = staff.post(
        "/v1/admin/login", json=LOGIN, headers={"origin": "https://attacker.invalid"}
    )
    assert response.status_code == 403
    token = staff.cookies.get("pakodi_session")
    assert staff.post("/v1/admin/logout").status_code == 200
    assert staff.get("/v1/admin/session").status_code == 401
    assert (
        staff.get("/v1/admin/session", headers={"cookie": "pakodi_session=" + token}).status_code
        == 401
    )
    assert staff.post("/v1/admin/login", json=LOGIN).status_code == 200
    with psycopg.connect(OWNER) as conn:
        conn.execute("UPDATE admins SET enabled=false")
    assert staff.get("/v1/admin/session").status_code == 401
