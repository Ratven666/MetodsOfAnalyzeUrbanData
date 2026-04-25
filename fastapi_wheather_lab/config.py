"""
Классы конфигурации приложения.

Содержит:
  - AppConfig      : статическая конфигурация (применяется только при старте)
  - RuntimeConfig  : динамическая конфигурация (обновляется во время работы)
"""

from __future__ import annotations

import os
from typing import List, Optional

# ---------------------------------------------------------------------------
# Статическая конфигурация
# ---------------------------------------------------------------------------


class AppConfig:
    """
    Кастомный класс статической конфигурации приложения.

    Параметры читаются из переменных среды один раз при создании объекта.
    После инициализации объект FastAPI использует эти значения —
    изменение переменных среды во время работы сервера НЕ влияет на него.
    """

    def __init__(self) -> None:
        self.app_name: str = os.getenv("APP_NAME", "Laboratory FastAPI Wheather App")
        self.app_version: str = os.getenv("APP_VERSION", "0.0.1")
        self.app_description: str = os.getenv(
            "APP_DESCRIPTION", "Учебное приложение FastAPI — лабораторная работа 5"
        )
        self.app_authors: List[str] = [
            a.strip()
            for a in os.getenv("APP_AUTHORS", "Выстрчил М.Г.").split(",")
            if a.strip()
        ]
        self.contact_email: Optional[str] = os.getenv(
            "CONTACT_EMAIL", "Ratven@yandex.ru"
        )
        self.license_name: str = os.getenv("LICENSE_NAME", "MIT")

    def to_dict(self) -> dict:
        return {
            "app_name": self.app_name,
            "app_version": self.app_version,
            "app_description": self.app_description,
            "app_authors": self.app_authors,
            "contact_email": self.contact_email,
            "license_name": self.license_name,
        }

    def __repr__(self) -> str:
        return f"AppConfig(name={self.app_name!r}, " f"version={self.app_version!r})"


# ---------------------------------------------------------------------------
# Динамическая (runtime) конфигурация
# ---------------------------------------------------------------------------


class RuntimeConfig:
    """
    Singleton-класс для runtime-настроек.

    Параметры можно обновлять через API без перезапуска сервера.
    Хранится как единственный экземпляр в памяти процесса.
    """

    _instance: Optional["RuntimeConfig"] = None

    def __new__(cls) -> "RuntimeConfig":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        if self._initialized:
            return
        self.log_level: str = os.getenv("LOG_LEVEL", "INFO")
        self.feature_flag: bool = os.getenv("FEATURE_FLAG", "false").lower() == "true"
        self.maintenance_mode: bool = (
            os.getenv("MAINTENANCE_MODE", "false").lower() == "true"
        )
        self.runtime_message: str = os.getenv(
            "RUNTIME_MESSAGE", "Приложение работает в штатном режиме"
        )
        self.max_request_size_mb: int = int(os.getenv("MAX_REQUEST_SIZE_MB", "10"))
        self._initialized = True

    def to_dict(self) -> dict:
        return {
            "log_level": self.log_level,
            "feature_flag": self.feature_flag,
            "maintenance_mode": self.maintenance_mode,
            "runtime_message": self.runtime_message,
            "max_request_size_mb": self.max_request_size_mb,
        }

    def update(self, data: dict) -> None:
        """Обновить только разрешённые поля."""
        allowed = {
            "log_level",
            "feature_flag",
            "maintenance_mode",
            "runtime_message",
            "max_request_size_mb",
        }
        for key, value in data.items():
            if key in allowed:
                setattr(self, key, value)
