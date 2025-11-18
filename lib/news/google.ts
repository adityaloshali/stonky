import Parser from 'rss-parser';

type NewsItem = { title: string; link: string; source?: string; publishedAt?: string };

const parser = new Parser();

function buildGoogleNewsUrl(query: string): string {
  const q = encodeURIComponent(query);
  // English India locale
  return `https://news.google.com/rss/search?q=${q}&hl=en-IN&gl=IN&ceid=IN:en`;
}

export async function getTopNews(query: string, count = 5): Promise<NewsItem[]> {
  if (!query) return [];
  const url = buildGoogleNewsUrl(query);
  const feed = await parser.parseURL(url);
  const items: NewsItem[] = (feed.items || []).slice(0, count).map((i) => {
    let title = i.title || '';
    let source: string | undefined;
    // Many Google News titles end with ` - Source`
    const parts = title.split(' - ');
    if (parts.length > 1) {
      source = parts.pop();
      title = parts.join(' - ');
    }
    return {
      title,
      link: i.link || '',
      source,
      publishedAt: (i as any).isoDate || undefined,
    };
  });
  return items;
}

