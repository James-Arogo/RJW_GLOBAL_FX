"""Main FastAPI application entry point."""

import logging
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.core.database import init_db, close_db
from app.api import auth, trade, health, prices, dashboard, payments
from app.services.price_engine import adjust_bias_periodically
from app.utils.logger import logger

# Setup logging
logging.getLogger().setLevel(settings.LOG_LEVEL)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager."""
    # Startup
    logger.info(f"🚀 Starting {settings.APP_NAME}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    
    # Initialize database
    try:
        await init_db()
        logger.info("✅ Database initialized")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        raise
    
    # Start background task for bias adjustment
    bias_task = asyncio.create_task(adjust_bias_periodically(interval=300))
    logger.info("✅ Price engine bias adjustment task started")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down...")
    bias_task.cancel()
    await close_db()
    logger.info("✅ Database connection closed")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Simulated Forex Trading Platform for Kenyan University Students",
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# Add middleware
# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Trusted hosts
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"] if settings.DEBUG else ["localhost", "127.0.0.1", "*.localhost"]
)


# Include routers
app.include_router(health.router)
app.include_router(auth.router, prefix="/api")
app.include_router(trade.router, prefix="/api")
app.include_router(prices.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")
app.include_router(payments.router, prefix="/api")


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "disclaimer": settings.SIMULATION_DISCLAIMER,
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "auth_register": "/api/auth/register",
            "auth_login": "/api/auth/login",
            "trades": "/api/trades",
        }
    }


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger.error(f"Unexpected error: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error_code": "INTERNAL_ERROR"
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"Starting server on 0.0.0.0:8000")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )
