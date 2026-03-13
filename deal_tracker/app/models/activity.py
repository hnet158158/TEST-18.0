# START_MODULE_CONTRACT
# Module: models.activity
# Intent: ORM модель активности по сделке с enum ActivityType.
# Immutable запись для истории. Содержит deal_id, type, description.
# END_MODULE_CONTRACT

import uuid
from datetime import datetime
from enum import Enum
from sqlalchemy import String, Text, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base


class ActivityType(str, Enum):
    """
    [START_CONTRACT_ACTIVITYTYPE]
    Intent: Фиксированные типы активностей по сделке.
    Input: Нет (enum).
    Output: 4 значения: call, email, meeting, note.
    [END_CONTRACT_ACTIVITYTYPE]
    """
    CALL = "call"
    EMAIL = "email"
    MEETING = "meeting"
    NOTE = "note"


class Activity(Base):
    """
    [START_CONTRACT_ACTIVITY]
    Intent: Immutable модель активности для истории сделки. Только created_at (no updated_at).
    Input: deal_id (FK), type (default NOTE), description (required).
    Output: ORM модель с UUID PK, FK с RESTRICT, только created_at.
    [END_CONTRACT_ACTIVITY]
    """
    __tablename__ = "activities"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4
    )
    deal_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("deals.id", ondelete="RESTRICT"),
        nullable=False
    )
    type: Mapped[ActivityType] = mapped_column(
        default=ActivityType.NOTE, nullable=False
    )
    description: Mapped[str] = mapped_column(
        Text, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), nullable=False
    )

    # Relationship
    deal: Mapped["Deal"] = relationship(
        "Deal", back_populates="activities"
    )