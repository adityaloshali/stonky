"""
Company information and quote endpoints.
"""

from fastapi import APIRouter, Path, Depends, HTTPException
from loguru import logger

from app.api.v1.schemas.responses import QuoteResponse, ShareholdingPattern, CompanyInfo
from app.core.dependencies import ServiceFactory, get_service_factory
from app.services.base import ServiceError

router = APIRouter()


@router.get("/company/{symbol}/quote", response_model=QuoteResponse, tags=["company"])
async def get_quote(
    symbol: str = Path(..., description="Stock symbol (e.g., 'RELIANCE' without .NS suffix)"),
    factory: ServiceFactory = Depends(get_service_factory)
):
    """
    Get current quote and market data for a stock.

    Uses Yahoo Finance for comprehensive quote data.

    **Example:**
    - `/api/v1/company/RELIANCE/quote` - Get Reliance quote
    - `/api/v1/company/TCS/quote` - Get TCS quote

    **Note:** Symbol should be without .NS/.BO suffix. The API will add .NS automatically.
    """
    logger.info(f"Fetching quote for {symbol}")

    try:
        yahoo = factory.create_yahoo_service()

        # Ensure .NS suffix for NSE
        symbol_with_suffix = symbol if '.NS' in symbol or '.BO' in symbol else f"{symbol}.NS"

        data = await yahoo.fetch_data(symbol_with_suffix)

        return QuoteResponse(
            symbol=data['symbol'],
            name=data.get('name'),
            current_price=data.get('current_price', 0),
            previous_close=data.get('previous_close'),
            open=data.get('open'),
            day_high=data.get('day_high'),
            day_low=data.get('day_low'),
            volume=data.get('volume'),
            change=data.get('current_price', 0) - data.get('previous_close', 0) if data.get('previous_close') else None,
            percent_change=((data.get('current_price', 0) - data.get('previous_close', 0)) / data.get('previous_close', 1) * 100) if data.get('previous_close') else None,
            market_cap=data.get('market_cap'),
            pe_ratio=data.get('pe_ratio'),
            week_52_high=data.get('week_52_high'),
            week_52_low=data.get('week_52_low'),
            timestamp=data.get('timestamp')
        )

    except ServiceError as e:
        logger.error(f"Service error fetching quote for {symbol}: {e}")
        raise HTTPException(status_code=503, detail=f"Unable to fetch quote: {str(e)}")
    except Exception as e:
        logger.error(f"Error fetching quote for {symbol}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/company/{symbol}/info", response_model=CompanyInfo, tags=["company"])
async def get_company_info(
    symbol: str = Path(..., description="Stock symbol"),
    factory: ServiceFactory = Depends(get_service_factory)
):
    """
    Get basic company information.

    **Example:**
    - `/api/v1/company/RELIANCE/info` - Get Reliance company info
    """
    logger.info(f"Fetching company info for {symbol}")

    try:
        yahoo = factory.create_yahoo_service()
        symbol_with_suffix = symbol if '.NS' in symbol or '.BO' in symbol else f"{symbol}.NS"

        data = await yahoo.fetch_data(symbol_with_suffix)

        return CompanyInfo(
            symbol=data['symbol'],
            name=data.get('name', symbol),
            sector=data.get('sector'),
            industry=data.get('industry'),
            market_cap=data.get('market_cap')
        )

    except Exception as e:
        logger.error(f"Error fetching company info for {symbol}: {e}")
        raise HTTPException(status_code=500, detail="Unable to fetch company information")


@router.get("/company/{symbol}/shareholding", response_model=ShareholdingPattern, tags=["company"])
async def get_shareholding(
    symbol: str = Path(..., description="NSE stock symbol (without .NS)"),
    factory: ServiceFactory = Depends(get_service_factory)
):
    """
    Get shareholding pattern from NSE.

    Returns promoter, FII, DII, and public holdings, plus promoter pledging data.

    **Example:**
    - `/api/v1/company/RELIANCE/shareholding` - Get Reliance shareholding

    **Note:** This data comes from NSE and may not always be available due to
    rate limiting or API restrictions.
    """
    logger.info(f"Fetching shareholding for {symbol}")

    try:
        nse = factory.create_nse_service()

        # Remove any suffix for NSE
        symbol_clean = symbol.replace('.NS', '').replace('.BO', '')

        data = await nse.get_shareholding(symbol_clean)

        # Handle case where NSE returns error dict
        if data.get('status') == 'error':
            raise HTTPException(
                status_code=503,
                detail=f"NSE service unavailable: {data.get('message', 'Unknown error')}"
            )

        # Extract data
        promoter = data.get('promoter', {})
        fii = data.get('fii', {})
        dii = data.get('dii', {})
        public = data.get('public', {})
        pledging = data.get('pledging', {})

        return ShareholdingPattern(
            promoter_percentage=promoter.get('percentage'),
            fii_percentage=fii.get('percentage'),
            dii_percentage=dii.get('percentage'),
            public_percentage=public.get('percentage'),
            promoter_pledged_percentage=pledging.get('promoter_pledged_percentage'),
            date=data.get('date')
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching shareholding for {symbol}: {e}")
        raise HTTPException(
            status_code=503,
            detail="NSE service temporarily unavailable. Please try again later."
        )
