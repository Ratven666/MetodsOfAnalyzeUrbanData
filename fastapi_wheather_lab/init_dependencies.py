"""
Кастомный словарь зависимостей и фабричная функция init_dependencies().
"""

from __future__ import annotations

from typing import Type, TypeVar

from fastapi_wheather_lab.schemas.app_config import AppConfigModel
from fastapi_wheather_lab.schemas.runtime_config import RuntimeConfigModel
from fastapi_wheather_lab.services.runtime_config_service import RuntimeConfigService
from fastapi_wheather_lab.services.wind_db_service import WindDBService

T = TypeVar("T")


class DependencyContainer(dict):
    def get_dep(self, key: str, expected_type: Type[T]) -> T:
        if key not in self:
            raise KeyError(
                f"Зависимость '{key}' не найдена в DependencyContainer. "
                f"Доступные ключи: {list(self.keys())}"
            )
        obj = self[key]
        if not isinstance(obj, expected_type):
            raise TypeError(
                f"Зависимость '{key}' имеет тип {type(obj).__name__!r}, "
                f"ожидался {expected_type.__name__!r}."
            )
        return obj

    def __repr__(self) -> str:
        keys = list(self.keys())
        return f"DependencyContainer(keys={keys})"


def init_dependencies() -> DependencyContainer:
    app_config = AppConfigModel()
    initial_runtime = RuntimeConfigModel()
    runtime_service = RuntimeConfigService(initial_config=initial_runtime)
    wind_db_service = WindDBService()

    container = DependencyContainer(
        {
            "app_config": app_config,
            "runtime_config_service": runtime_service,
            "wind_db_service": wind_db_service,
        }
    )
    return container
