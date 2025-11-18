'use client';

import { useRef, useState } from 'react';

export default function CompanyAI({ symbol }: { symbol: string }) {
  const [text, setText] = useState('');
  const [structured, setStructured] = useState<any | null>(null);
  const [loading, setLoading] = useState(false);
  const controller = useRef<AbortController | null>(null);

  async function run() {
    setLoading(true);
    controller.current?.abort();
    controller.current = new AbortController();
    setText('');
    try {
      const res = await fetch('/api/ai/structured', {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({ symbol }),
        signal: controller.current.signal,
      });
      const data = await res.json();
      setText(data?.text || '');
      setStructured(data?.data || null);
    } catch (e) {
      setText('AI summary failed.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{ marginTop: 16 }}>
      <button onClick={run} disabled={loading} className="btn">
        {loading ? 'Summarizing…' : 'Summarize with AI'}
      </button>
      {structured && (
        <div className="grid section" style={{ gridTemplateColumns: 'repeat(12, 1fr)', alignItems: 'start' }}>
          <div className="card" style={{ gridColumn: 'span 12' }}>
            <div style={{ fontWeight: 700, marginBottom: 8 }}>{structured.headline || 'Overview'}</div>
            {text && <div className="ai-summary" style={{ color: 'var(--muted)', fontSize: 13 }}>{text}</div>}
          </div>
          <div className="card" style={{ gridColumn: 'span 6' }}>
            <div className="section"><h2>Segments</h2>
              <ul className="bullets">{(structured.segments || []).map((s: string, i: number) => <li key={i}>{s}</li>)}</ul>
            </div>
          </div>
          <div className="card" style={{ gridColumn: 'span 6' }}>
            <div className="section"><h2>Recent results</h2>
              <ul className="bullets">{(structured.recentResults || []).map((s: string, i: number) => <li key={i}>{s}</li>)}</ul>
            </div>
          </div>
          <div className="card" style={{ gridColumn: 'span 6' }}>
            <div className="section"><h2>Key themes</h2>
              <ul className="bullets">{(structured.keyThemes || []).map((s: string, i: number) => <li key={i}>{s}</li>)}</ul>
            </div>
          </div>
          <div className="card" style={{ gridColumn: 'span 6' }}>
            <div className="section"><h2>Risks</h2>
              <ul className="bullets">{(structured.risks || []).map((s: string, i: number) => <li key={i}>{s}</li>)}</ul>
            </div>
          </div>
          <div className="card" style={{ gridColumn: 'span 12' }}>
            <div className="section"><h2>Opportunities</h2>
              <ul className="bullets">{(structured.opportunities || []).map((s: string, i: number) => <li key={i}>{s}</li>)}</ul>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

