# START_MODULE_CONTRACT
# Module: api.v1.activities
# Intent: HTTP роуты для активностей.
# POST (создать активность), GET (timeline сделки).
# DELETE и PUT не реализованы (Activity immutable).
# END_MODULE_CONTRACT

import uuid
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.activity import ActivityCreate, ActivityResponse
from app.services import ActivityService, NotFoundError, ForeignKeyValidationError

router = APIRouter(tags=["activities"])


@router.post(
    "/deals/{deal_id}/activities",
    response_model=ActivityResponse,
    status_code=201
)
def create_activity(
    deal_id: uuid.UUID,
    activity_data: ActivityCreate,
    db: Session = Depends(get_db)
):
    """
    [START_CONTRACT_CREATE_ACTIVITY_API]
    Intent: Создать активность для сделки. FK валидация deal_id.
    Input: deal_id (UUID), ActivityCreate (type?, description).
    Output: ActivityResponse (201) или 400 при невалидном deal_id.
    [END_CONTRACT_CREATE_ACTIVITY_API]
    """
    service = ActivityService(db)
    try:
        return service.create_activity(
            deal_id=deal_id,
            activity_type=activity_data.type,
            description=activity_data.description
        )
    except ForeignKeyValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/deals/{deal_id}/activities",
    response_model=list[ActivityResponse]
)
def get_deal_timeline(
    deal_id: uuid.UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """
    [START_CONTRACT_GET_TIMELINE_API]
    Intent: Получить timeline сделки (активности DESC) с пагинацией.
    Input: deal_id (UUID); skip, limit - пагинация.
    Output: List[ActivityResponse] (200) отсортирован по created_at DESC.
    [END_CONTRACT_GET_TIMELINE_API]
    """
    service = ActivityService(db)
    try:
        return service.get_deal_timeline(deal_id, skip=skip, limit=limit)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))