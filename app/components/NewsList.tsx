'use client';

import { useEffect, useState } from 'react';
import { getNews, type NewsArticle } from '@/lib/api/backend';

export default function NewsList({ symbol }: { symbol: string }) {
  const [items, setItems] = useState<NewsArticle[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    let mounted = true;
    setLoading(true);

    async function loadNews() {
      try {
        const response = await getNews(symbol, 10);
        if (mounted) {
          setItems(response.articles);
        }
      } catch (error) {
        console.error('Failed to fetch news:', error);
        if (mounted) {
          setItems([]);
        }
      } finally {
        if (mounted) {
          setLoading(false);
        }
      }
    }

    loadNews();
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
              <div style={{ fontSize: 12, color: 'var(--muted)' }}>
                {it.source}{it.published ? ` • ${new Date(it.published).toLocaleDateString()}` : ''}
              </div>
            </div>
          </a>
        ))}
      </div>
    </div>
  );
}

