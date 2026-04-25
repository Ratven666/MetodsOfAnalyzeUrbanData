"""
Эндпоинт проверки работоспособности.
"""

from fastapi import APIRouter

router = APIRouter(tags=["Health"])


@router.get(
    "/health",
    summary="Проверка работоспособности",
    description="Возвращает статус приложения. Используется для мониторинга.",
)
async def health_check():
    """
    Возвращает {"status": "ok"}, если приложение запущено и отвечает на запросы.
    """
    return {"status": "ok"}
