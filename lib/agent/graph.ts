import { z } from 'zod';

export const AnalyzeRequest = z.object({ query: z.string().min(1) });
export type AnalyzeRequest = z.infer<typeof AnalyzeRequest>;

export const AnalyzeResponse = z.object({
  entity: z.any().nullable(),
  plan: z.array(z.any()),
  insights: z.array(z.any()),
  citations: z.array(z.any()),
});
export type AnalyzeResponse = z.infer<typeof AnalyzeResponse>;

export async function analyzeCompany(_input: AnalyzeRequest): Promise<AnalyzeResponse> {
  // Placeholder implementation; will be replaced by LangGraph agent
  return { entity: null, plan: [], insights: [], citations: [] };
}

