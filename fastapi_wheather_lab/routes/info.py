"""
Вспомогательные информационные эндпоинты.
"""

from fastapi import APIRouter, Depends

from fastapi_wheather_lab.config import RuntimeConfig
from fastapi_wheather_lab.services.runtime_service import get_runtime_config

router = APIRouter(tags=["Info"])


@router.get("/", summary="Корневой маршрут")
async def root():
    return {
        "message": "Добро пожаловать в Laboratory FastAPI App!",
        "docs": "/docs",
        "health": "/health",
    }


@router.get("/status", summary="Расширенный статус приложения")
async def status(cfg: RuntimeConfig = Depends(get_runtime_config)):
    if cfg.maintenance_mode:
        return {
            "status": "maintenance",
            "message": cfg.runtime_message,
        }
    return {
        "status": "running",
        "log_level": cfg.log_level,
        "message": cfg.runtime_message,
    }
