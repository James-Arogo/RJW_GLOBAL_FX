"""Logging configuration."""

import logging
import logging.handlers
from pathlib import Path
from app.core.config import settings

# Create logs directory
logs_dir = Path("logs")
logs_dir.mkdir(exist_ok=True)

# Configure logging
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),  # Console
        logging.handlers.RotatingFileHandler(
            logs_dir / "app.log",
            maxBytes=10485760,  # 10MB
            backupCount=10
        )
    ]
)

logger = logging.getLogger("rjw_global_fx")
