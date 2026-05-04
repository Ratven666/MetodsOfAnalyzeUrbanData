"""
Кастомный словарь зависимостей и фабричная функция init_dependencies().

DependencyContainer расширяет обычный dict и добавляет типизированный
метод get_dep() для безопасного получения зависимости по ключу.

Пример содержимого контейнера:
    {
        "app_config":             AppConfigModel(...),
        "runtime_config_service": RuntimeConfigService(...),
    }
"""

from __future__ import annotations

from typing import Type, TypeVar

from fastapi_wheather_lab.schemas.app_config import AppConfigModel
from fastapi_wheather_lab.schemas.runtime_config import RuntimeConfigModel
from fastapi_wheather_lab.services.runtime_config_service import RuntimeConfigService

T = TypeVar("T")


class DependencyContainer(dict):
    """
    Кастомный словарь зависимостей.

    Наследует dict, добавляет get_dep() — безопасное получение зависимости
    с проверкой типа и информативным сообщением об ошибке.
    """

    def get_dep(self, key: str, expected_type: Type[T]) -> T:
        """
        Получить зависимость по ключу.

        Raises
        ------
        KeyError  — если ключ отсутствует.
        TypeError — если тип не совпадает с ожидаемым.
        """
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
        return obj  # type: ignore[return-value]

    def __repr__(self) -> str:
        keys = list(self.keys())
        return f"DependencyContainer(keys={keys})"


def init_dependencies() -> DependencyContainer:
    """
    Фабричная функция, вызываемая один раз в lifespan FastAPI.

    Создаёт и возвращает DependencyContainer со всеми зависимостями приложения.
    """
    # 1. Статическая конфигурация — читает env-переменные один раз
    app_config = AppConfigModel()

    # 2. Начальная runtime-конфигурация
    initial_runtime = RuntimeConfigModel()

    # 3. Сервис runtime-конфигурации
    runtime_service = RuntimeConfigService(initial_config=initial_runtime)

    container = DependencyContainer(
        {
            "app_config": app_config,
            "runtime_config_service": runtime_service,
        }
    )
    return container
