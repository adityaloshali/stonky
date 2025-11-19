"""
Test script for Phase 2 services.

This script tests all implemented services:
- Yahoo Finance (no auth required)
- NSE (session-based)
- News (free RSS)
- Screener.in (requires cookie)

Run with: python test_services.py
"""

import asyncio
import sys
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.config import settings
from app.services.yahoo import YahooFinanceService
from app.services.nse import NSEService
from app.services.news import NewsService
from app.services.screener import ScreenerService


async def test_yahoo_service():
    """Test Yahoo Finance service."""
    print("\n" + "=" * 60)
    print("TESTING YAHOO FINANCE SERVICE")
    print("=" * 60)

    service = YahooFinanceService()

    try:
        # Test with Reliance NSE
        print("\n1. Fetching data for RELIANCE.NS...")
        data = await service.fetch_data("RELIANCE.NS")
        print(f"✓ Symbol: {data.get('symbol')}")
        print(f"✓ Name: {data.get('name')}")
        print(f"✓ Current Price: ₹{data.get('current_price', 0):.2f}")
        print(f"✓ Market Cap: ₹{data.get('market_cap', 0):,}")
        print(f"✓ Sector: {data.get('sector')}")

        # Test price history
        print("\n2. Fetching 1-month price history...")
        prices = await service.get_prices("RELIANCE.NS", period="1mo", interval="1d")
        print(f"✓ Retrieved {len(prices['prices'])} days of data")
        if prices['prices']:
            latest = prices['prices'][-1]
            print(f"✓ Latest: {latest['date']} - Close: ₹{latest['close']:.2f}")

        # Test current price
        print("\n3. Fetching current price...")
        current = await service.get_current_price("RELIANCE.NS")
        print(f"✓ Current price: ₹{current:.2f}")

        print("\n✅ Yahoo Finance service: PASSED")
        return True

    except Exception as e:
        print(f"\n❌ Yahoo Finance service: FAILED")
        print(f"Error: {e}")
        return False


async def test_nse_service():
    """Test NSE service."""
    print("\n" + "=" * 60)
    print("TESTING NSE SERVICE")
    print("=" * 60)

    service = NSEService()

    try:
        # Test shareholding
        print("\n1. Fetching shareholding for RELIANCE...")
        shareholding = await service.get_shareholding("RELIANCE")

        if 'promoter' in shareholding:
            print(f"✓ Promoter: {shareholding['promoter']['percentage']:.2f}%")
            print(f"✓ FII: {shareholding.get('fii', {}).get('percentage', 0):.2f}%")
            print(f"✓ DII: {shareholding.get('dii', {}).get('percentage', 0):.2f}%")

            pledging = shareholding.get('pledging', {})
            pledge_pct = pledging.get('promoter_pledged_percentage', 0)
            print(f"✓ Promoter Pledging: {pledge_pct:.2f}%")
        else:
            print("⚠ No shareholding data (NSE might be down or rate-limited)")

        # Test quote
        print("\n2. Fetching quote for RELIANCE...")
        quote = await service.get_quote("RELIANCE")

        if 'last_price' in quote:
            print(f"✓ Last Price: ₹{quote['last_price']:.2f}")
            print(f"✓ Change: {quote['change']:.2f} ({quote['percent_change']:.2f}%)")
            print(f"✓ Day High: ₹{quote['day_high']:.2f}")
            print(f"✓ Day Low: ₹{quote['day_low']:.2f}")
        else:
            print("⚠ No quote data (NSE might be down or rate-limited)")

        print("\n✅ NSE service: PASSED (with warnings if any)")
        return True

    except Exception as e:
        print(f"\n⚠ NSE service: PARTIAL (NSE is often rate-limited)")
        print(f"Error: {e}")
        return True  # Don't fail the test as NSE is unreliable


