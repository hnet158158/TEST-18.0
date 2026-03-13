# START_MODULE_CONTRACT
# Module: models.deal
# Intent: ORM модель сделки с enum DealStage для стадий.
# Содержит title, company_id, owner_id, stage, value, description.
# END_MODULE_CONTRACT

import uuid
from decimal import Decimal
from enum import Enum
from sqlalchemy import String, Text, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin


class DealStage(str, Enum):
    """
    [START_CONTRACT_DEALSTAGE]
    Intent: Фиксированный пайплайн стадий сделки.
    Input: Нет (enum).
    Output: 6 значений: lead, qualified, proposal, negotiation, won, lost.
    [END_CONTRACT_DEALSTAGE]
    """
    LEAD = "lead"
    QUALIFIED = "qualified"
    PROPOSAL = "proposal"
    NEGOTIATION = "negotiation"
    WON = "won"
    LOST = "lost"


class Deal(Base, TimestampMixin):
    """
    [START_CONTRACT_DEAL]
    Intent: Модель сделки с immutable company_id и owner_id, stage по умолчанию LEAD.
    Input: title (required), company_id (FK), owner_id (FK), value (optional), description (optional).
    Output: ORM модель с UUID PK, FK с RESTRICT, timestamps.
    [END_CONTRACT_DEAL]
    """
    __tablename__ = "deals"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4
    )
    title: Mapped[str] = mapped_column(
        String(255), nullable=False
    )
    company_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("companies.id", ondelete="RESTRICT"),
        nullable=False
    )
    owner_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False
    )
    stage: Mapped[DealStage] = mapped_column(
        default=DealStage.LEAD, nullable=False
    )
    value: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 2), nullable=True
    )
    description: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )

    # Relationships
    company: Mapped["Company"] = relationship(
        "Company", back_populates="deals"
    )
    owner: Mapped["User"] = relationship(
        "User"
    )
    activities: Mapped[list["Activity"]] = relationship(
        "Activity", back_populates="deal"
    )