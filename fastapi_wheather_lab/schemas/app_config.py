from __future__ import annotations

import os
from typing import List, Optional

from pydantic import BaseModel, Field


class AppConfigModel(BaseModel):
    """Статическая конфигурация — задаётся при старте, не изменяется через API."""

    app_name: str = Field(
        default_factory=lambda: os.getenv("APP_NAME", "Wave Climate FastAPI App"),
        description="Название приложения",
    )
    app_version: str = Field(
        default_factory=lambda: os.getenv("APP_VERSION", "1.0.0"),
        description="Версия приложения",
    )
    app_description: str = Field(
        default_factory=lambda: os.getenv(
            "APP_DESCRIPTION",
            "FastAPI-сервис для расчёта климата волнового воздействия",
        ),
        description="Описание приложения",
    )
    app_authors: List[str] = Field(
        default_factory=lambda: [
            a.strip()
            for a in os.getenv("APP_AUTHORS", "Выстрчил М.Г.").split(",")
            if a.strip()
        ],
        description="Список авторов",
    )
    contact_email: Optional[str] = Field(
        default_factory=lambda: os.getenv("CONTACT_EMAIL", "ratven@yandex.ru"),
        description="Контактный e-mail",
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "app_name": "Wave Climate FastAPI App",
                "app_version": "1.0.0",
                "app_description": "FastAPI-сервис для расчёта климата волнового воздействия",
                "app_authors": ["Выстрчил М.Г."],
                "contact_email": "ratven@yandex.ru",
            }
        }
    }
