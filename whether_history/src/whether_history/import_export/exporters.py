from __future__ import annotations

import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

import pandas as pd


class BaseExporter(ABC):
    @abstractmethod
    def export(self, data: Any, path: str | Path) -> Path: ...


class JsonExporter(BaseExporter):
    def export(self, data: [pd.DataFrame | dict], path: str | Path) -> Path:
        path = Path(path)
        if isinstance(data, pd.DataFrame):
            data.to_json(path, orient="records", force_ascii=False, indent=2)
            return path
        path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return path


class CsvExporter(BaseExporter):
    def export(self, data: pd.DataFrame, path: str | Path) -> Path:
        path = Path(path)
        data.to_csv(path, index=False)
        return path


class ExcelExporter(BaseExporter):
    def export(self, data: pd.DataFrame, path: str | Path) -> Path:
        path = Path(path)
        data.to_excel(path, sheet_name="daily", index=False)
        return path


class ExportWhetherFactory:
    _registry: dict[str, type[BaseExporter]] = dict(
        json=JsonExporter,
        csv=CsvExporter,
        xlsx=ExcelExporter,
        xls=ExcelExporter,
        excel=ExcelExporter,
    )

    @classmethod
    def get(cls, format_: str) -> BaseExporter:
        key = format_.lower()
        if key not in cls._registry:
            raise ValueError(f"Unknown export format: {format_}")
        return cls._registry[key]()

    @classmethod
    def export(cls, data: pd.DataFrame | dict, file_path: str | Path) -> None:
        format_ = Path(file_path).suffix
        exporter = cls.get(format_=format_[1:])
        exporter.export(data, file_path)
