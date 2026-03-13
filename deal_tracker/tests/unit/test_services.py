# START_MODULE_CONTRACT
# Module: tests.unit.test_services
# Intent: Unit-тесты для бизнес-логики сервисов Phase 3.
# Покрывает: UserService, CompanyService, DealService, ActivityService.
# END_MODULE_CONTRACT

import pytest
import uuid
from decimal import Decimal
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.company import Company
from app.models.deal import Deal, DealStage
from app.models.activity import Activity, ActivityType
from app.services.user_service import UserService
from app.services.company_service import CompanyService
from app.services.deal_service import DealService
from app.services.activity_service import ActivityService
from app.services.errors import (
    NotFoundError,
    InvalidStageTransitionError,
    ForeignKeyValidationError,
    DuplicateEmailError,
    HasRelatedEntitiesError,
)


# ============================================================
# USER SERVICE TESTS
# ============================================================

class TestUserService:
    """Тесты для UserService."""

    def test_create_user_success(self, db_session: Session):
        """[HAPPY PATH] Создание пользователя с валидными данными."""
        service = UserService(db_session)
        user = service.create_user(email="new@example.com", name="New User")
        
        assert user.id is not None
        assert user.email == "new@example.com"
        assert user.name == "New User"

    def test_create_user_duplicate_email(self, db_session: Session, sample_user: User):
        """[ADVERSARIAL] Дублирование email должно вызывать DuplicateEmailError."""
        service = UserService(db_session)
        
        with pytest.raises(DuplicateEmailError) as exc_info:
            service.create_user(email=sample_user.email, name="Another User")
        
        assert sample_user.email in str(exc_info.value)

    def test_get_user_success(self, db_session: Session, sample_user: User):
        """[HAPPY PATH] Получение пользователя по ID."""
        service = UserService(db_session)
        found = service.get_user(sample_user.id)
        
        assert found.id == sample_user.id
        assert found.email == sample_user.email

    def test_get_user_not_found(self, db_session: Session):
        """[ADVERSARIAL] Получение несуществующего пользователя."""
        service = UserService(db_session)
        fake_id = uuid.uuid4()
        
        with pytest.raises(NotFoundError) as exc_info:
            service.get_user(fake_id)
        
        assert "User" in str(exc_info.value)
        assert str(fake_id) in str(exc_info.value)

    def test_get_users_list(self, db_session: Session, sample_user: User):
        """[HAPPY PATH] Получение списка пользователей."""
        service = UserService(db_session)
        users = service.get_users()
        
        assert len(users) >= 1
        assert any(u.id == sample_user.id for u in users)

    def test_get_users_pagination(self, db_session: Session):
        """[EDGE CASE] Пагинация списка пользователей."""
        service = UserService(db_session)
        # Создаём 5 пользователей
        for i in range(5):
            service.create_user(email=f"user{i}@example.com", name=f"User {i}")
        
        page1 = service.get_users(skip=0, limit=2)
        page2 = service.get_users(skip=2, limit=2)
        
        assert len(page1) == 2
        assert len(page2) == 2
        assert page1[0].id != page2[0].id


# ============================================================
# COMPANY SERVICE TESTS
# ============================================================

