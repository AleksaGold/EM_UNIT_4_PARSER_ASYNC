from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi_cache.decorator import cache
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.schema import TradingFilter
from app.services import seconds_until_14_11
from db.db_depends import get_db
from db.model import SpimexTradingResults

router = APIRouter(prefix="/tradings", tags=["trading"])


@router.get("/last-trading-dates")
@cache(expire=seconds_until_14_11())
async def get_last_trading_dates(
    db: Annotated[AsyncSession, Depends(get_db)], limit: int = Query(10, ge=1, le=100)
):
    """
    Получение списка последних торговых дат.

    Возвращает уникальные даты торгов, отсортированные по убыванию, с ограничением по количеству.

    Args:
        db (AsyncSession): Асинхронная сессия для работы с базой данных.
        limit (int): Максимальное количество дат в ответе (от 1 до 100).

    Returns:
        List[date]: Список последних уникальных дат торгов.
    """
    result = await db.scalars(
        select(SpimexTradingResults.date)
        .distinct()
        .order_by(SpimexTradingResults.date.desc())
        .limit(limit)
    )

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nothing found for your request",
        )

    return {trading_date for trading_date in result.all()}


@router.get("/dynamics")
@cache(expire=seconds_until_14_11())
async def get_dynamics(
    db: Annotated[AsyncSession, Depends(get_db)],
    start_date: date,
    end_date: date,
    filters: TradingFilter = Depends(),
):
    """
    Получение списка торгов за заданный период с возможной фильтрацией по параметрам.

    Возвращает отсортированный по дате список торгов, попадающих в диапазон от `start_date` до `end_date`,
    с дополнительной фильтрацией по `oil_id`, `delivery_type_id` и `delivery_basis_id`, если они указаны.

    Args:
        db (AsyncSession): Асинхронная сессия базы данных.
        start_date (date): Начальная дата фильтрации (включительно).
        end_date (date): Конечная дата фильтрации (включительно).
        filters (TradingFilter): Дополнительные параметры фильтрации по id продукта, типу и базе доставки.

    Returns:
        List[SpimexTradingResults]: Список торгов, соответствующих условиям фильтрации.
    """
    query = select(SpimexTradingResults).where(
        SpimexTradingResults.date.between(start_date, end_date)
    )

    if filters.oil_id:
        query = query.where(SpimexTradingResults.oil_id == filters.oil_id)

    if filters.delivery_type_id:
        query = query.where(
            SpimexTradingResults.delivery_type_id == filters.delivery_type_id
        )

    if filters.delivery_basis_id:
        query = query.where(
            SpimexTradingResults.delivery_basis_id == filters.delivery_basis_id
        )

    result = await db.scalars(query.order_by(SpimexTradingResults.date))

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nothing found for your request",
        )

    return result.all()


@router.get("/trading-results")
@cache(expire=seconds_until_14_11())
async def get_trading_results(
    db: Annotated[AsyncSession, Depends(get_db)],
    filters: TradingFilter = Depends(),
    limit: int = Query(10, ge=1),
):
    """
    Получение списка последних торгов с возможной фильтрацией по параметрам.

    Возвращает отсортированный по дате список торгов (ограниченный параметром `limit`).
    Доступна фильтрация по `oil_id`, `delivery_type_id`, `delivery_basis_id`.

    Args:
        db (AsyncSession): Асинхронная сессия БД, предоставляемая зависимостью.
        filters (TradingFilter): Параметры фильтрации, передаются через query-параметры.
        limit (int): Максимальное количество записей в ответе (по умолчанию 10).

    Returns:
        List[SpimexTradingResults]: Список объектов торгов, соответствующих фильтрам.
    """

    query = select(SpimexTradingResults)

    if filters.oil_id:
        query = query.where(SpimexTradingResults.oil_id == filters.oil_id)

    if filters.delivery_type_id:
        query = query.where(
            SpimexTradingResults.delivery_type_id == filters.delivery_type_id
        )

    if filters.delivery_basis_id:
        query = query.where(
            SpimexTradingResults.delivery_basis_id == filters.delivery_basis_id
        )

    result = await db.scalars(
        query.order_by(SpimexTradingResults.date.desc()).limit(limit)
    )

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nothing found for your request",
        )

    return result.all()
