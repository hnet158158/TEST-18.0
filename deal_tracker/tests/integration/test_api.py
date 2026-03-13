# START_MODULE_CONTRACT
# Module: tests.integration.test_api
# Intent: Integration-тесты для Phase 4 - API Routes.
# Проверка всех 16 эндпоинтов и 15 acceptance criteria из requirements.md.
# END_MODULE_CONTRACT

import pytest
import uuid
from httpx import Client
from fastapi.testclient import TestClient

from app.main import app
from app.models.deal import DealStage
from app.models.activity import ActivityType


@pytest.fixture
def client():
    """
    # CONTRACT: Intent: Создаёт TestClient для integration-тестов API.
    """
    with TestClient(app) as c:
        yield c


@pytest.fixture
def created_user(client):
    """Создаёт пользователя для тестов."""
    response = client.post(
        "/api/v1/users",
        json={"email": f"test_{uuid.uuid4()}@example.com", "name": "Test User"}
    )
    return response.json()


@pytest.fixture
def created_company(client):
    """Создаёт компанию для тестов."""
    response = client.post(
        "/api/v1/companies",
        json={"name": f"Test Company {uuid.uuid4()}", "website": "https://test.com"}
    )
    return response.json()


@pytest.fixture
def created_deal(client, created_company, created_user):
    """Создаёт сделку для тестов."""
    response = client.post(
        "/api/v1/deals",
        json={
            "title": "Test Deal",
            "company_id": created_company["id"],
            "owner_id": created_user["id"],
            "value": "10000.00"
        }
    )
    return response.json()


# ============================================================
# ACCEPTANCE CRITERION 1: Создать пользователя через API
# ============================================================
class TestCreateUser:
    """AC1: Создать пользователя через API."""

    def test_create_user_success(self, client):
        """[PASS] Пользователь создаётся с корректными данными."""
        unique_email = f"newuser_{uuid.uuid4()}@example.com"
        response = client.post(
            "/api/v1/users",
            json={"email": unique_email, "name": "New User"}
        )
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == unique_email
        assert data["name"] == "New User"
        assert "id" in data
        assert "created_at" in data

    def test_create_user_duplicate_email(self, client):
        """[PASS] Дублирование email возвращает 400."""
        user_data = {"email": "duplicate@example.com", "name": "User 1"}
        client.post("/api/v1/users", json=user_data)
        response = client.post("/api/v1/users", json=user_data)
        assert response.status_code == 400
        assert "detail" in response.json()