class TestCompanyService:
    """Тесты для CompanyService."""

    def test_create_company_minimal(self, db_session: Session):
        """[HAPPY PATH] Создание компании только с name."""
        service = CompanyService(db_session)
        company = service.create_company(name="Minimal Company")
        
        assert company.id is not None
        assert company.name == "Minimal Company"
        assert company.website is None
        assert company.industry is None

    def test_create_company_full(self, db_session: Session):
        """[HAPPY PATH] Создание компании со всеми полями."""
        service = CompanyService(db_session)
        company = service.create_company(
            name="Full Company",
            website="https://full.com",
            industry="Finance"
        )
        
        assert company.name == "Full Company"
        assert company.website == "https://full.com"
        assert company.industry == "Finance"

    def test_get_company_success(self, db_session: Session, sample_company: Company):
        """[HAPPY PATH] Получение компании по ID."""
        service = CompanyService(db_session)
        found = service.get_company(sample_company.id)
        
        assert found.id == sample_company.id
        assert found.name == sample_company.name

    def test_get_company_not_found(self, db_session: Session):
        """[ADVERSARIAL] Получение несуществующей компании."""
        service = CompanyService(db_session)
        fake_id = uuid.uuid4()
        
        with pytest.raises(NotFoundError) as exc_info:
            service.get_company(fake_id)
        
        assert "Company" in str(exc_info.value)

    def test_get_companies_list(self, db_session: Session, sample_company: Company):
        """[HAPPY PATH] Получение списка компаний."""
        service = CompanyService(db_session)
        companies = service.get_companies()
        
        assert len(companies) >= 1
        assert any(c.id == sample_company.id for c in companies)

    def test_update_company_name(self, db_session: Session, sample_company: Company):
        """[HAPPY PATH] Обновление названия компании."""
        service = CompanyService(db_session)
        updated = service.update_company(sample_company.id, name="Updated Name")
        
        assert updated.name == "Updated Name"
        assert updated.website == sample_company.website

    def test_update_company_partial(self, db_session: Session, sample_company: Company):
        """[HAPPY PATH] Частичное обновление компании."""
        service = CompanyService(db_session)
        updated = service.update_company(sample_company.id, industry="Healthcare")
        
        assert updated.industry == "Healthcare"
        assert updated.name == sample_company.name

    def test_update_company_not_found(self, db_session: Session):
        """[ADVERSARIAL] Обновление несуществующей компании."""
        service = CompanyService(db_session)
        fake_id = uuid.uuid4()
        
        with pytest.raises(NotFoundError):
            service.update_company(fake_id, name="New Name")

    def test_delete_company_success(self, db_session: Session):
        """[HAPPY PATH] Удаление компании без сделок."""
        service = CompanyService(db_session)
        company = service.create_company(name="To Delete")
        
        result = service.delete_company(company.id)
        
        assert result is True
        with pytest.raises(NotFoundError):
            service.get_company(company.id)

    def test_delete_company_with_deals(
        self, db_session: Session, sample_company: Company, sample_user: User
    ):
        """[ADVERSARIAL] Удаление компании со сделками должно вызывать ошибку."""
        # Создаём сделку для компании
        deal_service = DealService(db_session)
        deal_service.create_deal(
            title="Test Deal",
            company_id=sample_company.id,
            owner_id=sample_user.id
        )
        
        company_service = CompanyService(db_session)
        
        with pytest.raises(HasRelatedEntitiesError) as exc_info:
            company_service.delete_company(sample_company.id)
        
        assert "company" in str(exc_info.value)
        assert "deals" in str(exc_info.value)

    def test_delete_company_not_found(self, db_session: Session):
        """[ADVERSARIAL] Удаление несуществующей компании."""
        service = CompanyService(db_session)
        fake_id = uuid.uuid4()
        
        with pytest.raises(NotFoundError):
            service.delete_company(fake_id)


# ============================================================
# DEAL SERVICE TESTS
# ============================================================

