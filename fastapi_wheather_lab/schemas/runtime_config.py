from __future__ import annotations

import os
from typing import Literal, Optional

from pydantic import BaseModel, Field

LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR"]
SignConvention = Literal["positive_water", "negative_water"]


class RuntimeConfigModel(BaseModel):
    log_level: LogLevel = Field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"), description="Уровень логирования")
    feature_flag: bool = Field(default_factory=lambda: os.getenv("FEATURE_FLAG", "false").lower() == "true")
    maintenance_mode: bool = Field(default_factory=lambda: os.getenv("MAINTENANCE_MODE", "false").lower() == "true")
    runtime_message: str = Field(default_factory=lambda: os.getenv("RUNTIME_MESSAGE", "Приложение работает в штатном режиме"), max_length=500)
    breaking_coeff: float = Field(default_factory=lambda: float(os.getenv("BREAKING_COEFF", "0.55")), ge=0.3, le=0.9)
    sign_convention: SignConvention = Field(default_factory=lambda: os.getenv("SIGN_CONVENTION", "positive_water"))
    directional_sector_deg: float = Field(default_factory=lambda: float(os.getenv("DIRECTIONAL_SECTOR_DEG", "45.0")), gt=0.0, le=180.0)
    fetch_length_limit_km: Optional[float] = Field(default_factory=lambda: float(os.getenv("FETCH_LENGTH_LIMIT_KM", "300.0")), gt=0.0)


class RuntimeConfigUpdateModel(BaseModel):
    log_level: LogLevel | None = None
    feature_flag: bool | None = None
    maintenance_mode: bool | None = None
    runtime_message: str | None = Field(default=None, max_length=500)
    breaking_coeff: float | None = Field(default=None, ge=0.3, le=0.9)
    sign_convention: SignConvention | None = None
    directional_sector_deg: float | None = Field(default=None, gt=0.0, le=180.0)
    fetch_length_limit_km: Optional[float] = Field(default=None, gt=0.0)
