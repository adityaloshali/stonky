// Ambient declarations to avoid type resolution errors in minimal scaffold
declare module 'yahoo-finance2';
declare module '@ai-sdk/openai' {
  export function createOpenAI(config?: any): any;
}
declare module 'ai' {
  export function streamText(args: any): any;
  export function generateText(args: any): Promise<{ text: string }>;
}

// Minimal JSX to satisfy TS without @types/react
declare namespace JSX {
  interface IntrinsicElements {
    [elemName: string]: any;
  }
}

// Minimal process.env typing without @types/node
declare const process: { env: Record<string, string | undefined> };

