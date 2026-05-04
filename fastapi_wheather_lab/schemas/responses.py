"""
Pydantic-модели HTTP-ответов.

Отдельный модуль позволяет использовать response_model=<Model>
в декораторах маршрутов без циклических импортов.
"""

from __future__ import annotations

from typing import Any, Dict

from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Ответ эндпоинта GET /health."""

    status: str

    model_config = {"json_schema_extra": {"example": {"status": "ok"}}}


class MessageResponse(BaseModel):
    """Универсальный ответ с сообщением (например, для ошибок или уведомлений)."""

    message: str
    detail: Dict[str, Any] | None = None

    model_config = {
        "json_schema_extra": {
            "example": {"message": "Операция выполнена успешно", "detail": None}
        }
    }
