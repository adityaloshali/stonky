"""
Logging configuration using Loguru.
Provides structured logging with rotation and JSON formatting.
"""

import sys
from loguru import logger
from app.core.config import settings


def setup_logging() -> None:
    """
    Configure logging based on environment.

    Development: Pretty console output
    Production: JSON structured logs
    """
    # Remove default handler
    logger.remove()

    # Console handler
    if settings.is_development:
        # Pretty format for development
        logger.add(
            sys.stdout,
            colorize=True,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            level=settings.LOG_LEVEL,
        )
    else:
        # JSON format for production (easier to parse)
        logger.add(
            sys.stdout,
            serialize=True,  # JSON output
            level=settings.LOG_LEVEL,
        )

    # File handler (rotate at 10 MB)
    logger.add(
        "logs/app.log",
        rotation="10 MB",
        retention="10 days",
        compression="zip",
        level=settings.LOG_LEVEL,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    )

    # Error file handler (errors only)
    logger.add(
        "logs/error.log",
        rotation="10 MB",
        retention="30 days",
        compression="zip",
        level="ERROR",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    )

    logger.info(f"Logging configured for {settings.ENV} environment")
