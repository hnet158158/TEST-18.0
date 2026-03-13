# START_MODULE_CONTRACT
# Module: tests.conftest
# Intent: Pytest fixtures для тестирования Deal Tracker API.
# Предоставляет изолированную in-memory БД для каждого теста.
# END_MODULE_CONTRACT

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from app.models.base import Base
from app.models import User, Company, Deal, Activity


@event.listens_for(engine := create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    echo=False
), "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """
    # CONTRACT: Intent: Включает PRAGMA foreign_keys=ON для SQLite FK enforcement.
    """
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


@pytest.fixture
def db_engine():
    """
    [START_CONTRACT_DB_ENGINE]
    Intent: Создаёт изолированную in-memory SQLite БД для каждого теста.
    Input: Нет.
    Output: SQLAlchemy engine с созданными таблицами и включёнными FK constraints.
    [END_CONTRACT_DB_ENGINE]
    """
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session(db_engine) -> Session:
    """
    [START_CONTRACT_DB_SESSION]
    Intent: Создаёт изолированную сессию БД для каждого теста с автооткатом.
    Input: db_engine fixture.
    Output: Session с транзакцией, откатываемой после теста.
    [END_CONTRACT_DB_SESSION]
    """
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture
def sample_user(db_session) -> User:
    """
    # CONTRACT: Intent: Создаёт тестового пользователя для тестов.
    """
    user = User(email="test@example.com", name="Test User")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def sample_company(db_session) -> Company:
    """
    # CONTRACT: Intent: Создаёт тестовую компанию для тестов.
    """
    company = Company(name="Test Company", website="https://test.com", industry="Tech")
    db_session.add(company)
    db_session.commit()
    db_session.refresh(company)
    return company


@pytest.fixture
def sample_deal(db_session, sample_company, sample_user) -> Deal:
    """
    # CONTRACT: Intent: Создаёт тестовую сделку для тестов.
    """
    deal = Deal(
        title="Test Deal",
        company_id=sample_company.id,
        owner_id=sample_user.id,
        value=10000
    )
    db_session.add(deal)
    db_session.commit()
    db_session.refresh(deal)
    return deal