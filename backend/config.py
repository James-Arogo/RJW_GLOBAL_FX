"""
config.py
=================================
Professional configuration module for the RJW GLOBAL FX backend.
Manages environment-specific settings for database, security, logging,
and system control.
"""

import os
from datetime import timedelta


# ==========================================================
# Base Configuration (shared across all environments)
# ==========================================================
class BaseConfig:
    """Base configuration shared by all environments."""

    # --- General App Info ---
    APP_NAME = "RJW GLOBAL FX"
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    SECRET_KEY = os.environ.get("SECRET_KEY", "rjw_global_fx_secret_key")

    # --- Database Configuration ---
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        f"sqlite:///{os.path.join(BASE_DIR, 'database.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # --- Session & Security Settings ---
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    
    # --- JWT Configuration ---
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "rjw_global_fx_jwt_secret")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # --- Email Configuration ---
    MAIL_SERVER = os.environ.get("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.environ.get("MAIL_PORT", 587))
    MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS", "true").lower() in ["true", "on", "1"]
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.environ.get("MAIL_DEFAULT_SENDER", "noreply@rjwglobalfx.com")
    
    # --- Email Verification Settings ---
    EMAIL_VERIFICATION_EXPIRE_HOURS = 24
    PASSWORD_RESET_EXPIRE_HOURS = 1
    
    # --- Frontend URL Configuration ---
    FRONTEND_URL = os.environ.get("FRONTEND_URL", "http://localhost:4000")

    # --- Platform Business Logic ---
    PLATFORM_PROFIT_MARGIN = 0.30  # Maintain 30% system-controlled profit margin
    AUTO_TRADE_INTERVAL = 5        # Seconds between simulated trades

    # --- Logging Configuration ---
    LOG_DIR = os.path.join(BASE_DIR, "logs")
    os.makedirs(LOG_DIR, exist_ok=True)
    LOG_FILE = os.path.join(LOG_DIR, "app.log")

    # --- Default States ---
    DEBUG = False
    TESTING = False


# ==========================================================
# Development Environment
# ==========================================================
class DevelopmentConfig(BaseConfig):
    """Development environment configuration."""
    DEBUG = True
    SQLALCHEMY_ECHO = True  # Show executed SQL queries for debugging
    ENV_NAME = "development"
    SERVER_NAME = "localhost:4000"


# ==========================================================
# Production Environment
# ==========================================================
class ProductionConfig(BaseConfig):
    """Production environment configuration."""
    DEBUG = False
    SQLALCHEMY_ECHO = False
    SESSION_COOKIE_SECURE = True   # Enforce HTTPS in production
    PERMANENT_SESSION_LIFETIME = timedelta(days=30)
    ENV_NAME = "production"


# ==========================================================
# Testing Environment
# ==========================================================
class TestingConfig(BaseConfig):
    """Testing environment configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    ENV_NAME = "testing"
    DEBUG = True


# ==========================================================
# Configuration Selector
# ==========================================================
config_by_name = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig
}


def get_config():
    """
    Dynamically select configuration class based on environment variable.
    - Reads FLASK_ENV (default: 'development')
    - Falls back gracefully if invalid or unset.
    """
    env = os.environ.get("FLASK_ENV", "development").lower()
    config_class = config_by_name.get(env, DevelopmentConfig)

    print(f"[*] Environment detected: {config_class.ENV_NAME.upper()}")
    print(f"[*] Database: {config_class.SQLALCHEMY_DATABASE_URI}")
    print(f"[*] Debug mode: {config_class.DEBUG}")

    return config_class
