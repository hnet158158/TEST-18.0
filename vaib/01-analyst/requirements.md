# Deal Tracker API — Requirements Document

**Версия:** 1.2  
**Дата:** 2026-03-13  
**Статус:** Finalized  
**Режим:** PROTOTYPE

---

## 1. Intent Summary (AAG Model)

| Компонент | Значение |
|-----------|----------|
| **Actor** | Backend-разработчик / Система |
| **Action** | Создать Deal Tracker API с фазовой архитектурой |
| **Goal** | Отслеживание сделок через стадии с хронологической историей активностей |

---

## 2. Technology Stack

| Компонент | Решение |
|-----------|---------|
| **Язык** | Python 3.11+ |
| **Фреймворк** | FastAPI |
| **База данных** | SQLite (zero-config, file-based) |
| **ORM** | SQLAlchemy 2.0 |
| **API формат** | REST с версионностью `/api/v1/` |
| **Масштаб** | Прототип для демо (десятки сделок) |

---

## 3. Core Entities

### 3.1 User
```
User {
  id: UUID (PK)
  email: String (unique, not null)
  name: String (not null)
  created_at: DateTime (auto)
  updated_at: DateTime (auto)
}
```
**Lifecycle:** Нельзя удалить через API. Только через БД администратором.

### 3.2 Company
```
Company {
  id: UUID (PK)
  name: String (not null)
  website: String (nullable)
  industry: String (nullable)
  created_at: DateTime (auto)
  updated_at: DateTime (auto)
}
```
**Lifecycle:** Можно удалить только если нет связанных Deal.

### 3.3 Deal
```
Deal {
  id: UUID (PK)
  title: String (not null)
  company_id: UUID (FK -> Company, not null, immutable)
  owner_id: UUID (FK -> User, not null, immutable)
  stage: Enum[DealStage] (default: LEAD)
  value: Decimal (nullable)
  description: Text (nullable)
  created_at: DateTime (auto)
  updated_at: DateTime (auto)
}
```
**Lifecycle:** Можно удалить только если нет связанных Activity.

### 3.4 Activity
```
Activity {
  id: UUID (PK)
  deal_id: UUID (FK -> Deal, not null)
  type: Enum[ActivityType] (default: NOTE)
  description: Text (not null)
  created_at: DateTime (auto)
}
```
**Lifecycle:** Immutable. Нельзя удалить или изменить. Является исторической записью.

---

## 4. Enumerations

### 4.1 DealStage (фиксированный пайплайн)
```python
class DealStage(str, Enum):
    LEAD = "lead"
    QUALIFIED = "qualified"
    PROPOSAL = "proposal"
    NEGOTIATION = "negotiation"
    WON = "won"
    LOST = "lost"
```

**Граф переходов:**
```
LEAD → QUALIFIED → PROPOSAL → NEGOTIATION → WON
  ↓         ↓           ↓           ↓        ↓
  └─────────┴───────────┴───────────┴────→ LOST

WON → LEAD (реанимация)
LOST → LEAD (реанимация)
```

**Правила:**
1. Переход вперёд на следующую стадию — разрешён.
2. Переход на `WON` или `LOST` из любой стадии — разрешён.
3. Переход назад — запрещён, **кроме** `WON` → `LEAD` и `LOST` → `LEAD` (реанимация).
4. `WON` и `LOST` — терминальные, только переход на `LEAD` разрешён.

**Таблица допустимых переходов:**
| From | To |
|------|-----|
| LEAD | QUALIFIED, WON, LOST |
| QUALIFIED | PROPOSAL, WON, LOST |
| PROPOSAL | NEGOTIATION, WON, LOST |
| NEGOTIATION | WON, LOST |
| WON | LEAD |
| LOST | LEAD |

### 4.2 ActivityType (фиксированные типы)
```python
class ActivityType(str, Enum):
    CALL = "call"
    EMAIL = "email"
    MEETING = "meeting"
    NOTE = "note"
```

---

## 5. API Endpoints

### 5.1 Users
| Метод | Endpoint | Описание | Request Body | Response |
|-------|----------|----------|--------------|----------|
| POST | `/api/v1/users` | Создать пользователя | `{email, name}` | `User` |
| GET | `/api/v1/users` | Список пользователей | — | `User[]` |
| GET | `/api/v1/users/{id}` | Получить пользователя | — | `User` |

**Примечание:** DELETE не реализуется. User нельзя удалить через API.

