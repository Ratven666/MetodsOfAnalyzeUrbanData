import datetime as dt
import re
from typing import Optional
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import pandas as pd

from abc import ABC

from ..exeptions import InvalidCoordinateError, InvalidTimezoneError, InvalidDateFormatError


class BaseDataAggregator(ABC):

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
        self.__validate_data(latitude, longitude, timezone)

        self.latitude = latitude
        self.longitude = longitude
        self.timezone = timezone

    def __validate_data(self, latitude, longitude, timezone):
        self.__validate_wgs84(latitude, longitude)
        self.__validate_timezone(timezone)

    @staticmethod
    def __validate_wgs84(latitude: float, longitude: float) -> None:
        if not (-90.0 <= latitude <= 90.0):
            raise InvalidCoordinateError(
                f"Invalid latitude {latitude}. "
                "Допустимый диапазон: [-90, 90] градусов."
            )
        if not (-180.0 <= longitude <= 180.0):
            raise InvalidCoordinateError(
                f"Invalid longitude {longitude}. "
                "Допустимый диапазон: [-180, 180] градусов."
            )

    @staticmethod
    def __validate_timezone(tz: str | None) -> str:
        """Проверяет, что tz — валидное имя таймзоны IANA.
        Если tz is None, возвращает значение по умолчанию 'Europe/Moscow'.
        """
        if tz is None:
            tz = "Europe/Moscow"

        try:
            ZoneInfo(tz)
        except ZoneInfoNotFoundError:
            raise InvalidTimezoneError(
                f"Invalid timezone '{tz}'. "
                "Ожидается имя из базы IANA, например 'Europe/Moscow'."
            )

        return tz

    @staticmethod
    def __validate_ymd(date_str: str) -> dt.datetime:
        """Проверяет, что дата строго в формате 'YYYY-MM-DD' и существует."""
        DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
        if not DATE_RE.match(date_str):
            raise InvalidDateFormatError(
                f"Invalid date '{date_str}'. "
                "Ожидается формат 'YYYY-MM-DD', например '2025-02-15'."
            )
        try:
            return dt.datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError as exc:
            raise InvalidDateFormatError(
                f"Invalid date '{date_str}'. "
                "Некорректный день/месяц/год."
            ) from exc


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
        self.__validate_ymd(start_date)
        if end_date is not None:
            self.__validate_ymd(end_date)
