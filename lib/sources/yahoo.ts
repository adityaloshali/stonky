import yf from 'yahoo-finance2';

export async function getDailyOHLC(symbol: string, period = '1y') {
  // Use chart endpoint and filter out null closes to avoid zeros
  const result: any = await (yf as any).chart(symbol, { period, interval: '1d' });
  const quotes: any[] = (result?.quotes ?? []).filter((q: any) => q && q.close != null);
  const candles = quotes.map((q: any) => ({
    date: new Date(q.date),
    open: Number(q.open ?? q.close ?? 0),
    high: Number(q.high ?? q.close ?? 0),
    low: Number(q.low ?? q.close ?? 0),
    close: Number(q.close ?? 0),
    volume: Number(q.volume ?? 0),
  }));
  return candles;
}

export async function getLastPrice(symbol: string) {
  try {
    const q: any = await (yf as any).quote(symbol, { lang: 'en-IN', region: 'IN' });
    const price = q?.regularMarketPrice ?? q?.postMarketPrice ?? q?.preMarketPrice ?? q?.currentPrice ?? q?.regularMarketPreviousClose ?? null;
    const time = q?.regularMarketTime ? new Date(q.regularMarketTime * 1000) : undefined;
    return { price: typeof price === 'number' ? price : null, currency: q?.currency, time };
  } catch {
    return { price: null, currency: undefined, time: undefined };
  }
}

export async function searchSymbols(query: string, count = 10) {
  if (!query || query.trim().length < 1) return [] as Array<{ symbol: string; name: string; exchange?: string; type?: string }>;
  const res: any = await (yf as any).search(query, { lang: 'en-IN', region: 'IN' });
  const quotes: any[] = res?.quotes ?? [];
  const isIN = (q: any) => {
    const sym = String(q.symbol || '').toUpperCase();
    const exch = String(q.exch || q.exchange || '').toUpperCase();
    const exchDisp = String(q.exchDisp || '').toUpperCase();
    return sym.endsWith('.NS') || sym.endsWith('.BO') || exch.includes('NSI') || exch.includes('BSE') || exchDisp.includes('NSE') || exchDisp.includes('BSE');
  };
  const filtered = quotes.filter(isIN).slice(0, count);
  return filtered.map((q: any) => ({
    symbol: q.symbol,
    name: q.longname || q.shortname || q.name || q.symbol,
    exchange: q.exchDisp,
    type: q.quoteType,
  }));
}

