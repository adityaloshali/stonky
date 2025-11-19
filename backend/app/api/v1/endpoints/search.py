"""
Stock symbol search endpoints.
"""

from fastapi import APIRouter, Query, Depends
from loguru import logger

from app.api.v1.schemas.responses import SearchResponse, StockSearchResult
from app.core.dependencies import ServiceFactory, get_service_factory

router = APIRouter()


@router.get("/search", response_model=SearchResponse, tags=["search"])
async def search_symbols(
    q: str = Query(..., min_length=1, description="Search query (symbol or company name)"),
    limit: int = Query(10, ge=1, le=50, description="Maximum number of results"),
    factory: ServiceFactory = Depends(get_service_factory)
):
    """
    Search for stock symbols by company name or symbol.

    Uses Yahoo Finance for Indian stocks (NSE/BSE).

    **Example:**
    - `/api/v1/search?q=RELIANCE` - Search for Reliance
    - `/api/v1/search?q=TCS&limit=5` - Search for TCS, max 5 results
    """
    logger.info(f"Symbol search: query='{q}', limit={limit}")

    try:
        yahoo = factory.create_yahoo_service()
        results = await yahoo.search_symbols(q, limit=limit)

        # Transform to response format
        search_results = [
            StockSearchResult(
                symbol=r['symbol'],
                name=r['name'],
                exchange=r['type'],
                sector=r.get('sector'),
                industry=r.get('industry')
            )
            for r in results
        ]

        return SearchResponse(
            query=q,
            results=search_results,
            count=len(search_results)
        )

    except Exception as e:
        logger.error(f"Search failed for '{q}': {e}")
        return SearchResponse(query=q, results=[], count=0)
