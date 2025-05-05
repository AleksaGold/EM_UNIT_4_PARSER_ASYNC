import asyncio
from time import time

from db.database import async_session_maker, create_db, drop_db
from parser.spimex_downloader import URLManager
from parser.spimex_parser import process_all_files_in_folder


async def main():
    """
    Основная асинхронная функция для обработки данных торгов Spimex.

    Выполняет последовательно следующие операции:
    1. Удаляет существующую базу данных (если есть)
    2. Создает новую базу данных
    3. Загружает XLS-файлы с результатами торгов с сайта Spimex
    4. Обрабатывает все загруженные файлы из папки 'tables' и сохраняет данные в БД
    5. Замеряет и выводит общее время выполнения
    """

    start_time = time()

    await drop_db()
    await create_db()
    print("База данных создана")

    # Загружаем XLS-файлы с результатами торгов с сайта Spimex

    manager = URLManager()
    await manager.download_xls_files()

    # Обрабатываем все файлы в папке tables

    async with async_session_maker() as session:
        await process_all_files_in_folder("tables", session)

    print("Обработка всех файлов завершена")

    elapsed_time = time() - start_time
    print(f"Время выполнения: {elapsed_time} сек")


if __name__ == "__main__":
    asyncio.run(main())
