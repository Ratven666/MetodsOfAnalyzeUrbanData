from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from fastapi_wheather_lab.db.base import Base


class WindMeasurement(Base):
    """ORM-модель таблицы wind_measurements."""

    __tablename__ = "wind_measurements"

    id: Mapped[int] = mapped_column(primary_key=True)
    wind_point_id: Mapped[int] = mapped_column(
        ForeignKey("wind_points.id", ondelete="CASCADE"), nullable=False
    )
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    wind_speed_ms: Mapped[Decimal] = mapped_column(Numeric(8, 2), nullable=False)
    wind_direction_deg: Mapped[Decimal] = mapped_column(Numeric(6, 2), nullable=False)
    wind_gust_ms: Mapped[Decimal | None] = mapped_column(Numeric(8, 2), nullable=True)
    source: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    point: Mapped[WindPoint] = relationship(back_populates="measurements")  # noqa: F821
