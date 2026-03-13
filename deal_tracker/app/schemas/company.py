# START_MODULE_CONTRACT
# Module: schemas.company
# Intent: Pydantic схемы для Company API.
# CompanyCreate, CompanyUpdate для request, CompanyResponse для response.
# END_MODULE_CONTRACT

import uuid
from datetime import datetime
from pydantic import BaseModel


class CompanyCreate(BaseModel):
    """
    [START_CONTRACT_COMPANY_CREATE]
    Intent: Схема для создания компании. Name обязательное поле.
    Input: name (required), website (optional), industry (optional).
    Output: Pydantic model для request body.
    [END_CONTRACT_COMPANY_CREATE]
    """
    name: str
    website: str | None = None
    industry: str | None = None


class CompanyUpdate(BaseModel):
    """
    [START_CONTRACT_COMPANY_UPDATE]
    Intent: Схема для обновления компании. Все поля опциональны.
    Input: name, website, industry (all optional).
    Output: Pydantic model для request body.
    [END_CONTRACT_COMPANY_UPDATE]
    """
    name: str | None = None
    website: str | None = None
    industry: str | None = None


class CompanyResponse(BaseModel):
    """
    [START_CONTRACT_COMPANY_RESPONSE]
    Intent: Схема ответа для компании. Включает все поля ORM модели.
    Input: ORM Company object.
    Output: JSON с id, name, website, industry, created_at, updated_at.
    [END_CONTRACT_COMPANY_RESPONSE]
    """
    id: uuid.UUID
    name: str
    website: str | None
    industry: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}