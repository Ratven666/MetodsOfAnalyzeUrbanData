import datetime as dt
from typing import Optional

import pandas as pd

from whether.import_export.exporters import ExportWhetherFactory
from whether.import_export.importers import ImportWhetherFactory
from whether import OpenMeteoWhetherDataAggregator


class Whether:


    def __init__(self, latitude: float,
                 longitude: float,
                 timezone: str = "Europe/Moscow",
                 data_aggregator = OpenMeteoWhetherDataAggregator,
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

    @property
    def whether_data(self) -> pd.DataFrame:
        return self._whether_data

    def __add_data(self, df: pd.DataFrame) -> None:
        def normalize_date_column(df: pd.DataFrame, col: str = "date") -> pd.DataFrame:
            df = df.copy()
            df[col] = pd.to_datetime(df[col]).dt.date  # только дата, без времени
            return df
        if "date" not in df.columns:
            raise KeyError("Колонка 'date' отсутствует в переданном DataFrame.")
        df = normalize_date_column(df, "date")
        if self._whether_data is None or self._whether_data.empty:
            self._whether_data = df
            return
        self._whether_data = pd.concat([self._whether_data, df], ignore_index=True)
        self._whether_data = self._whether_data.drop_duplicates(subset=["date"], keep="first")

    def download_whether_data(self,
                       start_date: dt.date | dt.datetime | str,
                       end_date: Optional[dt.date | dt.datetime | str] = None,
                       timeout: int = 120,
                       ) -> pd.DataFrame:
        df = self._data_aggregator.get_daily_data(start_date, end_date, timeout)
        self.__add_data(df)
        return df

    def export_whether_data(self, file_path, exporter=ExportWhetherFactory):
        return exporter.export(data=self._whether_data, file_path=file_path)

    def read_whether_data(self, file_path, importer=ImportWhetherFactory):
        df =  importer.read_data(file_path=file_path)
        self.__add_data(df)
        return df

    def get_statistic_df(self):
        return self.whether_data.describe()
