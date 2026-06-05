# ЛР №9 — Контейнеризация FastAPI + PostgreSQL/PostGIS

## Добавленные файлы

| Файл | Назначение |
|---|---|
| `Dockerfile` | Многостадийная сборка API-контейнера |
| `.dockerignore` | Исключения при сборке образа |
| `docker-compose.yaml` | Оркестрация db + api сервисов |
| `.env` | Переменные окружения (не коммитить в git!) |
| `.env.example` | Шаблон переменных для документации |

## Структура docker-compose.yaml

```
services:
  db   — postgis/postgis:16-3.4, healthcheck pg_isready
  api  — собирается из Dockerfile, ждёт db healthy,
         запускает: alembic upgrade head && uvicorn ...
```

## Запуск

```bash
# Первый запуск (сборка образа)
docker compose up --build

# Последующие запуски
docker compose up -d

# Остановка (данные сохраняются в volume)
docker compose down

# Остановка с удалением данных
docker compose down -v
```

## Проверка

```bash
# Статус контейнеров
docker compose ps

# Логи API (включая вывод alembic upgrade head)
docker compose logs api

# Проверка health
curl http://127.0.0.1:8000/health
# {"status": "ok"}

# Swagger UI
# http://127.0.0.1:8000/docs
```

## Переменные окружения

| Переменная | Описание | Значение в Docker |
|---|---|---|
| `DATABASE_URL` | Строка подключения SQLAlchemy/Alembic | `...@db:5432/...` (хост = имя сервиса) |
| `POSTGRES_DB` | Имя базы данных | `urban_wind_data` |
| `POSTGRES_USER` | Пользователь PostgreSQL | `urban_user` |
| `POSTGRES_PASSWORD` | Пароль | задать в `.env` |

> **Важно:** внутри Docker Compose хост базы данных — это имя сервиса `db`,
> а не `localhost`. Строка `@db:5432/` обязательна.

## CRUD-запросы (пример)

```bash
# Создать точку наблюдений
curl -X POST http://localhost:8000/wind/points \
  -H "Content-Type: application/json" \
  -d '{"point_id":"spb_01","point_name":"СПб Залив","geom_wkt":"POINT(30.20 59.95)","shore_normal_azimuth_deg":270}'

# Список точек
curl http://localhost:8000/wind/points

# Добавить измерение (id=1)
curl -X POST http://localhost:8000/wind/points/1/measurements \
  -H "Content-Type: application/json" \
  -d '{"observed_at":"2026-06-04T08:00:00+03:00","wind_speed_ms":7.5,"wind_direction_deg":245}'

# Пространственный запрос
curl -G http://localhost:8000/wind/points/intersects \
  --data-urlencode "wkt=POLYGON((30.0 59.8, 30.5 59.8, 30.5 60.2, 30.0 60.2, 30.0 59.8))"
```
