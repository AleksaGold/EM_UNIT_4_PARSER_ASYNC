from dotenv import load_dotenv
import os

load_dotenv()

# DataBase
DB_NAME = os.environ.get("DB_NAME")
DB_HOST = os.environ.get("DB_HOST")
DB_PORT = os.environ.get("DB_PORT")
DB_USER = os.environ.get("DB_USER")
DB_PASS = os.environ.get("DB_PASS")


# Spimex URL

SPIMEX_URL = "https://spimex.com/markets/oil_products/trades/results/"
SPIMEX_TABLE_NAME = "Единица измерения: Метрическая тонна"
