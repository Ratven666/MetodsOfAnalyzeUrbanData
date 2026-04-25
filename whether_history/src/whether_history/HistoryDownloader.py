import datetime as dt
from pathlib import Path
from typing import Optional, Type

from loguru import logger

from .whether import Whether  # или общий базовый класс для Whether/Wind


class HistoryDownloader:
    """
    Обёртка над базовыми объектами Whether/Wind.

    - Бьёт временной интервал на чанки.
    - Для каждого чанка вызывает download_whether_data() базового объекта.
    - Дубли по датам чистит сам базовый объект (через свою __add_data).
    - Может сохранять/читать объект целиком через export_whether_data/read_whether_data.
    """

    def __init__(
        self,
        latitude: float,
        longitude: float,
        timezone: str = "Europe/Moscow",
        cls: Type[Whether] = Whether,  # сюда можно подставить и Wind
    ) -> None:
        self.latitude = latitude
        self.longitude = longitude
        self.timezone = timezone
        self._cls = cls

        # Один экземпляр Whether/Wind, в который всё складывается
        self._obj = cls(latitude=latitude, longitude=longitude, timezone=timezone)

    @property
    def base_object(self) -> Whether:
        """Вернуть базовый объект (Whether/Wind) с накопленными данными."""
        return self._obj

    def _download_chunk(
        self,
        start: dt.date,
        end: dt.date,
        timeout: int,
        max_retries: int = 3,
    ) -> None:
        """
        Скачивает один чанк через базовый объект.
        Все данные попадают в self._obj.whether_data через его внутреннюю логику.
        """
        import time

        for attempt in range(1, max_retries + 1):
            try:
                logger.info(
                    "Downloading {} chunk from {} to {} (attempt {}/{})",
                    self._cls.__name__,
                    start,
                    end,
                    attempt,
                    max_retries,
                )
                df = self._obj.download_whether_data(
                    start_date=start.isoformat(),
                    end_date=end.isoformat(),
                    timeout=timeout,
                )

                # Базовая проверка полноты: число уникальных дат в чанке
                if "date" not in df.columns:
                    raise ValueError("Missing 'date' column in downloaded DataFrame")

                got = df["date"].nunique()
                expected = (end - start).days + 1
                if got != expected:
                    raise ValueError(
                        f"Incomplete data for chunk {start}–{end}: "
                        f"expected {expected} days, got {got}"
                    )

                logger.success(
                    "Successfully downloaded chunk {}–{} ({} days)",
                    start,
                    end,
                    got,
                )
                return

            except Exception as exc:  # noqa: BLE001
                logger.error(
                    "Error downloading chunk {}–{}: {}",
                    start,
                    end,
                    exc,
                )
                if attempt == max_retries:
                    logger.error(
                        "Max retries reached for chunk {}–{}. Giving up.",
                        start,
                        end,
                    )
                    raise
                time.sleep(2)

    def download_history(
        self,
        start_date: str,
        end_date: Optional[str] = None,
        chunk_days: int = 365,
        timeout: int = 120,
    ) -> Whether:
        """
        Скачивает историю для одной точки чанками и возвращает базовый объект
        (Whether/Wind) с единым DataFrame в .whether_data.
        """
        start = dt.date.fromisoformat(start_date)
        if end_date is None:
            end = dt.date.today() - dt.timedelta(days=5)
        else:
            end = dt.date.fromisoformat(end_date)

        if start > end:
            raise ValueError("start_date must be <= end_date")

        logger.info(
            "Downloading {} history for lat={}, lon={} from {} to {} "
            "with chunk size {} days",
            self._cls.__name__,
            self.latitude,
            self.longitude,
            start,
            end,
            chunk_days,
        )

        cur = start
        delta = dt.timedelta(days=chunk_days - 1)

        while cur <= end:
            chunk_start = cur
            chunk_end = min(cur + delta, end)
            self._download_chunk(
                start=chunk_start,
                end=chunk_end,
                timeout=timeout,
            )
            cur = chunk_end + dt.timedelta(days=1)

        logger.info(
            "{} history download complete: {} rows, {} unique dates",
            self._cls.__name__,
            len(self._obj.whether_data),
            (
                self._obj.whether_data["date"].nunique()
                if not self._obj.whether_data.empty
                else 0
            ),
        )
        return self._obj

    # --- Логика сохранения / загрузки через внутренние методы Whether ---

    def save(self, path: str | Path) -> Path:
        """
        Сохранить текущие данные объекта в файл.
        Формат определяется по расширению пути (csv/xlsx/json/parquet/...),
        а фактическое сохранение делает ExportWhetherFactory через
        метод self._obj.export_whether_data().
        """
        path = Path(path)
        logger.info(
            "Saving {} history to {} (rows: {})",
            self._cls.__name__,
            path,
            len(self._obj.whether_data),
        )
        result = self._obj.export_whether_data(file_path=path)
        logger.success("Saved {} history to {}", self._cls.__name__, result)
        return Path(result)

    def load(self, path: str | Path) -> None:
        """
        Прочитать данные из файла и добавить их во внутренний DataFrame
        объекта через ImportWhetherFactory и __add_data().
        """
        path = Path(path)
        logger.info("Loading {} history from {}", self._cls.__name__, path)
        df = self._obj.read_whether_data(file_path=path)
        logger.success(
            "Loaded {} history from {} (rows now: {})",
            self._cls.__name__,
            path,
            len(self._obj.whether_data),
        )
