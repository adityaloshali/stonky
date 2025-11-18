export const runtime = 'nodejs';

import { searchSymbols } from '@/lib/sources/yahoo';

export async function GET(req: Request) {
  const url = new URL(req.url);
  const q = url.searchParams.get('q') || '';
  const items = await searchSymbols(q, 10);
  // Explicitly ensure only NSE/BSE symbols remain
  const filtered = items.filter((i: any) => /\.(NS|BO)$/i.test(i.symbol));
  return new Response(JSON.stringify({ items: filtered }), { headers: { 'content-type': 'application/json' } });
}

