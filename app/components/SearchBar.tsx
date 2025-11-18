'use client';

import { useEffect, useMemo, useRef, useState } from 'react';
import { useRouter } from 'next/navigation';

type Item = { symbol: string; name: string; exchange?: string; type?: string };

export default function SearchBar() {
  const [q, setQ] = useState('');
  const [items, setItems] = useState<Item[]>([]);
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const router = useRouter();
  const timer = useRef<any>(null);

  useEffect(() => {
    if (!q) { setItems([]); setOpen(false); return; }
    setLoading(true);
    if (timer.current) clearTimeout(timer.current);
    timer.current = setTimeout(async () => {
      try {
        const res = await fetch(`/api/search?q=${encodeURIComponent(q)}`);
        const data = await res.json();
        setItems(data.items || []);
        setOpen(true);
      } catch {
        setItems([]);
        setOpen(false);
      } finally {
        setLoading(false);
      }
    }, 200);
  }, [q]);

  function goto(item: Item) {
    setOpen(false);
    router.push(`/company/${encodeURIComponent(item.symbol)}`);
  }

  return (
    <div style={{ position: 'relative', width: 560, maxWidth: '100%' }}>
      <input
        value={q}
        onChange={e => setQ(e.target.value)}
        placeholder="Search company or symbol (e.g., RELIANCE.NS)"
        className="input"
      />
      {open && items.length > 0 && (
        <div className="suggestions">
          {items.map((it) => (
            <div key={it.symbol} onClick={() => goto(it)} className="suggestion">
              <div className="sym">{it.symbol}</div>
              <div className="meta">{it.name}{it.exchange ? ` • ${it.exchange}` : ''}</div>
            </div>
          ))}
        </div>
      )}
      {loading && <div style={{ position: 'absolute', right: 8, top: 10, fontSize: 12, color: 'var(--muted)' }}>loading…</div>}
    </div>
  );
}

