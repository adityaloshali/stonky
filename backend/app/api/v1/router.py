"""
Main API v1 router.

Combines all endpoint routers into a single router for the API.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import (
    search,
    company,
    prices,
    news,
    fundamentals
)

# Create main API router
api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(search.router, tags=["search"])
api_router.include_router(company.router, tags=["company"])
api_router.include_router(prices.router, tags=["prices"])
api_router.include_router(news.router, tags=["news"])
api_router.include_router(fundamentals.router, tags=["fundamentals"])
