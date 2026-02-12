


from app.wheather.open_meteo import OpenMeteoWheatherDataAggregator


# Координаты Новороссийска
LATITUDE = 44.72439
LONGITUDE = 37.76752

# Период данных (ERA5-Land доступна с 1950, обновляется с задержкой 5 дней)
START_DATE = "2026-01-01"
# START_DATE = "2025-01-01"


om = OpenMeteoWheatherDataAggregator(longitude=LONGITUDE, latitude=LATITUDE)

df = om.get_daily_data(start_date=START_DATE)

print(df)