### 5.2 Companies
| Метод | Endpoint | Описание | Request Body | Response |
|-------|----------|----------|--------------|----------|
| POST | `/api/v1/companies` | Создать компанию | `{name, website?, industry?}` | `Company` |
| GET | `/api/v1/companies` | Список компаний | — | `Company[]` |
| GET | `/api/v1/companies/{id}` | Получить компанию | — | `Company` |
| PUT | `/api/v1/companies/{id}` | Обновить компанию | `{name?, website?, industry?}` | `Company` |
| DELETE | `/api/v1/companies/{id}` | Удалить компанию | — | `204 No Content` |

### 5.3 Deals
| Метод | Endpoint | Описание | Request Body | Response |
|-------|----------|----------|--------------|----------|
| POST | `/api/v1/deals` | Создать сделку | `{title, company_id, owner_id, value?, description?}` | `Deal` |
| GET | `/api/v1/deals` | Список сделок | Query: `?stage=&company_id=` | `Deal[]` |
| GET | `/api/v1/deals/{id}` | Получить сделку | — | `Deal` |
| PUT | `/api/v1/deals/{id}` | Обновить сделку | `{title?, value?, description?}` | `Deal` |
| PATCH | `/api/v1/deals/{id}/stage` | Изменить стадию | `{stage}` | `Deal` |
| DELETE | `/api/v1/deals/{id}` | Удалить сделку | — | `204 No Content` |

**Примечание:** PUT не позволяет изменять `company_id` и `owner_id` (immutable).

### 5.4 Activities
| Метод | Endpoint | Описание | Request Body | Response |
|-------|----------|----------|--------------|----------|
| POST | `/api/v1/deals/{deal_id}/activities` | Добавить активность | `{type?, description}` | `Activity` |
| GET | `/api/v1/deals/{deal_id}/activities` | Timeline сделки | — | `Activity[]` |

**Примечание:** DELETE и PUT не реализуются. Activity immutable.

---

## 6. Behavior Requirements

### 6.1 Создание пользователя
- Обязательные поля: `email`, `name`.
- `email` должен быть уникальным.
- При дублировании email → `400 Bad Request`.

### 6.2 Создание компании
- Обязательное поле: `name`.
- `website`, `industry` — опциональны.

### 6.3 Создание сделки
- Обязательные поля: `title`, `company_id`, `owner_id`.
- `stage` — нельзя указать при создании, всегда `LEAD`.
- `value`, `description` — опциональны.
- `company_id` и `owner_id` — immutable после создания.
- Валидация FK:
  - Если `company_id` не существует → `400 Bad Request` с сообщением.
  - Если `owner_id` не существует → `400 Bad Request` с сообщением.

### 6.4 Обновление сделки
- Разрешено обновлять: `title`, `value`, `description`.
- Запрещено обновлять: `company_id`, `owner_id`, `stage`.
- Для изменения `stage` использовать отдельный эндпоинт `PATCH /deals/{id}/stage`.

### 6.5 Изменение стадии сделки
- Эндпоинт: `PATCH /api/v1/deals/{id}/stage`.
- Request: `{"stage": "new_stage"}`.
- Валидация по таблице переходов (раздел 4.1).
- При невалидном переходе → `400 Bad Request` с сообщением о допустимых стадиях.
- При успешном переходе:
  - Обновить `stage` в Deal.
  - Создать Activity с `type=NOTE`, `description="Stage changed from {old} to {new}"`.

### 6.6 Добавление активности
- Обязательное поле: `description`.
- Опциональное поле: `type` (по умолчанию `NOTE`).
- Валидация FK:
  - Если `deal_id` не существует → `400 Bad Request`.

### 6.7 Timeline сделки
- Эндпоинт: `GET /api/v1/deals/{deal_id}/activities`.
- Сортировка: `created_at DESC` (новые сначала).
- Включает все активности, включая системные (переходы стадий).
- Если сделка не существует → `404 Not Found`.

### 6.8 Удаление сущностей

**Стратегия: RESTRICT для всех связей.**

| Удаляемая сущность | Проверка | Код ответа при наличии связей |
|--------------------|----------|-------------------------------|
| Company | Есть Deal с этим company_id? | `400 Bad Request` |
| Deal | Есть Activity с этим deal_id? | `400 Bad Request` |
| User | — | Не реализовано (нельзя удалить) |
| Activity | — | Не реализовано (immutable) |

**Сообщение об ошибке:** `Cannot delete {entity} because it has associated {related_entities}`.

---

## 7. Error Responses

Все ошибки возвращаются в едином формате:
```json
{
  "detail": "Human readable message"
}
```

| Код | Ситуация |
|-----|----------|
| 400 | Неверный запрос, невалидный переход стадии, нарушение FK, дублирование email |
| 404 | Сущность не найдена |
| 422 | Ошибка валидации Pydantic |

---

## 8. Phase Boundaries (Strict)

