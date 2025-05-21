from typing import Optional

from pydantic import BaseModel, Field, field_validator


class TradingFilter(BaseModel):
    """
    Модель фильтрации торгов на основе заданных параметров.

    Атрибуты:
        oil_id (Optional[str]): Идентификатор нефти. Приводится к верхнему регистру.
        delivery_type_id (Optional[str]): Идентификатор типа поставки. Приводится к верхнему регистру.
        delivery_basis_id (Optional[str]): Идентификатор базы поставки. Приводится к верхнему регистру.

    Валидаторы:
        Преобразует строковые значения всех трёх полей к верхнему регистру перед валидацией.
    """

    oil_id: Optional[str] = Field(None, description="Oil ID")
    delivery_type_id: Optional[str] = Field(None, description="Delivery Type ID")
    delivery_basis_id: Optional[str] = Field(None, description="Delivery Basis ID")

    @field_validator("oil_id", "delivery_type_id", "delivery_basis_id", mode="before")
    @classmethod
    def to_upper(cls, value):
        if isinstance(value, str):
            return value.upper()
        return value
