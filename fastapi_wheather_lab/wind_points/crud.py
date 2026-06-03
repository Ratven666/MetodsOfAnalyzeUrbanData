from __future__ import annotations

from geoalchemy2 import WKTElement
from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from fastapi_wheather_lab.models.wind_measurement import WindMeasurement
from fastapi_wheather_lab.models.wind_point import WindPoint
from fastapi_wheather_lab.schemas.wind import (
    WindMeasurementCreate,
    WindMeasurementUpdate,
    WindPointCreate,
    WindPointUpdate,
)


# ─── helpers ───────────────────────────────────────────────────────────────────

def _point_select():
    """Базовый SELECT для wind_points с геометрией как WKT."""
    return select(
        WindPoint.id,
        WindPoint.point_id,
        WindPoint.point_name,
        WindPoint.description,
        WindPoint.source,
        WindPoint.shore_normal_azimuth_deg,
        WindPoint.measurement_height_m,
        func.ST_AsText(WindPoint.geom).label("geom_wkt"),
        WindPoint.created_at,
    )


def _measurement_select():
    """Базовый SELECT для wind_measurements с join на wind_points."""
    return (
        select(
            WindMeasurement.id,
            WindMeasurement.wind_point_id,
            WindPoint.point_id,
            WindPoint.point_name,
            WindMeasurement.observed_at,
            WindMeasurement.wind_speed_ms,
            WindMeasurement.wind_direction_deg,
            WindMeasurement.wind_gust_ms,
            WindMeasurement.source,
            WindMeasurement.created_at,
        )
        .join(WindPoint, WindPoint.id == WindMeasurement.wind_point_id)
    )


# ─── WindPoint CRUD ─────────────────────────────────────────────────────────────

def get_wind_point(db: Session, point_db_id: int):
    """Получить точку наблюдений по суррогатному PK."""
    row = db.execute(
        _point_select().where(WindPoint.id == point_db_id)
    ).mappings().first()
    return dict(row) if row else None


def get_wind_point_by_point_id(db: Session, point_id: str):
    """Получить точку наблюдений по бизнес-ключу point_id."""
    row = db.execute(
        _point_select().where(WindPoint.point_id == point_id)
    ).mappings().first()
    return dict(row) if row else None


def list_wind_points(db: Session, limit: int = 100, offset: int = 0) -> list[dict]:
    rows = db.execute(
        _point_select().order_by(WindPoint.id).limit(limit).offset(offset)
    ).mappings().all()
    return [dict(r) for r in rows]


def create_wind_point(db: Session, data: WindPointCreate) -> dict:
    obj = WindPoint(
        point_id=data.point_id,
        point_name=data.point_name,
        description=data.description,
        source=data.source,
        shore_normal_azimuth_deg=data.shore_normal_azimuth_deg,
        measurement_height_m=data.measurement_height_m,
        geom=WKTElement(data.geom_wkt, srid=4326),
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return get_wind_point(db, obj.id)


def update_wind_point(db: Session, point_db_id: int, data: WindPointUpdate) -> dict | None:
    obj = db.get(WindPoint, point_db_id)
    if obj is None:
        return None
    patch = data.model_dump(exclude_unset=True)
    if "geom_wkt" in patch:
        obj.geom = WKTElement(patch.pop("geom_wkt"), srid=4326)
    for key, value in patch.items():
        setattr(obj, key, value)
    db.commit()
    db.refresh(obj)
    return get_wind_point(db, obj.id)


def delete_wind_point(db: Session, point_db_id: int) -> bool:
    obj = db.get(WindPoint, point_db_id)
    if obj is None:
        return False
    db.delete(obj)
    db.commit()
    return True


def list_points_near(db: Session, wkt: str, radius_m: float = 50_000, limit: int = 100, offset: int = 0) -> list[dict]:
    """Точки в радиусе radius_m метров от переданной геометрии WKT (geography-дистанция)."""
    search_geom = WKTElement(wkt, srid=4326)
    rows = db.execute(
        _point_select()
        .where(
            func.ST_DWithin(
                func.ST_Transform(WindPoint.geom, 4326).cast(func.ST_Geography.__class__),
                func.ST_GeomFromText(wkt, 4326).cast(func.ST_Geography.__class__),
                radius_m,
            )
        )
        .order_by(WindPoint.id)
        .limit(limit)
        .offset(offset)
    ).mappings().all()
    return [dict(r) for r in rows]


def list_points_within_polygon(db: Session, wkt: str, limit: int = 100, offset: int = 0) -> list[dict]:
    """Точки, геометрия которых пересекает переданный полигон/геометрию WKT."""
    search_geom = WKTElement(wkt, srid=4326)
    rows = db.execute(
        _point_select()
        .where(func.ST_Intersects(WindPoint.geom, search_geom))
        .order_by(WindPoint.id)
        .limit(limit)
        .offset(offset)
    ).mappings().all()
    return [dict(r) for r in rows]


# ─── WindMeasurement CRUD ───────────────────────────────────────────────────────

def get_measurement(db: Session, measurement_id: int) -> dict | None:
    row = db.execute(
        _measurement_select().where(WindMeasurement.id == measurement_id)
    ).mappings().first()
    return dict(row) if row else None


def list_measurements_by_point(
    db: Session, wind_point_id: int, limit: int = 500, offset: int = 0
) -> list[dict]:
    rows = db.execute(
        _measurement_select()
        .where(WindMeasurement.wind_point_id == wind_point_id)
        .order_by(WindMeasurement.observed_at)
        .limit(limit)
        .offset(offset)
    ).mappings().all()
    return [dict(r) for r in rows]


def list_all_measurements(db: Session, limit: int = 500, offset: int = 0) -> list[dict]:
    rows = db.execute(
        _measurement_select()
        .order_by(WindMeasurement.observed_at, WindMeasurement.wind_point_id)
        .limit(limit)
        .offset(offset)
    ).mappings().all()
    return [dict(r) for r in rows]


def create_measurement(db: Session, wind_point_id: int, data: WindMeasurementCreate) -> dict:
    obj = WindMeasurement(
        wind_point_id=wind_point_id,
        observed_at=data.observed_at,
        wind_speed_ms=data.wind_speed_ms,
        wind_direction_deg=data.wind_direction_deg,
        wind_gust_ms=data.wind_gust_ms,
        source=data.source,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return get_measurement(db, obj.id)


def update_measurement(db: Session, measurement_id: int, data: WindMeasurementUpdate) -> dict | None:
    obj = db.get(WindMeasurement, measurement_id)
    if obj is None:
        return None
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(obj, key, value)
    db.commit()
    db.refresh(obj)
    return get_measurement(db, obj.id)


def delete_measurement(db: Session, measurement_id: int) -> bool:
    obj = db.get(WindMeasurement, measurement_id)
    if obj is None:
        return False
    db.delete(obj)
    db.commit()
    return True
