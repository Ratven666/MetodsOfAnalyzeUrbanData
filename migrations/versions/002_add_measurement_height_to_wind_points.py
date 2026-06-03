"""add measurement height to wind points

Revision ID: 002_add_measurement_height_to_wind_points
Revises: 001_create_wind_points_and_measurements
Create Date: 2026-06-03
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "002_add_measurement_height_to_wind_points"
down_revision: Union[str, None] = "001_create_wind_points_and_measurements"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("wind_points", sa.Column("measurement_height_m", sa.Numeric(precision=6, scale=2), nullable=True))
    op.create_check_constraint(
        "ck_wind_points_measurement_height_positive",
        "wind_points",
        "measurement_height_m IS NULL OR measurement_height_m > 0",
    )
    op.execute("UPDATE wind_points SET measurement_height_m = 10.00 WHERE id = 1")
    op.execute("UPDATE wind_points SET measurement_height_m = 15.00 WHERE id = 2")


def downgrade() -> None:
    op.drop_constraint("ck_wind_points_measurement_height_positive", "wind_points", type_="check")
    op.drop_column("wind_points", "measurement_height_m")
