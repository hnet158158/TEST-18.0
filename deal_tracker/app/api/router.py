# START_MODULE_CONTRACT
# Module: api.router
# Intent: Агрегация всех API роутов в один корневой роутер.
# END_MODULE_CONTRACT

from fastapi import APIRouter
from app.api.v1 import users, companies, deals, activities

api_router = APIRouter(prefix="/api/v1")

# START_BLOCK_ROUTES
api_router.include_router(users.router)
api_router.include_router(companies.router)
api_router.include_router(deals.router)
api_router.include_router(activities.router)
# END_BLOCK_ROUTES