# Technology Stack

**Проект:** Deal Tracker (Backend + Frontend)  
**Режим:** PROTOTYPE  
**Дата:** 2026-03-13

---

## Core Stack

| Компонент | Технология | Версия | Обоснование |
|-----------|------------|--------|-------------|
| **Язык** | Python | 3.11+ | Современный async-friendly Python |
| **Backend Framework** | FastAPI | >=0.109.0 | Автоматическая OpenAPI документация, Pydantic интеграция |
| **Frontend Framework** | NiceGUI | >=1.4.0 | Python-native web UI, не требует JavaScript |
| **ASGI сервер** | Uvicorn | >=0.27.0 | Production-ready ASGI server |
| **ORM** | SQLAlchemy | >=2.0.0 | Зрелый ORM с поддержкой async (опционально) |
| **База данных** | SQLite | 3.x | Zero-config, file-based, достаточно для прототипа |
| **Валидация** | Pydantic | >=2.0.0 | Интеграция с FastAPI, type hints |
| **Конфигурация** | pydantic-settings | >=2.0.0 | ENV переменные, settings management |

---

## Development Dependencies

| Компонент | Технология | Версия | Обоснование |
|-----------|------------|--------|-------------|
| **Тестирование** | pytest | >=7.0.0 | Стандарт тестирования Python |
| **HTTP клиент** | httpx | >=0.26.0 | TestClient для FastAPI (sync) |

> **NOTE:** pytest-asyncio НЕ используется, т.к. приложение синхронное (ADR-002).

---

## Architecture Decisions

### ADR-001: SQLite вместо PostgreSQL
- **Статус:** Accepted
- **Контекст:** Прототип для демо, десятки записей
- **Решение:** SQLite (zero-config, file-based)
- **Последствия:** Нет миграций, нет connection pooling, достаточно для прототипа

### ADR-002: Sync SQLAlchemy
- **Статус:** Accepted
- **Контекст:** Прототип, простота разработки
- **Решение:** Синхронный SQLAlchemy (без async)
- **Последствия:** Простой код, достаточно для прототипа

### ADR-003: REST API с версионностью
- **Статус:** Accepted
- **Контекст:** Стандартный подход для backend API
- **Решение:** REST с префиксом `/api/v1/`
- **Последствия:** Возможность будущих версий API

### ADR-004: NiceGUI для Frontend
- **Статус:** Accepted
- **Контекст:** Python-only команда, быстрый прототип
- **Решение:** NiceGUI вместо React/Vue
- **Последствия:**
  - Весь код на Python (backend + frontend)
  - Не требует JavaScript/TypeScript
  - Быстрая разработка UI
  - Ограниченная кастомизация по сравнению с JS фреймворками

### ADR-005: Separate Frontend Process
- **Статус:** Accepted
- **Контекст:** NiceGUI и FastAPI могут конфликтовать на одном порту
- **Решение:** Запускать frontend и backend как отдельные процессы
- **Последствия:**
  - Backend: `uvicorn app.main:app --port 8000`
  - Frontend: `python frontend/app.py --port 8080`
  - Frontend делает HTTP запросы к Backend API

---

## Project Structure

```
deal_tracker/
├── app/                      # Backend (FastAPI)
│   ├── __init__.py
│   ├── main.py               # FastAPI app entry point
│   ├── config.py             # Settings (pydantic-settings)
│   ├── database.py           # SQLAlchemy setup
│   ├── models/               # ORM models
│   ├── repositories/         # Data access layer
│   ├── services/             # Business logic layer
│   ├── api/                  # HTTP routes
│   │   └── v1/               # API version 1
│   └── schemas/              # Pydantic schemas
├── frontend/                 # Frontend (NiceGUI)
│   ├── __init__.py
│   ├── app.py                # NiceGUI entry point
│   ├── api_client.py         # HTTP client for backend
│   ├── layout.py             # Main layout with navigation
│   ├── components/           # Reusable UI components
│   │   ├── __init__.py
│   │   ├── table.py          # Data table component
│   │   ├── form.py           # Form component
│   │   ├── dialogs.py        # Confirmation dialogs
│   │   ├── timeline.py       # Activity timeline
│   │   ├── kanban.py         # Kanban board
│   │   ├── filters.py        # Filter components
│   │   └── stat_card.py      # Dashboard stat cards
│   └── pages/                # Page modules
│       ├── __init__.py
│       ├── home.py           # Home placeholder
│       ├── dashboard.py      # Main dashboard
│       ├── users/
│       │   ├── list.py       # Users list
│       │   ├── detail.py     # User detail
│       │   └── create.py     # Create user
│       ├── companies/
│       │   ├── list.py       # Companies list
│       │   ├── detail.py     # Company detail
│       │   ├── create.py     # Create company
│       │   └── edit.py       # Edit company
│       ├── deals/
│       │   ├── list.py       # Deals list with filters
│       │   ├── kanban.py     # Kanban board
│       │   ├── detail.py     # Deal detail + timeline
│       │   ├── create.py     # Create deal
│       │   ├── edit.py       # Edit deal
│       │   └── stage_change.py # Stage change UI
│       └── activities/
│           └── create.py     # Create activity
├── tests/
│   ├── conftest.py           # Fixtures
│   ├── unit/                 # Unit tests
│   └── integration/          # API tests
├── requirements.txt
└── README.md
```

