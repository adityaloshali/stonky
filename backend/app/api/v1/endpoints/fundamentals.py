"""
Fundamental data endpoints (10-year historical).
"""

from fastapi import APIRouter, Path, Depends, HTTPException
from loguru import logger

from app.api.v1.schemas.responses import FundamentalsResponse
from app.core.dependencies import ServiceFactory, get_service_factory
from app.services.base import ServiceError

router = APIRouter()


@router.get("/fundamentals/{symbol}", response_model=FundamentalsResponse, tags=["fundamentals"])
async def get_fundamentals(
    symbol: str = Path(..., description="Stock symbol (NSE, without .NS suffix)"),
    factory: ServiceFactory = Depends(get_service_factory)
):
    """
    Get 10-year fundamental data from Screener.in.

    Returns annual consolidated financial data including:
    - Revenue and Net Profit
    - ROCE (Return on Capital Employed)
    - ROE (Return on Equity)
    - Debt to Equity ratio
    - EPS (Earnings Per Share)
    - Book Value per Share
    - PE Ratio
    - Market Cap

    **Example:**
    - `/api/v1/fundamentals/RELIANCE` - Get 10-year data for Reliance

    **Note:** Requires SCREENER_COOKIE to be configured in backend/.env

    **Setup:**
    1. Login to https://www.screener.in
    2. Get 'sessionid' cookie from browser DevTools
    3. Set SCREENER_COOKIE in backend/.env

    If cookie is not configured or has expired, this endpoint will return an error.
    """
    logger.info(f"Fetching fundamentals for {symbol}")

    try:
        # Check if Screener cookie is configured
        try:
            screener = factory.create_screener_service()
        except ValueError as e:
            logger.warning(f"Screener service not available: {e}")
            raise HTTPException(
                status_code=503,
                detail="Screener service not configured. Please set SCREENER_COOKIE in .env file. See API docs for setup instructions."
            )

        # Remove any suffix
        symbol_clean = symbol.replace('.NS', '').replace('.BO', '')

        # Fetch data
        data = await screener.fetch_data(symbol_clean)

        # Handle error response
        if data.get('status') == 'error':
            raise ServiceError(data.get('message', 'Unknown error'))

        return FundamentalsResponse(
            symbol=symbol_clean,
            years=data.get('years', []),
            revenue=data.get('revenue', []),
            net_profit=data.get('net_profit', []),
            roce=data.get('roce', []),
            roe=data.get('roe', []),
            debt_to_equity=data.get('debt_to_equity', []),
            eps=data.get('eps', []),
            book_value=data.get('book_value', []),
            pe_ratio=data.get('pe_ratio', []),
            market_cap=data.get('market_cap', []),
            source="screener.in"
        )

    except HTTPException:
        raise
    except ServiceError as e:
        logger.error(f"Screener service error for {symbol}: {e}")

        # Check for specific error types
        error_msg = str(e).lower()
        if '403' in error_msg or 'expired' in error_msg or 'session' in error_msg:
            raise HTTPException(
                status_code=401,
                detail="Screener.in session expired. Please update SCREENER_COOKIE in .env file."
            )
        elif '404' in error_msg or 'not found' in error_msg:
            raise HTTPException(
                status_code=404,
                detail=f"Company '{symbol}' not found on Screener.in. Please check the symbol."
            )
        else:
            raise HTTPException(status_code=503, detail=f"Screener service error: {str(e)}")

    except Exception as e:
        logger.error(f"Error fetching fundamentals for {symbol}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
