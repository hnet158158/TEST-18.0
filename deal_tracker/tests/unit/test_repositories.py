# START_MODULE_CONTRACT
# Module: tests.unit.test_repositories
# Intent: Unit-тесты для Phase 2 - Repositories.
# Проверяет все CRUD операции и специальные методы репозиториев.
# END_MODULE_CONTRACT

import pytest
import uuid
from sqlalchemy.orm import Session

from app.models import User, Company, Deal, Activity
from app.models.deal import DealStage
from app.models.activity import ActivityType
from app.repositories.user_repo import UserRepository
from app.repositories.company_repo import CompanyRepository
from app.repositories.deal_repo import DealRepository
from app.repositories.activity_repo import ActivityRepository


# ============================================================================
# UserRepository Tests
# ============================================================================

class TestUserRepository:
    """Tests for UserRepository CRUD operations."""

    def test_create_user(self, db_session: Session):
        """[BELIEF] UserRepository.create creates a new user."""
        repo = UserRepository(db_session)
        user_data = {"email": "newuser@example.com", "name": "New User"}
        
        user = repo.create(user_data)
        
        assert user.id is not None
        assert user.email == "newuser@example.com"
        assert user.name == "New User"
        assert user.created_at is not None

    def test_get_by_id_existing_user(self, db_session: Session, sample_user: User):
        """[BELIEF] UserRepository.get_by_id returns existing user."""
        repo = UserRepository(db_session)
        
        found = repo.get_by_id(sample_user.id)
        
        assert found is not None
        assert found.id == sample_user.id
        assert found.email == sample_user.email

    def test_get_by_id_nonexistent_user(self, db_session: Session):
        """[BELIEF] UserRepository.get_by_id returns None for nonexistent UUID."""
        repo = UserRepository(db_session)
        
        found = repo.get_by_id(uuid.uuid4())
        
        assert found is None

    def test_get_all_users(self, db_session: Session, sample_user: User):
        """[BELIEF] UserRepository.get_all returns list of users."""
        repo = UserRepository(db_session)
        # Create additional user
        repo.create({"email": "second@example.com", "name": "Second User"})
        
        users = repo.get_all()
        
        assert len(users) == 2

    def test_get_all_pagination(self, db_session: Session):
        """[BELIEF] UserRepository.get_all respects skip and limit."""
        repo = UserRepository(db_session)
        # Create 5 users
        for i in range(5):
            repo.create({"email": f"user{i}@example.com", "name": f"User {i}"})
        
        page1 = repo.get_all(skip=0, limit=2)
        page2 = repo.get_all(skip=2, limit=2)
        
        assert len(page1) == 2
        assert len(page2) == 2

    def test_get_by_email_existing(self, db_session: Session, sample_user: User):
        """[BELIEF] UserRepository.get_by_email finds user by email."""
        repo = UserRepository(db_session)
        
        found = repo.get_by_email("test@example.com")
        
        assert found is not None
        assert found.id == sample_user.id

    def test_get_by_email_nonexistent(self, db_session: Session):
        """[BELIEF] UserRepository.get_by_email returns None for unknown email."""
        repo = UserRepository(db_session)
        
        found = repo.get_by_email("nonexistent@example.com")
        
        assert found is None

    def test_update_user(self, db_session: Session, sample_user: User):
        """[BELIEF] UserRepository.update modifies user fields."""
        repo = UserRepository(db_session)
        
        updated = repo.update(sample_user.id, {"name": "Updated Name"})
        
        assert updated is not None
        assert updated.name == "Updated Name"
        assert updated.email == sample_user.email  # unchanged

    def test_update_nonexistent_user(self, db_session: Session):
        """[BELIEF] UserRepository.update returns None for nonexistent UUID."""
        repo = UserRepository(db_session)
        
        updated = repo.update(uuid.uuid4(), {"name": "New Name"})
        
        assert updated is None

    def test_delete_user(self, db_session: Session, sample_user: User):
        """[BELIEF] UserRepository.delete removes user and returns True."""
        repo = UserRepository(db_session)
        user_id = sample_user.id
        
        result = repo.delete(user_id)
        
        assert result is True
        assert repo.get_by_id(user_id) is None

    def test_delete_nonexistent_user(self, db_session: Session):
        """[BELIEF] UserRepository.delete returns False for nonexistent UUID."""
        repo = UserRepository(db_session)
        
        result = repo.delete(uuid.uuid4())
        
        assert result is False


