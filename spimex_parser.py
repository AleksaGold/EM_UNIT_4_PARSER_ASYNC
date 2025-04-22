import asyncio
import os
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from xlrd import open_workbook

from config import SPIMEX_TABLE_NAME
from db.model import SpimexTradingResults


def read_table_by_name(sheet, table_name):
    """
    Читает таблицу, находящуюся между указанным названием и строкой "Итого"
    :param sheet: лист Excel
    :param table_name: название таблицы для поиска
    :return: найденная таблица (список строк) или None
    """
    table_data = []
    found_table = False

    for row_idx in range(sheet.nrows):
        row_values = sheet.row_values(row_idx)

        # Проверяем, содержит ли строка название таблицы
        if table_name in row_values:
            found_table = True
            continue

        # Проверяем, содержит ли строка "Итого" (в любом месте строки)
        if found_table and any(
            isinstance(cell, str) and "Итого" in cell for cell in row_values
        ):
            break

        # Если нашли название и это не пустая строка
        if found_table and any(row_values):
            table_data.append(row_values)

    return table_data if table_data else None


def filter_by_column_number(table_data, column_num, condition=lambda x: x > 0):
    """
    Фильтрует таблицу по номеру столбца (начиная с 0)
    :param table_data: исходная таблица
    :param column_num: номер столбца
    :param condition: условие фильтрации (по умолчанию x > 0)
    :return: отфильтрованная таблица
    """
    if not table_data:
        return []

    # Проверяем что столбец существует
    if column_num >= len(table_data[0]):
        print(f"Ошибка: в таблице только {len(table_data[0])} столбцов")
        return []

    filtered = [table_data[0]]  # Сохраняем заголовки

    for row in table_data[1:]:
        try:
            value = float(row[column_num]) if str(row[column_num]).strip() else 0
            if condition(value):
                filtered.append(row)
        except (ValueError, TypeError):
            continue  # Пропускаем некорректные данные

    return filtered


async def save_to_db(data, path, session: AsyncSession):
    """
    Асинхронно сохраняет данные о торгах в БД
    :param data: список строк для сохранения
    :param path: имя файла для формирования даты
    :param session: сессия для работы с БД
    """

    date_str = "{0}.{1}.{2}".format(path[-12:-10], path[-14:-12], path[-18:-14])

    for row in data[1:]:  # Пропускаем заголовок
        try:
            exchange_product_id = str(row[1])
            exchange_product_name = str(row[2])
            delivery_basis_name = str(row[3])
            volume = str(row[5])
            total = str(row[6])
            count = int(float(row[14]))

            oil_id = str(exchange_product_id)[:4]
            delivery_basis_id = str(exchange_product_id)[4:7]
            delivery_type_id = str(exchange_product_id)[-1]

            new_entry = SpimexTradingResults(
                exchange_product_id=exchange_product_id,
                exchange_product_name=exchange_product_name,
                oil_id=oil_id,
                delivery_basis_id=delivery_basis_id,
                delivery_basis_name=delivery_basis_name,
                delivery_type_id=delivery_type_id,
                volume=volume,
                total=total,
                count=count,
                date=datetime.strptime(date_str, "%d.%m.%Y").date(),
            )

            session.add(new_entry)

        except Exception as e:
            print(f"Ошибка при добавлении строки: {e}")

    await session.commit()


async def process_file(file_path, session):
    """
    Асинхронно обрабатывает один XLS-файл
    :param file_path: путь к файлу
    :param session: сессия для работы с БД
    """
    try:
        workbook = await asyncio.to_thread(
            open_workbook, file_path, formatting_info=True
        )
        sheet = workbook.sheet_by_index(0)

        # Извлекаем таблицу по названию
        sales_table = read_table_by_name(sheet, SPIMEX_TABLE_NAME)

        if sales_table:

            # Фильтруем по количеству договоров
            filtered = filter_by_column_number(sales_table, 14)

            # Сохраняем данные в БД
            await save_to_db(filtered, file_path, session)

    except Exception as e:
        print(f"Ошибка при обработке файла {os.path.basename(file_path)}: {e}")


async def process_all_files_in_folder(folder_path, session):
    """
    Асинхронно обрабатывает все XLS-файлы в указанной папке
    :param folder_path: путь к папке с файлами
    :param session: сессия для работы с БД
    """
    for filename in os.listdir(folder_path):
        if filename.endswith(".xls") or filename.endswith(".xlsx"):
            file_path = os.path.join(folder_path, filename)
            await process_file(file_path, session)
