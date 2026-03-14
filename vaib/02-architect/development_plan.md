# Development Plan

## Project Overview

**Deal Tracker** — Full-stack приложение для отслеживания сделок через стадии с хронологической историей активностей. 

**Архитектура:**
- **Backend:** FastAPI + SQLite (REST API `/api/v1/`)
- **Frontend:** NiceGUI (Python web framework)

**Режим:** PROTOTYPE  
**Масштаб:** Десятки сделок, демо-версия

---

## Architecture / Modules

### Module: Backend Models
- **Contract**: Определяет структуру данных и связи между сущностями через SQLAlchemy ORM.
- **Negative Constraints**:
  - НЕ добавлять поля, не указанные в requirements
  - НЕ каскадное удаление (RESTRICT для всех FK)
- **Map**:
  - `User` — пользователь системы
  - `Company` — компания-клиент
  - `Deal` — сделка
  - `Activity` — активность по сделке
  - `DealStage` (Enum) — стадии сделки
  - `ActivityType` (Enum) — типы активностей
- **Internal Logic**: Simple ORM mapping.
- **Mental Test**: "Passed: Модели импортируются, БД создаётся."

### Module: Backend Services
- **Contract**: Бизнес-логика приложения. Валидация, транзакции, системные события.
- **Negative Constraints**:
  - НЕ прямой доступ к БД (только через repositories)
  - НЕ HTTP-коды (это в API layer)
- **Map**:
  - `UserService`: create_user, get_user, get_users
  - `CompanyService`: create_company, get_company, get_companies, update_company, delete_company
  - `DealService`: create_deal, get_deal, get_deals, update_deal, delete_deal, change_deal_stage
  - `ActivityService`: create_activity, get_deal_timeline
- **Internal Logic**: Валидация переходов стадий, FK валидация.
- **Mental Test**: "Passed: Невалидный переход стадии возвращает ошибку."

### Module: Backend API Routes
- **Contract**: HTTP интерфейс. REST endpoints с Pydantic схемами.
- **Negative Constraints**:
  - НЕ бизнес-логика в роутах
  - НЕ прямой доступ к БД из роутов
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
  - `GET /api/v1/deals` — список сделок (фильтры + пагинация)
  - `GET /api/v1/deals/{id}` — получить сделку
  - `PUT /api/v1/deals/{id}` — обновить сделку
  - `PATCH /api/v1/deals/{id}/stage` — изменить стадию
  - `DELETE /api/v1/deals/{id}` — удалить сделку
  - `POST /api/v1/deals/{deal_id}/activities` — добавить активность
  - `GET /api/v1/deals/{deal_id}/activities` — timeline сделки
- **Internal Logic**: Simple routing.
- **Mental Test**: "Passed: Все 16 эндпоинтов работают."

### Module: Frontend Core
- **Contract**: NiceGUI приложение с навигацией, layout и API клиентом.
- **Negative Constraints**:
  - НЕ дублировать бизнес-логику (делегировать backend API)
  - НЕ прямое подключение к БД из фронтенда
- **Map**:
  - `app.py` — точка входа NiceGUI
  - `api_client.py` — HTTP клиент для backend API
  - `layout.py` — общий layout с навигацией
  - `components/` — переиспользуемые UI компоненты
- **Internal Logic**: Simple UI routing.
- **Mental Test**: "Passed: Страницы открываются, навигация работает."

### Module: Frontend Pages - Users
- **Contract**: UI для управления пользователями.
- **Negative Constraints**:
  - НЕ показывать DELETE (User нельзя удалить)
  - НЕ показывать EDIT (User нельзя редактировать)
- **Map**:
  - `pages/users/list.py` — список пользователей
  - `pages/users/detail.py` — детали пользователя
  - `pages/users/create.py` — создание пользователя
- **Internal Logic**: Simple CRUD UI.
- **Mental Test**: "Passed: Пользователь создаётся, список отображается."

### Module: Frontend Pages - Companies
- **Contract**: UI для управления компаниями.
- **Negative Constraints**:
  - НЕ удалять компанию со связанными сделками (показать ошибку)
- **Map**:
  - `pages/companies/list.py` — список компаний
  - `pages/companies/detail.py` — детали компании + связанные сделки
  - `pages/companies/create.py` — создание компании
  - `pages/companies/edit.py` — редактирование компании
