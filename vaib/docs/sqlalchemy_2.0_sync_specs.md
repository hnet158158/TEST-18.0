# SQLAlchemy 2.0 Sync ORM Specs

## 2.0 Style Declarative Mapping

SQLAlchemy 2.0 introduces `Mapped` and `mapped_column` for better type hinting support.

```python
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "user_account"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))
    fullname: Mapped[str | None]
```

## Engine and Session Setup (Sync)

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
```
*Note: `check_same_thread: False` is required for SQLite when used with FastAPI.*

## CRUD Operations (2.0 Style)

### Select
```python
from sqlalchemy import select

# 2.0 style select
stmt = select(User).where(User.name == "spongebob")
user = session.execute(stmt).scalar_one()
```

### Insert/Update/Delete
```python
# Insert
new_user = User(name="patrick")
session.add(new_user)
session.commit()

# Update
user.name = "squidward"
session.commit()

# Delete
session.delete(user)
session.commit()
```

## Key Constraints for this Project:
- **Sync Only**: Use `create_engine`, not `create_async_engine`.
- **No Async Drivers**: Use `sqlite3` (default), not `aiosqlite`.
- **Session Management**: Use `SessionLocal()` in a `try...finally` block or FastAPI `Depends`.
