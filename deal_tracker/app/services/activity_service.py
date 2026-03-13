# START_MODULE_CONTRACT
# Module: services.activity_service
# Intent: Бизнес-логика для активностей.
# Создание активностей и получение timeline сделки.
# END_MODULE_CONTRACT

import uuid
import logging
from sqlalchemy.orm import Session
from app.models.activity import Activity, ActivityType
from app.repositories.activity_repo import ActivityRepository
from app.repositories.deal_repo import DealRepository
from app.services.errors import NotFoundError, ForeignKeyValidationError

logger = logging.getLogger(__name__)


class ActivityService:
    """
    [START_CONTRACT_ACTIVITY_SERVICE]
    Intent: Сервис для управления активностями с FK валидацией.
    Input: db - SQLAlchemy Session.
    Output: Методы: create_activity, get_deal_timeline.
    [END_CONTRACT_ACTIVITY_SERVICE]
    """

    def __init__(self, db: Session):
        self.activity_repo = ActivityRepository(db)
        self.deal_repo = DealRepository(db)

    def create_activity(
        self,
        deal_id: uuid.UUID,
        description: str,
        activity_type: ActivityType = ActivityType.NOTE,
    ) -> Activity:
        """
        [START_CONTRACT_CREATE_ACTIVITY]
        Intent: Создать активность для сделки с FK валидацией.
        Input: deal_id - UUID сделки; description - обязательное; type - по умолчанию NOTE.
        Output: Activity объект или ForeignKeyValidationError.
        [END_CONTRACT_CREATE_ACTIVITY]
        """
        logger.debug(
            f"[ActivityService][create_activity] Belief: Create activity | "
            f"Input: deal_id={deal_id}, type={activity_type.value} | "
            "Expected: Activity created"
        )
        # FK validation
        if not self.deal_repo.get_by_id(deal_id):
            raise ForeignKeyValidationError("deal_id", "Deal")
        activity = self.activity_repo.create({
            "deal_id": deal_id,
            "type": activity_type,
            "description": description,
        })
        return activity

    def get_deal_timeline(
        self, deal_id: uuid.UUID, skip: int = 0, limit: int = 100
    ) -> list[Activity]:
        """
        [START_CONTRACT_GET_DEAL_TIMELINE]
        Intent: Получить timeline активностей сделки, отсортированный DESC.
        Input: deal_id - UUID сделки; skip, limit - пагинация.
        Output: Список Activity объектов (новые сначала) или NotFoundError.
        [END_CONTRACT_GET_DEAL_TIMELINE]
        """
        logger.debug(
            f"[ActivityService][get_deal_timeline] Belief: Get timeline | "
            f"Input: deal_id={deal_id} | Expected: Activities DESC sorted"
        )
        # Check deal exists
        if not self.deal_repo.get_by_id(deal_id):
            raise NotFoundError("Deal", str(deal_id))
        return self.activity_repo.get_by_deal_id(deal_id, skip=skip, limit=limit)