class TestDealService:
    """Тесты для DealService."""

    def test_create_deal_success(
        self, db_session: Session, sample_company: Company, sample_user: User
    ):
        """[HAPPY PATH] Создание сделки с валидными FK."""
        service = DealService(db_session)
        deal = service.create_deal(
            title="New Deal",
            company_id=sample_company.id,
            owner_id=sample_user.id,
            value=Decimal("50000.00")
        )
        
        assert deal.id is not None
        assert deal.title == "New Deal"
        assert deal.stage == DealStage.LEAD  # Всегда LEAD при создании
        assert deal.value == Decimal("50000.00")

    def test_create_deal_invalid_company_id(self, db_session: Session, sample_user: User):
        """[ADVERSARIAL] Создание сделки с несуществующим company_id."""
        service = DealService(db_session)
        fake_company_id = uuid.uuid4()
        
        with pytest.raises(ForeignKeyValidationError) as exc_info:
            service.create_deal(
                title="Bad Deal",
                company_id=fake_company_id,
                owner_id=sample_user.id
            )
        
        assert "company_id" in str(exc_info.value)
        assert "Company" in str(exc_info.value)

    def test_create_deal_invalid_owner_id(
        self, db_session: Session, sample_company: Company
    ):
        """[ADVERSARIAL] Создание сделки с несуществующим owner_id."""
        service = DealService(db_session)
        fake_user_id = uuid.uuid4()
        
        with pytest.raises(ForeignKeyValidationError) as exc_info:
            service.create_deal(
                title="Bad Deal",
                company_id=sample_company.id,
                owner_id=fake_user_id
            )
        
        assert "owner_id" in str(exc_info.value)
        assert "User" in str(exc_info.value)

    def test_get_deal_success(self, db_session: Session, sample_deal: Deal):
        """[HAPPY PATH] Получение сделки по ID."""
        service = DealService(db_session)
        found = service.get_deal(sample_deal.id)
        
        assert found.id == sample_deal.id
        assert found.title == sample_deal.title

    def test_get_deal_not_found(self, db_session: Session):
        """[ADVERSARIAL] Получение несуществующей сделки."""
        service = DealService(db_session)
        fake_id = uuid.uuid4()
        
        with pytest.raises(NotFoundError) as exc_info:
            service.get_deal(fake_id)
        
        assert "Deal" in str(exc_info.value)

    def test_get_deals_list(self, db_session: Session, sample_deal: Deal):
        """[HAPPY PATH] Получение списка сделок."""
        service = DealService(db_session)
        deals = service.get_deals()
        
        assert len(deals) >= 1
        assert any(d.id == sample_deal.id for d in deals)

    def test_get_deals_filter_by_stage(
        self, db_session: Session, sample_company: Company, sample_user: User
    ):
        """[HAPPY PATH] Фильтрация сделок по стадии."""
        service = DealService(db_session)
        
        # Создаём сделки на разных стадиях
        deal1 = service.create_deal(
            title="Lead Deal",
            company_id=sample_company.id,
            owner_id=sample_user.id
        )
        deal2 = service.create_deal(
            title="Won Deal Base",
            company_id=sample_company.id,
            owner_id=sample_user.id
        )
        # Переводим deal2 в WON
        service.change_deal_stage(deal2.id, DealStage.WON)
        
        lead_deals = service.get_deals(stage=DealStage.LEAD)
        won_deals = service.get_deals(stage=DealStage.WON)
        
        assert any(d.id == deal1.id for d in lead_deals)
        assert any(d.id == deal2.id for d in won_deals)

    def test_get_deals_filter_by_company(
        self, db_session: Session, sample_user: User
    ):
        """[HAPPY PATH] Фильтрация сделок по компании."""
        service = DealService(db_session)
        company_service = CompanyService(db_session)
        
        company1 = company_service.create_company(name="Company 1")
        company2 = company_service.create_company(name="Company 2")
        
        deal1 = service.create_deal(
            title="Deal 1",
            company_id=company1.id,
            owner_id=sample_user.id
        )
        deal2 = service.create_deal(
            title="Deal 2",
            company_id=company2.id,
            owner_id=sample_user.id
        )
        
        company1_deals = service.get_deals(company_id=company1.id)
        
        assert any(d.id == deal1.id for d in company1_deals)
        assert not any(d.id == deal2.id for d in company1_deals)

    def test_update_deal_title(self, db_session: Session, sample_deal: Deal):
        """[HAPPY PATH] Обновление названия сделки."""
        service = DealService(db_session)
        updated = service.update_deal(sample_deal.id, title="Updated Title")
        
        assert updated.title == "Updated Title"

    def test_update_deal_value(self, db_session: Session, sample_deal: Deal):
        """[HAPPY PATH] Обновление value сделки."""
        service = DealService(db_session)
        updated = service.update_deal(sample_deal.id, value=Decimal("99999.99"))
        
        assert updated.value == Decimal("99999.99")

    def test_update_deal_not_found(self, db_session: Session):
        """[ADVERSARIAL] Обновление несуществующей сделки."""
        service = DealService(db_session)
        fake_id = uuid.uuid4()
        
        with pytest.raises(NotFoundError):
            service.update_deal(fake_id, title="New Title")

    def test_delete_deal_success(
        self, db_session: Session, sample_company: Company, sample_user: User
    ):
        """[HAPPY PATH] Удаление сделки без активностей."""
        service = DealService(db_session)
        deal = service.create_deal(
            title="To Delete",
            company_id=sample_company.id,
            owner_id=sample_user.id
        )
        
        result = service.delete_deal(deal.id)
        
        assert result is True
        with pytest.raises(NotFoundError):
            service.get_deal(deal.id)

    def test_delete_deal_with_activities(
        self, db_session: Session, sample_deal: Deal
    ):
        """[ADVERSARIAL] Удаление сделки с активностями должно вызывать ошибку."""
        activity_service = ActivityService(db_session)
        activity_service.create_activity(
            deal_id=sample_deal.id,
            description="Some activity"
        )
        
        deal_service = DealService(db_session)
        
        with pytest.raises(HasRelatedEntitiesError) as exc_info:
            deal_service.delete_deal(sample_deal.id)
        
        assert "deal" in str(exc_info.value)
        assert "activities" in str(exc_info.value)

    def test_delete_deal_not_found(self, db_session: Session):
        """[ADVERSARIAL] Удаление несуществующей сделки."""
        service = DealService(db_session)
        fake_id = uuid.uuid4()
        
        with pytest.raises(NotFoundError):
            service.delete_deal(fake_id)


