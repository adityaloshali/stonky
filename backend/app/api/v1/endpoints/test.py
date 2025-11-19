from fastapi import APIRouter, Depends
from app.core.dependencies import ServiceFactory, get_service_factory

router = APIRouter()

@router.get("/test/yahoo/{symbol}")
async def test_yahoo(
    symbol: str,
    factory: ServiceFactory = Depends(get_service_factory)
):
    yahoo = factory.create_yahoo_service()
    return await yahoo.fetch_data(f"{symbol}.NS")

@router.get("/test/nse/{symbol}")
async def test_nse(
    symbol: str,
    factory: ServiceFactory = Depends(get_service_factory)
):
    nse = factory.create_nse_service()
    return await nse.get_shareholding(symbol)

@router.get("/test/news")
async def test_news(
    q: str,
    factory: ServiceFactory = Depends(get_service_factory)
):
    news = factory.create_news_service()
    return await news.get_news(q, limit=5)