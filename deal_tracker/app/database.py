# START_MODULE_CONTRACT
# Module: database
# Intent: Конфигурация SQLAlchemy для синхронного SQLite.
# Предоставляет engine, SessionLocal, get_db dependency и create_tables.
# END_MODULE_CONTRACT

from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.config import settings

# START_BLOCK_ENGINE
# SQLite sync engine с check_same_thread=False для FastAPI
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False},
    echo=settings.debug
)
# END_BLOCK_ENGINE

# START_BLOCK_SESSION
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)
# END_BLOCK_SESSION


def get_db() -> Generator[Session, None, None]:
    """
    [START_CONTRACT_GET_DB]
    Intent: Dependency injection для FastAPI. Создаёт и закрывает сессию БД.
    Input: Нет.
    Output: Generator, yield Session, гарантированно закрывает сессию.
    [END_CONTRACT_GET_DB]
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables() -> None:
    """
    [START_CONTRACT_CREATE_TABLES]
    Intent: Инициализация схемы БД. Создаёт все таблицы из моделей.
    Input: Нет.
    Output: Все таблицы созданы в БД. Idempotent.
    [END_CONTRACT_CREATE_TABLES]
    """
    from app.models.base import Base
    from app.models import User, Company, Deal, Activity
    
    Base.metadata.create_all(bind=engine)