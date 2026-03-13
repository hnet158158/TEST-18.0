# START_MODULE_CONTRACT
# Module: services.user_service
# Intent: Бизнес-логика для пользователей.
# Валидация email уникальности, делегирование к репозиторию.
# END_MODULE_CONTRACT

import uuid
import logging
from sqlalchemy.orm import Session
from app.models.user import User
from app.repositories.user_repo import UserRepository
from app.services.errors import NotFoundError, DuplicateEmailError

logger = logging.getLogger(__name__)


class UserService:
    """
    [START_CONTRACT_USER_SERVICE]
    Intent: Сервис для управления пользователями с валидацией email.
    Input: db - SQLAlchemy Session.
    Output: Методы: create_user, get_user, get_users.
    [END_CONTRACT_USER_SERVICE]
    """

    def __init__(self, db: Session):
        self.user_repo = UserRepository(db)

    def create_user(self, email: str, name: str) -> User:
        """
        [START_CONTRACT_CREATE_USER]
        Intent: Создать пользователя с проверкой уникальности email.
        Input: email - уникальный email; name - имя пользователя.
        Output: User объект или DuplicateEmailError если email занят.
        [END_CONTRACT_CREATE_USER]
        """
        logger.debug(
            "[UserService][create_user] Belief: Create user | "
            f"Input: email={email} | Expected: User created"
        )
        existing = self.user_repo.get_by_email(email)
        if existing:
            logger.debug(
                "[UserService][create_user] Belief: Duplicate detected | "
                f"Input: email={email} | Expected: DuplicateEmailError"
            )
            raise DuplicateEmailError(email)
        user = self.user_repo.create({"email": email, "name": name})
        logger.debug(
            "[UserService][create_user] Belief: User created | "
            f"Input: email={email} | Expected: User id={user.id}"
        )
        return user

    def get_user(self, user_id: uuid.UUID) -> User:
        """
        [START_CONTRACT_GET_USER]
        Intent: Получить пользователя по ID.
        Input: user_id - UUID пользователя.
        Output: User объект или NotFoundError если не найден.
        [END_CONTRACT_GET_USER]
        """
        logger.debug(
            f"[UserService][get_user] Belief: Fetch user | "
            f"Input: id={user_id} | Expected: User or NotFoundError"
        )
        user = self.user_repo.get_by_id(user_id)
        if user is None:
            raise NotFoundError("User", str(user_id))
        return user

    def get_users(self, skip: int = 0, limit: int = 100) -> list[User]:
        """
        [START_CONTRACT_GET_USERS]
        Intent: Получить список всех пользователей.
        Input: skip, limit - пагинация.
        Output: Список User объектов.
        [END_CONTRACT_GET_USERS]
        """
        # CONTRACT: Intent: Получить всех пользователей с пагинацией.
        return self.user_repo.get_all(skip=skip, limit=limit)