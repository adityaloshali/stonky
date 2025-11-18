export const runtime = 'nodejs';

import { getOpenAI, getDefaultModelId } from '@/lib/ai/modelRouter';
import { generateText } from 'ai';

export async function POST(req: Request) {
  const body = await req.json().catch(() => ({}));
  const prompt = (body?.prompt as string) || '';
  if (!prompt) return new Response(JSON.stringify({ error: 'Missing prompt' }), { status: 400 });

  const provider = getOpenAI();
  const modelId = getDefaultModelId();
  try {
    const result = await generateText({ model: provider(modelId), prompt });
    return new Response(JSON.stringify({ text: result.text }), { headers: { 'content-type': 'application/json' } });
  } catch (e: any) {
    return new Response(JSON.stringify({ error: e?.message || 'LLM failed' }), { status: 500 });
  }
}

