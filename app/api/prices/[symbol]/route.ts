export const runtime = 'nodejs';

import { getDailyOHLC } from '@/lib/sources/yahoo';

export async function GET(request: Request, { params }: { params: { symbol: string } }) {
  const { symbol } = params;
  try {
    const candles = await getDailyOHLC(symbol, '1y');
    return new Response(JSON.stringify({ symbol, prices: candles }), {
      headers: { 'content-type': 'application/json', 'cache-control': 'public, s-maxage=300, stale-while-revalidate=60' },
    });
  } catch (e) {
    return new Response(JSON.stringify({ symbol, prices: [], error: 'fetch_failed' }), { status: 500 });
  }
}

