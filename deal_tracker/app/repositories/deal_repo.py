# START_MODULE_CONTRACT
# Module: repositories.deal_repo
# Intent: Репозиторий для операций со сделками.
# Инкапсулирует доступ к данным модели Deal с фильтрацией по stage.
# END_MODULE_CONTRACT

import uuid
from typing import Any
from sqlalchemy.orm import Session
from app.models.deal import Deal, DealStage
from app.models.activity import Activity
from app.repositories.base import BaseRepository


class DealRepository(BaseRepository[Deal]):
    """
    [START_CONTRACT_DEAL_REPOSITORY]
    Intent: Репозиторий для CRUD операций над сделками с фильтрацией.
    Input: db - SQLAlchemy Session.
    Output: Методы: create, get_by_id, get_all, update, delete, change_stage, has_activities.
    [END_CONTRACT_DEAL_REPOSITORY]
    """

    def __init__(self, db: Session):
        super().__init__(Deal, db)

    def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        stage: DealStage | None = None,
        company_id: uuid.UUID | None = None,
    ) -> list[Deal]:
        """
        [START_CONTRACT_GET_ALL_DEALS]
        Intent: Получить сделки с опциональной фильтрацией по stage и company_id.
        Input: skip, limit - пагинация; stage - фильтр по стадии; company_id - фильтр по компании.
        Output: Список сделок, отфильтрованный по параметрам.
        [END_CONTRACT_GET_ALL_DEALS]
        """
        query = self.db.query(Deal)
        if stage is not None:
            query = query.filter(Deal.stage == stage)
        if company_id is not None:
            query = query.filter(Deal.company_id == company_id)
        return query.offset(skip).limit(limit).all()

    def change_stage(
        self, deal_id: uuid.UUID, new_stage: DealStage
    ) -> Deal | None:
        """
        [START_CONTRACT_CHANGE_STAGE]
        Intent: Изменить стадию сделки (без валидации перехода).
        Input: deal_id - UUID сделки, new_stage - новая стадия.
        Output: Обновлённая сделка или None если не найдена.
        [END_CONTRACT_CHANGE_STAGE]
        """
        db_obj = self.get_by_id(deal_id)
        if db_obj is None:
            return None
        db_obj.stage = new_stage
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def has_activities(self, deal_id: uuid.UUID) -> bool:
        """
        [START_CONTRACT_HAS_ACTIVITIES]
        Intent: Проверить наличие активностей у сделки перед удалением.
        Input: deal_id - UUID сделки.
        Output: True если есть активности, False если нет.
        [END_CONTRACT_HAS_ACTIVITIES]
        """
        return (
            self.db.query(Activity)
            .filter(Activity.deal_id == deal_id)
            .first()
            is not None
        )