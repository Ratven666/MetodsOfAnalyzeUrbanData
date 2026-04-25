from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

import pandas as pd


class BaseImporter(ABC):
    @abstractmethod
    def load(self, path: str | Path) -> Any: ...


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


class ParquetImporter(BaseImporter):
    def load(self, path: str | Path) -> pd.DataFrame:
        # engine=None — pandas сам выберет pyarrow/fastparquet, если есть
        return pd.read_parquet(Path(path))


class ImportWhetherFactory:
    _registry: dict[str, type[BaseImporter]] = {
        "csv": CsvImporter,
        "xls": ExcelImporter,
        "xlsx": ExcelImporter,
        "json": JsonImporter,
        "parquet": ParquetImporter,
        "pq": ParquetImporter,
    }

    @classmethod
    def get(cls, format_or_ext: str) -> BaseImporter:
        key = format_or_ext.lower().lstrip(".")
        if key not in cls._registry:
            raise ValueError(f"Unknown import format: {format_or_ext}")
        return cls._registry[key]()

    @classmethod
    def read_data(cls, file_path: str | Path) -> Any:
        path = Path(file_path)
        suffix = path.suffix
        if not suffix:
            raise ValueError(f"File '{file_path}' has no extension")
        importer = cls.get(format_or_ext=suffix[1:])
        return importer.load(path)
