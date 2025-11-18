export const runtime = 'nodejs';

import { getTopNews } from '@/lib/news/google';

export async function GET(_req: Request, { params }: { params: { symbol: string } }) {
  const { symbol } = params;
  const items = await getTopNews(symbol, 5);
  return new Response(JSON.stringify({ items }), { headers: { 'content-type': 'application/json' } });
}

