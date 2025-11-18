import { cacheJson } from '../cache/redis';

const BASE = 'https://www.nseindia.com';

async function fetchJson<T>(url: string): Promise<T> {
  const res = await fetch(url, { headers: { 'user-agent': 'Mozilla/5.0' } });
  if (!res.ok) throw new Error(`NSE fetch failed ${res.status}`);
  return (await res.json()) as T;
}

export async function getQuote(symbol: string) {
  const key = `nse:quote:${symbol}`;
  return cacheJson(key, async () => {
    // Public quote endpoint pattern; may require cookies. Fallbacks added later.
    const url = `${BASE}/api/quote-equity?symbol=${encodeURIComponent(symbol)}`;
    try {
      return await fetchJson(url);
    } catch {
      return { status: 'unavailable' };
    }
  }, 300);
}

