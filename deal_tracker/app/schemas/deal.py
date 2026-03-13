# START_MODULE_CONTRACT
# Module: schemas.deal
# Intent: Pydantic схемы для Deal API.
# DealCreate, DealUpdate, DealStageUpdate для request, DealResponse для response.
# END_MODULE_CONTRACT

import uuid
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel
from app.models.deal import DealStage


class DealCreate(BaseModel):
    """
    [START_CONTRACT_DEAL_CREATE]
    Intent: Схема для создания сделки. Stage нельзя указать - всегда LEAD.
    Input: title, company_id, owner_id (required), value, description (optional).
    Output: Pydantic model для request body.
    [END_CONTRACT_DEAL_CREATE]
    """
    title: str
    company_id: uuid.UUID
    owner_id: uuid.UUID
    value: Decimal | None = None
    description: str | None = None


class DealUpdate(BaseModel):
    """
    [START_CONTRACT_DEAL_UPDATE]
    Intent: Схема для обновления сделки. company_id, owner_id, stage нельзя менять.
    Input: title, value, description (all optional).
    Output: Pydantic model для request body.
    [END_CONTRACT_DEAL_UPDATE]
    """
    title: str | None = None
    value: Decimal | None = None
    description: str | None = None


class DealStageUpdate(BaseModel):
    """
    [START_CONTRACT_DEAL_STAGE_UPDATE]
    Intent: Схема для изменения стадии сделки через PATCH.
    Input: stage (required, valid DealStage).
    Output: Pydantic model для request body.
    [END_CONTRACT_DEAL_STAGE_UPDATE]
    """
    stage: DealStage


class DealResponse(BaseModel):
    """
    [START_CONTRACT_DEAL_RESPONSE]
    Intent: Схема ответа для сделки. Включает все поля ORM модели.
    Input: ORM Deal object.
    Output: JSON с id, title, company_id, owner_id, stage, value, description, timestamps.
    [END_CONTRACT_DEAL_RESPONSE]
    """
    id: uuid.UUID
    title: str
    company_id: uuid.UUID
    owner_id: uuid.UUID
    stage: DealStage
    value: Decimal | None
    description: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}