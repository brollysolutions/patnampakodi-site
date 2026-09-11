"""Cross-platform server entry point with Psycopg's required selector loop."""

import asyncio
import os

import uvicorn

from app.config import validate_runtime


def selector_loop():
    return asyncio.SelectorEventLoop()


if __name__ == "__main__":
    validate_runtime()
    uvicorn.run(
        "app.main:app",
        host=os.environ.get("API_HOST", "127.0.0.1"),
        port=int(os.environ.get("API_PORT", "8500")),
        loop="app.serve:selector_loop",
        proxy_headers=bool(os.environ.get("TRUSTED_PROXY_IPS")),
        forwarded_allow_ips=os.environ.get("TRUSTED_PROXY_IPS", ""),
        access_log=False,
    )
