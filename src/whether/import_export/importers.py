from __future__ import annotations

import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

import pandas as pd


class BaseImporter(ABC):
    @abstractmethod
    def load(self, path: str | Path) -> Any:
        ...


class CsvImporter(BaseImporter):
    def load(self, path: str | Path) -> pd.DataFrame:
        return pd.read_csv(Path(path))


class ExcelImporter(BaseImporter):
    def load(self, path: str | Path) -> pd.DataFrame:
        return pd.read_excel(Path(path))


class JsonImporter(BaseImporter):
    """Импорт табличного JSON (список объектов) в DataFrame."""

    def load(self, path: str | Path) -> pd.DataFrame:
        return pd.read_json(Path(path), orient="records")


class ImportWhetherFactory:
    _registry: dict[str, type[BaseImporter]] = {
        "csv": CsvImporter,
        "xls": ExcelImporter,
        "xlsx": ExcelImporter,
        "json": JsonImporter,

    }

    @classmethod
    def get(cls, format_or_ext: str) -> BaseImporter:
        key = format_or_ext.lower().lstrip(".")
        if key not in cls._registry:
            raise ValueError(f"Unknown import format: {format_or_ext}")
        return cls._registry[key]()

    @classmethod
    def read_data(cls, file_path: str | Path) -> None:
        format_ = Path(file_path).suffix
        importer = cls.get(format_or_ext=format_[1:])
        return importer.load(file_path)