# ============================================================================
# CompanyRepository Tests
# ============================================================================

class TestCompanyRepository:
    """Tests for CompanyRepository CRUD operations."""

    def test_create_company(self, db_session: Session):
        """[BELIEF] CompanyRepository.create creates a new company."""
        repo = CompanyRepository(db_session)
        company_data = {
            "name": "Acme Corp",
            "website": "https://acme.com",
            "industry": "Manufacturing"
        }
        
        company = repo.create(company_data)
        
        assert company.id is not None
        assert company.name == "Acme Corp"
        assert company.website == "https://acme.com"
        assert company.industry == "Manufacturing"

    def test_get_by_id_existing_company(self, db_session: Session, sample_company: Company):
        """[BELIEF] CompanyRepository.get_by_id returns existing company."""
        repo = CompanyRepository(db_session)
        
        found = repo.get_by_id(sample_company.id)
        
        assert found is not None
        assert found.id == sample_company.id

    def test_get_by_id_nonexistent_company(self, db_session: Session):
        """[BELIEF] CompanyRepository.get_by_id returns None for nonexistent UUID."""
        repo = CompanyRepository(db_session)
        
        found = repo.get_by_id(uuid.uuid4())
        
        assert found is None

    def test_get_all_companies(self, db_session: Session, sample_company: Company):
        """[BELIEF] CompanyRepository.get_all returns list of companies."""
        repo = CompanyRepository(db_session)
        repo.create({"name": "Second Corp", "website": None, "industry": None})
        
        companies = repo.get_all()
        
        assert len(companies) == 2

    def test_update_company(self, db_session: Session, sample_company: Company):
        """[BELIEF] CompanyRepository.update modifies company fields."""
        repo = CompanyRepository(db_session)
        
        updated = repo.update(sample_company.id, {
            "name": "Updated Corp",
            "industry": "Finance"
        })
        
        assert updated is not None
        assert updated.name == "Updated Corp"
        assert updated.industry == "Finance"

    def test_delete_company_without_deals(self, db_session: Session, sample_company: Company):
        """[BELIEF] CompanyRepository.delete removes company without deals."""
        repo = CompanyRepository(db_session)
        company_id = sample_company.id
        
        result = repo.delete(company_id)
        
        assert result is True
        assert repo.get_by_id(company_id) is None

    def test_has_deals_returns_false_when_no_deals(self, db_session: Session, sample_company: Company):
        """[BELIEF] CompanyRepository.has_deals returns False when company has no deals."""
        repo = CompanyRepository(db_session)
        
        result = repo.has_deals(sample_company.id)
        
        assert result is False

    def test_has_deals_returns_true_when_deals_exist(self, db_session: Session, sample_deal: Deal):
        """[BELIEF] CompanyRepository.has_deals returns True when company has deals."""
        repo = CompanyRepository(db_session)
        
        result = repo.has_deals(sample_deal.company_id)
        
        assert result is True


# ============================================================================
# DealRepository Tests
# ============================================================================