# ============================================================
# STAGE TRANSITION TESTS (CRITICAL)
# ============================================================

class TestDealStageTransitions:
    """
    Тесты для валидации переходов стадий.
    Таблица переходов из requirements.md раздел 4.1.
    """

    @pytest.fixture
    def deal_service(self, db_session: Session) -> DealService:
        return DealService(db_session)

    @pytest.fixture
    def deal_on_stage(
        self, db_session: Session, sample_company: Company, sample_user: User
    ):
        """Фабрика для создания сделки на определённой стадии."""
        def _create(stage: DealStage) -> Deal:
            service = DealService(db_session)
            deal = service.create_deal(
                title=f"Deal on {stage.value}",
                company_id=sample_company.id,
                owner_id=sample_user.id
            )
            # Переводим в нужную стадию через цепочку
            if stage == DealStage.LEAD:
                return deal
            service.change_deal_stage(deal.id, DealStage.QUALIFIED)
            if stage == DealStage.QUALIFIED:
                return service.get_deal(deal.id)
            service.change_deal_stage(deal.id, DealStage.PROPOSAL)
            if stage == DealStage.PROPOSAL:
                return service.get_deal(deal.id)
            service.change_deal_stage(deal.id, DealStage.NEGOTIATION)
            return service.get_deal(deal.id)
        return _create

    # --- LEAD transitions ---
    def test_lead_to_qualified(self, deal_service: DealService, deal_on_stage):
        """[STAGE] LEAD → QUALIFIED: разрешено."""
        deal = deal_on_stage(DealStage.LEAD)
        updated = deal_service.change_deal_stage(deal.id, DealStage.QUALIFIED)
        assert updated.stage == DealStage.QUALIFIED

    def test_lead_to_won(self, deal_service: DealService, deal_on_stage):
        """[STAGE] LEAD → WON: разрешено."""
        deal = deal_on_stage(DealStage.LEAD)
        updated = deal_service.change_deal_stage(deal.id, DealStage.WON)
        assert updated.stage == DealStage.WON

    def test_lead_to_lost(self, deal_service: DealService, deal_on_stage):
        """[STAGE] LEAD → LOST: разрешено."""
        deal = deal_on_stage(DealStage.LEAD)
        updated = deal_service.change_deal_stage(deal.id, DealStage.LOST)
        assert updated.stage == DealStage.LOST

    def test_lead_to_proposal_forbidden(self, deal_service: DealService, deal_on_stage):
        """[STAGE] LEAD → PROPOSAL: запрещено (пропуск стадии)."""
        deal = deal_on_stage(DealStage.LEAD)
        with pytest.raises(InvalidStageTransitionError):
            deal_service.change_deal_stage(deal.id, DealStage.PROPOSAL)

    def test_lead_to_negotiation_forbidden(self, deal_service: DealService, deal_on_stage):
        """[STAGE] LEAD → NEGOTIATION: запрещено."""
        deal = deal_on_stage(DealStage.LEAD)
        with pytest.raises(InvalidStageTransitionError):
            deal_service.change_deal_stage(deal.id, DealStage.NEGOTIATION)

    # --- QUALIFIED transitions ---
    def test_qualified_to_proposal(self, deal_service: DealService, deal_on_stage):
        """[STAGE] QUALIFIED → PROPOSAL: разрешено."""
        deal = deal_on_stage(DealStage.QUALIFIED)
        updated = deal_service.change_deal_stage(deal.id, DealStage.PROPOSAL)
        assert updated.stage == DealStage.PROPOSAL

    def test_qualified_to_won(self, deal_service: DealService, deal_on_stage):
        """[STAGE] QUALIFIED → WON: разрешено."""
        deal = deal_on_stage(DealStage.QUALIFIED)
        updated = deal_service.change_deal_stage(deal.id, DealStage.WON)
        assert updated.stage == DealStage.WON

    def test_qualified_to_lost(self, deal_service: DealService, deal_on_stage):
        """[STAGE] QUALIFIED → LOST: разрешено."""
        deal = deal_on_stage(DealStage.QUALIFIED)
        updated = deal_service.change_deal_stage(deal.id, DealStage.LOST)
        assert updated.stage == DealStage.LOST

    def test_qualified_to_lead_forbidden(self, deal_service: DealService, deal_on_stage):
        """[STAGE] QUALIFIED → LEAD: запрещено (назад нельзя)."""
        deal = deal_on_stage(DealStage.QUALIFIED)
        with pytest.raises(InvalidStageTransitionError):
            deal_service.change_deal_stage(deal.id, DealStage.LEAD)

    def test_qualified_to_negotiation_forbidden(self, deal_service: DealService, deal_on_stage):
        """[STAGE] QUALIFIED → NEGOTIATION: запрещено (пропуск стадии)."""
        deal = deal_on_stage(DealStage.QUALIFIED)
        with pytest.raises(InvalidStageTransitionError):
            deal_service.change_deal_stage(deal.id, DealStage.NEGOTIATION)

    # --- PROPOSAL transitions ---
    def test_proposal_to_negotiation(self, deal_service: DealService, deal_on_stage):
        """[STAGE] PROPOSAL → NEGOTIATION: разрешено."""
        deal = deal_on_stage(DealStage.PROPOSAL)
        updated = deal_service.change_deal_stage(deal.id, DealStage.NEGOTIATION)
        assert updated.stage == DealStage.NEGOTIATION

    def test_proposal_to_won(self, deal_service: DealService, deal_on_stage):
        """[STAGE] PROPOSAL → WON: разрешено."""
        deal = deal_on_stage(DealStage.PROPOSAL)
        updated = deal_service.change_deal_stage(deal.id, DealStage.WON)
        assert updated.stage == DealStage.WON

    def test_proposal_to_lost(self, deal_service: DealService, deal_on_stage):
        """[STAGE] PROPOSAL → LOST: разрешено."""
        deal = deal_on_stage(DealStage.PROPOSAL)
        updated = deal_service.change_deal_stage(deal.id, DealStage.LOST)
        assert updated.stage == DealStage.LOST

    def test_proposal_to_qualified_forbidden(self, deal_service: DealService, deal_on_stage):
        """[STAGE] PROPOSAL → QUALIFIED: запрещено (назад нельзя)."""
        deal = deal_on_stage(DealStage.PROPOSAL)
        with pytest.raises(InvalidStageTransitionError):
            deal_service.change_deal_stage(deal.id, DealStage.QUALIFIED)

    def test_proposal_to_lead_forbidden(self, deal_service: DealService, deal_on_stage):
        """[STAGE] PROPOSAL → LEAD: запрещено."""
        deal = deal_on_stage(DealStage.PROPOSAL)
        with pytest.raises(InvalidStageTransitionError):
            deal_service.change_deal_stage(deal.id, DealStage.LEAD)

    # --- NEGOTIATION transitions ---
    def test_negotiation_to_won(self, deal_service: DealService, deal_on_stage):
        """[STAGE] NEGOTIATION → WON: разрешено."""
        deal = deal_on_stage(DealStage.NEGOTIATION)
        updated = deal_service.change_deal_stage(deal.id, DealStage.WON)
        assert updated.stage == DealStage.WON

    def test_negotiation_to_lost(self, deal_service: DealService, deal_on_stage):
        """[STAGE] NEGOTIATION → LOST: разрешено."""
        deal = deal_on_stage(DealStage.NEGOTIATION)
        updated = deal_service.change_deal_stage(deal.id, DealStage.LOST)
        assert updated.stage == DealStage.LOST

    def test_negotiation_to_proposal_forbidden(self, deal_service: DealService, deal_on_stage):
        """[STAGE] NEGOTIATION → PROPOSAL: запрещено (назад нельзя)."""
        deal = deal_on_stage(DealStage.NEGOTIATION)
        with pytest.raises(InvalidStageTransitionError):
            deal_service.change_deal_stage(deal.id, DealStage.PROPOSAL)

    def test_negotiation_to_lead_forbidden(self, deal_service: DealService, deal_on_stage):
        """[STAGE] NEGOTIATION → LEAD: запрещено."""
        deal = deal_on_stage(DealStage.NEGOTIATION)
        with pytest.raises(InvalidStageTransitionError):
            deal_service.change_deal_stage(deal.id, DealStage.LEAD)

    def test_negotiation_to_qualified_forbidden(self, deal_service: DealService, deal_on_stage):
        """[STAGE] NEGOTIATION → QUALIFIED: запрещено."""
        deal = deal_on_stage(DealStage.NEGOTIATION)
        with pytest.raises(InvalidStageTransitionError):
            deal_service.change_deal_stage(deal.id, DealStage.QUALIFIED)

    # --- WON transitions (терминальная) ---
    def test_won_to_lead_reanimation(self, deal_service: DealService, deal_on_stage):
        """[STAGE] WON → LEAD: разрешено (реанимация)."""
        deal = deal_on_stage(DealStage.NEGOTIATION)
        deal_service.change_deal_stage(deal.id, DealStage.WON)
        updated = deal_service.change_deal_stage(deal.id, DealStage.LEAD)
        assert updated.stage == DealStage.LEAD

    def test_won_to_qualified_forbidden(self, deal_service: DealService, deal_on_stage):
        """[STAGE] WON → QUALIFIED: запрещено."""
        deal = deal_on_stage(DealStage.NEGOTIATION)
        deal_service.change_deal_stage(deal.id, DealStage.WON)
        with pytest.raises(InvalidStageTransitionError):
            deal_service.change_deal_stage(deal.id, DealStage.QUALIFIED)

    def test_won_to_lost_forbidden(self, deal_service: DealService, deal_on_stage):
        """[STAGE] WON → LOST: запрещено."""
        deal = deal_on_stage(DealStage.NEGOTIATION)
        deal_service.change_deal_stage(deal.id, DealStage.WON)
        with pytest.raises(InvalidStageTransitionError):
            deal_service.change_deal_stage(deal.id, DealStage.LOST)

    # --- LOST transitions (терминальная) ---
    def test_lost_to_lead_reanimation(self, deal_service: DealService, deal_on_stage):
        """[STAGE] LOST → LEAD: разрешено (реанимация)."""
        deal = deal_on_stage(DealStage.LEAD)
        deal_service.change_deal_stage(deal.id, DealStage.LOST)
        updated = deal_service.change_deal_stage(deal.id, DealStage.LEAD)
        assert updated.stage == DealStage.LEAD

    def test_lost_to_qualified_forbidden(self, deal_service: DealService, deal_on_stage):
        """[STAGE] LOST → QUALIFIED: запрещено."""
        deal = deal_on_stage(DealStage.LEAD)
        deal_service.change_deal_stage(deal.id, DealStage.LOST)
        with pytest.raises(InvalidStageTransitionError):
            deal_service.change_deal_stage(deal.id, DealStage.QUALIFIED)

    def test_lost_to_won_forbidden(self, deal_service: DealService, deal_on_stage):
        """[STAGE] LOST → WON: запрещено."""
        deal = deal_on_stage(DealStage.LEAD)
        deal_service.change_deal_stage(deal.id, DealStage.LOST)
        with pytest.raises(InvalidStageTransitionError):
            deal_service.change_deal_stage(deal.id, DealStage.WON)

    # --- Error message contains allowed stages ---
    def test_invalid_transition_error_message(
        self, deal_service: DealService, deal_on_stage
    ):
        """[CONTRACT] Ошибка содержит список допустимых стадий."""
        deal = deal_on_stage(DealStage.LEAD)
        
        with pytest.raises(InvalidStageTransitionError) as exc_info:
            deal_service.change_deal_stage(deal.id, DealStage.NEGOTIATION)
        
        error = exc_info.value
        assert error.current_stage == DealStage.LEAD
        assert error.target_stage == DealStage.NEGOTIATION
        assert DealStage.QUALIFIED in error.allowed
        assert DealStage.WON in error.allowed
        assert DealStage.LOST in error.allowed