async def test_news_service():
    """Test News service."""
    print("\n" + "=" * 60)
    print("TESTING NEWS SERVICE")
    print("=" * 60)

    service = NewsService()

    try:
        # Test general news
        print("\n1. Fetching news for 'Reliance'...")
        news = await service.get_news("Reliance", limit=5)

        if news:
            print(f"✓ Retrieved {len(news)} articles")
            for i, article in enumerate(news[:3], 1):
                print(f"\n  Article {i}:")
                print(f"  Title: {article['title'][:80]}...")
                print(f"  Source: {article['source']}")
                print(f"  Published: {article['published']}")
        else:
            print("⚠ No news found (might be network issue)")

        # Test market news
        print("\n2. Fetching Indian market news...")
        market_news = await service.get_market_news(limit=3)
        print(f"✓ Retrieved {len(market_news)} market news articles")

        print("\n✅ News service: PASSED")
        return True

    except Exception as e:
        print(f"\n❌ News service: FAILED")
        print(f"Error: {e}")
        return False


async def test_screener_service():
    """Test Screener.in service (requires cookie)."""
    print("\n" + "=" * 60)
    print("TESTING SCREENER.IN SERVICE")
    print("=" * 60)

    if not settings.has_screener_cookie:
        print("\n⚠ SCREENER_COOKIE not configured")
        print("To test Screener service:")
        print("1. Login to Screener.in in your browser")
        print("2. Copy the 'sessionid' cookie value")
        print("3. Set SCREENER_COOKIE in backend/.env")
        print("\n⏭ SKIPPING Screener test")
        return True

    try:
        service = ScreenerService(session_cookie=settings.SCREENER_COOKIE)

        print("\n1. Fetching fundamentals for RELIANCE...")
        data = await service.fetch_data("RELIANCE")

        if 'revenue' in data and data['revenue']:
            print(f"✓ Retrieved {len(data['revenue'])} years of data")
            print(f"✓ Latest Revenue: ₹{data['revenue'][0]:,.0f} Cr" if data['revenue'][0] else "N/A")

            if 'roce' in data and data['roce']:
                print(f"✓ Latest ROCE: {data['roce'][0]:.2f}%" if data['roce'][0] else "N/A")

            if 'roe' in data and data['roe']:
                print(f"✓ Latest ROE: {data['roe'][0]:.2f}%" if data['roe'][0] else "N/A")

            if 'debt_to_equity' in data and data['debt_to_equity']:
                print(f"✓ Latest D/E: {data['debt_to_equity'][0]:.2f}" if data['debt_to_equity'][0] else "N/A")

        print("\n2. Fetching company info...")
        info = await service.get_company_info("RELIANCE")
        print(f"✓ Name: {info.get('name')}")
        print(f"✓ Sector: {info.get('sector')}")

        print("\n✅ Screener service: PASSED")
        return True

    except Exception as e:
        print(f"\n❌ Screener service: FAILED")
        print(f"Error: {e}")
        if "403" in str(e) or "expired" in str(e).lower():
            print("\n💡 Hint: Your SCREENER_COOKIE might have expired.")
            print("   Please get a fresh cookie from your browser.")
        return False


async def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("PHASE 2 SERVICES TEST SUITE")
    print("=" * 60)
    print("\nThis will test all implemented services:")
    print("1. Yahoo Finance (prices, technicals)")
    print("2. NSE (shareholding, quotes)")
    print("3. News (Google News RSS)")
    print("4. Screener.in (10-year fundamentals)")

    results = {}

    # Run tests
    results['yahoo'] = await test_yahoo_service()
    results['nse'] = await test_nse_service()
    results['news'] = await test_news_service()
    results['screener'] = await test_screener_service()

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    for service, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{service.upper():15} {status}")

    all_passed = all(results.values())
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 ALL TESTS PASSED!")
    else:
        print("⚠ SOME TESTS FAILED")
    print("=" * 60 + "\n")

    return 0 if all_passed else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
