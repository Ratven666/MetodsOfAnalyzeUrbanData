"""
Точка входа FastAPI-приложения

Порядок инициализации:
  1. lifespan создаёт DependencyContainer через init_dependencies().
  2. Контейнер сохраняется в app.state.deps — единственное место хранения.
  3. Функции-провайдеры (dependencies.py) достают объекты из контейнера
     через Depends в маршрутах.
  4. CRUD-маршруты для ветровых точек используют get_db() напрямую
     (сессия SQLAlchemy на запрос), не через DependencyContainer.

Запуск:
    uvicorn fastapi_wheather_lab.main:app --reload

Документация:
    http://127.0.0.1:8000/docs
"""

from __future__ import annotations

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from fastapi_wheather_lab.init_dependencies import init_dependencies
from fastapi_wheather_lab.routes.config import router as config_router
from fastapi_wheather_lab.routes.wind import router as wind_router_legacy
from fastapi_wheather_lab.wind_points.router import router as wind_points_crud_router
from fastapi_wheather_lab.schemas.app_config import AppConfigModel


@asynccontextmanager
async def lifespan(app: FastAPI):
    deps = init_dependencies()
    app.state.deps = deps

    app_cfg: AppConfigModel = deps.get_dep("app_config", AppConfigModel)
    print(f"\n[STARTUP] {app_cfg.app_name!r} v{app_cfg.app_version} запущено.")
    print("[STARTUP] Приложение готово к работе с множеством точек.")
    print("[STARTUP] Документация: http://127.0.0.1:8000/docs")
    print(f"[STARTUP] Контейнер зависимостей: {deps}\n")

    yield

    print(f"\n[SHUTDOWN] {app_cfg.app_name!r} остановлено.")


_startup_cfg = AppConfigModel()

app = FastAPI(
    lifespan=lifespan,
    title=_startup_cfg.app_name,
    version=_startup_cfg.app_version,
    description=_startup_cfg.app_description,
    contact={
        "name": ", ".join(_startup_cfg.app_authors),
        "email": _startup_cfg.contact_email,
    },
    openapi_tags=[
        {
            "name": "configuration",
            "description": "Управление статической и runtime-конфигурацией приложения",
        },
        {
            "name": "wind-research",
            "description": (
                "Точки наблюдений ветра и измерения скорости/направления. "
                "Полный CRUD через /wind/points, пространственные запросы "
                "/wind/points/intersects и /wind/points/near."
            ),
        },
    ],
)

_startup_cfg.app_name = "CHANGED_AFTER_INIT"
assert app.title != "CHANGED_AFTER_INIT"

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/docs")


@app.get("/ping", tags=["configuration"], summary="Пинг сервера")
async def ping() -> str:
    return "pong"


# ── роутеры ───────────────────────────────────────────────────────────────────
app.include_router(config_router)          # /health, /config/app, /config/runtime
app.include_router(wind_router_legacy)     # /wind/points (deprecated), /wind/measurements (deprecated)
app.include_router(wind_points_crud_router)  # /wind/points CRUD + /wind/points/{id}/measurements


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "fastapi_wheather_lab.main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8000")),
        reload=os.getenv("RELOAD", "true").lower() == "true",
        log_level=os.getenv("LOG_LEVEL", "info").lower(),
    )
