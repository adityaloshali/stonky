"""
FastAPI application entry point.
Main application setup with middleware, CORS, and routers.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from loguru import logger

from app.core.config import settings
from app.core.logging import setup_logging
from app.core.database import close_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.

    Startup:
        - Configure logging
        - Log configuration status

    Shutdown:
        - Close database connections
    """
    # Startup
    setup_logging()
    logger.info("Starting Stonky FastAPI Backend")
    logger.info(f"Environment: {settings.ENV}")
    logger.info(f"Debug mode: {settings.DEBUG}")
    logger.info(f"API prefix: {settings.API_V1_PREFIX}")
    logger.info(f"CORS origins: {settings.cors_origins_list}")

    # Log feature availability
    logger.info(f"Screener.in configured: {settings.has_screener_cookie}")
    logger.info(f"OpenAI configured: {settings.has_openai_key}")
    logger.info(f"OpenRouter configured: {settings.has_openrouter_key}")

    yield

    # Shutdown
    logger.info("Shutting down Stonky FastAPI Backend")
    await close_db()


# Create FastAPI application
app = FastAPI(
    title="Stonky API",
    description="AI-Augmented Stock Analysis Platform for Indian Markets (NSE/BSE)",
    version="2.0.0",
    docs_url="/docs" if settings.DEBUG else None,  # Disable docs in production
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# GZip compression middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)


# Health check endpoint
@app.get("/health", tags=["health"])
async def health_check():
    """
    Health check endpoint.
    Returns application status and configuration info.
    """
    return JSONResponse(
        content={
            "status": "healthy",
            "environment": settings.ENV,
            "version": "2.0.0",
            "features": {
                "screener_configured": settings.has_screener_cookie,
                "ai_configured": settings.has_openai_key or settings.has_openrouter_key,
            },
        }
    )


# Root endpoint
@app.get("/", tags=["root"])
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Stonky API - AI-Augmented Stock Analysis",
        "version": "2.0.0",
        "docs": "/docs" if settings.DEBUG else "Documentation disabled in production",
        "health": "/health",
    }


# API v1 router (to be added)
# from app.api.v1.router import api_router
# app.include_router(api_router, prefix=settings.API_V1_PREFIX)
