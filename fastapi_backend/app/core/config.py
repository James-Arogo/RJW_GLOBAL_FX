"""Application configuration using Pydantic Settings."""

from typing import List
from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # App
    APP_NAME: str = "RJW GLOBAL FX - FastAPI Backend"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./test.db"
    
    # Security
    SECRET_KEY: str = "your-super-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
    ]
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    # Refresh Token
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Forex Simulation
    MIN_STAKE_KES: float = 50.0
    STARTING_BALANCE_KES: float = 10_000.0
    MAX_LEVERAGE: float = 50.0
    DEFAULT_LEVERAGE: float = 5.0
    MAINTENANCE_MARGIN_RATIO: float = 0.35
    CURRENCY: str = "KES"
    SIMULATION_DISCLAIMER: str = (
        "This is a simulated forex game for learning & fun only. "
        "Prices are controlled by the platform. "
        "Not connected to real forex markets. "
        "Play at own risk – no real profits/losses outside the app."
    )

    # Payments / provider setup
    PAYMENT_PROVIDER_MODE: str = "simulated"
    MPESA_SHORTCODE: str = ""
    MPESA_PASSKEY: str = ""
    MPESA_CONSUMER_KEY: str = ""
    MPESA_CONSUMER_SECRET: str = ""
    MPESA_CALLBACK_URL: str = ""
    CARD_PROVIDER_NAME: str = "Flutterwave"
    CARD_PROVIDER_PUBLIC_KEY: str = ""
    CARD_PROVIDER_SECRET_KEY: str = ""
    CARD_PROVIDER_CALLBACK_URL: str = ""

    @field_validator("DEBUG", mode="before")
    @classmethod
    def parse_debug(cls, value):
        """Accept common env-style debug strings."""
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in {"1", "true", "yes", "on", "debug", "development"}:
                return True
            if normalized in {"0", "false", "no", "off", "release", "production"}:
                return False
        return value
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create settings instance
settings = Settings()