- **Internal Logic**: Simple CRUD UI.
- **Mental Test**: "Passed: Компания создаётся, редактируется, удаляется."

### Module: Frontend Pages - Deals
- **Contract**: UI для управления сделками с визуализацией пайплайна.
- **Negative Constraints**:
  - НЕ редактировать company_id и owner_id (immutable)
  - НЕ удалять сделку с активностями (показать ошибку)
  - НЕ указывать stage при создании (всегда LEAD)
- **Map**:
  - `pages/deals/list.py` — список сделок с фильтрами
  - `pages/deals/kanban.py` — Kanban доска по стадиям
  - `pages/deals/detail.py` — детали сделки + timeline
  - `pages/deals/create.py` — создание сделки
  - `pages/deals/edit.py` — редактирование сделки
  - `pages/deals/stage_change.py` — изменение стадии
- **Internal Logic**: 
  *** ALGORITHM DESIGN: Stage Change UI ***
  STEP 1: Получить текущую стадию сделки
  STEP 2: Показать только допустимые стадии для перехода
  STEP 3: При выборе — вызвать PATCH /deals/{id}/stage
  STEP 4: Показать результат (успех/ошибка)
  ************************
- **Mental Test**: "Passed: Сделка создаётся, стадия меняется по правилам."

### Module: Frontend Pages - Activities
- **Contract**: UI для работы с активностями (timeline сделки).
- **Negative Constraints**:
  - НЕ показывать DELETE (Activity immutable)
  - НЕ показывать EDIT (Activity immutable)
- **Map**:
  - `pages/activities/create.py` — создание активности
  - `pages/activities/timeline.py` — timeline сделки (встроен в deal detail)
- **Internal Logic**: Simple create + list UI.
- **Mental Test**: "Passed: Активность создаётся, timeline отображается."

### Module: Frontend Pages - Dashboard
- **Contract**: Главная страница с обзором пайплайна и статистикой.
- **Negative Constraints**:
  - НЕ показывать детальную информацию (только обзор)
- **Map**:
  - `pages/dashboard.py` — статистика по стадиям, последние сделки
- **Internal Logic**: Агрегация данных для отображения.
- **Mental Test**: "Passed: Dashboard показывает статистику."

---

## Negative Constraints (Global)

| Запрещено | Причина |
|-----------|---------|
| Аутентификация/авторизация | Не требуется в прототипе |
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
| Прямое подключение фронтенда к БД | Только через REST API |
| Дублирование бизнес-логики во фронтенде | Делегировать backend |

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
  - Проверить `has_deals()` и `has_activities()`

### Phase 3: Services
- **Goal**: Реализовать бизнес-логику с валидацией переходов стадий и FK.
- **Scope**: Сервисы для всех сущностей, валидация, системные активности.
- **Deliverables**:
  1. `app/services/user_service.py` — UserService
  2. `app/services/company_service.py` — CompanyService
  3. `app/services/deal_service.py` — DealService с валидацией переходов
  4. `app/services/activity_service.py` — ActivityService
  5. `app/services/errors.py` — доменные ошибки
  6. `tests/unit/test_services.py` — unit-тесты
- **Dependencies**: Phase 2
- **Negative Constraints**:
  - НЕ прямой SQL (только через repositories)
  - НЕ HTTP-коды в сервисах
- **Done Criteria**:
  - Валидация переходов стадий работает по таблице
  - FK валидация возвращает понятные ошибки
  - При смене стадии создаётся Activity
  - Unit-тесты проходят (минимум 80% coverage)
- **Notes for Tester**:
  - Проверить все переходы стадий по таблице
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
  - Все 15 acceptance criteria выполнены
- **Notes for Tester**:
  - Проверить все 15 acceptance criteria из requirements.md
  - Проверить формат ошибок `{"detail": "..."}`
  - Проверить immutable поля (company_id, owner_id)
  - Проверить сортировку timeline (DESC)

### Phase 5: API Pagination
- **Goal**: Экспонировать пагинацию через query parameters.
- **Scope**: Добавить `skip` и `limit` query parameters в GET endpoints.
- **Deliverables**:
  1. `app/api/v1/users.py` — добавить skip/limit в `GET /users`
  2. `app/api/v1/companies.py` — добавить skip/limit в `GET /companies`
  3. `app/api/v1/deals.py` — добавить skip/limit в `GET /deals`
  4. `app/api/v1/activities.py` — добавить skip/limit в `GET /deals/{deal_id}/activities`
  5. `tests/integration/test_api.py` — добавить тесты на API пагинацию
