'use client';

import { useEffect, useState } from 'react';
import { getPrices, type PricesResponse, formatCurrency } from '@/lib/api/backend';

export default function PriceCard({ symbol }: { symbol: string }) {
  const [data, setData] = useState<PricesResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [period, setPeriod] = useState<string>('1y');

  useEffect(() => {
    let mounted = true;

    async function load() {
      setLoading(true);
      setError(null);
      try {
        const prices = await getPrices(symbol, period);
        if (mounted) {
          setData(prices);
        }
      } catch (err) {
        if (mounted) {
          setError(err instanceof Error ? err.message : 'Failed to load prices');
        }
      } finally {
        if (mounted) {
          setLoading(false);
        }
      }
    }

    load();
    return () => { mounted = false; };
  }, [symbol, period]);

  if (loading) {
    return (
      <div className="card">
        <h2 style={{ marginBottom: 16 }}>Price History</h2>
        <div style={{ color: 'var(--muted)' }}>Loading price data...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="card">
        <h2 style={{ marginBottom: 16 }}>Price History</h2>
        <div style={{ color: 'var(--danger)', fontSize: 14 }}>Error: {error}</div>
      </div>
    );
  }

  if (!data || data.count === 0) {
    return (
      <div className="card">
        <h2 style={{ marginBottom: 16 }}>Price History</h2>
        <div style={{ color: 'var(--muted)' }}>No price data available.</div>
      </div>
    );
  }

  // Calculate statistics
  const prices = data.prices;
  const latest = prices[prices.length - 1];
  const first = prices[0];
  const change = latest.close - first.close;
  const changePercent = (change / first.close) * 100;

  const high = Math.max(...prices.map(p => p.high));
  const low = Math.min(...prices.map(p => p.low));
  const avgVolume = prices.reduce((sum, p) => sum + p.volume, 0) / prices.length;

  return (
    <div className="card">
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 16 }}>
        <h2 style={{ margin: 0 }}>Price History</h2>
        <div style={{ display: 'flex', gap: 8 }}>
          {['1mo', '3mo', '6mo', '1y', '5y'].map((p) => (
            <button
              key={p}
              onClick={() => setPeriod(p)}
              style={{
                padding: '4px 8px',
                fontSize: 12,
                border: '1px solid var(--border)',
                borderRadius: 4,
                background: period === p ? 'var(--primary)' : 'transparent',
                color: period === p ? 'white' : 'inherit',
                cursor: 'pointer',
              }}
            >
              {p.toUpperCase()}
            </button>
          ))}
        </div>
      </div>

      {/* Latest Price */}
      <div style={{ marginBottom: 20 }}>
        <div style={{ fontSize: 32, fontWeight: 700 }}>
          {formatCurrency(latest.close)}
        </div>
        <div style={{
          fontSize: 16,
          color: change >= 0 ? 'var(--success)' : 'var(--danger)',
          fontWeight: 600,
        }}>
          {change >= 0 ? '+' : ''}{formatCurrency(change)} ({change >= 0 ? '+' : ''}{changePercent.toFixed(2)}%)
        </div>
        <div style={{ fontSize: 12, color: 'var(--muted)', marginTop: 4 }}>
          Period: {data.period.toUpperCase()} • {data.count} data points
        </div>
      </div>

      {/* Statistics Grid */}
      <div className="grid" style={{ gridTemplateColumns: 'repeat(3, 1fr)', gap: 12 }}>
        <div className="stat">
          <div className="label">Open</div>
          <div className="value">{formatCurrency(latest.open)}</div>
        </div>

        <div className="stat">
          <div className="label">High</div>
          <div className="value">{formatCurrency(latest.high)}</div>
        </div>

        <div className="stat">
          <div className="label">Low</div>
          <div className="value">{formatCurrency(latest.low)}</div>
        </div>

        <div className="stat">
          <div className="label">Period High</div>
          <div className="value">{formatCurrency(high)}</div>
        </div>

        <div className="stat">
          <div className="label">Period Low</div>
          <div className="value">{formatCurrency(low)}</div>
        </div>

        <div className="stat">
          <div className="label">Avg Volume</div>
          <div className="value">{(avgVolume / 1000000).toFixed(2)}M</div>
        </div>
      </div>

      {/* Simple Price Visualization (text-based mini chart) */}
      <div style={{ marginTop: 20, paddingTop: 16, borderTop: '1px solid var(--border)' }}>
        <div style={{ fontSize: 12, color: 'var(--muted)', marginBottom: 8 }}>
          Price Range: {formatCurrency(low)} → {formatCurrency(high)}
        </div>
        <div style={{
          height: 8,
          background: 'var(--border)',
          borderRadius: 4,
          position: 'relative',
          overflow: 'hidden',
        }}>
          <div style={{
            position: 'absolute',
            left: `${((latest.close - low) / (high - low)) * 100}%`,
            top: 0,
            bottom: 0,
            width: 2,
            background: 'var(--primary)',
          }} />
        </div>
        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 10, color: 'var(--muted)', marginTop: 4 }}>
          <span>Low</span>
          <span>Current</span>
          <span>High</span>
        </div>
      </div>
    </div>
  );
}
