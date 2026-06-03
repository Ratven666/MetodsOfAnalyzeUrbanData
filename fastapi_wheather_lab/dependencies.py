"""
Функции-провайдеры зависимостей FastAPI.
"""

from __future__ import annotations

from fastapi import Request

from fastapi_wheather_lab.schemas.app_config import AppConfigModel
from fastapi_wheather_lab.schemas.runtime_config import RuntimeConfigModel
from fastapi_wheather_lab.services.runtime_config_service import RuntimeConfigService
from fastapi_wheather_lab.services.wind_db_service import WindDBService


def _get_container(request: Request):
    return request.app.state.deps


def get_app_config(request: Request) -> AppConfigModel:
    return _get_container(request).get_dep("app_config", AppConfigModel)


def get_runtime_config_service(request: Request) -> RuntimeConfigService:
    return _get_container(request).get_dep("runtime_config_service", RuntimeConfigService)


def get_runtime_config(request: Request) -> RuntimeConfigModel:
    service = get_runtime_config_service(request)
    return service.get_config()


def get_wind_db_service(request: Request) -> WindDBService:
    return _get_container(request).get_dep("wind_db_service", WindDBService)
