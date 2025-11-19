"""
Stock price data endpoints.
"""

from fastapi import APIRouter, Path, Query, Depends, HTTPException
from loguru import logger

from app.api.v1.schemas.responses import PricesResponse, PriceData, TechnicalIndicators
from app.core.dependencies import ServiceFactory, get_service_factory
from app.services.base import ServiceError

router = APIRouter()


@router.get("/prices/{symbol}", response_model=PricesResponse, tags=["prices"])
async def get_prices(
    symbol: str = Path(..., description="Stock symbol"),
    period: str = Query("1y", description="Time period", regex="^(1d|5d|1mo|3mo|6mo|1y|2y|5y|10y|ytd|max)$"),
    interval: str = Query("1d", description="Data interval", regex="^(1m|2m|5m|15m|30m|60m|90m|1h|1d|5d|1wk|1mo|3mo)$"),
    factory: ServiceFactory = Depends(get_service_factory)
):
    """
    Get historical OHLC price data.

    **Parameters:**
    - `period`: 1d, 5d, 1mo, 3mo, 6mo, 1y (default), 2y, 5y, 10y, ytd, max
    - `interval`: 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d (default), 5d, 1wk, 1mo, 3mo

    **Examples:**
    - `/api/v1/prices/RELIANCE?period=1y&interval=1d` - 1 year daily data
    - `/api/v1/prices/TCS?period=1mo&interval=1h` - 1 month hourly data
    - `/api/v1/prices/INFY?period=5y` - 5 years daily data

    **Note:** Intraday intervals (1m, 2m, etc.) are only valid for periods <= 60 days
    """
    logger.info(f"Fetching prices for {symbol}: period={period}, interval={interval}")

    try:
        yahoo = factory.create_yahoo_service()

        # Ensure .NS suffix
        symbol_with_suffix = symbol if '.NS' in symbol or '.BO' in symbol else f"{symbol}.NS"

        data = await yahoo.get_prices(symbol_with_suffix, period=period, interval=interval)

        # Transform to response format
        prices = [
            PriceData(
                date=p['date'],
                timestamp=p['timestamp'],
                open=p['open'],
                high=p['high'],
                low=p['low'],
                close=p['close'],
                volume=p['volume']
            )
            for p in data['prices']
        ]

        return PricesResponse(
            symbol=data['symbol'],
            period=period,
            interval=interval,
            prices=prices,
            count=len(prices)
        )

    except ServiceError as e:
        logger.error(f"Service error fetching prices for {symbol}: {e}")
        raise HTTPException(status_code=503, detail=str(e))
    except ValueError as e:
        logger.error(f"Invalid parameters for {symbol}: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error fetching prices for {symbol}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/prices/{symbol}/technicals", response_model=TechnicalIndicators, tags=["prices"])
async def get_technicals(
    symbol: str = Path(..., description="Stock symbol"),
    period: str = Query("1y", description="Period for calculation"),
    factory: ServiceFactory = Depends(get_service_factory)
):
    """
    Get technical indicators (SMA, RSI, trend).

    Calculates:
    - Simple Moving Averages (20, 50, 200 days)
    - Relative Strength Index (14-day)
    - Price momentum
    - Trend analysis

    **Example:**
    - `/api/v1/prices/RELIANCE/technicals` - Get technical indicators for Reliance
    - `/api/v1/prices/TCS/technicals?period=6mo` - 6-month technicals for TCS

    **Note:** Requires sufficient historical data (at least 200 days for SMA200)
    """
    logger.info(f"Fetching technicals for {symbol}: period={period}")

    try:
        yahoo = factory.create_yahoo_service()

        symbol_with_suffix = symbol if '.NS' in symbol or '.BO' in symbol else f"{symbol}.NS"

        data = await yahoo.get_technicals(symbol_with_suffix, period=period)

        # Handle error response
        if data.get('status') == 'error':
            raise HTTPException(status_code=503, detail=data.get('message', 'Unknown error'))

        return TechnicalIndicators(
            current_price=data['current_price'],
            sma_20=data.get('sma_20'),
            sma_50=data.get('sma_50'),
            sma_200=data.get('sma_200'),
            rsi_14=data.get('rsi_14'),
            momentum_percent=data.get('momentum_percent'),
            trend=data.get('trend'),
            rsi_signal=data.get('rsi_signal')
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching technicals for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
