import { Hono } from 'hono';
import { handle } from 'hono/nextjs';

export const runtime = 'nodejs';

const app = new Hono();

app.get('/health', (c) => c.json({ ok: true }));

app.get('/v1/company/:symbol/summary', async (c) => {
  const symbol = c.req.param('symbol');
  // TODO: Wire to agent/tools in later tasks
  return c.json({ symbol, summary: null, status: 'not_implemented' });
});

export const GET = handle(app);
export const POST = handle(app);

