"""
News and information endpoints.
"""

from fastapi import APIRouter, Path, Query, Depends
from loguru import logger

from app.api.v1.schemas.responses import NewsResponse, NewsArticle
from app.core.dependencies import ServiceFactory, get_service_factory

router = APIRouter()


@router.get("/news", response_model=NewsResponse, tags=["news"])
async def get_news(
    q: str = Query(..., min_length=2, description="Search query"),
    limit: int = Query(10, ge=1, le=50, description="Number of articles"),
    factory: ServiceFactory = Depends(get_service_factory)
):
    """
    Get news articles for a query.

    Uses Google News RSS (free, no API key required).

    **Examples:**
    - `/api/v1/news?q=Reliance` - News about Reliance
    - `/api/v1/news?q=India+stock+market&limit=20` - Market news
    - `/api/v1/news?q=IT+sector+stocks` - IT sector news
    """
    logger.info(f"Fetching news for query: '{q}'")

    try:
        news_service = factory.create_news_service()

        articles = await news_service.get_news(q, limit=limit)

        # Transform to response format
        news_articles = [
            NewsArticle(
                title=article['title'],
                link=article['link'],
                source=article['source'],
                published=article['published'],
                summary=article.get('summary')
            )
            for article in articles
        ]

        return NewsResponse(
            query=q,
            articles=news_articles,
            count=len(news_articles)
        )

    except Exception as e:
        logger.error(f"Error fetching news for '{q}': {e}")
        return NewsResponse(query=q, articles=[], count=0)


@router.get("/news/{symbol}", response_model=NewsResponse, tags=["news"])
async def get_company_news(
    symbol: str = Path(..., description="Stock symbol or company name"),
    limit: int = Query(10, ge=1, le=50, description="Number of articles"),
    factory: ServiceFactory = Depends(get_service_factory)
):
    """
    Get news articles for a specific company/stock.

    **Examples:**
    - `/api/v1/news/RELIANCE` - News about Reliance
    - `/api/v1/news/TCS?limit=5` - TCS news, max 5 articles
    """
    logger.info(f"Fetching company news for: {symbol}")

    try:
        news_service = factory.create_news_service()

        # Add "stock India" to query for better results
        query = f"{symbol} stock India"
        articles = await news_service.get_news(query, limit=limit)

        news_articles = [
            NewsArticle(
                title=article['title'],
                link=article['link'],
                source=article['source'],
                published=article['published'],
                summary=article.get('summary')
            )
            for article in articles
        ]

        return NewsResponse(
            symbol=symbol,
            query=query,
            articles=news_articles,
            count=len(news_articles)
        )

    except Exception as e:
        logger.error(f"Error fetching news for {symbol}: {e}")
        return NewsResponse(symbol=symbol, query=symbol, articles=[], count=0)


@router.get("/news/market/india", response_model=NewsResponse, tags=["news"])
async def get_market_news(
    limit: int = Query(15, ge=1, le=50, description="Number of articles"),
    factory: ServiceFactory = Depends(get_service_factory)
):
    """
    Get general Indian stock market news.

    **Example:**
    - `/api/v1/news/market/india` - Latest market news
    - `/api/v1/news/market/india?limit=20` - More market news
    """
    logger.info("Fetching Indian market news")

    try:
        news_service = factory.create_news_service()

        articles = await news_service.get_market_news(market="India", limit=limit)

        news_articles = [
            NewsArticle(
                title=article['title'],
                link=article['link'],
                source=article['source'],
                published=article['published'],
                summary=article.get('summary')
            )
            for article in articles
        ]

        return NewsResponse(
            query="India stock market",
            articles=news_articles,
            count=len(news_articles)
        )

    except Exception as e:
        logger.error(f"Error fetching market news: {e}")
        return NewsResponse(query="India stock market", articles=[], count=0)


@router.get("/news/sector/{sector}", response_model=NewsResponse, tags=["news"])
async def get_sector_news(
    sector: str = Path(..., description="Sector name (IT, Banking, Pharma, etc.)"),
    limit: int = Query(10, ge=1, le=50, description="Number of articles"),
    factory: ServiceFactory = Depends(get_service_factory)
):
    """
    Get sector-specific news.

    **Examples:**
    - `/api/v1/news/sector/IT` - IT sector news
    - `/api/v1/news/sector/Banking` - Banking sector news
    - `/api/v1/news/sector/Pharma?limit=15` - Pharma news
    """
    logger.info(f"Fetching news for sector: {sector}")

    try:
        news_service = factory.create_news_service()

        articles = await news_service.get_sector_news(sector=sector, limit=limit)

        news_articles = [
            NewsArticle(
                title=article['title'],
                link=article['link'],
                source=article['source'],
                published=article['published'],
                summary=article.get('summary')
            )
            for article in articles
        ]

        return NewsResponse(
            query=f"{sector} sector India",
            articles=news_articles,
            count=len(news_articles)
        )

    except Exception as e:
        logger.error(f"Error fetching sector news for {sector}: {e}")
        return NewsResponse(query=f"{sector} sector", articles=[], count=0)
