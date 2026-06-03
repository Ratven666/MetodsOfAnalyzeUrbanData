"""
Функции-провайдеры зависимостей FastAPI.

Функции используются в маршрутах через Depends(...)
Они извлекают нужные объекты из DependencyContainer,
хранящегося в app.state.deps.

Провайдеры:
    get_app_config()             → AppConfigModel
    get_runtime_config_service() → RuntimeConfigService
    get_runtime_config()         → RuntimeConfigModel (удобный shortcut)
"""

from __future__ import annotations

from fastapi import Request

from fastapi_wheather_lab.schemas.app_config import AppConfigModel
from fastapi_wheather_lab.schemas.runtime_config import RuntimeConfigModel
from fastapi_wheather_lab.services.runtime_config_service import RuntimeConfigService


def _get_container(request: Request):
    """Вспомогательная функция: достать DependencyContainer из app.state."""
    return request.app.state.deps


def get_app_config(request: Request) -> AppConfigModel:
    """
    Провайдер статической конфигурации.

    Использование в маршруте:
        config: AppConfigModel = Depends(get_app_config)
    """
    return _get_container(request).get_dep("app_config", AppConfigModel)


def get_runtime_config_service(request: Request) -> RuntimeConfigService:
    """
    Провайдер сервиса runtime-конфигурации.

    Использование в маршруте:
        service: RuntimeConfigService = Depends(get_runtime_config_service)
    """
    return _get_container(request).get_dep(
        "runtime_config_service", RuntimeConfigService
    )


def get_runtime_config(request: Request) -> RuntimeConfigModel:
    """
    Shortcut-провайдер: возвращает текущую RuntimeConfigModel напрямую.

    Использование в маршруте:
        cfg: RuntimeConfigModel = Depends(get_runtime_config)
    """
    service = get_runtime_config_service(request)
    return service.get_config()