### Phase 1: Models & Database
- SQLAlchemy модели для User, Company, Deal, Activity.
- Enum классы DealStage, ActivityType.
- Скрипт создания БД (create_tables).
- **Done Criteria:** Модели импортируются без ошибок, БД создаётся, таблицы существуют.

### Phase 2: Repositories
- CRUD операции для каждой сущности.
- Методы:
  - User: create, get_by_id, get_all, get_by_email
  - Company: create, get_by_id, get_all, update, delete, has_deals
  - Deal: create, get_by_id, get_all, update, delete, change_stage, has_activities
  - Activity: create, get_by_deal_id
- **Done Criteria:** Unit-тесты для всех методов проходят.

### Phase 3: Services
- User: create_user, get_user, get_users
- Company: create_company, get_company, get_companies, update_company, delete_company
- Deal: create_deal, get_deal, get_deals, update_deal, delete_deal, change_deal_stage
- Activity: create_activity, get_deal_timeline
- Валидация переходов стадий.
- Валидация FK.
- Создание системных активностей.
- **Done Criteria:** Unit-тесты для бизнес-логики проходят.

### Phase 4: API Routes
- FastAPI роуты для всех эндпоинтов.
- Pydantic схемы для request/response.
- Обработка ошибок с корректными HTTP кодами.
- **Done Criteria:** Integration-тесты через TestClient проходят.

---

## 9. Negative Constraints

| Запрещено | Причина |
|-----------|---------|
| Аутентификация/авторизация | Не требуется в первой итерации |
| Frontend | Backend only |
| WebSocket/Real-time | Избыточно для прототипа |
| Кэширование | Избыточно для прототипа |
| Микросервисная архитектура | Монолит достаточен |
| GraphQL | Выбран REST |
| Кастомизация стадий | Фиксированный пайплайн |
| Указание stage при создании Deal | Всегда LEAD |
| Каскадное удаление | RESTRICT для всех связей |
| DELETE /users/{id} | User нельзя удалить через API |
| DELETE /activities/{id} | Activity immutable (историческая запись) |
| PUT/PATCH company_id, owner_id | Immutable после создания |

---

## 10. Testing Requirements

### Unit Tests (Phase 2 & 3)
- Repositories: все CRUD методы.
- Services: валидация переходов стадий, валидация FK, создание системных активностей.

### Integration Tests (Phase 4)
- Все API эндпоинты через TestClient.
- Проверка HTTP кодов и формата ответов.

### Coverage
- Минимум 80% для services и repositories.

---

## 11. Project Structure

```
deal_tracker/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── user.py
│   │   ├── company.py
│   │   ├── deal.py
│   │   └── activity.py
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── user_repo.py
│   │   ├── company_repo.py
│   │   ├── deal_repo.py
│   │   └── activity_repo.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── user_service.py
│   │   ├── company_service.py
│   │   ├── deal_service.py
│   │   └── activity_service.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── router.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── users.py
│   │       ├── companies.py
│   │       ├── deals.py
│   │       └── activities.py
│   └── schemas/
│       ├── __init__.py
│       ├── user.py
│       ├── company.py
│       ├── deal.py
│       └── activity.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── unit/
│   │   ├── test_repositories.py
│   │   └── test_services.py
│   └── integration/
│       └── test_api.py
├── requirements.txt
└── README.md
```

---

## 12. Dependencies

```
fastapi>=0.109.0
uvicorn>=0.27.0
sqlalchemy>=2.0.0
pydantic>=2.0.0
pydantic-settings>=2.0.0
pytest>=7.0.0
pytest-asyncio>=0.23.0
httpx>=0.26.0
```

---

## 13. Acceptance Criteria

1. ✅ Создать пользователя через API.
2. ✅ Создать компанию через API.
3. ✅ Создать сделку (стадия всегда LEAD).
4. ✅ Ошибка 400 при создании сделки с несуществующим company_id/owner_id.
5. ✅ Переместить сделку на следующую стадию.
6. ✅ Ошибка 400 при невалидном переходе стадии.
7. ✅ При переходе стадии создаётся системная активность.
8. ✅ Добавить активность к сделке.
9. ✅ Timeline возвращается в порядке DESC (новые сначала).
10. ✅ Ошибка 400 при удалении компании со связанными сделками.
11. ✅ Ошибка 400 при удалении сделки с активностями.
12. ✅ User нельзя удалить через API (endpoint не существует).
13. ✅ Activity нельзя удалить через API (endpoint не существует).
14. ✅ company_id и owner_id нельзя изменить через PUT.
15. ✅ Все фазы независимо тестируются.

---

**Финализировано для передачи Architect.**