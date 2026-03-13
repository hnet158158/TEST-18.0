# START_MODULE_CONTRACT
# Module: repositories.base
# Intent: Базовый репозиторий с общими CRUD операциями.
# Использует SQLAlchemy Session для синхронного доступа к данным.
# END_MODULE_CONTRACT

import uuid
from typing import Generic, TypeVar, Type, Any
from sqlalchemy.orm import Session

ModelType = TypeVar("ModelType", bound=Any)


class BaseRepository(Generic[ModelType]):
    """
    [START_CONTRACT_BASE_REPOSITORY]
    Intent: Базовый класс репозитория с общими CRUD операциями.
    Input: model - SQLAlchemy модель, db - Session.
    Output: CRUD методы: create, get_by_id, get_all, update, delete.
    [END_CONTRACT_BASE_REPOSITORY]
    """

    def __init__(self, model: Type[ModelType], db: Session):
        # CONTRACT: Intent: Инициализация с моделью и сессией БД.
        self.model = model
        self.db = db

    def create(self, obj_in: dict) -> ModelType:
        """
        [START_CONTRACT_CREATE]
        Intent: Создать новую запись в БД.
        Input: obj_in - словарь с полями модели.
        Output: Созданный объект модели, добавленный в БД.
        [END_CONTRACT_CREATE]
        """
        db_obj = self.model(**obj_in)
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def get_by_id(self, id: uuid.UUID) -> ModelType | None:
        """
        [START_CONTRACT_GET_BY_ID]
        Intent: Получить запись по UUID.
        Input: id - UUID записи.
        Output: Объект модели или None если не найден.
        [END_CONTRACT_GET_BY_ID]
        """
        return self.db.query(self.model).filter(self.model.id == id).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> list[ModelType]:
        """
        [START_CONTRACT_GET_ALL]
        Intent: Получить все записи с пагинацией.
        Input: skip - смещение, limit - лимит записей.
        Output: Список объектов модели.
        [END_CONTRACT_GET_ALL]
        """
        return self.db.query(self.model).offset(skip).limit(limit).all()

    def update(self, id: uuid.UUID, obj_in: dict) -> ModelType | None:
        """
        [START_CONTRACT_UPDATE]
        Intent: Обновить запись по UUID.
        Input: id - UUID записи, obj_in - словарь с обновляемыми полями.
        Output: Обновлённый объект или None если не найден.
        [END_CONTRACT_UPDATE]
        """
        db_obj = self.get_by_id(id)
        if db_obj is None:
            return None
        for key, value in obj_in.items():
            if hasattr(db_obj, key):
                setattr(db_obj, key, value)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def delete(self, id: uuid.UUID) -> bool:
        """
        [START_CONTRACT_DELETE]
        Intent: Удалить запись по UUID.
        Input: id - UUID записи.
        Output: True если удалено, False если не найдено.
        [END_CONTRACT_DELETE]
        """
        db_obj = self.get_by_id(id)
        if db_obj is None:
            return False
        self.db.delete(db_obj)
        self.db.commit()
        return True