# START_MODULE_CONTRACT
# Module: schemas
# Intent: Pydantic модели для request/response валидации API.
# Отдельный слой от ORM моделей.
# END_MODULE_CONTRACT

from app.schemas.user import UserCreate, UserResponse
from app.schemas.company import CompanyCreate, CompanyUpdate, CompanyResponse
from app.schemas.deal import DealCreate, DealUpdate, DealStageUpdate, DealResponse
from app.schemas.activity import ActivityCreate, ActivityResponse

__all__ = [
    "UserCreate",
    "UserResponse",
    "CompanyCreate",
    "CompanyUpdate",
    "CompanyResponse",
    "DealCreate",
    "DealUpdate",
    "DealStageUpdate",
    "DealResponse",
    "ActivityCreate",
    "ActivityResponse",
]