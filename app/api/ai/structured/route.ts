export const runtime = 'nodejs';

import { getOpenAI, getDefaultModelId } from '@/lib/ai/modelRouter';
import { generateText } from 'ai';

const system = `You are an equity research assistant focused on Indian equities. 
Return a concise JSON with fields: 
{
  "headline": string,
  "segments": string[],
  "recentResults": string[],
  "keyThemes": string[],
  "risks": string[],
  "opportunities": string[]
}
Do not include markdown or extra commentary.`;

export async function POST(req: Request) {
  const body = await req.json().catch(() => ({}));
  const symbol = (body?.symbol as string) || '';
  if (!symbol) return new Response(JSON.stringify({ error: 'Missing symbol' }), { status: 400 });

  const provider = getOpenAI();
  const modelId = getDefaultModelId();
  const prompt = `${system}\nSummarize ${symbol} into the JSON schema.`;
  try {
    const res = await generateText({ model: provider(modelId), prompt });
    // Attempt to extract JSON
    const text = res.text || '';
    const jsonStart = text.indexOf('{');
    const jsonEnd = text.lastIndexOf('}');
    let data: any = {};
    if (jsonStart !== -1 && jsonEnd !== -1) {
      try { data = JSON.parse(text.substring(jsonStart, jsonEnd + 1)); } catch {}
    }
    return new Response(JSON.stringify({ raw: text, data }), { headers: { 'content-type': 'application/json' } });
  } catch (e: any) {
    return new Response(JSON.stringify({ error: e?.message || 'LLM failed' }), { status: 500 });
  }
}

