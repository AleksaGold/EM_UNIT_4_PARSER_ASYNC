from datetime import date
from typing import AsyncGenerator

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (AsyncSession, async_sessionmaker,
                                    create_async_engine)

from app.main import app
from db.database import DATABASE_URL, BaseModel
from db.db_depends import get_db
from db.model import SpimexTradingResults


@pytest_asyncio.fixture(scope="function")
async def test_engine():
    """
    Создаёт и возвращает тестовый асинхронный движок SQLAlchemy.

    Перед выполнением теста:
    - проверяет, что используется тестовая БД;
    - удаляет и создаёт все таблицы.

    После теста:
    - снова удаляет все таблицы;
    - освобождает ресурсы движка.
    """
    assert DATABASE_URL.endswith("_test")
    engine = create_async_engine(DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.drop_all)
        await conn.run_sync(BaseModel.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def test_sessionmaker(test_engine):
    """
    Возвращает асинхронный sessionmaker, связанный с тестовым движком.
    Используется для создания сессий БД в тестах.
    """
    return async_sessionmaker(test_engine, expire_on_commit=False)


@pytest_asyncio.fixture(scope="function")
async def db_session(test_sessionmaker) -> AsyncGenerator[AsyncSession, None]:
    """
    Возвращает асинхронную сессию БД.
    Используется в тестах для выполнения запросов к тестовой БД.
    """
    async with test_sessionmaker() as session:
        yield session


@pytest_asyncio.fixture(scope="function")
async def filled_spimex_data(db_session: AsyncSession):
    """
    Заполняет тестовую БД двумя записями SpimexTradingResults.
    Предоставляет сессию с предзаполненными данными.
    """
    test_data = [
        SpimexTradingResults(
            exchange_product_id="1001",
            exchange_product_name="Дизель",
            oil_id="OIL_1",
            delivery_basis_id="db_1",
            delivery_basis_name="СПб",
            delivery_type_id="dt_1",
            volume="100.5",
            total="100000",
            count=3,
            date=date(2024, 5, 1),
        ),
        SpimexTradingResults(
            exchange_product_id="1002",
            exchange_product_name="Бензин",
            oil_id="OIL_2",
            delivery_basis_id="db_2",
            delivery_basis_name="Москва",
            delivery_type_id="dt_2",
            volume="200.0",
            total="200000",
            count=5,
            date=date(2024, 5, 2),
        ),
    ]
    db_session.add_all(test_data)
    await db_session.commit()
    yield db_session


@pytest_asyncio.fixture(scope="function")
async def async_client(db_session: AsyncSession):
    """
    Создаёт асинхронный HTTP-клиент с переопределением зависимости get_db.
    Клиент используется для тестирования HTTP-эндпоинтов FastAPI с доступом к тестовой БД.
    """

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client
    app.dependency_overrides.clear()
