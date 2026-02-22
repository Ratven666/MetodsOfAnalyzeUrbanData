# MetodsOfAnalyzeUrbanData — HW3: Библиотека `whether`

![Красивая картинка](img/head_img.jpg)

---

Библиотека `whether` — учебный Python‑пакет для работы с суточными метеоданными.  


Рещаемая задача: загрузка данных погоды из API Open‑Meteo, объединение, сохранение в файлы и базовый анализ (статистика).

---

## Структура проекта

```text
MetodsOfAnalyzeUrbanData/
├── example/
│   └── demo_whether.ipynb      # демонстрационный Jupyter-ноутбук
├── src/
│   └── whether/
│       ├── __init__.py         # публичный API: класс Whether
│       ├── exeptions.py        # пользовательские исключения
│       ├── whether.py          # фасадный класс для работы с погодой
│       ├── data_aggregator/
│       │   ├── __init__.py
│       │   ├── BaseDataAggregator.py  # базовый агрегатор + валидация
│       │   └── open_meteo.py         # OpenMeteoWhetherDataAggregator
│       └── import_export/
│           ├── __init__.py
│           ├── exporters.py    # экспортёры + ExportWhetherFactory
│           └── importers.py    # импортёры + ImportWhetherFactory
├── .gitignore
├── .pre-commit-config.yaml
├── README.md
└── requirements.txt
```

---

## Установка

Рекомендуемый способ — через виртуальное окружение.

```bash
git clone https://github.com/Ratven666/MetodsOfAnalyzeUrbanData.git
cd MetodsOfAnalyzeUrbanData
git checkout home_works/HW3

python3.12 -m venv .venv
source .venv/bin/activate      # macOS / Linux
# .venv\Scripts\activate       # Windows

pip install -r requirements.txt
```

При желании можно установить пакет в editable‑режиме:

```bash
pip install -e .
```

После этого модуль `whether` будет доступен из любых скриптов в этом окружении.

---

## Быстрый старт

Пример работы приведён для координат Санкт‑Петербурга.

```python
from whether import Whether

LATITUDE = 59.93
LONGITUDE = 30.33

weather = Whether(latitude=LATITUDE, longitude=LONGITUDE, timezone="Europe/Moscow")
```

### Загрузка данных из Open‑Meteo

```python
# Январь 2025
df_jan = weather.download_whether_data(
    start_date="2025-01-01",
    end_date="2025-01-31",
)

# Февраль 2025
df_feb = weather.download_whether_data(
    start_date="2025-02-01",
    end_date="2025-02-28",
)

# Объединённые данные
weather.whether_data.head()
```

Особенности:

- `date` нормализуется к формату `YYYY-MM-DD`;
- новые данные добавляются во внутренний датафрейм `whether_data`;
- дубликаты по дате автоматически удаляются.

---

## Импорт и экспорт данных

Для работы с файлами используются фабрики:

- `ExportWhetherFactory` — выбирает экспортёр по расширению файла;
- `ImportWhetherFactory` — выбирает импортёр по типу входных данных.

### Экспорт

```python
# Экспорт в CSV
weather.export_whether_data("weather_spb.csv")

# Экспорт в Excel
weather.export_whether_data("weather_spb.xlsx")

# Экспорт в JSON (tabular, orient="records")
weather.export_whether_data("weather_spb.json")
```

Поддерживаемые форматы:

- `.csv` — табличный CSV;
- `.xlsx` / `.xls` — Excel;
- `.json` — JSON‑список записей.

### Импорт

```python
from whether import Whether

weather_from_files = Whether(latitude=LATITUDE, longitude=LONGITUDE)

# Читаем CSV
weather_from_files.read_whether_data("weather_spb.csv")

# Дочитываем Excel — дубликаты по дате не появятся
weather_from_files.read_whether_data("weather_spb.xlsx")

weather_from_files.whether_data.head()
```

---

## Валидация и пользовательские исключения

В модуле `exeptions.py` определены собственные исключения:

- `InvalidCoordinateError` — некорректные координаты WGS84  
  (широта не в `[-90, 90]`, долгота не в `[-180, 180]`).
- `InvalidTimezoneError` — неверное имя часового пояса IANA  
  (например, `"Moscow"` вместо `"Europe/Moscow"`).
- `InvalidDateFormatError` — некорректный формат/значение даты  
  (строго `'YYYY-MM-DD'`, дополнительно проверяется, что дата существует).

Базовый агрегатор (`BaseDataAggregator`) проверяет координаты, таймзону и даты до обращения к внешнему API и выбрасывает эти исключения при ошибках.

---

## Описательная статистика

Класс `Whether` предоставляет метод:

```python
stats_df = weather.get_statistic_df()
print(stats_df)
```

Это обёртка над `DataFrame.describe()` для внутренних погодных данных — можно быстро посмотреть распределения температур, осадков, ветров и т.п.

---

## Логирование

Библиотека использует `loguru`:

- логирует инициализацию объекта `Whether`;
- загрузку данных из API (диапазон дат, размер датафрейма);
- обновление внутреннего датафрейма и количество новых уникальных дат;
- операции импорта/экспорта;
- расчёт статистики.

Пример настройки логгера в ноутбуке:

```python
from loguru import logger
import sys

logger.remove()
logger.add(sys.stderr, format="{time:HH:mm:ss} | {level} | {message}")
```

---

## Демонстрационный ноутбук

```text
example/demo_whether.ipynb
```

Файл `example/demo_whether.ipynb` показывает:

- корректный импорт пакета `whether`;
- создание объекта `Whether`;
- загрузку данных за несколько периодов;
- экспорт/импорт в CSV, Excel и JSON;
- автоматическое устранение дублей по дате;
- получение описательной статистики;
- построение графиков температур;
- пример обработки ошибки при отсутствии колонки `date`.

---

## Контроль качества кода

В репозитории настроен `pre-commit`:

- `black` — автоформатирование кода;
- `isort` — сортировка импортов;
- базовые хуки (`trailing-whitespace`, `end-of-file-fixer` и т.п.).

Установка и запуск:

```bash
pip install pre-commit black isort
pre-commit install
pre-commit run --all-files
```

Версия интерпретатора для хуков указана в `.pre-commit-config.yaml` (Python 3.12).

---

## Назначение

Репозиторий используется как учебный пример для лабораторной работы по курсу «Методы анализа геоинформационных данных» и демонстрирует:

- проектирование модульной библиотеки;
- работу с внешним API;
- типизацию, обработку ошибок и логирование;
- автоматизацию форматирования и проверок кода.
```