class TestDealRepository:
    """Tests for DealRepository CRUD operations."""

    def test_create_deal(self, db_session: Session, sample_company: Company, sample_user: User):
        """[BELIEF] DealRepository.create creates a new deal with default stage LEAD."""
        repo = DealRepository(db_session)
        deal_data = {
            "title": "New Deal",
            "company_id": sample_company.id,
            "owner_id": sample_user.id,
            "value": 50000
        }
        
        deal = repo.create(deal_data)
        
        assert deal.id is not None
        assert deal.title == "New Deal"
        assert deal.stage == DealStage.LEAD
        assert deal.value == 50000

    def test_get_by_id_existing_deal(self, db_session: Session, sample_deal: Deal):
        """[BELIEF] DealRepository.get_by_id returns existing deal."""
        repo = DealRepository(db_session)
        
        found = repo.get_by_id(sample_deal.id)
        
        assert found is not None
        assert found.id == sample_deal.id

    def test_get_by_id_nonexistent_deal(self, db_session: Session):
        """[BELIEF] DealRepository.get_by_id returns None for nonexistent UUID."""
        repo = DealRepository(db_session)
        
        found = repo.get_by_id(uuid.uuid4())
        
        assert found is None

    def test_get_all_deals_no_filters(self, db_session: Session, sample_deal: Deal):
        """[BELIEF] DealRepository.get_all returns all deals without filters."""
        repo = DealRepository(db_session)
        
        deals = repo.get_all()
        
        assert len(deals) == 1
        assert deals[0].id == sample_deal.id

    def test_get_all_deals_filter_by_stage(
        self, db_session: Session, sample_company: Company, sample_user: User
    ):
        """[BELIEF] DealRepository.get_all filters by stage."""
        repo = DealRepository(db_session)
        # Create deals with different stages
        deal1 = repo.create({
            "title": "Lead Deal",
            "company_id": sample_company.id,
            "owner_id": sample_user.id,
            "value": 1000
        })
        deal2 = repo.create({
            "title": "Won Deal",
            "company_id": sample_company.id,
            "owner_id": sample_user.id,
            "value": 2000,
            "stage": DealStage.WON
        })
        
        lead_deals = repo.get_all(stage=DealStage.LEAD)
        won_deals = repo.get_all(stage=DealStage.WON)
        
        assert len(lead_deals) == 1
        assert len(won_deals) == 1
        assert lead_deals[0].title == "Lead Deal"
        assert won_deals[0].title == "Won Deal"

    def test_get_all_deals_filter_by_company(
        self, db_session: Session, sample_user: User
    ):
        """[BELIEF] DealRepository.get_all filters by company_id."""
        repo = DealRepository(db_session)
        company_repo = CompanyRepository(db_session)
        # Create two companies
        company1 = company_repo.create({"name": "Company 1", "website": None, "industry": None})
        company2 = company_repo.create({"name": "Company 2", "website": None, "industry": None})
        # Create deals for each company
        repo.create({
            "title": "Deal 1",
            "company_id": company1.id,
            "owner_id": sample_user.id,
            "value": 1000
        })
        repo.create({
            "title": "Deal 2",
            "company_id": company2.id,
            "owner_id": sample_user.id,
            "value": 2000
        })
        
        deals_company1 = repo.get_all(company_id=company1.id)
        deals_company2 = repo.get_all(company_id=company2.id)
        
        assert len(deals_company1) == 1
        assert len(deals_company2) == 1

    def test_get_all_deals_combined_filters(
        self, db_session: Session, sample_user: User
    ):
        """[BELIEF] DealRepository.get_all supports combined stage and company filters."""
        repo = DealRepository(db_session)
        company_repo = CompanyRepository(db_session)
        company1 = company_repo.create({"name": "Company 1", "website": None, "industry": None})
        company2 = company_repo.create({"name": "Company 2", "website": None, "industry": None})
        # Create deals with different stages and companies
        repo.create({
            "title": "Lead C1",
            "company_id": company1.id,
            "owner_id": sample_user.id,
            "value": 1000,
            "stage": DealStage.LEAD
        })
        repo.create({
            "title": "Won C1",
            "company_id": company1.id,
            "owner_id": sample_user.id,
            "value": 2000,
            "stage": DealStage.WON
        })
        repo.create({
            "title": "Lead C2",
            "company_id": company2.id,
            "owner_id": sample_user.id,
            "value": 3000,
            "stage": DealStage.LEAD
        })
        
        # Filter by company1 AND stage LEAD
        filtered = repo.get_all(stage=DealStage.LEAD, company_id=company1.id)
        
        assert len(filtered) == 1
        assert filtered[0].title == "Lead C1"

    def test_update_deal(self, db_session: Session, sample_deal: Deal):
        """[BELIEF] DealRepository.update modifies deal fields."""
        repo = DealRepository(db_session)
        
        updated = repo.update(sample_deal.id, {"title": "Updated Deal", "value": 99999})
        
        assert updated is not None
        assert updated.title == "Updated Deal"
        assert updated.value == 99999

    def test_delete_deal_without_activities(self, db_session: Session, sample_deal: Deal):
        """[BELIEF] DealRepository.delete removes deal without activities."""
        repo = DealRepository(db_session)
        deal_id = sample_deal.id
        
        result = repo.delete(deal_id)
        
        assert result is True
        assert repo.get_by_id(deal_id) is None

    def test_change_stage(self, db_session: Session, sample_deal: Deal):
        """[BELIEF] DealRepository.change_stage updates deal stage."""
        repo = DealRepository(db_session)
        
        updated = repo.change_stage(sample_deal.id, DealStage.QUALIFIED)
        
        assert updated is not None
        assert updated.stage == DealStage.QUALIFIED

    def test_change_stage_nonexistent_deal(self, db_session: Session):
        """[BELIEF] DealRepository.change_stage returns None for nonexistent deal."""
        repo = DealRepository(db_session)
        
        result = repo.change_stage(uuid.uuid4(), DealStage.WON)
        
        assert result is None

    def test_has_activities_returns_false_when_none(self, db_session: Session, sample_deal: Deal):
        """[BELIEF] DealRepository.has_activities returns False when deal has no activities."""
        repo = DealRepository(db_session)
        
        result = repo.has_activities(sample_deal.id)
        
        assert result is False

    def test_has_activities_returns_true_when_exist(
        self, db_session: Session, sample_deal: Deal
    ):
        """[BELIEF] DealRepository.has_activities returns True when deal has activities."""
        repo = DealRepository(db_session)
        activity_repo = ActivityRepository(db_session)
        # Create an activity
        activity_repo.create({
            "deal_id": sample_deal.id,
            "type": ActivityType.NOTE,
            "description": "Test activity"
        })
        
        result = repo.has_activities(sample_deal.id)
        
        assert result is True


