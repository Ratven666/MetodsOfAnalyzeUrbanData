from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from geoalchemy2 import Geometry
from sqlalchemy import DateTime, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from fastapi_wheather_lab.db.base import Base


class WindPoint(Base):
    __tablename__ = "wind_points"

    id: Mapped[int] = mapped_column(primary_key=True)
    point_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    point_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    source: Mapped[str | None] = mapped_column(String(255), nullable=True)
    shore_normal_azimuth_deg: Mapped[Decimal | None] = mapped_column(Numeric(6, 2), nullable=True)
    geom = mapped_column(Geometry(geometry_type="POINT", srid=4326, spatial_index=False), nullable=False)
    measurement_height_m: Mapped[Decimal | None] = mapped_column(Numeric(6, 2), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    measurements: Mapped[list[WindMeasurement]] = relationship(back_populates="point", cascade="all, delete-orphan")
