"""
Маршруты конфигурации приложения.

Обязательные эндпоинты (ЛР №6):
    GET  /health          — проверка работоспособности
    GET  /config/app      — статическая конфигурация (только чтение)
    GET  /config/runtime  — текущие runtime-настройки
    PUT  /config/runtime  — обновление runtime-настроек (с валидацией Pydantic)

Обработчики НЕ создают сервисы напрямую.
Все зависимости получаются исключительно через Depends.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends

from fastapi_wheather_lab.dependencies import (
    get_app_config,
    get_runtime_config,
    get_runtime_config_service,
)
from fastapi_wheather_lab.schemas.app_config import AppConfigModel
from fastapi_wheather_lab.schemas.responses import HealthResponse
from fastapi_wheather_lab.schemas.runtime_config import (
    RuntimeConfigModel,
    RuntimeConfigUpdateModel,
)
from fastapi_wheather_lab.services.runtime_config_service import RuntimeConfigService

router = APIRouter(tags=["configuration"])


# ── Проверка работоспособности ─────────────────────────────────────────────


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Проверка работоспособности приложения",
    description='Возвращает `{"status": "ok"}` если сервер доступен.',
)
def health() -> HealthResponse:
    return HealthResponse(status="ok")


# ── Статическая конфигурация ───────────────────────────────────────────────


@router.get(
    "/config/app",
    response_model=AppConfigModel,
    summary="Статическая конфигурация приложения",
    description=(
        "Возвращает параметры, заданные при старте приложения. "
        "**Не может быть изменена через API** — только через env-переменные и перезапуск."
    ),
)
def get_app_configuration(
    config: AppConfigModel = Depends(get_app_config),
) -> AppConfigModel:
    return config


# ── Runtime-конфигурация: чтение ───────────────────────────────────────────


@router.get(
    "/config/runtime",
    response_model=RuntimeConfigModel,
    summary="Текущая runtime-конфигурация",
    description="Возвращает текущие настройки, изменяемые без перезапуска сервера.",
)
def get_runtime_configuration(
    cfg: RuntimeConfigModel = Depends(get_runtime_config),
) -> RuntimeConfigModel:
    return cfg


# ── Runtime-конфигурация: обновление ──────────────────────────────────────


@router.put(
    "/config/runtime",
    response_model=RuntimeConfigModel,
    summary="Обновление runtime-конфигурации",
    description=(
        "Частичное обновление runtime-настроек. "
        "Передавайте только те поля, которые необходимо изменить. "
        "Остальные поля сохраняют текущие значения.\n\n"
        "**Валидация:** `log_level` допускает только `DEBUG`, `INFO`, `WARNING`, `ERROR`. "
        "Значение `TRACE` вернёт HTTP 422."
    ),
)
def update_runtime_configuration(
    update: RuntimeConfigUpdateModel,
    service: RuntimeConfigService = Depends(get_runtime_config_service),
) -> RuntimeConfigModel:
    return service.update_config(update)