# ============================================================
# SYSTEM ACTIVITY ON STAGE CHANGE TESTS
# ============================================================

class TestSystemActivityOnStageChange:
    """Тесты для создания системной Activity при смене стадии."""

    def test_stage_change_creates_activity(
        self, db_session: Session, sample_deal: Deal
    ):
        """[HAPPY PATH] При смене стадии создаётся системная Activity."""
        deal_service = DealService(db_session)
        activity_service = ActivityService(db_session)
        
        # Меняем стадию
        deal_service.change_deal_stage(sample_deal.id, DealStage.QUALIFIED)
        
        # Проверяем, что создана активность
        activities = activity_service.get_deal_timeline(sample_deal.id)
        
        assert len(activities) == 1
        assert activities[0].type == ActivityType.NOTE
        assert "Stage changed from lead to qualified" in activities[0].description

    def test_multiple_stage_changes_create_multiple_activities(
        self, db_session: Session, sample_deal: Deal
    ):
        """[HAPPY PATH] Каждая смена стадии создаёт новую активность."""
        deal_service = DealService(db_session)
        activity_service = ActivityService(db_session)
        
        # LEAD → QUALIFIED → PROPOSAL
        deal_service.change_deal_stage(sample_deal.id, DealStage.QUALIFIED)
        deal_service.change_deal_stage(sample_deal.id, DealStage.PROPOSAL)
        
        activities = activity_service.get_deal_timeline(sample_deal.id)
        
        assert len(activities) == 2
        # Проверяем что обе активности созданы (порядок зависит от created_at)
        descriptions = [a.description for a in activities]
        assert any("lead to qualified" in d for d in descriptions)
        assert any("qualified to proposal" in d for d in descriptions)

    def test_won_transition_creates_activity(
        self, db_session: Session, sample_deal: Deal
    ):
        """[HAPPY PATH] Переход в WON создаёт активность."""
        deal_service = DealService(db_session)
        activity_service = ActivityService(db_session)
        
        deal_service.change_deal_stage(sample_deal.id, DealStage.WON)
        
        activities = activity_service.get_deal_timeline(sample_deal.id)
        
        assert len(activities) == 1
        assert "Stage changed from lead to won" in activities[0].description


