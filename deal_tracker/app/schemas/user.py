# START_MODULE_CONTRACT
# Module: schemas.user
# Intent: Pydantic схемы для User API.
# UserCreate для request, UserResponse для response.
# END_MODULE_CONTRACT

import uuid
from datetime import datetime
from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    """
    [START_CONTRACT_USER_CREATE]
    Intent: Схема для создания пользователя. Email должен быть валидным.
    Input: email (valid email), name (required).
    Output: Pydantic model для request body.
    [END_CONTRACT_USER_CREATE]
    """
    email: EmailStr
    name: str


class UserResponse(BaseModel):
    """
    [START_CONTRACT_USER_RESPONSE]
    Intent: Схема ответа для пользователя. Включает все поля ORM модели.
    Input: ORM User object.
    Output: JSON с id, email, name, created_at, updated_at.
    [END_CONTRACT_USER_RESPONSE]
    """
    id: uuid.UUID
    email: str
    name: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}