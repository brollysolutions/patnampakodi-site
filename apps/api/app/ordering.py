"""One policy for every new-purchase entry point, including legacy requests."""

from fastapi import HTTPException

from app.config import ordering_enabled

PAUSED_MESSAGE = "Online ordering is paused. Explore our menu or contact our team."


def require_ordering() -> None:
    if not ordering_enabled():
        raise HTTPException(409, PAUSED_MESSAGE)
