from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


# ─── WindPoint schemas ─────────────────────────────────────────────────────────

class WindPointBase(BaseModel):
    point_id: str = Field(..., min_length=1, max_length=100, description="Уникальный идентификатор точки")
    point_name: str | None = Field(default=None, max_length=200, description="Название точки наблюдения")
    description: str | None = Field(default=None, max_length=500)
    source: str | None = Field(default=None, max_length=255)
    shore_normal_azimuth_deg: Decimal | None = Field(
        default=None, ge=0, lt=360, description="Азимут нормали к берегу в градусах (0..360)"
    )
    measurement_height_m: Decimal | None = Field(
        default=None, ge=0, description="Высота измерения над уровнем земли/воды, м"
    )
    geom_wkt: str = Field(..., description="Геометрия точки в формате WKT (POINT(lon lat))")


class WindPointCreate(WindPointBase):
    """Схема создания точки наблюдения. POST /wind/points"""


class WindPointUpdate(BaseModel):
    """Схема частичного обновления. PUT /wind/points/{point_id}"""
    point_name: str | None = Field(default=None, max_length=200)
    description: str | None = Field(default=None, max_length=500)
    source: str | None = Field(default=None, max_length=255)
    shore_normal_azimuth_deg: Decimal | None = Field(default=None, ge=0, lt=360)
    measurement_height_m: Decimal | None = Field(default=None, ge=0)
    geom_wkt: str | None = None


class WindPointDBResponse(BaseModel):
    """Схема чтения точки наблюдения из БД."""
    id: int
    point_id: str
    point_name: str | None = None
    description: str | None = None
    source: str | None = None
    shore_normal_azimuth_deg: Decimal | None = None
    measurement_height_m: Decimal | None = None
    geom_wkt: str
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


# ─── WindMeasurement schemas ────────────────────────────────────────────────────

class WindMeasurementCreate(BaseModel):
    """Схема создания измерения. POST /wind/points/{wind_point_id}/measurements"""
    observed_at: datetime = Field(..., description="Дата и время наблюдения (с таймзоной)")
    wind_speed_ms: Decimal = Field(..., ge=0, description="Скорость ветра, м/с")
    wind_direction_deg: Decimal = Field(..., ge=0, lt=360, description="Направление ветра, градусы (0..360)")
    wind_gust_ms: Decimal | None = Field(default=None, ge=0, description="Скорость порыва ветра, м/с")
    source: str | None = Field(default=None, max_length=255)


class WindMeasurementUpdate(BaseModel):
    """Схема частичного обновления измерения."""
    observed_at: datetime | None = None
    wind_speed_ms: Decimal | None = Field(default=None, ge=0)
    wind_direction_deg: Decimal | None = Field(default=None, ge=0, lt=360)
    wind_gust_ms: Decimal | None = Field(default=None, ge=0)
    source: str | None = None


class WindMeasurementResponse(BaseModel):
    """Схема чтения измерения ветра."""
    id: int
    wind_point_id: int
    point_id: str
    point_name: str | None = None
    observed_at: datetime
    wind_speed_ms: Decimal
    wind_direction_deg: Decimal
    wind_gust_ms: Decimal | None = None
    source: str | None = None
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
