"""
Сервис управления runtime-конфигурацией.
"""

from fastapi_wheather_lab.config import RuntimeConfig


def get_runtime_config() -> RuntimeConfig:
    """Dependency / helper — возвращает singleton RuntimeConfig."""
    return RuntimeConfig()


def update_runtime_config(data: dict) -> RuntimeConfig:
    """Применить обновления к runtime-конфигурации и вернуть обновлённый объект."""
    cfg = RuntimeConfig()
    cfg.update(data)
    return cfg
