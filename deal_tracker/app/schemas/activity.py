# START_MODULE_CONTRACT
# Module: schemas.activity
# Intent: Pydantic схемы для Activity API.
# ActivityCreate для request, ActivityResponse для response.
# END_MODULE_CONTRACT

import uuid
from datetime import datetime
from pydantic import BaseModel
from app.models.activity import ActivityType


class ActivityCreate(BaseModel):
    """
    [START_CONTRACT_ACTIVITY_CREATE]
    Intent: Схема для создания активности. Description обязательное поле.
    Input: type (optional, default NOTE), description (required).
    Output: Pydantic model для request body.
    [END_CONTRACT_ACTIVITY_CREATE]
    """
    type: ActivityType = ActivityType.NOTE
    description: str


class ActivityResponse(BaseModel):
    """
    [START_CONTRACT_ACTIVITY_RESPONSE]
    Intent: Схема ответа для активности. Включает все поля ORM модели.
    Input: ORM Activity object.
    Output: JSON с id, deal_id, type, description, created_at.
    [END_CONTRACT_ACTIVITY_RESPONSE]
    """
    id: uuid.UUID
    deal_id: uuid.UUID
    type: ActivityType
    description: str
    created_at: datetime

    model_config = {"from_attributes": True}