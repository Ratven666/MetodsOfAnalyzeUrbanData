"""
Точка входа приложения FastAPI.

Порядок инициализации:
  1. Создаётся объект AppConfig (читает переменные среды один раз).
  2. На основе AppConfig создаётся объект FastAPI с метаданными.
  3. Подключаются роутеры.
  4. Приложение запускается uvicorn-ом.

Ключевая идея разделения конфигураций:
  - AppConfig     → читается при старте, ЗАМОРОЖЕНА на время жизни процесса.
  - RuntimeConfig → singleton, обновляется через PUT /config/runtime.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from config import AppConfig
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.config_routes import router as config_router
from routes.health import router as health_router
from routes.info import router as info_router

# 1. Инициализация статической конфигурации
app_config = AppConfig()

# 2. Создание объекта FastAPI с метаданными из статической конфигурации.
#    После этой строки изменение app_config НЕ влияет на объект FastAPI.
app = FastAPI(
    title=app_config.app_name,
    version=app_config.app_version,
    description=app_config.app_description,
    contact={
        "name": ", ".join(app_config.app_authors),
        "email": app_config.contact_email,
    },
    license_info={"name": app_config.license_name},
    openapi_tags=[
        {"name": "Health", "description": "Проверка работоспособности сервиса"},
        {"name": "Configuration", "description": "Управление конфигурацией приложения"},
        {"name": "Info", "description": "Информационные эндпоинты"},
    ],
)

# 3. Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 4. Подключение роутеров
app.include_router(health_router)
app.include_router(config_router)
app.include_router(info_router)

# 5. Демонстрация иммутабельности статической конфигурации:
#    изменение app_config после создания app НЕ меняет app.title
app_config.app_name = "CHANGED_AT_RUNTIME"
assert (
    app.title != "CHANGED_AT_RUNTIME"
), "Статическая конфигурация не должна изменять уже созданный объект FastAPI!"


# 6. События жизненного цикла
@app.on_event("startup")
async def on_startup():
    print(f"[STARTUP] Приложение '{app.title}' v{app.version} запущено.")
    print(f"[STARTUP] Документация: http://127.0.0.1:8000/docs")


@app.on_event("shutdown")
async def on_shutdown():
    print(f"[SHUTDOWN] Приложение '{app.title}' остановлено.")


# 7. Запуск через CLI: python main.py
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8000")),
        reload=os.getenv("RELOAD", "false").lower() == "true",
        log_level=os.getenv("LOG_LEVEL", "info").lower(),
    )
