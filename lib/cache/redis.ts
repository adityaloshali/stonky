import Redis from 'ioredis';

let client: Redis | null = null;

export function getRedis(): Redis | null {
  if (client) return client;
  const url = process.env.REDIS_URL;
  const token = process.env.REDIS_TOKEN;
  if (!url) return null;
  client = new Redis(url, token ? { username: 'default', password: token } : undefined);
  return client;
}

export async function cacheJson<T>(key: string, fetcher: () => Promise<T>, ttlSec = 300): Promise<T> {
  const redis = getRedis();
  if (redis) {
    const cached = await redis.get(key);
    if (cached) return JSON.parse(cached) as T;
  }
  const value = await fetcher();
  if (redis) await redis.set(key, JSON.stringify(value), 'EX', ttlSec);
  return value;
}

