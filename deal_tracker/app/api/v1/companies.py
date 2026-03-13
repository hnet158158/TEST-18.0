# START_MODULE_CONTRACT
# Module: api.v1.companies
# Intent: HTTP роуты для компаний.
# POST, GET, GET/{id}, PUT, DELETE. DELETE возвращает 204.
# END_MODULE_CONTRACT

import uuid
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.company import CompanyCreate, CompanyUpdate, CompanyResponse
from app.services import CompanyService, NotFoundError, HasRelatedEntitiesError

router = APIRouter(prefix="/companies", tags=["companies"])


@router.post("", response_model=CompanyResponse, status_code=201)
def create_company(
    company_data: CompanyCreate,
    db: Session = Depends(get_db)
):
    """
    [START_CONTRACT_CREATE_COMPANY_API]
    Intent: Создать компанию. Name обязательное поле.
    Input: CompanyCreate (name, website?, industry?).
    Output: CompanyResponse (201).
    [END_CONTRACT_CREATE_COMPANY_API]
    """
    service = CompanyService(db)
    return service.create_company(
        name=company_data.name,
        website=company_data.website,
        industry=company_data.industry
    )


@router.get("", response_model=list[CompanyResponse])
def get_companies(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """
    [START_CONTRACT_GET_COMPANIES_API]
    Intent: Получить список компаний с пагинацией.
    Input: skip - смещение; limit - лимит записей.
    Output: List[CompanyResponse] (200).
    [END_CONTRACT_GET_COMPANIES_API]
    """
    service = CompanyService(db)
    return service.get_companies(skip=skip, limit=limit)


@router.get("/{company_id}", response_model=CompanyResponse)
def get_company(company_id: uuid.UUID, db: Session = Depends(get_db)):
    """
    [START_CONTRACT_GET_COMPANY_API]
    Intent: Получить компанию по ID.
    Input: company_id (UUID).
    Output: CompanyResponse (200) или 404 если не найдена.
    [END_CONTRACT_GET_COMPANY_API]
    """
    service = CompanyService(db)
    try:
        return service.get_company(company_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/{company_id}", response_model=CompanyResponse)
def update_company(
    company_id: uuid.UUID,
    company_data: CompanyUpdate,
    db: Session = Depends(get_db)
):
    """
    [START_CONTRACT_UPDATE_COMPANY_API]
    Intent: Обновить компанию. Все поля опциональны.
    Input: company_id (UUID), CompanyUpdate.
    Output: CompanyResponse (200) или 404 если не найдена.
    [END_CONTRACT_UPDATE_COMPANY_API]
    """
    service = CompanyService(db)
    try:
        return service.update_company(
            company_id=company_id,
            name=company_data.name,
            website=company_data.website,
            industry=company_data.industry
        )
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{company_id}", status_code=204)
def delete_company(company_id: uuid.UUID, db: Session = Depends(get_db)):
    """
    [START_CONTRACT_DELETE_COMPANY_API]
    Intent: Удалить компанию. Нельзя если есть связанные сделки.
    Input: company_id (UUID).
    Output: 204 No Content или 400 если есть сделки.
    [END_CONTRACT_DELETE_COMPANY_API]
    """
    service = CompanyService(db)
    try:
        service.delete_company(company_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except HasRelatedEntitiesError as e:
        raise HTTPException(status_code=400, detail=str(e))