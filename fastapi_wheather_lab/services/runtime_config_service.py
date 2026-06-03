from __future__ import annotations

from fastapi_wheather_lab.schemas.runtime_config import (
    RuntimeConfigModel,
    RuntimeConfigUpdateModel,
)


class RuntimeConfigService:
    def __init__(self, initial_config: RuntimeConfigModel):
        self._config = initial_config

    def get_config(self) -> RuntimeConfigModel:
        return self._config

    def update_config(self, update: RuntimeConfigUpdateModel) -> RuntimeConfigModel:
        current_data = self._config.model_dump()
        patch_data = update.model_dump(exclude_unset=True)
        merged = {**current_data, **patch_data}
        self._config = RuntimeConfigModel(**merged)
        return self._config
