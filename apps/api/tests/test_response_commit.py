"""Success responses must only become visible after their transaction commits."""

import json

import psycopg
from conftest import OWNER
from fastapi.middleware.asyncexitstack import AsyncExitStackMiddleware
from test_commerce import add_product, request_order, run

from app.main import app

pytest_plugins = ["test_commerce"]


def test_approval_is_committed_before_response_start(staff):
    variant = add_product(staff)
    order, _, _ = request_order(staff, variant)
    body = json.dumps({"delivery_paise": 1180}).encode()
    headers = [
        (b"content-type", b"application/json"),
        (b"origin", staff.headers["origin"].encode()),
        (b"x-csrf-token", staff.headers["x-csrf-token"].encode()),
        (b"cookie", "; ".join(f"{key}={value}" for key, value in staff.cookies.items()).encode()),
    ]
    observed = []

    async def operation():
        async def receive():
            return {"type": "http.request", "body": body, "more_body": False}

        async def send(message):
            if message["type"] == "http.response.start":
                async with await psycopg.AsyncConnection.connect(OWNER) as conn:
                    cursor = await conn.execute(
                        "SELECT status FROM orders WHERE id=%s", (order["id"],)
                    )
                    observed.append((message["status"], (await cursor.fetchone())[0]))

        # Exercise the actual route/dependencies at the ASGI send boundary, without
        # middleware buffering hiding the ordering from the test client.
        await AsyncExitStackMiddleware(app.router)(
            {
                "type": "http",
                "asgi": {"version": "3.0"},
                "http_version": "1.1",
                "method": "POST",
                "scheme": "http",
                "root_path": "",
                "path": f"/v1/admin/orders/{order['id']}/approve",
                "query_string": b"",
                "headers": headers,
                "client": ("127.0.0.1", 1234),
                "server": ("127.0.0.1", 3000),
                "app": app,
            },
            receive,
            send,
        )

    run(operation())
    assert observed == [(200, "approved")]
