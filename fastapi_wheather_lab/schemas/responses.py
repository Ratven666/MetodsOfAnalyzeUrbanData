from __future__ import annotations

from typing import Any, Dict

from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str


class MessageResponse(BaseModel):
    message: str
    detail: Dict[str, Any] | None = None
