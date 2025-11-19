from fastapi import APIRouter, Depends
from app.core.dependencies import ServiceFactory, get_service_factory
from app.core.config import settings
from app.services.screener import ScreenerService

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

@router.get("/test/screener/{symbol}")
async def test_screener(
    symbol: str,
    factory: ServiceFactory = Depends(get_service_factory)
):
    if not settings.has_screener_cookie:
        print("❌ Cookie not set!")
        return
    
    service = ScreenerService(session_cookie=settings.SCREENER_COOKIE)
    
    # Test fundamentals
    data = await service.fetch_data(symbol)
    
    print(f"Got {len(data.get('revenue', []))} years of data")
    
    if data.get('roce'):
        print(f"Latest ROCE: {data['roce'][0]:.2f}%")
    if data.get('roe'):
        print(f"Latest ROE: {data['roe'][0]:.2f}%")
    if data.get('debt_to_equity'):
        print(f"Latest D/E: {data['debt_to_equity'][0]:.2f}")

    return data
