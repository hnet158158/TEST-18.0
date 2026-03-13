# START_MODULE_CONTRACT
# Module: services.company_service
# Intent: Бизнес-логика для компаний.
# Валидация перед удалением (проверка связанных сделок).
# END_MODULE_CONTRACT

import uuid
import logging
from sqlalchemy.orm import Session
from app.models.company import Company
from app.repositories.company_repo import CompanyRepository
from app.services.errors import NotFoundError, HasRelatedEntitiesError

logger = logging.getLogger(__name__)


class CompanyService:
    """
    [START_CONTRACT_COMPANY_SERVICE]
    Intent: Сервис для управления компаниями с валидацией удаления.
    Input: db - SQLAlchemy Session.
    Output: Методы: create_company, get_company, get_companies, update_company, delete_company.
    [END_CONTRACT_COMPANY_SERVICE]
    """

    def __init__(self, db: Session):
        self.company_repo = CompanyRepository(db)

    def create_company(
        self, name: str, website: str | None = None, industry: str | None = None
    ) -> Company:
        """
        [START_CONTRACT_CREATE_COMPANY]
        Intent: Создать компанию с опциональными полями.
        Input: name - обязательное; website, industry - опциональные.
        Output: Company объект.
        [END_CONTRACT_CREATE_COMPANY]
        """
        logger.debug(
            f"[CompanyService][create_company] Belief: Create company | "
            f"Input: name={name} | Expected: Company created"
        )
        company = self.company_repo.create(
            {"name": name, "website": website, "industry": industry}
        )
        return company

    def get_company(self, company_id: uuid.UUID) -> Company:
        """
        [START_CONTRACT_GET_COMPANY]
        Intent: Получить компанию по ID.
        Input: company_id - UUID компании.
        Output: Company объект или NotFoundError.
        [END_CONTRACT_GET_COMPANY]
        """
        company = self.company_repo.get_by_id(company_id)
        if company is None:
            raise NotFoundError("Company", str(company_id))
        return company

    def get_companies(self, skip: int = 0, limit: int = 100) -> list[Company]:
        """
        [START_CONTRACT_GET_COMPANIES]
        Intent: Получить список всех компаний.
        Input: skip, limit - пагинация.
        Output: Список Company объектов.
        [END_CONTRACT_GET_COMPANIES]
        """
        return self.company_repo.get_all(skip=skip, limit=limit)

    def update_company(
        self,
        company_id: uuid.UUID,
        name: str | None = None,
        website: str | None = None,
        industry: str | None = None,
    ) -> Company:
        """
        [START_CONTRACT_UPDATE_COMPANY]
        Intent: Обновить компанию по ID.
        Input: company_id - UUID; name, website, industry - опциональные обновления.
        Output: Company объект или NotFoundError.
        [END_CONTRACT_UPDATE_COMPANY]
        """
        logger.debug(
            f"[CompanyService][update_company] Belief: Update company | "
            f"Input: id={company_id} | Expected: Company updated"
        )
        update_data = {}
        if name is not None:
            update_data["name"] = name
        if website is not None:
            update_data["website"] = website
        if industry is not None:
            update_data["industry"] = industry
        company = self.company_repo.update(company_id, update_data)
        if company is None:
            raise NotFoundError("Company", str(company_id))
        return company

    def delete_company(self, company_id: uuid.UUID) -> bool:
        """
        [START_CONTRACT_DELETE_COMPANY]
        Intent: Удалить компанию если нет связанных сделок.
        Input: company_id - UUID компании.
        Output: True если удалено, HasRelatedEntitiesError если есть сделки.
        [END_CONTRACT_DELETE_COMPANY]
        """
        logger.debug(
            f"[CompanyService][delete_company] Belief: Delete company | "
            f"Input: id={company_id} | Expected: Deleted or HasRelatedEntitiesError"
        )
        if self.company_repo.has_deals(company_id):
            raise HasRelatedEntitiesError("company", "deals")
        deleted = self.company_repo.delete(company_id)
        if not deleted:
            raise NotFoundError("Company", str(company_id))
        return True