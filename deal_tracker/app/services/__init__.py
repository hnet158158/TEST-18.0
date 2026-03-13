# START_MODULE_CONTRACT
# Module: services
# Intent: Слой бизнес-логики приложения.
# Сервисы инкапсулируют валидацию, транзакции и системные события.
# END_MODULE_CONTRACT

from app.services.errors import (
    NotFoundError,
    InvalidStageTransitionError,
    ForeignKeyValidationError,
    DuplicateEmailError,
    HasRelatedEntitiesError,
)
from app.services.user_service import UserService
from app.services.company_service import CompanyService
from app.services.deal_service import DealService
from app.services.activity_service import ActivityService

__all__ = [
    "NotFoundError",
    "InvalidStageTransitionError",
    "ForeignKeyValidationError",
    "DuplicateEmailError",
    "HasRelatedEntitiesError",
    "UserService",
    "CompanyService",
    "DealService",
    "ActivityService",
]