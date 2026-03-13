# START_MODULE_CONTRACT
# Module: services.deal_service
# Intent: Бизнес-логика для сделок.
# Валидация переходов стадий, FK валидация, создание системных активностей.
# END_MODULE_CONTRACT

import uuid
import logging
from decimal import Decimal
from sqlalchemy.orm import Session
from app.models.deal import Deal, DealStage
from app.models.activity import ActivityType
from app.repositories.deal_repo import DealRepository
from app.repositories.company_repo import CompanyRepository
from app.repositories.user_repo import UserRepository
from app.repositories.activity_repo import ActivityRepository
from app.services.errors import (
    NotFoundError,
    InvalidStageTransitionError,
    ForeignKeyValidationError,
    HasRelatedEntitiesError,
)

logger = logging.getLogger(__name__)

# START_BLOCK_STAGE_TRANSITIONS
# Таблица допустимых переходов стадий
STAGE_TRANSITIONS: dict[DealStage, list[DealStage]] = {
    DealStage.LEAD: [DealStage.QUALIFIED, DealStage.WON, DealStage.LOST],
    DealStage.QUALIFIED: [DealStage.PROPOSAL, DealStage.WON, DealStage.LOST],
    DealStage.PROPOSAL: [DealStage.NEGOTIATION, DealStage.WON, DealStage.LOST],
    DealStage.NEGOTIATION: [DealStage.WON, DealStage.LOST],
    DealStage.WON: [DealStage.LEAD],
    DealStage.LOST: [DealStage.LEAD],
}
# END_BLOCK_STAGE_TRANSITIONS


class DealService:
    """
    [START_CONTRACT_DEAL_SERVICE]
    Intent: Сервис для управления сделками с валидацией переходов стадий и FK.
    Input: db - SQLAlchemy Session.
    Output: Методы: create_deal, get_deal, get_deals, update_deal, delete_deal, change_deal_stage.
    [END_CONTRACT_DEAL_SERVICE]
    """

    def __init__(self, db: Session):
        self.deal_repo = DealRepository(db)
        self.company_repo = CompanyRepository(db)
        self.user_repo = UserRepository(db)
        self.activity_repo = ActivityRepository(db)

    def create_deal(
        self,
        title: str,
        company_id: uuid.UUID,
        owner_id: uuid.UUID,
        value: Decimal | None = None,
        description: str | None = None,
    ) -> Deal:
        """
        [START_CONTRACT_CREATE_DEAL]
        Intent: Создать сделку с FK валидацией. Stage всегда LEAD.
        Input: title, company_id, owner_id - обязательные; value, description - опциональные.
        Output: Deal объект или ForeignKeyValidationError.
        [END_CONTRACT_CREATE_DEAL]
        """
        logger.debug(
            f"[DealService][create_deal] Belief: Create deal | "
            f"Input: title={title}, company={company_id}, owner={owner_id} | "
            "Expected: Deal created"
        )
        # FK validation
        if not self.company_repo.get_by_id(company_id):
            raise ForeignKeyValidationError("company_id", "Company")
        if not self.user_repo.get_by_id(owner_id):
            raise ForeignKeyValidationError("owner_id", "User")
        deal = self.deal_repo.create({
            "title": title,
            "company_id": company_id,
            "owner_id": owner_id,
            "value": value,
            "description": description,
        })
        return deal

    def get_deal(self, deal_id: uuid.UUID) -> Deal:
        """
        [START_CONTRACT_GET_DEAL]
        Intent: Получить сделку по ID.
        Input: deal_id - UUID сделки.
        Output: Deal объект или NotFoundError.
        [END_CONTRACT_GET_DEAL]
        """
        deal = self.deal_repo.get_by_id(deal_id)
        if deal is None:
            raise NotFoundError("Deal", str(deal_id))
        return deal

    def get_deals(
        self,
        skip: int = 0,
        limit: int = 100,
        stage: DealStage | None = None,
        company_id: uuid.UUID | None = None,
    ) -> list[Deal]:
        """
        [START_CONTRACT_GET_DEALS]
        Intent: Получить сделки с фильтрацией.
        Input: skip, limit - пагинация; stage, company_id - фильтры.
        Output: Список Deal объектов.
        [END_CONTRACT_GET_DEALS]
        """
        return self.deal_repo.get_all(skip=skip, limit=limit, stage=stage, company_id=company_id)

    def update_deal(
        self,
        deal_id: uuid.UUID,
        title: str | None = None,
        value: Decimal | None = None,
        description: str | None = None,
    ) -> Deal:
        """
        [START_CONTRACT_UPDATE_DEAL]
        Intent: Обновить сделку (title, value, description). company_id и owner_id immutable.
        Input: deal_id - UUID; title, value, description - опциональные.
        Output: Deal объект или NotFoundError.
        [END_CONTRACT_UPDATE_DEAL]
        """
        logger.debug(
            f"[DealService][update_deal] Belief: Update deal | "
            f"Input: id={deal_id} | Expected: Deal updated"
        )
        update_data = {}
        if title is not None:
            update_data["title"] = title
        if value is not None:
            update_data["value"] = value
        if description is not None:
            update_data["description"] = description
        deal = self.deal_repo.update(deal_id, update_data)
        if deal is None:
            raise NotFoundError("Deal", str(deal_id))
        return deal

    def delete_deal(self, deal_id: uuid.UUID) -> bool:
        """
        [START_CONTRACT_DELETE_DEAL]
        Intent: Удалить сделку если нет активностей.
        Input: deal_id - UUID сделки.
        Output: True или HasRelatedEntitiesError.
        [END_CONTRACT_DELETE_DEAL]
        """
        logger.debug(
            f"[DealService][delete_deal] Belief: Delete deal | "
            f"Input: id={deal_id} | Expected: Deleted or HasRelatedEntitiesError"
        )
        if self.deal_repo.has_activities(deal_id):
            raise HasRelatedEntitiesError("deal", "activities")
        deleted = self.deal_repo.delete(deal_id)
        if not deleted:
            raise NotFoundError("Deal", str(deal_id))
        return True

    def change_deal_stage(self, deal_id: uuid.UUID, new_stage: DealStage) -> Deal:
        """
        [START_CONTRACT_CHANGE_DEAL_STAGE]
        Intent: Изменить стадию сделки с валидацией перехода. Создать системную Activity.
        Input: deal_id - UUID сделки; new_stage - целевая стадия.
        Output: Deal объект или InvalidStageTransitionError/NotFoundError.
        [END_CONTRACT_CHANGE_DEAL_STAGE]
        """
        logger.debug(
            f"[DealService][change_deal_stage] Belief: Change stage | "
            f"Input: id={deal_id}, new_stage={new_stage.value} | "
            "Expected: Stage changed + Activity created"
        )
        # STEP 1-2: Get deal and check existence
        deal = self.deal_repo.get_by_id(deal_id)
        if deal is None:
            raise NotFoundError("Deal", str(deal_id))
        # STEP 3: Get current stage
        old_stage = deal.stage
        # STEP 4-5: Validate transition
        allowed_stages = STAGE_TRANSITIONS.get(old_stage, [])
        if new_stage not in allowed_stages:
            raise InvalidStageTransitionError(old_stage, new_stage, allowed_stages)
        # STEP 6: Update stage
        self.deal_repo.change_stage(deal_id, new_stage)
        # STEP 7: Create system Activity
        self.activity_repo.create({
            "deal_id": deal_id,
            "type": ActivityType.NOTE,
            "description": f"Stage changed from {old_stage.value} to {new_stage.value}",
        })
        # STEP 8: Return updated deal
        return self.deal_repo.get_by_id(deal_id)