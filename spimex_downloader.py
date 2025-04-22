import re
import os
import asyncio

import aiofiles
import aiohttp


from config import SPIMEX_URL

if not os.path.isdir("tables/"):
    os.makedirs("tables/", exist_ok=True)


class URLManager:
    """
    Класс для управления загрузкой XLS-файлов с результатами торгов с сайта Spimex.
    """

    url: str  # адрес сайта Spimex
    page_number: int  # номер страницы для загрузки
    href_pattern: re.Pattern  # регулярное выражение для поиска ссылок на XLS-файлы
    tables_hrefs: list  # список найденных ссылок на XLS-файлы
    existing_files: list  # список файлов в локальной директории 'tables/'

    def __init__(self):
        self.url = SPIMEX_URL
        self.page_number = 0
        self.href_pattern = re.compile(r"/upload/reports/oil_xls/oil_xls_202[3-6]\d*")
        self.tables_hrefs = []
        self.existing_files = os.listdir("tables/")

    async def fetch_report_links(self):
        """
        Асинхронно получает данные с сайта Spimex и возвращает список ссылок на XLS-файлы.
        """
        print("Получение данных с сайта Spimex")
        async with aiohttp.ClientSession() as session:
            while True:
                self.page_number += 1
                url = f"{self.url}?page=page-{self.page_number}"
                async with session.get(url) as response:
                    if response.status != 200:
                        break
                    data = await response.text()
                    hrefs = re.findall(self.href_pattern, data)
                    # ищем ссылки на XLS-файлы с помощью регулярного выражения
                    if hrefs:
                        for href in hrefs:
                            href = f"https://spimex.com/{href}"
                            self.tables_hrefs.append(href)
                    else:
                        break
        return self.tables_hrefs

    async def download_file(self, session, href):
        """
        Асинхронно скачивает файл по ссылке, если он еще не скачан.
        """
        filename = href[-22:] + ".xls"
        filepath = os.path.join("tables", filename)
        if filename in self.existing_files:
            return

        try:
            async with session.get(href) as response:
                if response.status == 200:
                    content = await response.read()
                    async with aiofiles.open(filepath, mode="wb") as f:
                        await f.write(content)
                else:
                    print(f"Ошибка {response.status} при скачивании {href}")
        except Exception as e:
            print(f"Ошибка при скачивании {href}: {e}")

    async def download_xls_files(self):
        """
        Асинхронно скачивает все найденные файлы.
        """
        await self.fetch_report_links()
        print("XLS-файлы скачиваются")
        async with aiohttp.ClientSession() as session:
            tasks = [self.download_file(session, href) for href in self.tables_hrefs]
            await asyncio.gather(*tasks)
