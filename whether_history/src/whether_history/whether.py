import datetime as dt
from typing import Optional

import pandas as pd
from loguru import logger

from .data_aggregator import OpenMeteoWhetherDataAggregator
from .import_export.exporters import ExportWhetherFactory
from .import_export.importers import ImportWhetherFactory


class Whether:

    def __init__(
        self,
        latitude: float,
        longitude: float,
        timezone: str = "Europe/Moscow",
        data_aggregator=OpenMeteoWhetherDataAggregator,
    ):
        """
        Класс для работы с данными о погоде

        Args:
            latitude (float): Широта точки в координатах WGS84.
            longitude (float): Долгота точки в координатах WGS84.
            timezone (str, optional): Часовой пояс для агрегации суточных данных.
                Любое имя из базы IANA, по умолчанию 'Europe/Moscow'.
            data_aggregator (DataAggregatorABC): Класс для получения погодных данных с конкретного ресурса
        """
        self._whether_data = pd.DataFrame()
        self._data_aggregator = data_aggregator(latitude, longitude, timezone)
        logger.info(
            "Whether initialized at lat={lat}, lon={lon}, tz={tz}",
            lat=latitude,
            lon=longitude,
            tz=timezone,
        )

    @property
    def whether_data(self) -> pd.DataFrame:
        return self._whether_data

    def __add_data(self, df: pd.DataFrame) -> None:
        logger.debug("Adding data with shape {}", df.shape)

        def normalize_date_column(df: pd.DataFrame, col: str = "date") -> pd.DataFrame:
            df = df.copy()
            df[col] = pd.to_datetime(df[col]).dt.date
            return df

        if "date" not in df.columns:
            logger.error("Missing 'date' column in incoming DataFrame")
            raise KeyError("Колонка 'date' отсутствует в переданном DataFrame.")

        df = normalize_date_column(df, "date")

        if self._whether_data is None or self._whether_data.empty:
            self._whether_data = df
            logger.info(
                "Initial weather data set with {} rows", len(self._whether_data)
            )
            return

        before = len(self._whether_data)
        self._whether_data = pd.concat([self._whether_data, df], ignore_index=True)
        self._whether_data = self._whether_data.drop_duplicates(
            subset=["date"], keep="first"
        )
        after = len(self._whether_data)
        logger.info(
            "Weather data updated: {} -> {} rows ({} new unique dates)",
            before,
            after,
            after - before,
        )

    def download_whether_data(
        self,
        start_date: dt.date | dt.datetime | str,
        end_date: Optional[dt.date | dt.datetime | str] = None,
        timeout: int = 120,
    ) -> pd.DataFrame:
        logger.info(
            "Downloading weather data from {} to {}",
            start_date,
            end_date or start_date,
        )
        df = self._data_aggregator.get_daily_data(start_date, end_date, timeout)
        logger.debug("Downloaded DataFrame shape: {}", df.shape)
        self.__add_data(df)
        return df

    def export_whether_data(self, file_path, exporter=ExportWhetherFactory):
        logger.info("Exporting weather data to {}", file_path)
        result = exporter.export(data=self._whether_data, file_path=file_path)
        logger.success("Weather data exported to {}", result)
        return result

    def read_whether_data(self, file_path, importer=ImportWhetherFactory):
        logger.info("Reading weather data from {}", file_path)
        df = importer.read_data(file_path=file_path)
        logger.debug("Imported DataFrame shape: {}", df.shape)
        self.__add_data(df)
        return df

    def get_statistic_df(self) -> pd.DataFrame:
        logger.info(
            "Calculating statistics for weather data ({} rows)", len(self._whether_data)
        )
        stats = self.whether_data.describe()
        logger.debug("Statistics shape: {}", stats.shape)
        return stats
