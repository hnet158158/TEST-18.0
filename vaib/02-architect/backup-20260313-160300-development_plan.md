# Development Plan

## Project Overview

**Deal Tracker API** — REST API для отслеживания сделок через стадии с хронологической историей активностей. Прототип на FastAPI + SQLite с фазовой архитектурой.

**Режим:** PROTOTYPE  
**Масштаб:** Десятки сделок, демо-версия

---

## Architecture / Modules

### Module: Models
- **Contract**: Определяет структуру данных и связи между сущностями через SQLAlchemy ORM.
- **Negative Constraints**:
  - НЕ добавлять поля, не указанные в requirements
  - НЕ каскадное удаление (RESTRICT для всех FK)
- **Map**:
  - `Base` — базовый класс для моделей
  - `User` — пользователь системы
  - `Company` — компания-клиент
  - `Deal` — сделка
  - `Activity` — активность по сделке
  - `DealStage` (Enum) — стадии сделки
  - `ActivityType` (Enum) — типы активностей
- **Internal Logic**: Simple ORM mapping. Нет сложной логики.
- **Mental Test**: "Passed: Модели импортируются, БД создаётся."

### Module: Database
- **Contract**: Управляет соединением с SQLite и сессиями БД.
- **Negative Constraints**:
  - НЕ использовать асинхронный драйвер (sync SQLite)
  - НЕ connection pooling (прототип)
- **Map**:
  - `engine` — SQLAlchemy engine
  - `SessionLocal` — фабрика сессий
  - `get_db()` — dependency injection для FastAPI
  - `create_tables()` — инициализация схемы
- **Internal Logic**: Simple factory pattern.
- **Mental Test**: "Passed: Сессия создаётся и закрывается корректно."

### Module: Repositories
- **Contract**: Инкапсулирует все операции с БД. CRUD для каждой сущности.
- **Negative Constraints**:
  - НЕ бизнес-логика (только данные)
  - НЕ валидация бизнес-правил
- **Map**:
  - `UserRepository`: create, get_by_id, get_all, get_by_email
  - `CompanyRepository`: create, get_by_id, get_all, update, delete, has_deals
  - `DealRepository`: create, get_by_id, get_all, update, delete, change_stage, has_activities
  - `ActivityRepository`: create, get_by_deal_id
- **Internal Logic**: Simple CRUD. Нет сложных алгоритмов.
- **Mental Test**: "Passed: Все CRUD операции работают."

### Module: Services
- **Contract**: Бизнес-логика приложения. Валидация, транзакции, системные события. Возвращает доменные ошибки (не HTTP-коды).
- **Negative Constraints**:
  - НЕ прямой доступ к БД (только через repositories)
  - НЕ HTTP-коды (это в API layer)
  - НЕ знание о HTTP протоколе
- **Map**:
  - `UserService`: create_user, get_user, get_users
  - `CompanyService`: create_company, get_company, get_companies, update_company, delete_company
  - `DealService`: create_deal, get_deal, get_deals, update_deal, delete_deal, change_deal_stage
  - `ActivityService`: create_activity, get_deal_timeline
  - `Domain Errors`: NotFoundError, InvalidStageTransitionError, ForeignKeyValidationError
- **Internal Logic**:
  *** ALGORITHM DESIGN: change_deal_stage ***
  STEP 1: Получить текущую сделку по ID
  STEP 2: Проверить существование сделки → ЕСЛИ нет → поднять NotFoundError
  STEP 3: Получить текущую стадию (old_stage)
  STEP 4: Проверить допустимость перехода по таблице переходов
  STEP 5: ЕСЛИ переход недопустим → поднять InvalidStageTransitionError с допустимыми стадиями
  STEP 6: Обновить stage в сделке
  STEP 7: Создать Activity с type=NOTE, description="Stage changed from {old} to {new}"
  STEP 8: Вернуть обновлённую сделку
  ************************
- **Mental Test**: "Passed: Невалидный переход стадии поднимает InvalidStageTransitionError."

### Module: API Routes
- **Contract**: HTTP интерфейс. Обработка запросов, валидация Pydantic, возврат ответов.
- **Negative Constraints**:
  - НЕ бизнес-логика (делегировать services)
  - НЕ прямой доступ к БД
