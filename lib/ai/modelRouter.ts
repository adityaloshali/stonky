import { createOpenAI } from '@ai-sdk/openai';

export type ChatModel = ReturnType<typeof createOpenAI>;

export function getOpenAI(): any {
  const apiKey = process.env.OPENROUTER_API_KEY || process.env.OPENAI_API_KEY || '';
  const isOpenRouter = !!process.env.OPENROUTER_API_KEY || (process.env.OPENAI_BASE_URL || '').includes('openrouter.ai');
  const baseURL = process.env.OPENAI_BASE_URL || (isOpenRouter ? 'https://openrouter.ai/api/v1' : undefined);
  if (!apiKey) {
    // In dev we allow missing key so that non-LLM flows work; callers should handle failures.
    // eslint-disable-next-line no-console
    console.warn('No API key found for OpenAI/OpenRouter. Set OPENROUTER_API_KEY or OPENAI_API_KEY.');
  }
  return createOpenAI({ apiKey, baseURL });
}

export function getDefaultModelId(): string {
  const configured = process.env.AI_MODEL;
  if (configured) return configured;
  const isOpenRouter = !!process.env.OPENROUTER_API_KEY || (process.env.OPENAI_BASE_URL || '').includes('openrouter.ai');
  return isOpenRouter ? 'openai/gpt-4o-mini' : 'gpt-4o-mini';
}

