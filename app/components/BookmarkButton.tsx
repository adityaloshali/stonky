'use client';

import { useEffect, useState } from 'react';

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

function writeBookmarks(items: Item[]) {
  try { localStorage.setItem(KEY, JSON.stringify(items)); } catch {}
}

export default function BookmarkButton({ symbol, name }: { symbol: string; name?: string }) {
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    const items = readBookmarks();
    setSaved(items.some(i => i.symbol === symbol));
    const onStorage = (e: StorageEvent) => {
      if (e.key === KEY) {
        const items = readBookmarks();
        setSaved(items.some(i => i.symbol === symbol));
      }
    };
    window.addEventListener('storage', onStorage);
    return () => window.removeEventListener('storage', onStorage);
  }, [symbol]);

  function toggle() {
    const items = readBookmarks();
    const exists = items.findIndex(i => i.symbol === symbol);
    if (exists >= 0) {
      items.splice(exists, 1);
      writeBookmarks(items);
      setSaved(false);
    } else {
      items.unshift({ symbol, name: name || symbol });
      // keep at most 50
      writeBookmarks(items.slice(0, 50));
      setSaved(true);
    }
  }

  return (
    <button onClick={toggle} className="btn secondary">
      {saved ? '★ Bookmarked' : '☆ Bookmark'}
    </button>
  );
}