- **Dependencies**: Phase 4
- **Negative Constraints**:
  - НЕ менять сигнатуры services/repositories
  - НЕ добавлять пагинацию в non-list endpoints
- **Done Criteria**:
  - Все 4 list endpoints принимают skip и limit
  - Default values: skip=0, limit=100
  - Integration-тесты на пагинацию проходят
- **Notes for Tester**:
  - Проверить GET /users?skip=0&limit=10
  - Проверить GET /companies?skip=5&limit=20
  - Проверить GET /deals?skip=0&limit=50&stage=lead
  - Проверить GET /deals/{id}/activities?skip=0&limit=25

### Phase 6: Frontend Foundation
- **Goal**: Создать базовую структуру NiceGUI приложения с навигацией и API клиентом.
- **Scope**: NiceGUI setup, layout, navigation, HTTP client для backend API.
- **Deliverables**:
  1. `frontend/app.py` — точка входа NiceGUI
  2. `frontend/api_client.py` — HTTP клиент для backend API
  3. `frontend/layout.py` — общий layout с sidebar навигацией
  4. `frontend/components/__init__.py` — инициализация компонентов
  5. `frontend/pages/__init__.py` — инициализация страниц
  6. `frontend/pages/home.py` — домашняя страница (placeholder)
  7. `requirements.txt` — добавить nicegui
- **Dependencies**: Phase 5
- **Negative Constraints**:
  - НЕ дублировать бизнес-логику
  - НЕ прямое подключение к БД
- **Done Criteria**:
  - NiceGUI приложение запускается
  - Навигация между страницами работает
  - API клиент может вызывать backend endpoints
- **Notes for Tester**:
  - Проверить запуск `python frontend/app.py`
  - Проверить навигацию: Dashboard, Users, Companies, Deals
  - Проверить API клиент: GET /api/v1/users

### Phase 7: Users Pages
- **Goal**: Реализовать UI для управления пользователями.
- **Scope**: Список, детали, создание пользователей.
- **Deliverables**:
  1. `frontend/pages/users/list.py` — таблица пользователей
  2. `frontend/pages/users/detail.py` — карточка пользователя
  3. `frontend/pages/users/create.py` — форма создания
  4. `frontend/components/table.py` — переиспользуемый компонент таблицы
  5. `frontend/components/form.py` — переиспользуемый компонент формы
- **Dependencies**: Phase 6
- **Negative Constraints**:
  - НЕ показывать DELETE (User нельзя удалить)
  - НЕ показывать EDIT (User нельзя редактировать)
- **Done Criteria**:
  - Список пользователей отображается с пагинацией
  - Форма создания работает с валидацией email
  - Детали пользователя показывают связанные сделки
- **Notes for Tester**:
  - Проверить создание пользователя с duplicate email (ошибка)
  - Проверить пагинацию списка
  - Проверить переход: список → детали

### Phase 8: Companies Pages
- **Goal**: Реализовать полный CRUD UI для компаний.
- **Scope**: Список, детали, создание, редактирование, удаление компаний.
- **Deliverables**:
  1. `frontend/pages/companies/list.py` — таблица компаний
  2. `frontend/pages/companies/detail.py` — карточка компании + связанные сделки
  3. `frontend/pages/companies/create.py` — форма создания
  4. `frontend/pages/companies/edit.py` — форма редактирования
  5. `frontend/components/dialogs.py` — диалог подтверждения удаления
- **Dependencies**: Phase 7
- **Negative Constraints**:
  - НЕ удалять компанию со связанными сделками (показать ошибку)
- **Done Criteria**:
  - CRUD для компаний работает полностью
  - При удалении компании со сделками — показывается ошибка
  - В деталях компании видны связанные сделки
- **Notes for Tester**:
  - Проверить удаление компании со сделками (ошибка 400)
  - Проверить редактирование: name, website, industry
  - Проверить переход: компания → связанные сделки

