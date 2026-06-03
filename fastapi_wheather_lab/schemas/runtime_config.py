from __future__ import annotations

import os
from typing import Literal, Optional

from pydantic import BaseModel, Field

LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR"]
SignConvention = Literal["positive_water", "negative_water"]


class RuntimeConfigModel(BaseModel):
    """Полная runtime-конфигурация."""

    log_level: LogLevel = Field(
        default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"),
        description="Уровень логирования",
    )
    feature_flag: bool = Field(
        default_factory=lambda: os.getenv("FEATURE_FLAG", "false").lower() == "true",
        description="Флаг включения экспериментальных функций",
    )
    maintenance_mode: bool = Field(
        default_factory=lambda: os.getenv("MAINTENANCE_MODE", "false").lower()
        == "true",
        description="Режим технического обслуживания",
    )
    runtime_message: str = Field(
        default_factory=lambda: os.getenv(
            "RUNTIME_MESSAGE", "Приложение работает в штатном режиме"
        ),
        max_length=500,
        description="Текущее сообщение о статусе сервиса",
    )
    breaking_coeff: float = Field(
        default_factory=lambda: float(os.getenv("BREAKING_COEFF", "0.55")),
        ge=0.3,
        le=0.9,
        description="Коэффициент γ_b критерия разрушения волны H ≤ γ_b·h",
    )
    overwater_factor: float = Field(
        default_factory=lambda: float(os.getenv("OVERWATER_FACTOR", "1.1")),
        ge=1.0,
        le=1.5,
        description="Поправочный коэффициент скорости ветра над водой",
    )
    bathy_radius_m: float = Field(
        default_factory=lambda: float(os.getenv("BATHY_RADIUS_M", "20000.0")),
        gt=0,
        description="Радиус луча батиметрии (м)",
    )
    bathy_n_steps: int = Field(
        default_factory=lambda: int(os.getenv("BATHY_N_STEPS", "200")),
        ge=10,
        le=5000,
        description="Число точек вдоль луча батиметрии",
    )
    sign_convention: SignConvention = Field(
        default_factory=lambda: os.getenv("SIGN_CONVENTION", "positive_water"),
        description='Знаковое соглашение батиметрии: "positive_water" или "negative_water"',
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "log_level": "INFO",
                "feature_flag": False,
                "maintenance_mode": False,
                "runtime_message": "Приложение работает в штатном режиме",
                "breaking_coeff": 0.55,
                "overwater_factor": 1.1,
                "bathy_radius_m": 20000.0,
                "bathy_n_steps": 200,
                "sign_convention": "positive_water",
            }
        }
    }


class RuntimeConfigUpdateModel(BaseModel):
    """Тело запроса для обновления runtime-конфигурации."""

    log_level: Optional[LogLevel] = Field(default=None)
    feature_flag: Optional[bool] = Field(default=None)
    maintenance_mode: Optional[bool] = Field(default=None)
    runtime_message: Optional[str] = Field(default=None, max_length=500)
    breaking_coeff: Optional[float] = Field(default=None, ge=0.3, le=0.9)
    overwater_factor: Optional[float] = Field(default=None, ge=1.0, le=1.5)
    bathy_radius_m: Optional[float] = Field(default=None, gt=0)
    bathy_n_steps: Optional[int] = Field(default=None, ge=10, le=5000)
    sign_convention: Optional[SignConvention] = Field(default=None)

    model_config = {
        "json_schema_extra": {
            "example": {
                "log_level": "DEBUG",
                "feature_flag": True,
                "maintenance_mode": False,
                "runtime_message": "Обновлены параметры батиметрии",
                "bathy_radius_m": 15000.0,
                "bathy_n_steps": 150,
                "sign_convention": "negative_water",
            }
        }
    }
