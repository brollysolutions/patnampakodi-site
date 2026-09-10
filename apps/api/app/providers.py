"""Narrow provider adapters. Never include responses or credentials in errors."""

import httpx

from app.config import fixture_mode, setting


async def razorpay(method, path, **kwargs):
    if fixture_mode():
        return await fixture_request(method, path, **kwargs)
    key = setting("RAZORPAY_KEY_ID")
    secret = setting("RAZORPAY_KEY_SECRET")
    if not key or not secret:
        raise RuntimeError("Payment provider is not configured")
    async with httpx.AsyncClient(
        base_url="https://api.razorpay.com/v1/", auth=(key, secret), timeout=15
    ) as client:
        response = await client.request(method, path, **kwargs)
        response.raise_for_status()
        return response.json()


async def send_whatsapp(payload):
    if fixture_mode():
        result = await fixture_request("POST", "messages", json={"template": payload["template"]})
        return result["id"]
    token = setting("META_ACCESS_TOKEN")
    phone_id = setting("META_PHONE_ID")
    version = setting("META_GRAPH_VERSION")
    if not token or not phone_id or not version:
        raise RuntimeError("Messaging provider is not configured")
    parameters = [{"type": "text", "text": str(value)} for value in payload["parameters"]]
    if payload["template"] == "order_update_v1":
        from app.config import origin

        parameters[-1]["text"] = origin() + "/track/#access=" + parameters[-1]["text"]
    body = {
        "messaging_product": "whatsapp",
        "to": payload["phone"],
        "type": "template",
        "template": {
            "name": payload["template"],
            "language": {"code": "en"},
            "components": [{"type": "body", "parameters": parameters}],
        },
    }
    async with httpx.AsyncClient(timeout=15) as client:
        response = await client.post(
            f"https://graph.facebook.com/{version}/{phone_id}/messages",
            headers={"Authorization": "Bearer " + token},
            json=body,
        )
        response.raise_for_status()
        return response.json()["messages"][0]["id"]


async def fixture_request(method, path, **kwargs):
    if not fixture_mode():
        raise RuntimeError("Provider fixture is disabled")
    async with httpx.AsyncClient(
        base_url="http://fixture-provider:8000/v1/",
        auth=("fixture", "local-fixture-only"),
        timeout=15,
    ) as client:
        response = await client.request(method, path, **kwargs)
        response.raise_for_status()
        return response.json()
