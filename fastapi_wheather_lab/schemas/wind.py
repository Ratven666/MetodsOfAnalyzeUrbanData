from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class WindPointDBResponse(BaseModel):
    id: int
    point_id: str
    point_name: str | None = None
    description: str | None = None
    source: str | None = None
    shore_normal_azimuth_deg: Decimal | None = None
    measurement_height_m: Decimal | None = None
    geom_wkt: str


class WindMeasurementResponse(BaseModel):
    id: int
    wind_point_id: int
    point_id: str
    point_name: str | None = None
    observed_at: datetime
    wind_speed_ms: Decimal
    wind_direction_deg: Decimal
    wind_gust_ms: Decimal | None = None
    source: str | None = None
