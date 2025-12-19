from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Trading Risk Governor"
    API_V1_STR: str = "/api/v1"
    
    # Database
    DATABASE_URL: str = "postgresql+psycopg://postgres:postgres@localhost:5432/trading_risk_governor"
    
    # Gemini
    GEMINI_API_KEY: Optional[str] = None

    # Delta Exchange
    DELTA_API_KEY: Optional[str] = None
    DELTA_API_SECRET: Optional[str] = None
    DELTA_BASE_URL: str = "https://api.india.delta.exchange"
    
    # Risk Defaults (Can be overridden in DB)
    DEFAULT_MAX_DAILY_LOSS_R: float = 3.0
    DEFAULT_MAX_TRADES_DAY: int = 5
    DEFAULT_STARTING_BALANCE: float = 10000.0

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

settings = Settings()
