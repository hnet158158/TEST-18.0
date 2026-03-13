# START_MODULE_CONTRACT
# Module: models.base
# Intent: Базовый класс для всех ORM моделей SQLAlchemy 2.0.
# Предоставляет общий ID (UUID) и timestamp поля.
# END_MODULE_CONTRACT

import uuid
from datetime import datetime
from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """
    [START_CONTRACT_BASE]
    Intent: Базовый класс для всех моделей с общими полями id, created_at, updated_at.
    Input: Нет (абстрактный класс).
    Output: Класс с UUID PK и авто-обновляемыми timestamp.
    [END_CONTRACT_BASE]
    """
    pass


class TimestampMixin:
    """
    # CONTRACT: Intent: Миксин для добавления created_at и updated_at.
    """
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now(), nullable=False
    )