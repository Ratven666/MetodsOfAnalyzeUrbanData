"""create wind points and measurements

Revision ID: 001_create_wind_points_and_measurements
Revises:
Create Date: 2026-06-03
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from geoalchemy2 import Geometry

revision: str = "001_create_wind_points_and_measurements"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis")

    op.create_table(
        "wind_points",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("point_id", sa.String(length=100), nullable=False, unique=True),
        sa.Column("point_name", sa.String(length=200), nullable=True),
        sa.Column("description", sa.String(length=500), nullable=True),
        sa.Column("source", sa.String(length=255), nullable=True),
        sa.Column("shore_normal_azimuth_deg", sa.Numeric(precision=6, scale=2), nullable=True),
        sa.Column(
            "geom",
            Geometry(geometry_type="POINT", srid=4326, spatial_index=False),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.create_index("idx_wind_points_geom", "wind_points", ["geom"], postgresql_using="gist")

    op.create_table(
        "wind_measurements",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("wind_point_id", sa.Integer(), nullable=False),
        sa.Column("observed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("wind_speed_ms", sa.Numeric(precision=8, scale=2), nullable=False),
        sa.Column("wind_direction_deg", sa.Numeric(precision=6, scale=2), nullable=False),
        sa.Column("wind_gust_ms", sa.Numeric(precision=8, scale=2), nullable=True),
        sa.Column("source", sa.String(length=255), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["wind_point_id"], ["wind_points.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("wind_point_id", "observed_at", name="uq_wind_measurements_point_time"),
        sa.CheckConstraint("wind_speed_ms >= 0", name="ck_wind_speed_non_negative"),
        sa.CheckConstraint("wind_gust_ms IS NULL OR wind_gust_ms >= 0", name="ck_wind_gust_non_negative"),
        sa.CheckConstraint("wind_direction_deg >= 0 AND wind_direction_deg < 360", name="ck_wind_direction_range"),
    )
    op.create_index("idx_wind_measurements_point_time", "wind_measurements", ["wind_point_id", "observed_at"])

    op.execute("""
        INSERT INTO wind_points (id, point_id, point_name, description, source, shore_normal_azimuth_deg, geom)
        VALUES
        (1, 'point_001', 'Южный участок берега', 'Контрольная точка для анализа ветра', 'manual setup', 135.00, ST_GeomFromText('POINT(37.80218 44.6705683)', 4326)),
        (2, 'point_002', 'Северный участок берега', 'Вторая контрольная точка для анализа ветра', 'manual setup', 110.00, ST_GeomFromText('POINT(37.90000 44.7200000)', 4326));
    """)

    op.execute("""
        INSERT INTO wind_measurements (wind_point_id, observed_at, wind_speed_ms, wind_direction_deg, wind_gust_ms, source)
        VALUES
        (1, '2026-06-01 00:00:00+03', 5.20, 245.00, 8.10, 'test dataset'),
        (1, '2026-06-01 03:00:00+03', 6.40, 252.00, 9.30, 'test dataset'),
        (1, '2026-06-01 06:00:00+03', 7.10, 260.00, 10.80, 'test dataset'),
        (2, '2026-06-01 00:00:00+03', 8.60, 238.00, 12.40, 'test dataset'),
        (2, '2026-06-01 03:00:00+03', 9.10, 241.00, 13.20, 'test dataset');
    """)


def downgrade() -> None:
    op.drop_index("idx_wind_measurements_point_time", table_name="wind_measurements")
    op.drop_table("wind_measurements")
    op.drop_index("idx_wind_points_geom", table_name="wind_points")
    op.drop_table("wind_points")
