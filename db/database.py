from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import sessionmaker
from config import DB_HOST, DB_NAME, DB_PASS, DB_PORT, DB_USER


DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

BaseModel = declarative_base()

engine = create_async_engine(DATABASE_URL, echo=False)

AsyncSessionMaker = async_sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)


async def create_db():
    """
    Создает новую базу данных.
    """
    async with engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.create_all)


async def drop_db():
    """
    Удаляет существующую базу данных.
    """
    async with engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.drop_all)
