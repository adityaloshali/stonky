"""
News service for stock-related news aggregation.

Fetches news from multiple sources:
- Google News RSS (free, no API key required)
- Financial news specific to Indian stocks
- Company-specific news and announcements

Sources are completely free using RSS feeds.
"""

from typing import Dict, Any, List, Optional
import feedparser
from datetime import datetime, timedelta
from urllib.parse import quote_plus
from loguru import logger

from app.services.base import BaseService, ServiceError


class NewsService(BaseService):
    """
    Service for fetching stock-related news.

    Uses Google News RSS feed which is free and doesn't require authentication.
    """

    GOOGLE_NEWS_RSS = "https://news.google.com/rss/search"

    def __init__(self, timeout: int = 30):
        """
        Initialize News service.

        Args:
            timeout: Request timeout in seconds
        """
        super().__init__(timeout=timeout)

    async def fetch_data(self, symbol: str) -> Dict[str, Any]:
        """
        Fetch news articles for a stock symbol.

        Args:
            symbol: Stock symbol or company name

        Returns:
            Dictionary with news articles

        Raises:
            ServiceError: If fetch fails
        """
        try:
            news = await self.get_news(symbol, limit=10)
            return {
                'symbol': symbol,
                'articles': news,
                'count': len(news),
                'source': 'google_news',
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            return self._handle_error(e, f"Failed to fetch news for {symbol}")

    async def get_news(
        self,
        query: str,
        limit: int = 5,
        language: str = 'en',
        region: str = 'IN'
    ) -> List[Dict[str, Any]]:
        """
        Get news articles for a query.

        Args:
            query: Search query (company name or stock symbol)
            limit: Maximum number of articles to return
            language: Language code (default: 'en')
            region: Region code (default: 'IN' for India)

        Returns:
            List of news articles
        """
        if not query:
            return []

        try:
            import asyncio
            loop = asyncio.get_event_loop()

            articles = await loop.run_in_executor(
                None, self._get_news_sync, query, limit, language, region
            )
            return articles

        except Exception as e:
            self.logger.error(f"Failed to fetch news for '{query}': {e}")
            return []

    def _get_news_sync(
        self,
        query: str,
        limit: int,
        language: str,
        region: str
    ) -> List[Dict[str, Any]]:
        """
        Synchronous fetch of news articles.

        Args:
            query: Search query
            limit: Max articles
            language: Language code
            region: Region code

        Returns:
            List of news articles
        """
        try:
            # Construct RSS URL
            # Google News RSS format: /rss/search?q={query}&hl={lang}&gl={region}&ceid={region}:{lang}
            encoded_query = quote_plus(f"{query} stock India")
            url = (
                f"{self.GOOGLE_NEWS_RSS}?"
                f"q={encoded_query}&"
                f"hl={language}&"
                f"gl={region}&"
                f"ceid={region}:{language}"
            )

            # Parse RSS feed
            feed = feedparser.parse(url)

            if not feed.entries:
                self.logger.warning(f"No news found for query: {query}")
                return []

            # Extract articles
            articles = []
            for entry in feed.entries[:limit]:
                article = self._parse_entry(entry)
                articles.append(article)

            return articles

        except Exception as e:
            raise ServiceError(f"Failed to parse news feed: {e}")

    def _parse_entry(self, entry) -> Dict[str, Any]:
        """
        Parse a single RSS feed entry.

        Args:
            entry: feedparser entry object

        Returns:
            Dictionary with article information
        """
        # Extract published date
        published = None
        if hasattr(entry, 'published_parsed'):
            try:
                published = datetime(*entry.published_parsed[:6]).isoformat()
            except Exception:
                pass

        # Extract source from title (Google News format: "Title - Source")
        title = entry.get('title', '')
        source = None
        if ' - ' in title:
            parts = title.rsplit(' - ', 1)
            title = parts[0]
            source = parts[1]

        return {
            'title': title,
            'link': entry.get('link', ''),
            'source': source or 'Unknown',
            'published': published or datetime.now().isoformat(),
            'summary': entry.get('summary', ''),
            'id': entry.get('id', entry.get('link', ''))
        }

    async def get_company_news(
        self,
        company_name: str,
        symbol: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get news specifically for a company.

        Uses both company name and stock symbol for better results.

        Args:
            company_name: Full company name
            symbol: Stock symbol
            limit: Maximum number of articles

        Returns:
            List of news articles
        """
        # Combine company name and symbol for better search
        query = f"{company_name} {symbol}"
        return await self.get_news(query, limit=limit)

    async def get_market_news(
        self,
        market: str = 'India',
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get general market news.

        Args:
            market: Market name (e.g., 'India', 'NSE', 'BSE')
            limit: Maximum number of articles

        Returns:
            List of news articles
        """
        query = f"{market} stock market news"
        return await self.get_news(query, limit=limit)

    async def get_sector_news(
        self,
        sector: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get sector-specific news.

        Args:
            sector: Sector name (e.g., 'IT', 'Banking', 'Pharma')
            limit: Maximum number of articles

        Returns:
            List of news articles
        """
        query = f"{sector} sector India stocks"
        return await self.get_news(query, limit=limit)

    async def filter_by_sentiment(
        self,
        articles: List[Dict[str, Any]],
        sentiment: str = 'all'
    ) -> List[Dict[str, Any]]:
        """
        Filter articles by sentiment (basic keyword-based).

        Note: This is a simple keyword-based filter. For production,
        consider using a proper sentiment analysis model.

        Args:
            articles: List of articles
            sentiment: 'positive', 'negative', or 'all'

        Returns:
            Filtered articles
        """
        if sentiment == 'all':
            return articles

        positive_keywords = [
            'profit', 'growth', 'surge', 'gain', 'rally', 'high', 'beat',
            'upgrade', 'bullish', 'positive', 'strong', 'record', 'up'
        ]

        negative_keywords = [
            'loss', 'decline', 'fall', 'drop', 'crash', 'low', 'miss',
            'downgrade', 'bearish', 'negative', 'weak', 'concern', 'down'
        ]

        filtered = []
        for article in articles:
            text = (article.get('title', '') + ' ' + article.get('summary', '')).lower()

            if sentiment == 'positive':
                if any(keyword in text for keyword in positive_keywords):
                    filtered.append(article)
            elif sentiment == 'negative':
                if any(keyword in text for keyword in negative_keywords):
                    filtered.append(article)

        return filtered

    async def get_trending_stocks(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get news about trending/popular stocks.

        Args:
            limit: Maximum number of articles

        Returns:
            List of news articles about trending stocks
        """
        query = "trending stocks India NSE BSE"
        return await self.get_news(query, limit=limit)

    async def search_by_date_range(
        self,
        query: str,
        days_back: int = 7,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search for news within a date range.

        Note: Google News RSS doesn't support exact date filtering,
        so we filter results after fetching.

        Args:
            query: Search query
            days_back: Number of days to look back
            limit: Maximum articles

        Returns:
            Filtered articles within date range
        """
        # Fetch more articles than needed since we'll filter
        articles = await self.get_news(query, limit=limit * 2)

        cutoff_date = datetime.now() - timedelta(days=days_back)

        # Filter by date
        filtered = []
        for article in articles:
            try:
                published = datetime.fromisoformat(article['published'])
                if published >= cutoff_date:
                    filtered.append(article)
                    if len(filtered) >= limit:
                        break
            except Exception:
                # If can't parse date, include it
                filtered.append(article)
                if len(filtered) >= limit:
                    break

        return filtered

    def extract_keywords(self, text: str, top_n: int = 5) -> List[str]:
        """
        Extract keywords from text (simple frequency-based).

        For production, consider using NLP libraries like spaCy or NLTK.

        Args:
            text: Input text
            top_n: Number of top keywords to return

        Returns:
            List of keywords
        """
        # Remove common words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
            'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
            'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those'
        }

        # Tokenize and count
        words = text.lower().split()
        word_count = {}

        for word in words:
            # Clean word
            word = word.strip('.,!?;:"()[]{}')
            if len(word) > 3 and word not in stop_words:
                word_count[word] = word_count.get(word, 0) + 1

        # Sort by frequency
        sorted_words = sorted(word_count.items(), key=lambda x: x[1], reverse=True)

        return [word for word, count in sorted_words[:top_n]]
