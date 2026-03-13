# Technology Stack

**Проект:** Deal Tracker API  
**Режим:** PROTOTYPE  
**Дата:** 2026-03-13

---

## Core Stack

| Компонент | Технология | Версия | Обоснование |
|-----------|------------|--------|-------------|
| **Язык** | Python | 3.11+ | Современный async-friendly Python |
| **Фреймворк** | FastAPI | >=0.109.0 | Автоматическая OpenAPI документация, Pydantic интеграция |
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

---

## Project Structure

```
deal_tracker/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app entry point
│   ├── config.py            # Settings (pydantic-settings)
│   ├── database.py          # SQLAlchemy setup
│   ├── models/              # ORM models
│   ├── repositories/        # Data access layer
│   ├── services/            # Business logic layer
│   ├── api/                 # HTTP routes
│   │   └── v1/              # API version 1
│   └── schemas/             # Pydantic schemas
├── tests/
│   ├── conftest.py          # Fixtures
│   ├── unit/                # Unit tests
│   └── integration/         # API tests
├── requirements.txt
└── README.md
```

---

## Requirements File

```
fastapi>=0.109.0
uvicorn>=0.27.0
sqlalchemy>=2.0.0
pydantic>=2.0.0
pydantic-settings>=2.0.0
pytest>=7.0.0
httpx>=0.26.0
```

---

## Configuration

| Переменная | По умолчанию | Описание |
|------------|--------------|----------|
| `DATABASE_URL` | `sqlite:///./deal_tracker.db` | Путь к БД |
| `APP_ENV` | `development` | Окружение |
| `DEBUG` | `True` | Режим отладки |

---

## Compatibility Notes

- Python 3.11+ требуется для современных type hints
- SQLAlchemy 2.0+ имеет другой API чем 1.x (новый синтаксис)
- Pydantic 2.0+ имеет значительные изменения производительности
- FastAPI 0.109+ включает улучшения OpenAPI 3.1