---

## Requirements File

```
# Backend
fastapi>=0.109.0
uvicorn>=0.27.0
sqlalchemy>=2.0.0
pydantic>=2.0.0
pydantic-settings>=2.0.0

# Frontend
nicegui>=1.4.0
httpx>=0.26.0

# Testing
pytest>=7.0.0
```

---

## Configuration

| Переменная | По умолчанию | Описание |
|------------|--------------|----------|
| `DATABASE_URL` | `sqlite:///./deal_tracker.db` | Путь к БД |
| `BACKEND_URL` | `http://127.0.0.1:8000` | URL backend API для frontend |
| `APP_ENV` | `development` | Окружение |
| `DEBUG` | `True` | Режим отладки |

---

## Frontend Pages Mapping

| Страница | URL | Описание |
|----------|-----|----------|
| Dashboard | `/` | Главная страница со статистикой |
| Users List | `/users` | Список пользователей |
| User Detail | `/users/{id}` | Детали пользователя |
| User Create | `/users/create` | Создание пользователя |
| Companies List | `/companies` | Список компаний |
| Company Detail | `/companies/{id}` | Детали компании + сделки |
| Company Create | `/companies/create` | Создание компании |
| Company Edit | `/companies/{id}/edit` | Редактирование компании |
| Deals List | `/deals` | Список сделок с фильтрами |
| Deals Kanban | `/deals/kanban` | Kanban доска |
| Deal Detail | `/deals/{id}` | Детали сделки + timeline |
| Deal Create | `/deals/create` | Создание сделки |
| Deal Edit | `/deals/{id}/edit` | Редактирование сделки |
| Activity Create | `/deals/{id}/activities/create` | Создание активности |

**Всего страниц:** 14

---

## API Endpoints Used by Frontend

| Endpoint | Method | Используется на странице |
|----------|--------|--------------------------|
| `/api/v1/users` | GET | Users List |
| `/api/v1/users` | POST | User Create |
| `/api/v1/users/{id}` | GET | User Detail |
| `/api/v1/companies` | GET | Companies List, Deal Create (select) |
| `/api/v1/companies` | POST | Company Create |
| `/api/v1/companies/{id}` | GET | Company Detail |
| `/api/v1/companies/{id}` | PUT | Company Edit |
| `/api/v1/companies/{id}` | DELETE | Company Detail (delete button) |
| `/api/v1/deals` | GET | Deals List, Kanban |
| `/api/v1/deals` | POST | Deal Create |
| `/api/v1/deals/{id}` | GET | Deal Detail |
| `/api/v1/deals/{id}` | PUT | Deal Edit |
| `/api/v1/deals/{id}` | DELETE | Deal Detail (delete button) |
| `/api/v1/deals/{id}/stage` | PATCH | Deal Detail, Kanban |
| `/api/v1/deals/{id}/activities` | GET | Deal Detail (timeline) |
| `/api/v1/deals/{id}/activities` | POST | Activity Create |

**Всего endpoints:** 16

---

## Compatibility Notes

- Python 3.11+ требуется для современных type hints
- SQLAlchemy 2.0+ имеет другой API чем 1.x (новый синтаксис)
- Pydantic 2.0+ имеет значительные изменения производительности
- FastAPI 0.109+ включает улучшения OpenAPI 3.1
- NiceGUI 1.4+ поддерживает Python 3.11+ и имеет встроенный WebSocket