# START_MODULE_CONTRACT
# Module: models.user
# Intent: ORM модель пользователя системы.
# Содержит email, name и timestamps. Email уникален.
# END_MODULE_CONTRACT

import uuid
from sqlalchemy import String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base, TimestampMixin


class User(Base, TimestampMixin):
    """
    [START_CONTRACT_USER]
    Intent: Модель пользователя системы с уникальным email.
    Input: email (unique), name.
    Output: ORM модель с UUID PK и timestamps.
    [END_CONTRACT_USER]
    """
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(
        String(255), nullable=False, unique=True
    )
    name: Mapped[str] = mapped_column(
        String(255), nullable=False
    )

    __table_args__ = (
        UniqueConstraint("email", name="uq_user_email"),
    )