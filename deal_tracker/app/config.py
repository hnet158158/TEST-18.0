# START_MODULE_CONTRACT
# Module: config
# Intent: Конфигурация приложения через pydantic-settings.
# Загружает переменные окружения с дефолтными значениями.
# END_MODULE_CONTRACT

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    [START_CONTRACT_SETTINGS]
    Intent: Централизованная конфигурация приложения.
    Input: ENV переменные (опционально).
    Output: Объект с настройками для использования во всём приложении.
    [END_CONTRACT_SETTINGS]
    """
    database_url: str = "sqlite:///./deal_tracker.db"
    app_env: str = "development"
    debug: bool = True

    class Config:
        env_file = ".env"


settings = Settings()