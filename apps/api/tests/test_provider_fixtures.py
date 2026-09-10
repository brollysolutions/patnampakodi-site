"""Synthetic provider routing, persistence and payment authorization boundaries."""

import asyncio
import hashlib
import hmac
import json
import uuid

import httpx
import psycopg
import pytest
from conftest import OWNER
from fastapi.testclient import TestClient
from test_commerce import approved, start_payment

from app import config, fixture_provider, providers

pytest_plugins = ["test_commerce"]


@pytest.mark.parametrize(
    "environment,origin,allowed",
    [
        ("test", "http://127.0.0.1:3100", True),
        ("staging", "http://localhost:3100", True),
        ("production", "http://127.0.0.1:3100", False),
        ("development", "http://127.0.0.1:3100", False),
        ("staging", "https://patnampakodi.com", False),
        ("staging", "http://127.0.0.1.evil.test", False),
        ("staging", "http://user@127.0.0.1:3100", False),
        ("staging", "http://127.0.0.1:3100/path", False),
    ],
)
def test_fixture_mode_requires_explicit_local_nonproduction(
    monkeypatch, environment, origin, allowed
):
    monkeypatch.setenv("APP_ENV", environment)
    monkeypatch.setenv("PUBLIC_ORIGIN", origin)
    monkeypatch.setenv("PROVIDER_MODE", "fixtures")
    if allowed:
        assert config.fixture_mode()
    else:
        with pytest.raises(RuntimeError):
            config.validate_runtime()
    monkeypatch.setenv("PROVIDER_MODE", "unknown")
    with pytest.raises(RuntimeError):
        config.fixture_mode()


def test_fixture_provider_persists_idempotent_captures_and_refunds(monkeypatch, tmp_path):
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv("PUBLIC_ORIGIN", "http://127.0.0.1:3100")
    monkeypatch.setenv("PROVIDER_MODE", "fixtures")
    monkeypatch.setenv("FIXTURE_STORE", str(tmp_path / "provider.sqlite3"))
    events = []

    async def deliver(provider, event, identifier):
        events.append((provider, event, identifier))

    monkeypatch.setattr(fixture_provider, "webhook", deliver)
    with TestClient(fixture_provider.app) as client:
        assert client.get("/health").status_code == 401
        client.headers["Authorization"] = fixture_provider.AUTH
        payload = {"amount": 12980, "currency": "INR", "receipt": str(uuid.uuid4())}
        order = client.post("/v1/orders", json=payload).json()
        assert client.post("/v1/orders", json=payload).json() == order
        assert client.post("/v1/orders", json={**payload, "amount": 100}).status_code == 409
        for _ in range(2):
            assert client.post("/v1/orders/" + order["id"] + "/capture").status_code == 200
        assert len(events) == 2 and events[0] == events[1]
        payment = client.get("/v1/orders/" + order["id"] + "/payments").json()["items"][0]
        refund = {"amount": 1000, "speed": "normal", "receipt": str(uuid.uuid4())}
        headers = {"X-Refund-Idempotency": refund["receipt"]}
        path = "/v1/payments/" + payment["id"] + "/refund"
        result = client.post(path, json=refund, headers=headers)
        assert result.status_code == 200
        assert client.post(path, json=refund, headers=headers).json() == result.json()
        assert (
            client.post(path, json={**refund, "amount": 2000}, headers=headers).status_code == 409
        )
        over = {**refund, "amount": 12980, "receipt": str(uuid.uuid4())}
        assert (
            client.post(
                path, json=over, headers={"X-Refund-Idempotency": over["receipt"]}
            ).status_code
            == 409
        )
    # Re-open the application against the same local store, as after a restart.
    with TestClient(
        fixture_provider.app, headers={"Authorization": fixture_provider.AUTH}
    ) as client:
        assert client.get("/v1/refunds/" + result.json()["id"]).json() == result.json()
        assert len(client.get("/v1/orders/" + order["id"] + "/payments").json()["items"]) == 1
        monkeypatch.setenv("PROVIDER_MODE", "live")
        assert client.get("/health").status_code == 404


def test_fixture_webhooks_sign_the_exact_request_bytes(monkeypatch):
    sent = []

    def respond(request):
        sent.append(request)
        return httpx.Response(200, json={"detail": "accepted"})

    real_client = httpx.AsyncClient
    monkeypatch.setattr(
        fixture_provider.httpx,
        "AsyncClient",
        lambda **kwargs: real_client(transport=httpx.MockTransport(respond), **kwargs),
    )
    event = {"event": "payment.captured", "payload": {"fixture": "signed"}}
    asyncio.run(fixture_provider.webhook("razorpay", event, "fixture-event"))
    request = sent[0]
    assert str(request.url) == "http://api:8000/v1/webhooks/razorpay"
    assert json.loads(request.content) == event
    assert (
        request.headers["X-Razorpay-Signature"]
        == hmac.new(
            fixture_provider.WEBHOOK_KEY.encode(), request.content, hashlib.sha256
        ).hexdigest()
    )


def test_capture_route_requires_private_order_current_quote_and_reservation(staff, monkeypatch):
    _, order, headers, _ = approved(staff)
    payload = {"quote_version": order["quote_version"]}
    assert staff.post("/v1/order/fixture-capture", json=payload, headers=headers).status_code == 404
    monkeypatch.setenv("PROVIDER_MODE", "fixtures")
    assert staff.post("/v1/order/fixture-capture", json=payload).status_code == 404
    assert (
        staff.post(
            "/v1/order/fixture-capture",
            json=payload,
            headers={**headers, "Origin": "https://evil.test"},
        ).status_code
        == 403
    )
    assert staff.post("/v1/order/fixture-capture", json=payload, headers=headers).status_code == 409
    payment = start_payment(staff, order, headers)
    checkout = staff.post("/v1/order/payment", json=payload, headers=headers)
    assert checkout.json()["fixture"] is True
    calls = []

    async def request(method, path, **kwargs):
        calls.append((method, path))
        return {"detail": "accepted"}

    monkeypatch.setattr(providers, "fixture_request", request)
    assert (
        staff.post(
            "/v1/order/fixture-capture",
            json={"quote_version": order["quote_version"] + 1},
            headers=headers,
        ).status_code
        == 409
    )
    assert staff.post("/v1/order/fixture-capture", json=payload, headers=headers).status_code == 200
    assert calls == [("POST", "orders/" + payment["order_id"] + "/capture")]
    with psycopg.connect(OWNER) as conn:
        conn.execute(
            "UPDATE orders SET reserved_until=now()-interval '1 minute' WHERE id=%s", (order["id"],)
        )
    assert staff.post("/v1/order/fixture-capture", json=payload, headers=headers).status_code == 409
    assert len(calls) == 1


def test_fixture_message_adapter_omits_customer_phone_and_private_parameters(monkeypatch):
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv("PUBLIC_ORIGIN", "http://127.0.0.1:3100")
    monkeypatch.setenv("PROVIDER_MODE", "fixtures")
    calls = []

    async def request(method, path, **kwargs):
        calls.append((method, path, kwargs))
        return {"id": "wamid_fixture"}

    monkeypatch.setattr(providers, "fixture_request", request)
    result = asyncio.run(
        providers.send_whatsapp(
            {
                "template": "order_update_v1",
                "phone": "+919876543210",
                "parameters": ["private-test-token"],
            }
        )
    )
    assert result == "wamid_fixture"
    assert calls == [("POST", "messages", {"json": {"template": "order_update_v1"}})]
