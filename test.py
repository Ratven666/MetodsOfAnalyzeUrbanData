import whether_history as wh
from whether_history import HistoryDownloader

LATITUDE = 59.93
LONGITUDE = 30.33

wind = wh.Wind(latitude=LATITUDE, longitude=LONGITUDE, timezone="Europe/Moscow")

df_jan = wind.download_whether_data(
    start_date="2025-01-01",
    end_date="2025-01-31",
)

print(df_jan.head())

# Погода (все дневные переменные)


weather_dl = HistoryDownloader(
    latitude=59.93,
    longitude=30.33,
    timezone="Europe/Moscow",
    cls=wh.Whether,
)
df_weather = weather_dl.download_history("2009-01-01", "2020-12-31", chunk_days=3650)
print(df_weather.whether_data)

# # Ветер (только ветровые переменные)
# wind_dl = HistoryDownloader(
#     latitude=59.93,
#     longitude=30.33,
#     timezone="Europe/Moscow",
#     cls=Wind,
# )
# df_wind = wind_dl.download_history("1979-01-01", "2020-12-31", chunk_days=365)
