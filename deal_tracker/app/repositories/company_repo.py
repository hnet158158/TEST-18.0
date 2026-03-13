# START_MODULE_CONTRACT
# Module: repositories.company_repo
# Intent: Репозиторий для операций с компаниями.
# Инкапсулирует доступ к данным модели Company.
# END_MODULE_CONTRACT

import uuid
from sqlalchemy.orm import Session
from app.models.company import Company
from app.models.deal import Deal
from app.repositories.base import BaseRepository


class CompanyRepository(BaseRepository[Company]):
    """
    [START_CONTRACT_COMPANY_REPOSITORY]
    Intent: Репозиторий для CRUD операций над компаниями.
    Input: db - SQLAlchemy Session.
    Output: Методы: create, get_by_id, get_all, update, delete, has_deals.
    [END_CONTRACT_COMPANY_REPOSITORY]
    """

    def __init__(self, db: Session):
        super().__init__(Company, db)

    def has_deals(self, company_id: uuid.UUID) -> bool:
        """
        [START_CONTRACT_HAS_DEALS]
        Intent: Проверить наличие сделок у компании перед удалением.
        Input: company_id - UUID компании.
        Output: True если есть сделки, False если нет.
        [END_CONTRACT_HAS_DEALS]
        """
        return (
            self.db.query(Deal)
            .filter(Deal.company_id == company_id)
            .first()
            is not None
        )