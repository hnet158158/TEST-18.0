# START_MODULE_CONTRACT
# Module: models.company
# Intent: ORM модель компании-клиента.
# Содержит name, website, industry и timestamps.
# END_MODULE_CONTRACT

import uuid
from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin


class Company(Base, TimestampMixin):
    """
    [START_CONTRACT_COMPANY]
    Intent: Модель компании-клиента с опциональными website и industry.
    Input: name (required), website (optional), industry (optional).
    Output: ORM модель с UUID PK и timestamps.
    [END_CONTRACT_COMPANY]
    """
    __tablename__ = "companies"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(
        String(255), nullable=False
    )
    website: Mapped[str | None] = mapped_column(
        String(500), nullable=True
    )
    industry: Mapped[str | None] = mapped_column(
        String(255), nullable=True
    )

    # Relationship для каскадной проверки при удалении
    deals: Mapped[list["Deal"]] = relationship(
        "Deal", back_populates="company", passive_deletes=True
    )