- **Map**:
  - `POST /api/v1/users` — создать пользователя
  - `GET /api/v1/users` — список пользователей
  - `GET /api/v1/users/{id}` — получить пользователя
  - `POST /api/v1/companies` — создать компанию
  - `GET /api/v1/companies` — список компаний
  - `GET /api/v1/companies/{id}` — получить компанию
  - `PUT /api/v1/companies/{id}` — обновить компанию
  - `DELETE /api/v1/companies/{id}` — удалить компанию
  - `POST /api/v1/deals` — создать сделку
  - `GET /api/v1/deals` — список сделок (фильтры: stage, company_id)
  - `GET /api/v1/deals/{id}` — получить сделку
  - `PUT /api/v1/deals/{id}` — обновить сделку
  - `PATCH /api/v1/deals/{id}/stage` — изменить стадию
  - `DELETE /api/v1/deals/{id}` — удалить сделку
  - `POST /api/v1/deals/{deal_id}/activities` — добавить активность
  - `GET /api/v1/deals/{deal_id}/activities` — timeline сделки
- **Internal Logic**: Simple routing. Валидация через Pydantic schemas.
- **Mental Test**: "Passed: Все эндпоинты возвращают корректные HTTP коды."

### Module: Schemas
- **Contract**: Pydantic модели для request/response валидации.
- **Negative Constraints**:
  - НЕ ORM модели (отдельный слой)
- **Map**:
  - `UserCreate`, `UserResponse`
  - `CompanyCreate`, `CompanyUpdate`, `CompanyResponse`
  - `DealCreate`, `DealUpdate`, `DealStageUpdate`, `DealResponse`
  - `ActivityCreate`, `ActivityResponse`
- **Internal Logic**: Simple Pydantic models.
- **Mental Test**: "Passed: Валидация работает, лишние поля отбрасываются."

---

## Negative Constraints (Global)

| Запрещено | Причина |
|-----------|---------|
| Аутентификация/авторизация | Не требуется в прототипе |
| Frontend | Backend only |
| WebSocket/Real-time | Избыточно |
| Кэширование | Избыточно |
| Микросервисы | Монолит достаточен |
| GraphQL | Выбран REST |
| Кастомизация стадий | Фиксированный пайплайн |
| Указание stage при создании Deal | Всегда LEAD |
| Каскадное удаление | RESTRICT для всех связей |
| DELETE /users/{id} | User нельзя удалить через API |
| DELETE /activities/{id} | Activity immutable |
| PUT/PATCH company_id, owner_id | Immutable после создания |
| Секреты в коде | Использовать ENV переменные |

---

## Phases

### Phase 1: Models & Database
- **Goal**: Создать базовую структуру данных и инициализацию БД.
- **Scope**: SQLAlchemy модели, Enum классы, конфигурация БД.
- **Deliverables**:
  1. `app/models/base.py` — базовый класс модели
  2. `app/models/user.py` — модель User
  3. `app/models/company.py` — модель Company
  4. `app/models/deal.py` — модель Deal с DealStage enum
  5. `app/models/activity.py` — модель Activity с ActivityType enum
  6. `app/database.py` — engine, SessionLocal, get_db, create_tables
  7. `app/config.py` — настройки приложения
  8. `app/__init__.py` — инициализация пакета
- **Dependencies**: Нет
- **Negative Constraints**:
  - НЕ добавлять cascade delete
  - НЕ добавлять поля вне требований
- **Done Criteria**:
  - Модели импортируются без ошибок
  - БД создаётся, таблицы существуют
  - Foreign keys настроены с RESTRICT
- **Notes for Tester**:
  - Проверить `create_tables()` создаёт все 4 таблицы
  - Проверить FK constraints: company_id, owner_id, deal_id

