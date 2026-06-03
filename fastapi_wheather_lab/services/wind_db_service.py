from __future__ import annotations

import os

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from fastapi_wheather_lab.schemas.wind import WindMeasurementResponse, WindPointDBResponse


class WindDBService:
    def __init__(self, database_url: str | None = None):
        self.database_url = database_url or os.getenv(
            "DATABASE_URL",
            "postgresql+psycopg://urban_user:urban_password@localhost:5432/urban_wind_data",
        )
        self.engine = create_engine(self.database_url, future=True)
        self.SessionLocal = sessionmaker(bind=self.engine, autoflush=False, autocommit=False, future=True)

    def list_points(self) -> list[WindPointDBResponse]:
        with self.SessionLocal() as session:
            rows = session.execute(text("""
                SELECT id, point_id, point_name, description, source,
                       shore_normal_azimuth_deg, measurement_height_m,
                       ST_AsText(geom) AS geom_wkt
                FROM wind_points
                ORDER BY id
            """)).mappings().all()
            return [WindPointDBResponse(**dict(row)) for row in rows]

    def list_measurements(self) -> list[WindMeasurementResponse]:
        with self.SessionLocal() as session:
            rows = session.execute(text("""
                SELECT wm.id,
                       wm.wind_point_id,
                       wp.point_id,
                       wp.point_name,
                       wm.observed_at,
                       wm.wind_speed_ms,
                       wm.wind_direction_deg,
                       wm.wind_gust_ms,
                       wm.source
                FROM wind_measurements AS wm
                JOIN wind_points AS wp ON wp.id = wm.wind_point_id
                ORDER BY wm.observed_at, wm.wind_point_id
            """)).mappings().all()
            return [WindMeasurementResponse(**dict(row)) for row in rows]
