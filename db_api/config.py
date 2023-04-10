import os

from aiogram import Bot, types
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

# Загрузка переменных окружения из файла .env
load_dotenv()

# Получение значения переменной окружения
db_host = os.getenv("DB_HOST")
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
database = os.getenv("DATABASE")

# Создание асинхронного движка SQLAlchemy для PostgreSQL
async_engine = create_async_engine(f"postgresql+asyncpg://{db_user}:{db_password}@{db_host}/{database}")

# Создание асинхронной фабрики сессий SQLAlchemy
async_session = sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False, autoflush=False)

# Создание базового класса для моделей данных
Base = declarative_base()
bot = Bot(token=os.getenv("BOT_TOKEN"), parse_mode=types.ParseMode.HTML)
