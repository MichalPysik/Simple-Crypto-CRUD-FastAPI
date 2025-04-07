from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Application settings
    APP_NAME: str = "Crypto CRUD API"
    
    # Database settings
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "crypto"
    POSTGRES_HOST: str = "db"
    POSTGRES_PORT: int = 5432
    DATABASE_URL: Optional[str] = None
    
    # Redis settings
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6381
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None
    
    # CoinGecko API settings
    COINGECKO_API_URL: str = "https://api.coingecko.com/api/v3"
    
    @property
    def get_database_url(self) -> str:
        """Generate database URL from components if not explicitly provided via docker compose"""
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    class Config:
        case_sensitive = True

settings = Settings()
