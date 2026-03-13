# START_MODULE_CONTRACT
# Module: repositories.user_repo
# Intent: Репозиторий для операций с пользователями.
# Инкапсулирует доступ к данным модели User.
# END_MODULE_CONTRACT

import uuid
from sqlalchemy.orm import Session
from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """
    [START_CONTRACT_USER_REPOSITORY]
    Intent: Репозиторий для CRUD операций над пользователями.
    Input: db - SQLAlchemy Session.
    Output: Методы: create, get_by_id, get_all, get_by_email.
    [END_CONTRACT_USER_REPOSITORY]
    """

    def __init__(self, db: Session):
        super().__init__(User, db)

    def get_by_email(self, email: str) -> User | None:
        """
        [START_CONTRACT_GET_BY_EMAIL]
        Intent: Найти пользователя по email (уникальное поле).
        Input: email - строка email для поиска.
        Output: User объект или None если не найден.
        [END_CONTRACT_GET_BY_EMAIL]
        """
        return self.db.query(User).filter(User.email == email).first()