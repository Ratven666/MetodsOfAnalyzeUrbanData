from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query

from fastapi_wheather_lab.db.base import get_db
from fastapi_wheather_lab.schemas.wind import (
    WindMeasurementCreate,
    WindMeasurementResponse,
    WindMeasurementUpdate,
    WindPointCreate,
    WindPointDBResponse,
    WindPointUpdate,
)
from fastapi_wheather_lab.wind_points import crud
from sqlalchemy.orm import Session

router = APIRouter(prefix="/wind/points", tags=["wind-research"])


# ─── WindPoint endpoints ────────────────────────────────────────────────────────

@router.post(
    "",
    response_model=WindPointDBResponse,
    status_code=201,
    summary="Создать точку наблюдений ветра",
)
def create_wind_point(data: WindPointCreate, db: Session = Depends(get_db)):
    existing = crud.get_wind_point_by_point_id(db, data.point_id)
    if existing:
        raise HTTPException(status_code=409, detail=f"Точка с point_id='{data.point_id}' уже существует")
    return crud.create_wind_point(db, data)


@router.get(
    "",
    response_model=list[WindPointDBResponse],
    summary="Список точек наблюдений ветра",
)
def list_wind_points(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    return crud.list_wind_points(db, limit=limit, offset=offset)


@router.get(
    "/intersects",
    response_model=list[WindPointDBResponse],
    summary="Точки, пересекающие заданную геометрию WKT",
)
def points_intersecting(
    wkt: str = Query(..., description="WKT-геометрия для пространственного фильтра, SRID 4326"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    return crud.list_points_within_polygon(db, wkt, limit=limit, offset=offset)


@router.get(
    "/near",
    response_model=list[WindPointDBResponse],
    summary="Точки в радиусе от заданной WKT-геометрии",
)
def points_near(
    wkt: str = Query(..., description="Центральная геометрия WKT (POINT), SRID 4326"),
    radius_m: float = Query(50_000, gt=0, description="Радиус поиска в метрах"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    return crud.list_points_near(db, wkt, radius_m=radius_m, limit=limit, offset=offset)


@router.get(
    "/{point_db_id}",
    response_model=WindPointDBResponse,
    summary="Получить точку по внутреннему ID",
)
def get_wind_point(point_db_id: int, db: Session = Depends(get_db)):
    result = crud.get_wind_point(db, point_db_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Точка наблюдений не найдена")
    return result


@router.put(
    "/{point_db_id}",
    response_model=WindPointDBResponse,
    summary="Обновить точку наблюдений",
)
def update_wind_point(point_db_id: int, data: WindPointUpdate, db: Session = Depends(get_db)):
    result = crud.update_wind_point(db, point_db_id, data)
    if result is None:
        raise HTTPException(status_code=404, detail="Точка наблюдений не найдена")
    return result


@router.delete(
    "/{point_db_id}",
    status_code=204,
    summary="Удалить точку наблюдений (cascade удаляет все измерения)",
)
def delete_wind_point(point_db_id: int, db: Session = Depends(get_db)):
    deleted = crud.delete_wind_point(db, point_db_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Точка наблюдений не найдена")


# ─── WindMeasurement endpoints ──────────────────────────────────────────────────

@router.post(
    "/{point_db_id}/measurements",
    response_model=WindMeasurementResponse,
    status_code=201,
    summary="Добавить измерение ветра к точке",
)
def create_measurement(
    point_db_id: int,
    data: WindMeasurementCreate,
    db: Session = Depends(get_db),
):
    point = crud.get_wind_point(db, point_db_id)
    if point is None:
        raise HTTPException(status_code=404, detail="Точка наблюдений не найдена")
    return crud.create_measurement(db, point_db_id, data)


@router.get(
    "/{point_db_id}/measurements",
    response_model=list[WindMeasurementResponse],
    summary="Список измерений ветра по точке",
)
def list_measurements(
    point_db_id: int,
    limit: int = Query(500, ge=1, le=5000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    point = crud.get_wind_point(db, point_db_id)
    if point is None:
        raise HTTPException(status_code=404, detail="Точка наблюдений не найдена")
    return crud.list_measurements_by_point(db, point_db_id, limit=limit, offset=offset)


@router.put(
    "/{point_db_id}/measurements/{measurement_id}",
    response_model=WindMeasurementResponse,
    summary="Обновить измерение ветра",
)
def update_measurement(
    point_db_id: int,
    measurement_id: int,
    data: WindMeasurementUpdate,
    db: Session = Depends(get_db),
):
    point = crud.get_wind_point(db, point_db_id)
    if point is None:
        raise HTTPException(status_code=404, detail="Точка наблюдений не найдена")
    result = crud.update_measurement(db, measurement_id, data)
    if result is None:
        raise HTTPException(status_code=404, detail="Измерение не найдено")
    return result


@router.delete(
    "/{point_db_id}/measurements/{measurement_id}",
    status_code=204,
    summary="Удалить измерение ветра",
)
def delete_measurement(
    point_db_id: int,
    measurement_id: int,
    db: Session = Depends(get_db),
):
    point = crud.get_wind_point(db, point_db_id)
    if point is None:
        raise HTTPException(status_code=404, detail="Точка наблюдений не найдена")
    deleted = crud.delete_measurement(db, measurement_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Измерение не найдено")
