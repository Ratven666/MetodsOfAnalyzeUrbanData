from __future__ import annotations

from fastapi import APIRouter, Depends

from fastapi_wheather_lab.dependencies import get_wind_db_service
from fastapi_wheather_lab.schemas.wind import WindMeasurementResponse, WindPointDBResponse
from fastapi_wheather_lab.services.wind_db_service import WindDBService

router = APIRouter(tags=["wind-research"])


@router.get(
    "/wind/points",
    response_model=list[WindPointDBResponse],
    summary="Список точек наблюдений ветра (legacy — через WindDBService)",
    description="Устаревший маршрут. Для полного CRUD используйте /wind/points из CRUD-роутера.",
    deprecated=True,
)
def list_wind_points_legacy(service: WindDBService = Depends(get_wind_db_service)) -> list[WindPointDBResponse]:
    return service.list_points()


@router.get(
    "/wind/measurements",
    response_model=list[WindMeasurementResponse],
    summary="Список всех измерений ветра (legacy — через WindDBService)",
    deprecated=True,
)
def list_wind_measurements_legacy(service: WindDBService = Depends(get_wind_db_service)) -> list[WindMeasurementResponse]:
    return service.list_measurements()
