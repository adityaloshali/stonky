'use client';

import { useEffect, useState } from 'react';
import { getFundamentals, type FundamentalsResponse, formatLargeNumber } from '@/lib/api/backend';

export default function FundamentalsCard({ symbol }: { symbol: string }) {
  const [data, setData] = useState<FundamentalsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;

    async function load() {
      setLoading(true);
      setError(null);
      try {
        const fundamentals = await getFundamentals(symbol);
        if (mounted) {
          setData(fundamentals);
        }
      } catch (err) {
        if (mounted) {
          setError(err instanceof Error ? err.message : 'Failed to load fundamentals');
        }
      } finally {
        if (mounted) {
          setLoading(false);
        }
      }
    }

    load();
    return () => { mounted = false; };
  }, [symbol]);

  if (loading) {
    return (
      <div className="card">
        <h2 style={{ marginBottom: 16 }}>10-Year Fundamentals</h2>
        <div style={{ color: 'var(--muted)' }}>Loading fundamentals data...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="card">
        <h2 style={{ marginBottom: 16 }}>10-Year Fundamentals</h2>
        <div style={{ color: 'var(--danger)', fontSize: 14 }}>
          {error.includes('not configured') || error.includes('expired') ? (
            <div>
              <div style={{ marginBottom: 8 }}>⚠️ {error}</div>
              <div style={{ fontSize: 12, color: 'var(--muted)' }}>
                Note: This data requires Screener.in authentication. Please check backend configuration.
              </div>
            </div>
          ) : (
            `Error: ${error}`
          )}
        </div>
      </div>
    );
  }

  if (!data || !data.years || data.years.length === 0) {
    return (
      <div className="card">
        <h2 style={{ marginBottom: 16 }}>10-Year Fundamentals</h2>
        <div style={{ color: 'var(--muted)' }}>No fundamental data available.</div>
      </div>
    );
  }

  // Get latest values (first in array)
  const latest = {
    revenue: data.revenue[0],
    profit: data.net_profit[0],
    roce: data.roce[0],
    roe: data.roe[0],
    de: data.debt_to_equity[0],
    eps: data.eps[0],
  };

  // Calculate growth (latest vs 3 years ago if available)
  const getGrowth = (values: (number | null)[]) => {
    if (values.length < 4) return null;
    const latest = values[0];
    const threeYearsAgo = values[3];
    if (latest == null || threeYearsAgo == null || threeYearsAgo === 0) return null;
    return ((latest - threeYearsAgo) / threeYearsAgo) * 100;
  };

  const revenueGrowth = getGrowth(data.revenue);
  const profitGrowth = getGrowth(data.net_profit);

  return (
    <div className="card">
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 16 }}>
        <h2 style={{ margin: 0 }}>10-Year Fundamentals</h2>
        <div style={{ fontSize: 12, color: 'var(--muted)' }}>
          Source: {data.source}
        </div>
      </div>

      {/* Key Metrics Grid */}
      <div className="grid" style={{ gridTemplateColumns: 'repeat(3, 1fr)', gap: 12, marginBottom: 20 }}>
        <div className="stat">
          <div className="label">Revenue</div>
          <div className="value">{formatLargeNumber(latest.revenue)}</div>
          {revenueGrowth != null && (
            <div style={{ fontSize: 11, color: revenueGrowth >= 0 ? 'var(--success)' : 'var(--danger)' }}>
              {revenueGrowth >= 0 ? '+' : ''}{revenueGrowth.toFixed(1)}% (3Y)
            </div>
          )}
        </div>

        <div className="stat">
          <div className="label">Net Profit</div>
          <div className="value">{formatLargeNumber(latest.profit)}</div>
          {profitGrowth != null && (
            <div style={{ fontSize: 11, color: profitGrowth >= 0 ? 'var(--success)' : 'var(--danger)' }}>
              {profitGrowth >= 0 ? '+' : ''}{profitGrowth.toFixed(1)}% (3Y)
            </div>
          )}
        </div>

        <div className="stat">
          <div className="label">EPS</div>
          <div className="value">₹{latest.eps?.toFixed(2) ?? '-'}</div>
        </div>

        <div className="stat">
          <div className="label">ROCE %</div>
          <div className="value" style={{ color: (latest.roce ?? 0) >= 15 ? 'var(--success)' : 'inherit' }}>
            {latest.roce?.toFixed(1) ?? '-'}%
          </div>
        </div>

        <div className="stat">
          <div className="label">ROE %</div>
          <div className="value" style={{ color: (latest.roe ?? 0) >= 15 ? 'var(--success)' : 'inherit' }}>
            {latest.roe?.toFixed(1) ?? '-'}%
          </div>
        </div>

        <div className="stat">
          <div className="label">D/E Ratio</div>
          <div className="value" style={{ color: (latest.de ?? 0) > 1 ? 'var(--warning)' : 'var(--success)' }}>
            {latest.de?.toFixed(2) ?? '-'}
          </div>
        </div>
      </div>

      {/* Historical Data Summary */}
      <div style={{ fontSize: 12, color: 'var(--muted)', marginTop: 12 }}>
        <div>Data available for {data.years.length} years: {data.years[data.years.length - 1]} to {data.years[0]}</div>
      </div>
    </div>
  );
}
