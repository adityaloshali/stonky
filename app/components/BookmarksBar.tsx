'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';

type Item = { symbol: string; name?: string };
const KEY = 'bookmarks:v1';

function readBookmarks(): Item[] {
  if (typeof window === 'undefined') return [];
  try {
    const raw = localStorage.getItem(KEY);
    if (!raw) return [];
    const data = JSON.parse(raw);
    if (Array.isArray(data)) return data as Item[];
  } catch {}
  return [];
}

export default function BookmarksBar() {
  const [items, setItems] = useState<Item[]>([]);
  const router = useRouter();

  useEffect(() => {
    setItems(readBookmarks());
    const onStorage = (e: StorageEvent) => {
      if (e.key === KEY) setItems(readBookmarks());
    };
    window.addEventListener('storage', onStorage);
    return () => window.removeEventListener('storage', onStorage);
  }, []);

  if (items.length === 0) return null;

  return (
    <div style={{ marginTop: 16, display: 'flex', gap: 8, flexWrap: 'wrap' }}>
      {items.slice(0, 12).map((it) => (
        <button key={it.symbol} className="toggle" onClick={() => router.push(`/company/${encodeURIComponent(it.symbol)}`)}>
          {it.symbol}
        </button>
      ))}
    </div>
  );
}