# ============================================================================
# ActivityRepository Tests
# ============================================================================

class TestActivityRepository:
    """Tests for ActivityRepository CRUD operations."""

    def test_create_activity(self, db_session: Session, sample_deal: Deal):
        """[BELIEF] ActivityRepository.create creates a new activity."""
        repo = ActivityRepository(db_session)
        activity_data = {
            "deal_id": sample_deal.id,
            "type": ActivityType.CALL,
            "description": "Called the client"
        }
        
        activity = repo.create(activity_data)
        
        assert activity.id is not None
        assert activity.deal_id == sample_deal.id
        assert activity.type == ActivityType.CALL
        assert activity.description == "Called the client"
        assert activity.created_at is not None

    def test_get_by_id_existing_activity(
        self, db_session: Session, sample_deal: Deal
    ):
        """[BELIEF] ActivityRepository.get_by_id returns existing activity."""
        repo = ActivityRepository(db_session)
        activity = repo.create({
            "deal_id": sample_deal.id,
            "type": ActivityType.EMAIL,
            "description": "Sent email"
        })
        
        found = repo.get_by_id(activity.id)
        
        assert found is not None
        assert found.id == activity.id

    def test_get_by_id_nonexistent_activity(self, db_session: Session):
        """[BELIEF] ActivityRepository.get_by_id returns None for nonexistent UUID."""
        repo = ActivityRepository(db_session)
        
        found = repo.get_by_id(uuid.uuid4())
        
        assert found is None

    def test_get_by_deal_id_returns_activities(
        self, db_session: Session, sample_deal: Deal
    ):
        """[BELIEF] ActivityRepository.get_by_deal_id returns activities for a deal."""
        repo = ActivityRepository(db_session)
        # Create multiple activities
        repo.create({
            "deal_id": sample_deal.id,
            "type": ActivityType.CALL,
            "description": "First call"
        })
        repo.create({
            "deal_id": sample_deal.id,
            "type": ActivityType.EMAIL,
            "description": "Follow-up email"
        })
        
        activities = repo.get_by_deal_id(sample_deal.id)
        
        assert len(activities) == 2

    def test_get_by_deal_id_sorted_desc(
        self, db_session: Session, sample_deal: Deal
    ):
        """[BELIEF] ActivityRepository.get_by_deal_id returns activities sorted DESC by created_at."""
        import time
        repo = ActivityRepository(db_session)
        # Create activities with slight time difference
        activity1 = repo.create({
            "deal_id": sample_deal.id,
            "type": ActivityType.CALL,
            "description": "First"
        })
        # Small delay to ensure different timestamp
        time.sleep(0.05)
        activity2 = repo.create({
            "deal_id": sample_deal.id,
            "type": ActivityType.EMAIL,
            "description": "Second"
        })
        
        activities = repo.get_by_deal_id(sample_deal.id)
        
        # Most recent first (DESC order by created_at)
        # Verify we have 2 activities
        assert len(activities) == 2
        # Verify DESC order: first activity should have created_at >= second
        assert activities[0].created_at >= activities[1].created_at

    def test_get_by_deal_id_empty_for_nonexistent_deal(self, db_session: Session):
        """[BELIEF] ActivityRepository.get_by_deal_id returns empty list for nonexistent deal."""
        repo = ActivityRepository(db_session)
        
        activities = repo.get_by_deal_id(uuid.uuid4())
        
        assert activities == []

    def test_get_by_deal_id_pagination(
        self, db_session: Session, sample_deal: Deal
    ):
        """[BELIEF] ActivityRepository.get_by_deal_id respects pagination."""
        repo = ActivityRepository(db_session)
        # Create 5 activities
        for i in range(5):
            repo.create({
                "deal_id": sample_deal.id,
                "type": ActivityType.NOTE,
                "description": f"Note {i}"
            })
        
        page1 = repo.get_by_deal_id(sample_deal.id, skip=0, limit=2)
        page2 = repo.get_by_deal_id(sample_deal.id, skip=2, limit=2)
        
        assert len(page1) == 2
        assert len(page2) == 2

    def test_get_all_activities(
        self, db_session: Session, sample_deal: Deal
    ):
        """[BELIEF] ActivityRepository.get_all returns all activities."""
        repo = ActivityRepository(db_session)
        repo.create({
            "deal_id": sample_deal.id,
            "type": ActivityType.CALL,
            "description": "Call"
        })
        
        activities = repo.get_all()
        
        assert len(activities) == 1