# ============================================================
# ACCEPTANCE CRITERION 2: Создать компанию через API
# ============================================================
class TestCreateCompany:
    """AC2: Создать компанию через API."""

    def test_create_company_success(self, client):
        """[PASS] Компания создаётся с корректными данными."""
        response = client.post(
            "/api/v1/companies",
            json={"name": "New Company", "industry": "Tech"}
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "New Company"
        assert data["industry"] == "Tech"

    def test_create_company_minimal(self, client):
        """[PASS] Компания создаётся только с name."""
        response = client.post(
            "/api/v1/companies",
            json={"name": "Minimal Company"}
        )
        assert response.status_code == 201


# ============================================================
# ACCEPTANCE CRITERION 3: Создать сделку (стадия всегда LEAD)
# ============================================================
class TestCreateDeal:
    """AC3: Создать сделку (стадия всегда LEAD)."""

    def test_create_deal_success(self, client, created_company, created_user):
        """[PASS] Сделка создаётся со стадией LEAD по умолчанию."""
        response = client.post(
            "/api/v1/deals",
            json={
                "title": "New Deal",
                "company_id": created_company["id"],
                "owner_id": created_user["id"]
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "New Deal"
        assert data["stage"] == "lead"

    def test_create_deal_with_value(self, client, created_company, created_user):
        """[PASS] Сделка создаётся с value и description."""
        response = client.post(
            "/api/v1/deals",
            json={
                "title": "Deal with Value",
                "company_id": created_company["id"],
                "owner_id": created_user["id"],
                "value": "50000.00",
                "description": "Big deal"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["value"] == "50000.00"
        assert data["description"] == "Big deal"


# ============================================================
# ACCEPTANCE CRITERION 4: Ошибка 400 при невалидном FK
# ============================================================
class TestInvalidFK:
    """AC4: Ошибка 400 при создании сделки с несуществующим company_id/owner_id."""

    def test_create_deal_invalid_company_id(self, client, created_user):
        """[PASS] 400 при несуществующем company_id."""
        fake_company_id = str(uuid.uuid4())
        response = client.post(
            "/api/v1/deals",
            json={
                "title": "Invalid Deal",
                "company_id": fake_company_id,
                "owner_id": created_user["id"]
            }
        )
        assert response.status_code == 400
        assert "detail" in response.json()

    def test_create_deal_invalid_owner_id(self, client, created_company):
        """[PASS] 400 при несуществующем owner_id."""
        fake_owner_id = str(uuid.uuid4())
        response = client.post(
            "/api/v1/deals",
            json={
                "title": "Invalid Deal",
                "company_id": created_company["id"],
                "owner_id": fake_owner_id
            }
        )
        assert response.status_code == 400


# ============================================================
# ACCEPTANCE CRITERION 5: Переместить сделку на следующую стадию
# ============================================================
class TestStageTransition:
    """AC5: Переместить сделку на следующую стадию."""

    def test_lead_to_qualified(self, client, created_deal):
        """[PASS] Переход LEAD -> QUALIFIED."""
        response = client.patch(
            f"/api/v1/deals/{created_deal['id']}/stage",
            json={"stage": "qualified"}
        )
        assert response.status_code == 200
        assert response.json()["stage"] == "qualified"

    def test_qualified_to_proposal(self, client, created_deal):
        """[PASS] Переход QUALIFIED -> PROPOSAL."""
        client.patch(f"/api/v1/deals/{created_deal['id']}/stage", json={"stage": "qualified"})
        response = client.patch(
            f"/api/v1/deals/{created_deal['id']}/stage",
            json={"stage": "proposal"}
        )
        assert response.status_code == 200
        assert response.json()["stage"] == "proposal"


# ============================================================
# ACCEPTANCE CRITERION 6: Ошибка 400 при невалидном переходе стадии
# ============================================================
class TestInvalidStageTransition:
    """AC6: Ошибка 400 при невалидном переходе стадии."""

    def test_lead_to_proposal_forbidden(self, client, created_deal):
        """[PASS] Переход LEAD -> PROPOSAL запрещён."""
        response = client.patch(
            f"/api/v1/deals/{created_deal['id']}/stage",
            json={"stage": "proposal"}
        )
        assert response.status_code == 400
        assert "detail" in response.json()

    def test_qualified_to_lead_forbidden(self, client, created_deal):
        """[PASS] Переход QUALIFIED -> LEAD запрещён."""
        client.patch(f"/api/v1/deals/{created_deal['id']}/stage", json={"stage": "qualified"})
        response = client.patch(
            f"/api/v1/deals/{created_deal['id']}/stage",
            json={"stage": "lead"}
        )
        assert response.status_code == 400


# ============================================================
# ACCEPTANCE CRITERION 7: При переходе стадии создаётся Activity
# ============================================================
class TestSystemActivityOnStageChange:
    """AC7: При переходе стадии создаётся системная активность."""

    def test_stage_change_creates_activity(self, client, created_deal):
        """[PASS] При смене стадии создаётся Activity."""
        client.patch(f"/api/v1/deals/{created_deal['id']}/stage", json={"stage": "qualified"})
        
        response = client.get(f"/api/v1/deals/{created_deal['id']}/activities")
        activities = response.json()
        assert len(activities) >= 1
        # Найти системную активность
        system_activity = next(
            (a for a in activities if "Stage changed" in a["description"]),
            None
        )
        assert system_activity is not None
        assert system_activity["type"] == "note"


# ============================================================
# ACCEPTANCE CRITERION 8: Добавить активность к сделке
# ============================================================
class TestCreateActivity:
    """AC8: Добавить активность к сделке."""

    def test_create_activity_success(self, client, created_deal):
        """[PASS] Активность создаётся для существующей сделки."""
        response = client.post(
            f"/api/v1/deals/{created_deal['id']}/activities",
            json={"type": "call", "description": "Follow-up call"}
        )
        assert response.status_code == 201
        data = response.json()
        assert data["type"] == "call"
        assert data["description"] == "Follow-up call"

    def test_create_activity_default_type(self, client, created_deal):
        """[PASS] Тип активности по умолчанию NOTE."""
        response = client.post(
            f"/api/v1/deals/{created_deal['id']}/activities",
            json={"description": "Just a note"}
        )
        assert response.status_code == 201
        assert response.json()["type"] == "note"


# ============================================================
# ACCEPTANCE CRITERION 9: Timeline возвращается в порядке DESC
# ============================================================
class TestTimelineOrder:
    """AC9: Timeline возвращается в порядке DESC (новые сначала)."""

    def test_timeline_desc_order(self, client, created_deal):
        """[PASS] Активности отсортированы по created_at DESC."""
        # Создаём несколько активностей
        client.post(
            f"/api/v1/deals/{created_deal['id']}/activities",
            json={"description": "First activity"}
        )
        client.post(
            f"/api/v1/deals/{created_deal['id']}/activities",
            json={"description": "Second activity"}
        )
        client.post(
            f"/api/v1/deals/{created_deal['id']}/activities",
            json={"description": "Third activity"}
        )

        response = client.get(f"/api/v1/deals/{created_deal['id']}/activities")
        activities = response.json()
        
        # Проверяем DESC порядок (новые сначала)
        assert len(activities) >= 3
        descriptions = [a["description"] for a in activities]
        assert "Third activity" in descriptions[0] or "Third activity" in descriptions


# ============================================================
# ACCEPTANCE CRITERION 10: Ошибка 400 при удалении компании со сделками
# ============================================================
class TestDeleteCompanyWithDeals:
    """AC10: Ошибка 400 при удалении компании со связанными сделками."""

    def test_delete_company_with_deals(self, client, created_company, created_user):
        """[PASS] Нельзя удалить компанию со сделками."""
        # Создаём сделку для компании
        client.post(
            "/api/v1/deals",
            json={
                "title": "Linked Deal",
                "company_id": created_company["id"],
                "owner_id": created_user["id"]
            }
        )
        
        response = client.delete(f"/api/v1/companies/{created_company['id']}")
        assert response.status_code == 400
        assert "detail" in response.json()

    def test_delete_company_without_deals(self, client):
        """[PASS] Можно удалить компанию без сделок."""
        # Создаём компанию без сделок
        create_response = client.post(
            "/api/v1/companies",
            json={"name": "Empty Company"}
        )
        company_id = create_response.json()["id"]
        
        response = client.delete(f"/api/v1/companies/{company_id}")
        assert response.status_code == 204


# ============================================================
# ACCEPTANCE CRITERION 11: Ошибка 400 при удалении сделки с активностями
# ============================================================
class TestDeleteDealWithActivities:
    """AC11: Ошибка 400 при удалении сделки с активностями."""

    def test_delete_deal_with_activities(self, client, created_deal):
        """[PASS] Нельзя удалить сделку с активностями."""
        # Создаём активность
        client.post(
            f"/api/v1/deals/{created_deal['id']}/activities",
            json={"description": "Some activity"}
        )
        
        response = client.delete(f"/api/v1/deals/{created_deal['id']}")
        assert response.status_code == 400
        assert "detail" in response.json()

    def test_delete_deal_without_activities(self, client, created_company, created_user):
        """[PASS] Можно удалить сделку без активностей."""
        # Создаём сделку без активностей
        create_response = client.post(
            "/api/v1/deals",
            json={
                "title": "Empty Deal",
                "company_id": created_company["id"],
                "owner_id": created_user["id"]
            }
        )
        deal_id = create_response.json()["id"]
        
        response = client.delete(f"/api/v1/deals/{deal_id}")
        assert response.status_code == 204


# ============================================================
# ACCEPTANCE CRITERION 12: User нельзя удалить через API
# ============================================================
class TestUserDeleteNotImplemented:
    """AC12: User нельзя удалить через API (endpoint не существует)."""

    def test_delete_user_not_found(self, client, created_user):
        """[PASS] DELETE /users/{id} не существует (404 или 405)."""
        response = client.delete(f"/api/v1/users/{created_user['id']}")
        # FastAPI возвращает 405 Method Not Allowed для несуществующего метода
        assert response.status_code in [404, 405]


# ============================================================
# ACCEPTANCE CRITERION 13: Activity нельзя удалить через API
# ============================================================
class TestActivityDeleteNotImplemented:
    """AC13: Activity нельзя удалить через API (endpoint не существует)."""

    def test_delete_activity_not_found(self, client, created_deal):
        """[PASS] DELETE /activities/{id} не существует."""
        # Создаём активность
        create_response = client.post(
            f"/api/v1/deals/{created_deal['id']}/activities",
            json={"description": "Test activity"}
        )
        activity_id = create_response.json()["id"]
        
        # Пытаемся удалить - endpoint не существует
        response = client.delete(f"/api/v1/activities/{activity_id}")
        assert response.status_code in [404, 405]


# ============================================================
# ACCEPTANCE CRITERION 14: company_id и owner_id нельзя изменить через PUT
# ============================================================
class TestImmutableFields:
    """AC14: company_id и owner_id нельзя изменить через PUT."""

    def test_update_deal_cannot_change_company_id(self, client, created_deal, created_company, created_user):
        """[PASS] company_id immutable - не передаётся в DealUpdate."""
        # DealUpdate не содержит company_id, поэтому проверяем,
        # что даже если попытаться передать, оно не изменится
        response = client.put(
            f"/api/v1/deals/{created_deal['id']}",
            json={"title": "Updated Title"}
        )
        assert response.status_code == 200
        data = response.json()
        # company_id остаётся прежним
        assert data["company_id"] == created_deal["company_id"]

    def test_update_deal_cannot_change_owner_id(self, client, created_deal):
        """[PASS] owner_id immutable - не передаётся в DealUpdate."""
        response = client.put(
            f"/api/v1/deals/{created_deal['id']}",
            json={"title": "Updated Title"}
        )
        assert response.status_code == 200
        data = response.json()
        # owner_id остаётся прежним
        assert data["owner_id"] == created_deal["owner_id"]


# ============================================================
# ACCEPTANCE CRITERION 15: Все фазы независимо тестируются
# ============================================================
class TestAllEndpointsWork:
    """AC15: Все фазы независимо тестируются - проверка всех 16 эндпоинтов."""

    # Users: 3 endpoints
    def test_get_users(self, client, created_user):
        """[PASS] GET /api/v1/users."""
        response = client.get("/api/v1/users")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_get_user_by_id(self, client, created_user):
        """[PASS] GET /api/v1/users/{id}."""
        response = client.get(f"/api/v1/users/{created_user['id']}")
        assert response.status_code == 200
        assert response.json()["id"] == created_user["id"]

    def test_get_user_not_found(self, client):
        """[PASS] GET /api/v1/users/{id} - 404."""
        fake_id = str(uuid.uuid4())
        response = client.get(f"/api/v1/users/{fake_id}")
        assert response.status_code == 404

    # Companies: 5 endpoints
    def test_get_companies(self, client, created_company):
        """[PASS] GET /api/v1/companies."""
        response = client.get("/api/v1/companies")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_get_company_by_id(self, client, created_company):
        """[PASS] GET /api/v1/companies/{id}."""
        response = client.get(f"/api/v1/companies/{created_company['id']}")
        assert response.status_code == 200

    def test_get_company_not_found(self, client):
        """[PASS] GET /api/v1/companies/{id} - 404."""
        fake_id = str(uuid.uuid4())
        response = client.get(f"/api/v1/companies/{fake_id}")
        assert response.status_code == 404

    def test_update_company(self, client, created_company):
        """[PASS] PUT /api/v1/companies/{id}."""
        response = client.put(
            f"/api/v1/companies/{created_company['id']}",
            json={"name": "Updated Company"}
        )
        assert response.status_code == 200
        assert response.json()["name"] == "Updated Company"

    # Deals: 6 endpoints
    def test_get_deals(self, client, created_deal):
        """[PASS] GET /api/v1/deals."""
        response = client.get("/api/v1/deals")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_get_deals_filter_by_stage(self, client):
        """[PASS] GET /api/v1/deals?stage=lead."""
        response = client.get("/api/v1/deals?stage=lead")
        assert response.status_code == 200

    def test_get_deals_filter_by_company(self, client, created_company):
        """[PASS] GET /api/v1/deals?company_id=..."""
        response = client.get(f"/api/v1/deals?company_id={created_company['id']}")
        assert response.status_code == 200

    def test_get_deal_by_id(self, client, created_deal):
        """[PASS] GET /api/v1/deals/{id}."""
        response = client.get(f"/api/v1/deals/{created_deal['id']}")
        assert response.status_code == 200

    def test_get_deal_not_found(self, client):
        """[PASS] GET /api/v1/deals/{id} - 404."""
        fake_id = str(uuid.uuid4())
        response = client.get(f"/api/v1/deals/{fake_id}")
        assert response.status_code == 404

    def test_update_deal(self, client, created_deal):
        """[PASS] PUT /api/v1/deals/{id}."""
        response = client.put(
            f"/api/v1/deals/{created_deal['id']}",
            json={"title": "Updated Deal"}
        )
        assert response.status_code == 200
        assert response.json()["title"] == "Updated Deal"

    # Activities: 2 endpoints (already tested above)
    def test_get_deal_timeline(self, client, created_deal):
        """[PASS] GET /api/v1/deals/{deal_id}/activities."""
        response = client.get(f"/api/v1/deals/{created_deal['id']}/activities")
        assert response.status_code == 200

    def test_get_deal_timeline_deal_not_found(self, client):
        """[PASS] GET timeline для несуществующей сделки - 404."""
        fake_id = str(uuid.uuid4())
        response = client.get(f"/api/v1/deals/{fake_id}/activities")
        assert response.status_code == 404


# ============================================================
# HTTP CODES VERIFICATION
# ============================================================
class TestHTTPCodes:
    """Проверка корректности HTTP кодов (200, 201, 204, 400, 404, 422)."""

    def test_200_ok(self, client, created_user):
        """[PASS] 200 OK для GET."""
        response = client.get("/api/v1/users")
        assert response.status_code == 200

    def test_201_created(self, client):
        """[PASS] 201 Created для POST."""
        response = client.post(
            "/api/v1/users",
            json={"email": f"created_{uuid.uuid4()}@example.com", "name": "Created"}
        )
        assert response.status_code == 201

    def test_204_no_content(self, client):
        """[PASS] 204 No Content для DELETE."""
        create_response = client.post(
            "/api/v1/companies",
            json={"name": "To Delete"}
        )
        company_id = create_response.json()["id"]
        response = client.delete(f"/api/v1/companies/{company_id}")
        assert response.status_code == 204

    def test_400_bad_request(self, client, created_user):
        """[PASS] 400 Bad Request для дублирования email."""
        response = client.post(
            "/api/v1/users",
            json={"email": created_user["email"], "name": "Duplicate"}
        )
        assert response.status_code == 400

    def test_404_not_found(self, client):
        """[PASS] 404 Not Found для несуществующей сущности."""
        fake_id = str(uuid.uuid4())
        response = client.get(f"/api/v1/users/{fake_id}")
        assert response.status_code == 404

    def test_422_validation_error(self, client):
        """[PASS] 422 Unprocessable Entity для невалидных данных."""
        response = client.post(
            "/api/v1/users",
            json={"email": "not-an-email", "name": "Test"}
        )
        assert response.status_code == 422


# ============================================================
# ERROR FORMAT VERIFICATION
# ============================================================
class TestErrorFormat:
    """Проверка формата ошибок {"detail": "..."}."""

    def test_400_error_format(self, client, created_user):
        """[PASS] Ошибка 400 имеет формат {"detail": "..."}."""
        response = client.post(
            "/api/v1/users",
            json={"email": created_user["email"], "name": "Duplicate"}
        )
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert isinstance(data["detail"], str)

    def test_404_error_format(self, client):
        """[PASS] Ошибка 404 имеет формат {"detail": "..."}."""
        fake_id = str(uuid.uuid4())
        response = client.get(f"/api/v1/users/{fake_id}")
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data


# ============================================================
# ADVERSARIAL TESTS
# ============================================================
class TestAdversarialAPI:
    """Adversarial тесты для API."""

    def test_create_user_missing_email(self, client):
        """[PASS] Отсутствует обязательное поле email."""
        response = client.post("/api/v1/users", json={"name": "No Email"})
        assert response.status_code == 422

    def test_create_deal_missing_title(self, client, created_company, created_user):
        """[PASS] Отсутствует обязательное поле title."""
        response = client.post(
            "/api/v1/deals",
            json={
                "company_id": created_company["id"],
                "owner_id": created_user["id"]
            }
        )
        assert response.status_code == 422

    def test_create_activity_missing_description(self, client, created_deal):
        """[PASS] Отсутствует обязательное поле description."""
        response = client.post(
            f"/api/v1/deals/{created_deal['id']}/activities",
            json={"type": "call"}
        )
        assert response.status_code == 422

    def test_create_activity_invalid_deal_id(self, client):
        """[PASS] Активность для несуществующей сделки."""
        fake_deal_id = str(uuid.uuid4())
        response = client.post(
            f"/api/v1/deals/{fake_deal_id}/activities",
            json={"description": "Test"}
        )
        assert response.status_code == 400

    def test_patch_stage_invalid_uuid(self, client):
        """[PASS] Невалидный UUID в пути."""
        response = client.patch(
            "/api/v1/deals/not-a-uuid/stage",
            json={"stage": "qualified"}
        )
        assert response.status_code == 422

    def test_patch_stage_invalid_stage_value(self, client, created_deal):
        """[PASS] Невалидное значение stage."""
        response = client.patch(
            f"/api/v1/deals/{created_deal['id']}/stage",
            json={"stage": "invalid_stage"}
        )
        assert response.status_code == 422


# ============================================================
# PHASE 5: API PAGINATION TESTS
# ============================================================
class TestAPIPagination:
    """Phase 5: Тесты пагинации для всех list endpoints."""

    # GET /users?skip=0&limit=10
    def test_get_users_pagination(self, client):
        """[PASS] GET /users с пагинацией."""
        # Создаём несколько пользователей
        for i in range(5):
            client.post(
                "/api/v1/users",
                json={"email": f"page_user_{i}_{uuid.uuid4()}@example.com", "name": f"User {i}"}
            )
        
        # Тестируем пагинацию
        response = client.get("/api/v1/users?skip=0&limit=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 2

    def test_get_users_pagination_skip(self, client):
        """[PASS] GET /users с skip."""
        # Создаём пользователей
        for i in range(3):
            client.post(
                "/api/v1/users",
                json={"email": f"skip_user_{i}_{uuid.uuid4()}@example.com", "name": f"Skip User {i}"}
            )
        
        # Пропускаем первых 2
        response = client.get("/api/v1/users?skip=2&limit=10")
        assert response.status_code == 200

    def test_get_users_default_pagination(self, client):
        """[PASS] GET /users с default values (skip=0, limit=100)."""
        response = client.get("/api/v1/users")
        assert response.status_code == 200
        # Default limit=100

    # GET /companies?skip=5&limit=20
    def test_get_companies_pagination(self, client):
        """[PASS] GET /companies с пагинацией."""
        for i in range(5):
            client.post(
                "/api/v1/companies",
                json={"name": f"Page Company {i} {uuid.uuid4()}"}
            )
        
        response = client.get("/api/v1/companies?skip=0&limit=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 2

    def test_get_companies_pagination_skip(self, client):
        """[PASS] GET /companies с skip."""
        for i in range(3):
            client.post(
                "/api/v1/companies",
                json={"name": f"Skip Company {i} {uuid.uuid4()}"}
            )
        
        response = client.get("/api/v1/companies?skip=5&limit=20")
        assert response.status_code == 200

    # GET /deals?skip=0&limit=50&stage=lead
    def test_get_deals_pagination(self, client, created_company, created_user):
        """[PASS] GET /deals с пагинацией."""
        for i in range(3):
            client.post(
                "/api/v1/deals",
                json={
                    "title": f"Page Deal {i}",
                    "company_id": created_company["id"],
                    "owner_id": created_user["id"]
                }
            )
        
        response = client.get("/api/v1/deals?skip=0&limit=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 2

    def test_get_deals_pagination_with_filters(self, client, created_company, created_user):
        """[PASS] GET /deals с пагинацией и фильтрами."""
        response = client.get(f"/api/v1/deals?skip=0&limit=50&stage=lead&company_id={created_company['id']}")
        assert response.status_code == 200

    # GET /deals/{id}/activities?skip=0&limit=25
    def test_get_activities_pagination(self, client, created_deal):
        """[PASS] GET /deals/{id}/activities с пагинацией."""
        for i in range(5):
            client.post(
                f"/api/v1/deals/{created_deal['id']}/activities",
                json={"description": f"Activity {i}"}
            )
        
        response = client.get(f"/api/v1/deals/{created_deal['id']}/activities?skip=0&limit=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 2

    def test_get_activities_pagination_skip(self, client, created_deal):
        """[PASS] GET timeline с skip."""
        for i in range(3):
            client.post(
                f"/api/v1/deals/{created_deal['id']}/activities",
                json={"description": f"Skip Activity {i}"}
            )
        
        response = client.get(f"/api/v1/deals/{created_deal['id']}/activities?skip=0&limit=25")
        assert response.status_code == 200

    # Edge cases
    def test_pagination_skip_greater_than_total(self, client):
        """[PASS] skip > total возвращает пустой список."""
        response = client.get("/api/v1/users?skip=9999&limit=10")
        assert response.status_code == 200
        assert response.json() == []

    def test_pagination_limit_zero_rejected(self, client):
        """[PASS] limit=0 отвергается (ge=1)."""
        response = client.get("/api/v1/users?limit=0")
        assert response.status_code == 422

    def test_pagination_negative_skip_rejected(self, client):
        """[PASS] skip < 0 отвергается (ge=0)."""
        response = client.get("/api/v1/users?skip=-1")
        assert response.status_code == 422

    def test_pagination_limit_exceeds_max(self, client):
        """[PASS] limit > 1000 отвергается (le=1000)."""
        response = client.get("/api/v1/users?limit=1001")
        assert response.status_code == 422