# ============================================================
# ACTIVITY SERVICE TESTS
# ============================================================

class TestActivityService:
    """Тесты для ActivityService."""

    def test_create_activity_success(self, db_session: Session, sample_deal: Deal):
        """[HAPPY PATH] Создание активности с валидным deal_id."""
        service = ActivityService(db_session)
        activity = service.create_activity(
            deal_id=sample_deal.id,
            description="Test activity"
        )
        
        assert activity.id is not None
        assert activity.deal_id == sample_deal.id
        assert activity.type == ActivityType.NOTE  # default
        assert activity.description == "Test activity"

    def test_create_activity_with_type(self, db_session: Session, sample_deal: Deal):
        """[HAPPY PATH] Создание активности с указанным типом."""
        service = ActivityService(db_session)
        activity = service.create_activity(
            deal_id=sample_deal.id,
            description="Call activity",
            activity_type=ActivityType.CALL
        )
        
        assert activity.type == ActivityType.CALL

    def test_create_activity_invalid_deal_id(self, db_session: Session):
        """[ADVERSARIAL] Создание активности с несуществующим deal_id."""
        service = ActivityService(db_session)
        fake_deal_id = uuid.uuid4()
        
        with pytest.raises(ForeignKeyValidationError) as exc_info:
            service.create_activity(
                deal_id=fake_deal_id,
                description="Bad activity"
            )
        
        assert "deal_id" in str(exc_info.value)
        assert "Deal" in str(exc_info.value)

    def test_get_deal_timeline_success(self, db_session: Session, sample_deal: Deal):
        """[HAPPY PATH] Получение timeline сделки."""
        service = ActivityService(db_session)
        
        # Создаём несколько активностей
        service.create_activity(deal_id=sample_deal.id, description="First")
        service.create_activity(deal_id=sample_deal.id, description="Second")
        service.create_activity(deal_id=sample_deal.id, description="Third")
        
        timeline = service.get_deal_timeline(sample_deal.id)
        
        assert len(timeline) == 3

    def test_get_deal_timeline_desc_order(self, db_session: Session, sample_deal: Deal):
        """[CONTRACT] Timeline отсортирован DESC (новые сначала)."""
        service = ActivityService(db_session)
        
        # Создаём активности и проверяем что они возвращаются
        act1 = service.create_activity(deal_id=sample_deal.id, description="First")
        act2 = service.create_activity(deal_id=sample_deal.id, description="Second")
        act3 = service.create_activity(deal_id=sample_deal.id, description="Third")
        
        timeline = service.get_deal_timeline(sample_deal.id)
        
        # Проверяем что все активности возвращены
        assert len(timeline) == 3
        activity_ids = {a.id for a in timeline}
        assert act1.id in activity_ids
        assert act2.id in activity_ids
        assert act3.id in activity_ids
        
        # Проверяем сортировку DESC по created_at (новые имеют больший created_at)
        for i in range(len(timeline) - 1):
            assert timeline[i].created_at >= timeline[i + 1].created_at

    def test_get_deal_timeline_empty(self, db_session: Session, sample_deal: Deal):
        """[EDGE CASE] Пустой timeline для сделки без активностей."""
        service = ActivityService(db_session)
        timeline = service.get_deal_timeline(sample_deal.id)
        
        assert timeline == []

    def test_get_deal_timeline_deal_not_found(self, db_session: Session):
        """[ADVERSARIAL] Timeline для несуществующей сделки."""
        service = ActivityService(db_session)
        fake_deal_id = uuid.uuid4()
        
        with pytest.raises(NotFoundError) as exc_info:
            service.get_deal_timeline(fake_deal_id)
        
        assert "Deal" in str(exc_info.value)

    def test_get_deal_timeline_pagination(
        self, db_session: Session, sample_deal: Deal
    ):
        """[EDGE CASE] Пагинация timeline."""
        service = ActivityService(db_session)
        
        # Создаём 5 активностей
        for i in range(5):
            service.create_activity(deal_id=sample_deal.id, description=f"Activity {i}")
        
        page1 = service.get_deal_timeline(sample_deal.id, skip=0, limit=2)
        page2 = service.get_deal_timeline(sample_deal.id, skip=2, limit=2)
        
        assert len(page1) == 2
        assert len(page2) == 2
        # Проверяем что это разные записи
        page1_ids = {a.id for a in page1}
        page2_ids = {a.id for a in page2}
        assert page1_ids.isdisjoint(page2_ids)


# ============================================================
# ALL ACTIVITY TYPES TEST
# ============================================================

class TestAllActivityTypes:
    """Тесты для всех типов активностей."""

    @pytest.mark.parametrize("activity_type", [
        ActivityType.CALL,
        ActivityType.EMAIL,
        ActivityType.MEETING,
        ActivityType.NOTE,
    ])
    def test_create_activity_all_types(
        self, db_session: Session, sample_deal: Deal, activity_type: ActivityType
    ):
        """[HAPPY PATH] Создание активности каждого типа."""
        service = ActivityService(db_session)
        activity = service.create_activity(
            deal_id=sample_deal.id,
            description=f"Test {activity_type.value}",
            activity_type=activity_type
        )
        
        assert activity.type == activity_type