# START_MODULE_CONTRACT
# Module: api.v1.deals
# Intent: HTTP роуты для сделок.
# POST, GET (с фильтрами), GET/{id}, PUT, PATCH/stage, DELETE.
# END_MODULE_CONTRACT

import uuid
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.deal import DealCreate, DealUpdate, DealStageUpdate, DealResponse
from app.models.deal import DealStage
from app.services import (
    DealService,
    NotFoundError,
    ForeignKeyValidationError,
    InvalidStageTransitionError,
    HasRelatedEntitiesError,
)

router = APIRouter(prefix="/deals", tags=["deals"])


@router.post("", response_model=DealResponse, status_code=201)
def create_deal(
    deal_data: DealCreate,
    db: Session = Depends(get_db)
):
    """
    [START_CONTRACT_CREATE_DEAL_API]
    Intent: Создать сделку. Stage всегда LEAD. FK валидация.
    Input: DealCreate (title, company_id, owner_id, value?, description?).
    Output: DealResponse (201) или 400 при невалидном FK.
    [END_CONTRACT_CREATE_DEAL_API]
    """
    service = DealService(db)
    try:
        return service.create_deal(
            title=deal_data.title,
            company_id=deal_data.company_id,
            owner_id=deal_data.owner_id,
            value=deal_data.value,
            description=deal_data.description
        )
    except ForeignKeyValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=list[DealResponse])
def get_deals(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    stage: DealStage | None = Query(None),
    company_id: uuid.UUID | None = Query(None),
    db: Session = Depends(get_db)
):
    """
    [START_CONTRACT_GET_DEALS_API]
    Intent: Получить список сделок с пагинацией и фильтрами.
    Input: skip, limit - пагинация; stage?, company_id? - фильтры.
    Output: List[DealResponse] (200).
    [END_CONTRACT_GET_DEALS_API]
    """
    service = DealService(db)
    return service.get_deals(skip=skip, limit=limit, stage=stage, company_id=company_id)


@router.get("/{deal_id}", response_model=DealResponse)
def get_deal(deal_id: uuid.UUID, db: Session = Depends(get_db)):
    """
    [START_CONTRACT_GET_DEAL_API]
    Intent: Получить сделку по ID.
    Input: deal_id (UUID).
    Output: DealResponse (200) или 404 если не найдена.
    [END_CONTRACT_GET_DEAL_API]
    """
    service = DealService(db)
    try:
        return service.get_deal(deal_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/{deal_id}", response_model=DealResponse)
def update_deal(
    deal_id: uuid.UUID,
    deal_data: DealUpdate,
    db: Session = Depends(get_db)
):
    """
    [START_CONTRACT_UPDATE_DEAL_API]
    Intent: Обновить сделку. company_id, owner_id, stage нельзя менять.
    Input: deal_id (UUID), DealUpdate (title?, value?, description?).
    Output: DealResponse (200) или 404 если не найдена.
    [END_CONTRACT_UPDATE_DEAL_API]
    """
    service = DealService(db)
    try:
        return service.update_deal(
            deal_id=deal_id,
            title=deal_data.title,
            value=deal_data.value,
            description=deal_data.description
        )
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.patch("/{deal_id}/stage", response_model=DealResponse)
def change_deal_stage(
    deal_id: uuid.UUID,
    stage_data: DealStageUpdate,
    db: Session = Depends(get_db)
):
    """
    [START_CONTRACT_CHANGE_STAGE_API]
    Intent: Изменить стадию сделки с валидацией перехода.
    Input: deal_id (UUID), DealStageUpdate (stage).
    Output: DealResponse (200) или 400 при невалидном переходе.
    [END_CONTRACT_CHANGE_STAGE_API]
    """
    service = DealService(db)
    try:
        return service.change_deal_stage(deal_id, stage_data.stage)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except InvalidStageTransitionError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{deal_id}", status_code=204)
def delete_deal(deal_id: uuid.UUID, db: Session = Depends(get_db)):
    """
    [START_CONTRACT_DELETE_DEAL_API]
    Intent: Удалить сделку. Нельзя если есть активности.
    Input: deal_id (UUID).
    Output: 204 No Content или 400 если есть активности.
    [END_CONTRACT_DELETE_DEAL_API]
    """
    service = DealService(db)
    try:
        service.delete_deal(deal_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except HasRelatedEntitiesError as e:
        raise HTTPException(status_code=400, detail=str(e))