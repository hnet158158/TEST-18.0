# START_MODULE_CONTRACT
# Module: api.v1.users
# Intent: HTTP роуты для пользователей.
# POST, GET, GET/{id}. DELETE не реализован (User нельзя удалить).
# END_MODULE_CONTRACT

import uuid
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.user import UserCreate, UserResponse
from app.services import UserService, NotFoundError, DuplicateEmailError

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=UserResponse, status_code=201)
def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """
    [START_CONTRACT_CREATE_USER_API]
    Intent: Создать пользователя. Email должен быть уникальным.
    Input: UserCreate (email, name).
    Output: UserResponse (201) или 400 при дублировании email.
    [END_CONTRACT_CREATE_USER_API]
    """
    service = UserService(db)
    try:
        user = service.create_user(email=user_data.email, name=user_data.name)
        return user
    except DuplicateEmailError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=list[UserResponse])
def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """
    [START_CONTRACT_GET_USERS_API]
    Intent: Получить список пользователей с пагинацией.
    Input: skip - смещение; limit - лимит записей.
    Output: List[UserResponse] (200).
    [END_CONTRACT_GET_USERS_API]
    """
    service = UserService(db)
    return service.get_users(skip=skip, limit=limit)


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: uuid.UUID, db: Session = Depends(get_db)):
    """
    [START_CONTRACT_GET_USER_API]
    Intent: Получить пользователя по ID.
    Input: user_id (UUID).
    Output: UserResponse (200) или 404 если не найден.
    [END_CONTRACT_GET_USER_API]
    """
    service = UserService(db)
    try:
        return service.get_user(user_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))