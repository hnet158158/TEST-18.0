# START_MODULE_CONTRACT
# Module: repositories
# Intent: Пакет репозиториев для доступа к данным.
# Инкапсулирует все операции с БД, без бизнес-логики.
# END_MODULE_CONTRACT

from app.repositories.base import BaseRepository
from app.repositories.user_repo import UserRepository
from app.repositories.company_repo import CompanyRepository
from app.repositories.deal_repo import DealRepository
from app.repositories.activity_repo import ActivityRepository

__all__ = [
    "BaseRepository",
    "UserRepository",
    "CompanyRepository",
    "DealRepository",
    "ActivityRepository",
]