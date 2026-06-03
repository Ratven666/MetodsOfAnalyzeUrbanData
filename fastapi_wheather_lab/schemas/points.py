from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field, field_validator


class PointCoordinatesModel(BaseModel):
    lon: float = Field(..., ge=-180.0, le=180.0, description="Долгота точки расчёта в градусах")
    lat: float = Field(..., ge=-90.0, le=90.0, description="Широта точки расчёта в градусах")


class ShoreNormalVectorModel(BaseModel):
    azimuth_deg: Optional[float] = Field(default=None, ge=0.0, lt=360.0, description="Азимут нормали к берегу в градусах (0..360)")
    x: Optional[float] = Field(default=None, ge=-1.0, le=1.0, description="X-компонента единичного вектора нормали")
    y: Optional[float] = Field(default=None, ge=-1.0, le=1.0, description="Y-компонента единичного вектора нормали")

    @field_validator("y")
    @classmethod
    def validate_vector_pair(cls, v, info):
        x = info.data.get("x")
        azimuth = info.data.get("azimuth_deg")
        if azimuth is None and (x is None or v is None):
            raise ValueError("Необходимо задать либо azimuth_deg, либо обе компоненты вектора x и y.")
        return v


class PointInputModel(BaseModel):
    point_id: str = Field(..., min_length=1, max_length=100, description="Уникальный идентификатор точки расчёта")
    point_name: Optional[str] = Field(default=None, max_length=200, description="Человекочитаемое название точки")
    coordinates: PointCoordinatesModel = Field(..., description="Географические координаты точки расчёта")
    shore_normal: ShoreNormalVectorModel = Field(..., description="Параметры нормали к берегу в точке расчёта")
    description: Optional[str] = Field(default=None, max_length=500, description="Произвольное описание точки")
