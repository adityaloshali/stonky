export const runtime = 'nodejs';

import { AnalyzeRequest, analyzeCompany } from '@/lib/agent/graph';

export async function POST(req: Request) {
  const json = await req.json().catch(() => ({}));
  const parsed = AnalyzeRequest.safeParse(json);
  if (!parsed.success) {
    return new Response(JSON.stringify({ error: 'Invalid body' }), { status: 400 });
  }
  const result = await analyzeCompany(parsed.data);
  return new Response(JSON.stringify(result), { headers: { 'content-type': 'application/json' } });
}