### Phase 2: Repositories
- **Goal**: Реализовать слой доступа к данным для всех сущностей.
- **Scope**: CRUD операции через SQLAlchemy.
- **Deliverables**:
  1. `app/repositories/base.py` — базовый репозиторий
  2. `app/repositories/user_repo.py` — UserRepository
  3. `app/repositories/company_repo.py` — CompanyRepository
  4. `app/repositories/deal_repo.py` — DealRepository
  5. `app/repositories/activity_repo.py` — ActivityRepository
  6. `tests/unit/test_repositories.py` — unit-тесты
- **Dependencies**: Phase 1
- **Negative Constraints**:
  - НЕ бизнес-логика в репозиториях
  - НЕ валидация бизнес-правил
- **Done Criteria**:
  - Все методы репозиториев работают
  - Unit-тесты проходят (минимум 80% coverage)
- **Notes for Tester**:
  - Проверить все CRUD методы для каждой сущности
  - Проверить `has_deals()` и `has_activities()` возвращают корректные значения

### Phase 3: Services
- **Goal**: Реализовать бизнес-логику с валидацией переходов стадий и FK.
- **Scope**: Сервисы для всех сущностей, валидация, системные активности.
- **Deliverables**:
  1. `app/services/user_service.py` — UserService
  2. `app/services/company_service.py` — CompanyService
  3. `app/services/deal_service.py` — DealService с валидацией переходов
  4. `app/services/activity_service.py` — ActivityService
  5. `tests/unit/test_services.py` — unit-тесты
- **Dependencies**: Phase 2
- **Negative Constraints**:
  - НЕ прямой SQL (только через repositories)
  - НЕ HTTP-коды в сервисах (это в API)
- **Done Criteria**:
  - Валидация переходов стадий работает по таблице
  - FK валидация возвращает понятные ошибки
  - При смене стадии создаётся Activity
  - Unit-тесты проходят (минимум 80% coverage)
- **Notes for Tester**:
  - Проверить все переходы стадий по таблице (раздел 4.1 requirements)
  - Проверить создание системной Activity при смене стадии
  - Проверить ошибки при невалидных FK

### Phase 4: API Routes
- **Goal**: Реализовать REST API эндпоинты с Pydantic схемами.
- **Scope**: FastAPI роуты, Pydantic схемы, обработка ошибок.
- **Deliverables**:
  1. `app/schemas/user.py` — Pydantic схемы для User
  2. `app/schemas/company.py` — Pydantic схемы для Company
  3. `app/schemas/deal.py` — Pydantic схемы для Deal
  4. `app/schemas/activity.py` — Pydantic схемы для Activity
  5. `app/api/v1/users.py` — роуты пользователей
  6. `app/api/v1/companies.py` — роуты компаний
  7. `app/api/v1/deals.py` — роуты сделок
  8. `app/api/v1/activities.py` — роуты активностей
  9. `app/api/router.py` — агрегация роутов
  10. `app/main.py` — FastAPI приложение
  11. `tests/integration/test_api.py` — integration-тесты
- **Dependencies**: Phase 3
- **Negative Constraints**:
  - НЕ бизнес-логика в роутах
  - НЕ прямой доступ к БД из роутов
- **Done Criteria**:
  - Все 16 эндпоинтов работают
  - HTTP коды корректны (200, 201, 204, 400, 404, 422)
  - Integration-тесты проходят
  - Все 15 acceptance criteria из requirements выполнены
- **Notes for Tester**:
  - Проверить все 15 acceptance criteria из requirements.md
  - Проверить формат ошибок `{"detail": "..."}`
  - Проверить immutable поля (company_id, owner_id)
  - Проверить сортировку timeline (DESC)

---

## Phase Execution Status

- Phase 1 - Models & Database - DONE
- Phase 2 - Repositories - DONE
- Phase 3 - Services - DONE
- Phase 4 - API Routes - DONE

---

## Open Questions / Risks

| Риск | Вероятность | Митигация |
|------|-------------|-----------|
| SQLite блокировки при конкурентных запросах | Низкая (прототип) | Не критично для демо |
| Нет миграций | Низкая | create_tables() достаточно для прототипа |
| Нет аутентификации | Принято | Требования не включают |

---

## Archive / Notes

- Требования финализированы 2026-03-13
- Режим PROTOTYPE — relaxed checks, NO Skeptic
- Фазы соответствуют разделу 8 requirements.md