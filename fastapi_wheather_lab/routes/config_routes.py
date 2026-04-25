"""
Эндпоинты конфигурации приложения.

Маршруты:
  GET  /config/app      — статическая конфигурация (только чтение)
  GET  /config/runtime  — текущие runtime-настройки
  PUT  /config/runtime  — обновление runtime-настроек
"""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, field_validator

from fastapi_wheather_lab.config import AppConfig, RuntimeConfig
from fastapi_wheather_lab.services.runtime_service import (
    get_runtime_config,
    update_runtime_config,
)

router = APIRouter(prefix="/config", tags=["Configuration"])


# ---------------------------------------------------------------------------
# Pydantic-модели запросов / ответов
# ---------------------------------------------------------------------------


class AppConfigResponse(BaseModel):
    app_name: str
    app_version: str
    app_description: str
    app_authors: list[str]
    contact_email: Optional[str] = None
    license_name: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "app_name": "Laboratory FastAPI App",
                "app_version": "1.0.0",
                "app_description": "Учебное приложение",
                "app_authors": ["Иванов И.И.", "Петров П.П."],
                "contact_email": "admin@example.com",
                "license_name": "MIT",
            }
        }
    }


class RuntimeConfigResponse(BaseModel):
    log_level: str
    feature_flag: bool
    maintenance_mode: bool
    runtime_message: str
    max_request_size_mb: int


ALLOWED_LOG_LEVELS = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}


class RuntimeConfigUpdate(BaseModel):
    """
    Модель для обновления runtime-настроек.
    Все поля опциональны — передаются только те, которые нужно изменить.
    """

    log_level: Optional[str] = Field(
        default=None,
        description=f"Уровень логирования. Допустимые значения: {ALLOWED_LOG_LEVELS}",
    )
    feature_flag: Optional[bool] = Field(
        default=None,
        description="Флаг включения экспериментальных функций",
    )
    maintenance_mode: Optional[bool] = Field(
        default=None,
        description="Режим технического обслуживания",
    )
    runtime_message: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Текущее сообщение о статусе сервиса",
    )
    max_request_size_mb: Optional[int] = Field(
        default=None,
        ge=1,
        le=1024,
        description="Максимальный размер запроса в мегабайтах (1–1024)",
    )

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v.upper() not in ALLOWED_LOG_LEVELS:
            raise ValueError(
                f"Недопустимый уровень логирования: '{v}'. "
                f"Допустимые значения: {sorted(ALLOWED_LOG_LEVELS)}"
            )
        return v.upper() if v else v

    model_config = {
        "json_schema_extra": {
            "example": {
                "log_level": "DEBUG",
                "feature_flag": True,
                "maintenance_mode": False,
                "runtime_message": "Новый режим работы",
                "max_request_size_mb": 50,
            }
        }
    }


# ---------------------------------------------------------------------------
# Эндпоинты
# ---------------------------------------------------------------------------

# Статическая конфигурация создаётся ОДИН РАЗ при импорте модуля
_static_config = AppConfig()


@router.get(
    "/app",
    response_model=AppConfigResponse,
    summary="Статическая конфигурация приложения",
    description=(
        "Возвращает конфигурацию, зафиксированную при **старте** приложения. "
        "Изменение переменных среды во время работы сервера **не влияет** на этот ответ."
    ),
)
async def get_app_config() -> AppConfigResponse:
    return AppConfigResponse(**_static_config.to_dict())


@router.get(
    "/runtime",
    response_model=RuntimeConfigResponse,
    summary="Текущие runtime-настройки",
    description="Возвращает динамические параметры, обновляемые через PUT /config/runtime.",
)
async def get_runtime(
    cfg: RuntimeConfig = Depends(get_runtime_config),
) -> RuntimeConfigResponse:
    return RuntimeConfigResponse(**cfg.to_dict())


@router.put(
    "/runtime",
    response_model=RuntimeConfigResponse,
    summary="Обновление runtime-настроек",
    description=(
        "Принимает JSON с новыми значениями динамических параметров и применяет их **немедленно**, "
        "без перезапуска сервера. Передавайте только те поля, которые нужно изменить."
    ),
    status_code=status.HTTP_200_OK,
)
async def update_runtime(payload: RuntimeConfigUpdate) -> RuntimeConfigResponse:
    updates = payload.model_dump(exclude_none=True)
    if not updates:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Тело запроса пустое или не содержит допустимых полей для обновления.",
        )
    updated_cfg = update_runtime_config(updates)
    return RuntimeConfigResponse(**updated_cfg.to_dict())