# ============================================================================
# Adversarial Tests - Edge Cases and Boundary Conditions
# ============================================================================

class TestRepositoryAdversarialCases:
    """Adversarial tests for edge cases and boundary conditions."""

    # --- User Repository Edge Cases ---

    def test_user_create_with_minimal_fields(self, db_session: Session):
        """[BELIEF] User can be created with only required fields (email, name)."""
        repo = UserRepository(db_session)
        
        user = repo.create({"email": "minimal@example.com", "name": "Minimal"})
        
        assert user.id is not None
        assert user.email == "minimal@example.com"

    def test_user_get_by_email_case_sensitive(self, db_session: Session, sample_user: User):
        """[BELIEF] Email lookup is case-sensitive (SQLite default)."""
        repo = UserRepository(db_session)
        
        # Exact match should work
        found = repo.get_by_email("test@example.com")
        assert found is not None
        
        # Different case should not match
        not_found = repo.get_by_email("TEST@EXAMPLE.COM")
        assert not_found is None

    def test_user_update_empty_dict(self, db_session: Session, sample_user: User):
        """[BELIEF] Update with empty dict returns unchanged user."""
        repo = UserRepository(db_session)
        original_name = sample_user.name
        
        updated = repo.update(sample_user.id, {})
        
        assert updated is not None
        assert updated.name == original_name

    # --- Company Repository Edge Cases ---

    def test_company_create_with_null_optional_fields(self, db_session: Session):
        """[BELIEF] Company can be created with null website and industry."""
        repo = CompanyRepository(db_session)
        
        company = repo.create({"name": "No Website Corp", "website": None, "industry": None})
        
        assert company.id is not None
        assert company.website is None
        assert company.industry is None

    def test_company_has_deals_nonexistent_company(self, db_session: Session):
        """[BELIEF] has_deals returns False for nonexistent company."""
        repo = CompanyRepository(db_session)
        
        result = repo.has_deals(uuid.uuid4())
        
        assert result is False

    # --- Deal Repository Edge Cases ---

    def test_deal_create_with_zero_value(self, db_session: Session, sample_company: Company, sample_user: User):
        """[BELIEF] Deal can be created with zero value."""
        repo = DealRepository(db_session)
        
        deal = repo.create({
            "title": "Zero Value Deal",
            "company_id": sample_company.id,
            "owner_id": sample_user.id,
            "value": 0
        })
        
        assert deal.value == 0

    def test_deal_get_all_with_both_filters_none(
        self, db_session: Session, sample_deal: Deal
    ):
        """[BELIEF] get_all with None filters returns all deals."""
        repo = DealRepository(db_session)
        
        deals = repo.get_all(stage=None, company_id=None)
        
        assert len(deals) == 1

    def test_deal_has_activities_nonexistent_deal(self, db_session: Session):
        """[BELIEF] has_activities returns False for nonexistent deal."""
        repo = DealRepository(db_session)
        
        result = repo.has_activities(uuid.uuid4())
        
        assert result is False

    # --- Activity Repository Edge Cases ---

    def test_activity_create_all_types(
        self, db_session: Session, sample_deal: Deal
    ):
        """[BELIEF] Activity can be created with all ActivityType values."""
        repo = ActivityRepository(db_session)
        
        for activity_type in [ActivityType.CALL, ActivityType.EMAIL, ActivityType.MEETING, ActivityType.NOTE]:
            activity = repo.create({
                "deal_id": sample_deal.id,
                "type": activity_type,
                "description": f"Test {activity_type.value}"
            })
            assert activity.type == activity_type

    def test_activity_create_with_long_description(
        self, db_session: Session, sample_deal: Deal
    ):
        """[BELIEF] Activity can be created with long description."""
        repo = ActivityRepository(db_session)
        long_desc = "A" * 1000  # 1000 characters
        
        activity = repo.create({
            "deal_id": sample_deal.id,
            "type": ActivityType.NOTE,
            "description": long_desc
        })
        
        assert activity.description == long_desc

    # --- Pagination Boundary Tests ---

    def test_pagination_skip_beyond_total(self, db_session: Session):
        """[BELIEF] Pagination skip beyond total returns empty list."""
        repo = UserRepository(db_session)
        repo.create({"email": "only@example.com", "name": "Only User"})
        
        result = repo.get_all(skip=100, limit=10)
        
        assert result == []

    def test_pagination_limit_zero(self, db_session: Session, sample_user: User):
        """[BELIEF] Pagination with limit=0 returns empty list."""
        repo = UserRepository(db_session)
        
        result = repo.get_all(limit=0)
        
        assert result == []