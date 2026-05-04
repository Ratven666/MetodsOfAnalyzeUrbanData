from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator


class PointCoordinatesModel(BaseModel):
    """Координаты расчётной точки."""

    lon: float = Field(
        ...,
        ge=-180.0,
        le=180.0,
        description="Долгота точки расчёта в градусах",
        examples=[37.80218],
    )
    lat: float = Field(
        ...,
        ge=-90.0,
        le=90.0,
        description="Широта точки расчёта в градусах",
        examples=[44.6705683],
    )


class ShoreNormalVectorModel(BaseModel):
    """
    Нормаль к берегу в точке расчёта.

    Можно хранить:
    - азимут нормали в градусах;
    - или декартовы компоненты единичного вектора (x, y).
    """

    azimuth_deg: Optional[float] = Field(
        default=None,
        ge=0.0,
        lt=360.0,
        description="Азимут нормали к берегу в градусах (0..360)",
        examples=[135.0],
    )
    x: Optional[float] = Field(
        default=None,
        ge=-1.0,
        le=1.0,
        description="X-компонента единичного вектора нормали",
        examples=[0.7071],
    )
    y: Optional[float] = Field(
        default=None,
        ge=-1.0,
        le=1.0,
        description="Y-компонента единичного вектора нормали",
        examples=[-0.7071],
    )

    @field_validator("y")
    @classmethod
    def validate_vector_pair(cls, v, info):
        x = info.data.get("x")
        azimuth = info.data.get("azimuth_deg")

        if azimuth is None and (x is None or v is None):
            raise ValueError(
                "Необходимо задать либо azimuth_deg, либо обе компоненты вектора x и y."
            )
        return v


class PointInputModel(BaseModel):
    """Описание расчётной точки для волновой модели."""

    point_id: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Уникальный идентификатор точки расчёта",
        examples=["point_001"],
    )
    point_name: Optional[str] = Field(
        default=None,
        max_length=200,
        description="Человекочитаемое название точки",
        examples=["Южный участок берега"],
    )
    coordinates: PointCoordinatesModel = Field(
        ...,
        description="Географические координаты точки расчёта",
    )
    shore_normal: ShoreNormalVectorModel = Field(
        ...,
        description="Параметры нормали к берегу в точке расчёта",
    )
    description: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Произвольное описание точки",
        examples=["Контрольная точка на аккумулятивном участке берега"],
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "point_id": "point_001",
                "point_name": "Южный участок берега",
                "coordinates": {"lon": 37.80218, "lat": 44.6705683},
                "shore_normal": {"azimuth_deg": 135.0},
                "description": "Контрольная точка на аккумулятивном участке берега",
            }
        }
    }
