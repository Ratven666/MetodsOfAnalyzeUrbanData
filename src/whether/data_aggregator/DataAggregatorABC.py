import datetime as dt
from typing import Optional
import pandas as pd

from abc import ABC, abstractmethod


class DataAggregatorABC(ABC):

    def __init__(self,
                 latitude: float,
                 longitude: float,
                 timezone: str = "Europe/Moscow",
                 ) -> None:
        """Агрегатор метеоданных Open-Meteo.

        Args:
            latitude (float): Широта точки в координатах WGS84.
            longitude (float): Долгота точки в координатах WGS84.
            timezone (str, optional): Часовой пояс для агрегации суточных данных.
                Любое имя из базы IANA, по умолчанию 'Europe/Moscow'.
        """
        self.latitude = latitude
        self.longitude = longitude
        self.timezone = timezone

    @abstractmethod
    def get_daily_data(self,
                       start_date: dt.date | dt.datetime | str,
                       end_date: Optional[dt.date | dt.datetime | str] = None,
                       timeout: int = 120,
                       ) -> pd.DataFrame:
        """
        Получить ежедневные метеоданные в виде DataFrame.

        Загружает суточные данные из API, формирует таблицу с датами,
        выбранными переменными и добавляет основные календарные и температурные
        признаки.

        Args:
            start_date (date | datetime | str): Начальная дата периода (включительно).
            end_date (date | datetime | str, optional): Конечная дата периода
                (включительно). Если не задана, используется только start_date.
            timeout (int, optional): Таймаут запроса к API в секундах.

        Returns:
            pandas.DataFrame: Таблица с колонками:
                - date (datetime64[ns]): Дата.
                - <vars> (...): Переменные из self.daily_variables.
                - year (int64): Год.
                - month (int64): Номер месяца.
                - day_of_year (int64): Номер дня в году.
        """
        pass
