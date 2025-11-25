from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Настройки приложения."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True
    )
    
    # База данных
    DATABASE_URL: str = "sqlite+aiosqlite:///./data/leads_crm.db"
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "Leads CRM"
    PROJECT_VERSION: str = "1.0.0"


settings = Settings()

