import datetime as dt
from typing import Optional

import requests
import pandas as pd

from .BaseDataAggregator import BaseDataAggregator


class OpenMeteoWhetherDataAggregator(BaseDataAggregator):
    # Все 18 доступных дневных переменных
    daily_variables = [
        # Температура
        "temperature_2m_max",
        "temperature_2m_min",
        "apparent_temperature_max",
        "apparent_temperature_min",

        # Осадки
        "precipitation_sum",
        "rain_sum",
        "snowfall_sum",
        "precipitation_hours",

        # Ветер
        "wind_speed_10m_max",
        "wind_gusts_10m_max",
        "wind_direction_10m_dominant",

        # Солнце
        "sunrise",
        "sunset",
        "sunshine_duration",
        "daylight_duration",
        "shortwave_radiation_sum",

        # Прочее
        "et0_fao_evapotranspiration",
        "weather_code",
    ]

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
        super().__init__(latitude, longitude, timezone)
        
        
    def __get_params(self, start_date, end_date):
        params = {
                    "latitude": self.latitude,
                    "longitude": self.longitude,
                    "start_date": start_date,
                    "end_date": end_date,
                    "daily": ",".join(self.daily_variables),
                    "models": "era5_seamless",  # Комбинирует ERA5-Land 0.1° + ERA5 0.25°
                    "timezone": self.timezone  # UTC+3 для корректного дневного агрегирования
                 }
        return params
    
    def _get_daily_data_json(self, start_date, end_date=None, timeout=120):
        if not end_date:
            end_date = (dt.datetime.now() - dt.timedelta(days=5)).strftime("%Y-%m-%d")
        params = self.__get_params(start_date=start_date, end_date=end_date)
        response = requests.get(
                                "https://archive-api.open-meteo.com/v1/archive",
                                params=params,
                                timeout=timeout  # 2 минуты таймаут для большого запроса
                                )
        response.raise_for_status()
        data = response.json()
        return data
    
    def get_daily_data(self,
                       start_date: dt.date | dt.datetime | str,
                       end_date: Optional[dt.date | dt.datetime | str] = None,
                       timeout: int = 120,
                       ) -> pd.DataFrame:
        """Получить ежедневные метеоданные в виде DataFrame.

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
        super().get_daily_data(start_date, end_date)
        data_json = self._get_daily_data_json(
            start_date,
            end_date=end_date,
            timeout=timeout,
        )
        daily_data = data_json["daily"]

        df = pd.DataFrame(
            {
                "date": pd.to_datetime(daily_data["time"]),
                **{var: daily_data[var] for var in self.daily_variables},
            }
        )

        # Добавление полезных производных переменных
        df["year"] = df["date"].dt.year
        df["month"] = df["date"].dt.month
        df["day_of_year"] = df["date"].dt.dayofyear

        return df


