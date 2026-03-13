# START_MODULE_CONTRACT
# Module: tests.test_phase1_models
# Intent: Тесты для Phase 1 - Models & Database.
# Проверяет модели, FK constraints, enum значения, create_tables.
# END_MODULE_CONTRACT

import pytest
import uuid
from decimal import Decimal
from sqlalchemy import inspect, text, event
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy.engine import Engine

from app.models.base import Base
from app.models import User, Company, Deal, Activity, DealStage, ActivityType
from app.database import create_tables, engine


# Включаем foreign key enforcement для SQLite
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Включает PRAGMA foreign_keys=ON для SQLite."""
    if "sqlite" in str(dbapi_connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


class TestModelImports:
    """Проверка импорта моделей без ошибок."""
    
    def test_import_base(self):
        """Base класс импортируется."""
        assert Base is not None
    
    def test_import_user(self):
        """User модель импортируется."""
        assert User is not None
    
    def test_import_company(self):
        """Company модель импортируется."""
        assert Company is not None
    
    def test_import_deal(self):
        """Deal модель импортируется."""
        assert Deal is not None
    
    def test_import_activity(self):
        """Activity модель импортируется."""
        assert Activity is not None
    
    def test_import_deal_stage_enum(self):
        """DealStage enum импортируется."""
        assert DealStage is not None
    
    def test_import_activity_type_enum(self):
        """ActivityType enum импортируется."""
        assert ActivityType is not None


class TestDealStageEnum:
    """Проверка enum DealStage."""
    
    def test_deal_stage_has_lead(self):
        """DealStage содержит LEAD."""
        assert DealStage.LEAD.value == "lead"
    
    def test_deal_stage_has_qualified(self):
        """DealStage содержит QUALIFIED."""
        assert DealStage.QUALIFIED.value == "qualified"
    
    def test_deal_stage_has_proposal(self):
        """DealStage содержит PROPOSAL."""
        assert DealStage.PROPOSAL.value == "proposal"
    
    def test_deal_stage_has_negotiation(self):
        """DealStage содержит NEGOTIATION."""
        assert DealStage.NEGOTIATION.value == "negotiation"
    
    def test_deal_stage_has_won(self):
        """DealStage содержит WON."""
        assert DealStage.WON.value == "won"
    
    def test_deal_stage_has_lost(self):
        """DealStage содержит LOST."""
        assert DealStage.LOST.value == "lost"
    
    def test_deal_stage_count(self):
        """DealStage содержит ровно 6 значений."""
        assert len(DealStage) == 6


class TestActivityTypeEnum:
    """Проверка enum ActivityType."""
    
    def test_activity_type_has_call(self):
        """ActivityType содержит CALL."""
        assert ActivityType.CALL.value == "call"
    
    def test_activity_type_has_email(self):
        """ActivityType содержит EMAIL."""
        assert ActivityType.EMAIL.value == "email"
    
    def test_activity_type_has_meeting(self):
        """ActivityType содержит MEETING."""
        assert ActivityType.MEETING.value == "meeting"
    
    def test_activity_type_has_note(self):
        """ActivityType содержит NOTE."""
        assert ActivityType.NOTE.value == "note"
    
    def test_activity_type_count(self):
        """ActivityType содержит ровно 4 значения."""
        assert len(ActivityType) == 4


class TestTableCreation:
    """Проверка создания таблиц."""
    
    def test_create_tables_creates_all_tables(self, db_engine):
        """create_tables создаёт все 4 таблицы."""
        inspector = inspect(db_engine)
        table_names = inspector.get_table_names()
        
        assert "users" in table_names, "Таблица users не создана"
        assert "companies" in table_names, "Таблица companies не создана"
        assert "deals" in table_names, "Таблица deals не создана"
        assert "activities" in table_names, "Таблица activities не создана"
    
    def test_users_table_columns(self, db_engine):
        """Таблица users имеет корректные колонки."""
        inspector = inspect(db_engine)
        columns = {col["name"] for col in inspector.get_columns("users")}
        
        assert "id" in columns
        assert "email" in columns
        assert "name" in columns
        assert "created_at" in columns
        assert "updated_at" in columns
    
    def test_companies_table_columns(self, db_engine):
        """Таблица companies имеет корректные колонки."""
        inspector = inspect(db_engine)
        columns = {col["name"] for col in inspector.get_columns("companies")}
        
        assert "id" in columns
        assert "name" in columns
        assert "website" in columns
        assert "industry" in columns
        assert "created_at" in columns
        assert "updated_at" in columns
    
    def test_deals_table_columns(self, db_engine):
        """Таблица deals имеет корректные колонки."""
        inspector = inspect(db_engine)
        columns = {col["name"] for col in inspector.get_columns("deals")}
        
        assert "id" in columns
        assert "title" in columns
        assert "company_id" in columns
        assert "owner_id" in columns
        assert "stage" in columns
        assert "value" in columns
        assert "description" in columns
        assert "created_at" in columns
        assert "updated_at" in columns
    
    def test_activities_table_columns(self, db_engine):
        """Таблица activities имеет корректные колонки."""
        inspector = inspect(db_engine)
        columns = {col["name"] for col in inspector.get_columns("activities")}
        
        assert "id" in columns
        assert "deal_id" in columns
        assert "type" in columns
        assert "description" in columns
        assert "created_at" in columns
        # activities НЕ имеет updated_at (immutable)


class TestForeignKeyConstraints:
    """Проверка FK constraints с RESTRICT."""
    
    def test_deal_company_id_fk_on_delete_restrict(self, db_session, sample_user):
        """FK company_id в deals настроен с RESTRICT."""
        # Создаём компанию и сделку
        company = Company(name="Test Company")
        db_session.add(company)
        db_session.commit()
        db_session.refresh(company)
        
        deal = Deal(title="Test Deal", company_id=company.id, owner_id=sample_user.id)
        db_session.add(deal)
        db_session.commit()
        
        # Попытка удалить компанию со связанной сделкой должна вызвать ошибку
        db_session.delete(company)
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    def test_deal_owner_id_fk_on_delete_restrict(self, db_session, sample_company):
        """FK owner_id в deals настроен с RESTRICT."""
        # Создаём пользователя и сделку
        user = User(email="owner@test.com", name="Owner")
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        deal = Deal(title="Test Deal", company_id=sample_company.id, owner_id=user.id)
        db_session.add(deal)
        db_session.commit()
        
        # Попытка удалить пользователя со связанной сделкой должна вызвать ошибку
        db_session.delete(user)
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    def test_activity_deal_id_fk_on_delete_restrict(self, db_session, sample_deal):
        """FK deal_id в activities настроен с RESTRICT."""
        # Создаём активность
        activity = Activity(deal_id=sample_deal.id, type=ActivityType.NOTE, description="Test")
        db_session.add(activity)
        db_session.commit()
        
        # Попытка удалить сделку со связанной активностью должна вызвать ошибку
        db_session.delete(sample_deal)
        with pytest.raises(IntegrityError):
            db_session.commit()


class TestUserModel:
    """Проверка модели User."""
    
    def test_user_creation(self, db_session):
        """User создаётся с корректными полями."""
        user = User(email="test@example.com", name="Test User")
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        assert user.id is not None
        assert isinstance(user.id, uuid.UUID)
        assert user.email == "test@example.com"
        assert user.name == "Test User"
        assert user.created_at is not None
        assert user.updated_at is not None
    
    def test_user_email_unique(self, db_session):
        """Email пользователя должен быть уникальным."""
        user1 = User(email="same@example.com", name="User 1")
        user2 = User(email="same@example.com", name="User 2")
        db_session.add(user1)
        db_session.commit()
        
        db_session.add(user2)
        with pytest.raises(IntegrityError):
            db_session.commit()


class TestCompanyModel:
    """Проверка модели Company."""
    
    def test_company_creation(self, db_session):
        """Company создаётся с корректными полями."""
        company = Company(name="Test Company", website="https://test.com", industry="Tech")
        db_session.add(company)
        db_session.commit()
        db_session.refresh(company)
        
        assert company.id is not None
        assert isinstance(company.id, uuid.UUID)
        assert company.name == "Test Company"
        assert company.website == "https://test.com"
        assert company.industry == "Tech"
    
    def test_company_optional_fields(self, db_session):
        """Опциональные поля Company могут быть None."""
        company = Company(name="Minimal Company")
        db_session.add(company)
        db_session.commit()
        db_session.refresh(company)
        
        assert company.website is None
        assert company.industry is None


class TestDealModel:
    """Проверка модели Deal."""
    
    def test_deal_creation(self, db_session, sample_company, sample_user):
        """Deal создаётся с корректными полями."""
        deal = Deal(
            title="Test Deal",
            company_id=sample_company.id,
            owner_id=sample_user.id,
            value=Decimal("10000.00"),
            description="Test description"
        )
        db_session.add(deal)
        db_session.commit()
        db_session.refresh(deal)
        
        assert deal.id is not None
        assert isinstance(deal.id, uuid.UUID)
        assert deal.title == "Test Deal"
        assert deal.stage == DealStage.LEAD  # Default value
        assert deal.value == Decimal("10000.00")
        assert deal.description == "Test description"
    
    def test_deal_default_stage_is_lead(self, db_session, sample_company, sample_user):
        """Стадия сделки по умолчанию LEAD."""
        deal = Deal(title="Test Deal", company_id=sample_company.id, owner_id=sample_user.id)
        db_session.add(deal)
        db_session.commit()
        db_session.refresh(deal)
        
        assert deal.stage == DealStage.LEAD
    
    def test_deal_optional_fields(self, db_session, sample_company, sample_user):
        """Опциональные поля Deal могут быть None."""
        deal = Deal(title="Test Deal", company_id=sample_company.id, owner_id=sample_user.id)
        db_session.add(deal)
        db_session.commit()
        db_session.refresh(deal)
        
        assert deal.value is None
        assert deal.description is None


class TestActivityModel:
    """Проверка модели Activity."""
    
    def test_activity_creation(self, db_session, sample_deal):
        """Activity создаётся с корректными полями."""
        activity = Activity(
            deal_id=sample_deal.id,
            type=ActivityType.CALL,
            description="Test call"
        )
        db_session.add(activity)
        db_session.commit()
        db_session.refresh(activity)
        
        assert activity.id is not None
        assert isinstance(activity.id, uuid.UUID)
        assert activity.deal_id == sample_deal.id
        assert activity.type == ActivityType.CALL
        assert activity.description == "Test call"
        assert activity.created_at is not None
    
    def test_activity_default_type_is_note(self, db_session, sample_deal):
        """Тип активности по умолчанию NOTE."""
        activity = Activity(deal_id=sample_deal.id, description="Test")
        db_session.add(activity)
        db_session.commit()
        db_session.refresh(activity)
        
        assert activity.type == ActivityType.NOTE
    
    def test_activity_has_no_updated_at(self, db_session, sample_deal):
        """Activity не имеет updated_at (immutable)."""
        activity = Activity(deal_id=sample_deal.id, description="Test")
        db_session.add(activity)
        db_session.commit()
        db_session.refresh(activity)
        
        assert not hasattr(activity, "updated_at") or activity.updated_at is None


class TestAdversarialCases:
    """Adversarial тесты для граничных случаев."""
    
    def test_deal_invalid_company_id(self, db_session, sample_user):
        """Deal с несуществующим company_id должен вызывать ошибку."""
        fake_company_id = uuid.uuid4()
        deal = Deal(title="Test", company_id=fake_company_id, owner_id=sample_user.id)
        db_session.add(deal)
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    def test_deal_invalid_owner_id(self, db_session, sample_company):
        """Deal с несуществующим owner_id должен вызывать ошибку."""
        fake_user_id = uuid.uuid4()
        deal = Deal(title="Test", company_id=sample_company.id, owner_id=fake_user_id)
        db_session.add(deal)
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    def test_activity_invalid_deal_id(self, db_session):
        """Activity с несуществующим deal_id должен вызывать ошибку."""
        fake_deal_id = uuid.uuid4()
        activity = Activity(deal_id=fake_deal_id, description="Test")
        db_session.add(activity)
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    def test_user_null_email(self, db_session):
        """User с NULL email должен вызывать ошибку."""
        user = User(email=None, name="Test")  # type: ignore
        db_session.add(user)
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    def test_user_null_name(self, db_session):
        """User с NULL name должен вызывать ошибку."""
        user = User(email="test@test.com", name=None)  # type: ignore
        db_session.add(user)
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    def test_company_null_name(self, db_session):
        """Company с NULL name должен вызывать ошибку."""
        company = Company(name=None)  # type: ignore
        db_session.add(company)
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    def test_deal_null_title(self, db_session, sample_company, sample_user):
        """Deal с NULL title должен вызывать ошибку."""
        deal = Deal(title=None, company_id=sample_company.id, owner_id=sample_user.id)  # type: ignore
        db_session.add(deal)
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    def test_activity_null_description(self, db_session, sample_deal):
        """Activity с NULL description должен вызывать ошибку."""
        activity = Activity(deal_id=sample_deal.id, description=None)  # type: ignore
        db_session.add(activity)
        with pytest.raises(IntegrityError):
            db_session.commit()