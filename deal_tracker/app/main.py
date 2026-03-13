# START_MODULE_CONTRACT
# Module: main
# Intent: Точка входа FastAPI приложения.
# Инициализация приложения, подключение роутов, создание таблиц.
# END_MODULE_CONTRACT

from fastapi import FastAPI
from app.api.router import api_router
from app.database import create_tables

# START_BLOCK_APP
app = FastAPI(
    title="Deal Tracker API",
    description="REST API для отслеживания сделок через стадии",
    version="1.0.0"
)

app.include_router(api_router)


@app.on_event("startup")
def startup_event():
    """
    [START_CONTRACT_STARTUP]
    Intent: Инициализация при запуске приложения. Создаёт таблицы БД.
    Input: Нет.
    Output: Таблицы созданы (idempotent).
    [END_CONTRACT_STARTUP]
    """
    create_tables()
# END_BLOCK_APP