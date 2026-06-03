"""
Сервис управления runtime-конфигурацией.

Отвечает ТОЛЬКО за хранение и обновление RuntimeConfigModel.
Не знает о маршрутизации, HTTP или создании FastAPI-приложения.
"""

from __future__ import annotations

from fastapi_wheather_lab.schemas.runtime_config import (
    RuntimeConfigModel,
    RuntimeConfigUpdateModel,
)


class RuntimeConfigService:
    """
    Хранит текущую runtime-конфигурацию и предоставляет методы
    для её чтения и обновления.

    Создаётся один раз в lifespan и живёт всё время работы приложения.
    """

    def __init__(self, initial_config: RuntimeConfigModel) -> None:
        # deep copy через Pydantic, чтобы мутации не затронули исходный объект
        self._config: RuntimeConfigModel = initial_config.model_copy(deep=True)

    # ── Публичный интерфейс ────────────────────────────────────────────────

    def get_config(self) -> RuntimeConfigModel:
        """Вернуть текущую конфигурацию (только чтение)."""
        return self._config

    def update_config(self, update: RuntimeConfigUpdateModel) -> RuntimeConfigModel:
        """
        Обновить только переданные поля (partial update).

        Поля со значением None игнорируются, что позволяет изменять
        конфигурацию частично, не передавая все поля.
        """
        current_data = self._config.model_dump()
        patch = update.model_dump(exclude_none=True)
        current_data.update(patch)
        self._config = RuntimeConfigModel(**current_data)
        return self._config

    def __repr__(self) -> str:
        return (
            f"RuntimeConfigService("
            f"log_level={self._config.log_level!r}, "
            f"maintenance_mode={self._config.maintenance_mode})"
        )
