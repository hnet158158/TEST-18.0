# START_MODULE_CONTRACT
# Module: repositories.activity_repo
# Intent: Репозиторий для операций с активностями.
# Инкапсулирует доступ к данным модели Activity.
# END_MODULE_CONTRACT

import uuid
from sqlalchemy.orm import Session
from app.models.activity import Activity
from app.repositories.base import BaseRepository


class ActivityRepository(BaseRepository[Activity]):
    """
    [START_CONTRACT_ACTIVITY_REPOSITORY]
    Intent: Репозиторий для CRUD операций над активностями.
    Input: db - SQLAlchemy Session.
    Output: Методы: create, get_by_deal_id.
    [END_CONTRACT_ACTIVITY_REPOSITORY]
    """

    def __init__(self, db: Session):
        super().__init__(Activity, db)

    def get_by_deal_id(
        self, deal_id: uuid.UUID, skip: int = 0, limit: int = 100
    ) -> list[Activity]:
        """
        [START_CONTRACT_GET_BY_DEAL_ID]
        Intent: Получить timeline активностей по сделке, отсортированный DESC по created_at.
        Input: deal_id - UUID сделки, skip, limit - пагинация.
        Output: Список активностей, отсортированный по убыванию created_at.
        [END_CONTRACT_GET_BY_DEAL_ID]
        """
        return (
            self.db.query(Activity)
            .filter(Activity.deal_id == deal_id)
            .order_by(Activity.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )