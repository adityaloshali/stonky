'use client';

import { useEffect, useState } from 'react';

type Item = { title: string; link: string; source?: string; publishedAt?: string };

export default function NewsList({ symbol }: { symbol: string }) {
  const [items, setItems] = useState<Item[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    let mounted = true;
    setLoading(true);
    fetch(`/api/news/${encodeURIComponent(symbol)}`)
      .then((r) => r.json())
      .then((d) => { if (mounted) setItems(d.items || []); })
      .catch(() => { if (mounted) setItems([]); })
      .finally(() => { if (mounted) setLoading(false); });
    return () => { mounted = false; };
  }, [symbol]);

  if (loading && items.length === 0) return <div className="card">Loading news…</div>;
  if (items.length === 0) return <div className="card">No recent news found.</div>;

  return (
    <div className="card" style={{ minHeight: 320 }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 8 }}>
        <h2 style={{ margin: 0 }}>Latest news</h2>
      </div>
      <div className="stack">
        {items.map((it, idx) => (
          <a key={idx} href={it.link} target="_blank" rel="noreferrer" style={{ textDecoration: 'none', color: 'inherit' }}>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
              <div style={{ fontWeight: 600 }} className="clamp-2">{it.title}</div>
              <div style={{ fontSize: 12, color: 'var(--muted)' }}>{it.source || 'News'}{it.publishedAt ? ` • ${new Date(it.publishedAt).toLocaleDateString()}` : ''}</div>
            </div>
          </a>
        ))}
      </div>
    </div>
  );
}

