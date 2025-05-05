from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from db.database import async_session_maker


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Асинхронный генератор зависимости FastAPI для получения сессии базы данных.

    Использует асинхронный контекстный менеджер `async_session_maker`
    для создания и автоматического закрытия сессии SQLAlchemy после использования.

    Returns:
        AsyncGenerator[AsyncSession, None]: Асинхронная сессия базы данных, используемая в маршрутах и сервисах.
    """
    async with async_session_maker() as session:
        yield session
