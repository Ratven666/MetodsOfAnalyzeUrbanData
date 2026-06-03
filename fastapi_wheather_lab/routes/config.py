"""
Маршруты конфигурации приложения.
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


@router.get("/health", response_model=HealthResponse, summary="Проверка работоспособности приложения")
def health() -> HealthResponse:
    return HealthResponse(status="ok")


@router.get("/config/app", response_model=AppConfigModel, summary="Статическая конфигурация приложения")
def get_app_configuration(config: AppConfigModel = Depends(get_app_config)) -> AppConfigModel:
    return config


@router.get("/config/runtime", response_model=RuntimeConfigModel, summary="Текущая runtime-конфигурация")
def get_runtime_configuration(cfg: RuntimeConfigModel = Depends(get_runtime_config)) -> RuntimeConfigModel:
    return cfg


@router.put("/config/runtime", response_model=RuntimeConfigModel, summary="Обновление runtime-конфигурации")
def update_runtime_configuration(
    update: RuntimeConfigUpdateModel,
    service: RuntimeConfigService = Depends(get_runtime_config_service),
) -> RuntimeConfigModel:
    return service.update_config(update)