### Phase 9: Deals List & Kanban
- **Goal**: Реализовать UI для просмотра сделок с Kanban доской.
- **Scope**: Список с фильтрами, Kanban доска по стадиям.
- **Deliverables**:
  1. `frontend/pages/deals/list.py` — таблица сделок с фильтрами
  2. `frontend/pages/deals/kanban.py` — Kanban доска (6 колонок)
  3. `frontend/components/kanban.py` — Kanban компонент
  4. `frontend/components/filters.py` — компонент фильтров
- **Dependencies**: Phase 8
- **Negative Constraints**:
  - НЕ показывать stage selector при создании
  - НЕ редактировать company_id и owner_id
- **Done Criteria**:
  - Список сделок с фильтрами по stage и company
  - Kanban доска показывает сделки по стадиям
  - Drag-and-drop для смены стадии (опционально)
- **Notes for Tester**:
  - Проверить фильтры: ?stage=lead, ?company_id=...
  - Проверить Kanban: 6 колонок (LEAD → WON/LOST)
  - Проверить переход: Kanban → детали сделки

### Phase 10: Deals CRUD & Stage Change
- **Goal**: Реализовать полный CRUD UI для сделок с валидацией смены стадии.
- **Scope**: Детали, создание, редактирование, удаление, смена стадии.
- **Deliverables**:
  1. `frontend/pages/deals/detail.py` — карточка сделки + timeline
  2. `frontend/pages/deals/create.py` — форма создания (select company, owner)
  3. `frontend/pages/deals/edit.py` — форма редактирования
  4. `frontend/pages/deals/stage_change.py` — UI смены стадии
  5. `frontend/components/timeline.py` — компонент timeline
- **Dependencies**: Phase 9
- **Negative Constraints**:
  - НЕ удалять сделку с активностями (показать ошибку)
  - НЕ показывать недопустимые стадии при смене
  - НЕ редактировать company_id, owner_id, stage через форму
- **Done Criteria**:
  - CRUD для сделок работает полностью
  - Смена стадии валидируется по таблице переходов
  - При удалении сделки с активностями — ошибка
  - Timeline показывает активности в DESC порядке
- **Notes for Tester**:
  - Проверить все переходы стадий по таблице
  - Проверить недопустимые переходы (ошибка 400)
  - Проверить удаление сделки с активностями (ошибка 400)
  - Проверить timeline: новые активности сверху

### Phase 11: Activities & Dashboard
- **Goal**: Реализовать UI для активностей и главную страницу с дашбордом.
- **Scope**: Создание активностей, timeline, dashboard со статистикой.
- **Deliverables**:
  1. `frontend/pages/activities/create.py` — форма создания активности
  2. `frontend/pages/dashboard.py` — главная страница со статистикой
  3. `frontend/components/stat_card.py` — карточка статистики
  4. `frontend/components/chart.py` — простая визуализация (опционально)
- **Dependencies**: Phase 10
- **Negative Constraints**:
  - НЕ показывать DELETE для активностей
  - НЕ показывать EDIT для активностей
- **Done Criteria**:
  - Активности создаются для сделки
  - Dashboard показывает статистику по стадиям
  - Dashboard показывает последние сделки
- **Notes for Tester**:
  - Проверить создание активности: type, description
  - Проверить dashboard: count по стадиям
  - Проверить dashboard: последние 5 сделок

---

## Phase Execution Status

- Phase 1 - Models & Database - DONE
- Phase 2 - Repositories - DONE
- Phase 3 - Services - DONE
- Phase 4 - API Routes - DONE
- Phase 5 - API Pagination - DONE
- Phase 6 - Frontend Foundation - PLANNED
- Phase 7 - Users Pages - PLANNED
- Phase 8 - Companies Pages - PLANNED
- Phase 9 - Deals List & Kanban - PLANNED
- Phase 10 - Deals CRUD & Stage Change - PLANNED
- Phase 11 - Activities & Dashboard - PLANNED

---

## Open Questions / Risks

| Риск | Вероятность | Митигация |
|------|-------------|-----------|
| NiceGUI async vs sync backend | Низкая | NiceGUI поддерживает оба режима |
| Drag-and-drop в Kanban | Средняя | Опционально, можно использовать кнопки |
| Производительность при большом количестве сделок | Низкая | Пагинация на backend |

---

## Archive / Notes

- Backend фазы 1-5 завершены 2026-03-13
- Фронтенд фазы 6-11 добавлены по запросу пользователя
- Режим PROTOTYPE — relaxed checks, NO Skeptic
- NiceGUI выбран как Python-native web framework