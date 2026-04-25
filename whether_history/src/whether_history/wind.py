from .data_aggregator.open_meteo import OpenMeteoWindDataAggregator
from .whether import Whether


class Wind(Whether):

    def __init__(
        self,
        latitude: float,
        longitude: float,
        timezone: str = "Europe/Moscow",
        data_aggregator=OpenMeteoWindDataAggregator,
    ):
        """
        Класс для работы с данными о ветре

        Args:
            latitude (float): Широта точки в координатах WGS84.
            longitude (float): Долгота точки в координатах WGS84.
            timezone (str, optional): Часовой пояс для агрегации суточных данных.
                Любое имя из базы IANA, по умолчанию 'Europe/Moscow'.
            data_aggregator (DataAggregatorABC): Класс для получения погодных данных с конкретного ресурса
        """
        super().__init__(
            latitude=latitude,
            longitude=longitude,
            timezone=timezone,
            data_aggregator=data_aggregator,
        )


if __name__ == "__main__":
    # Координаты Санкт-Петербурга
    LATITUDE = 59.93
    LONGITUDE = 30.33

    wind = Wind(latitude=LATITUDE, longitude=LONGITUDE, timezone="Europe/Moscow")

    df_jan = wind.download_whether_data(
        start_date="2025-01-01",
        end_date="2025-01-31",
    )
    print(df_jan.head())
