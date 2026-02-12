import requests
import pandas as pd
from datetime import datetime, timedelta

from app.wheather.config import DAILY_VARIABLES


class OpenMeteoWheatherDataAggregator:

    def __init__(self, latitude, longitude, timezone="Europe/Moscow", daily_variables=DAILY_VARIABLES):
        self.latitude = latitude
        self.longitude = longitude
        self.timezone = timezone
        self.daily_variables = daily_variables
        
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
            end_date = (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d")
        params = self.__get_params(start_date=start_date, end_date=end_date)
        response = requests.get(
                                "https://archive-api.open-meteo.com/v1/archive",
                                params=params,
                                timeout=timeout  # 2 минуты таймаут для большого запроса
                                )
        response.raise_for_status()
        data = response.json()
        return data
    
    def get_daily_data(self, start_date, end_date=None, timeout=120):
        data_json = self._get_daily_data_json(start_date, end_date=end_date, timeout=timeout)
        daily_data = data_json['daily']
        df = pd.DataFrame({
            'date': pd.to_datetime(daily_data['time']),
            **{var: daily_data[var] for var in self.daily_variables}
        })
        # Добавление полезных производных переменных
        df['year'] = df['date'].dt.year
        df['month'] = df['date'].dt.month
        df['day_of_year'] = df['date'].dt.dayofyear
        df['temperature_2m_mean'] = (df['temperature_2m_max'] + df['temperature_2m_min']) / 2
        return df
