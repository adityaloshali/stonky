interface Props {
  params: { symbol: string };
}

export const revalidate = 300; // 5 minutes ISR

export default async function CompanyPage({ params }: Props) {
  const { symbol } = params;
  const { getDailyOHLC, getLastPrice } = await import('@/lib/sources/yahoo');
  const CompanyAI = (await import('@/app/components/CompanyAI')).default;
  const NewsList = (await import('@/app/components/NewsList')).default;
  const BookmarkButton = (await import('@/app/components/BookmarkButton')).default;
  let lastClose: number | null = null;
  let count = 0;
  try {
    const prices = await getDailyOHLC(symbol, '1y');
    count = prices.length;
    if (count > 0) lastClose = Number(prices[count - 1]?.close ?? null);
  } catch {}
  if (lastClose == null) {
    const lp = await getLastPrice(symbol);
    if (lp.price != null) lastClose = lp.price;
  }
  return (
    <main>
      <div className="container">
        <div className="stock-sticky" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 12 }}>
          <h1 style={{ fontSize: 36, marginBottom: 8 }}>Company: {symbol.toUpperCase()}</h1>
          <BookmarkButton symbol={symbol} />
        </div>
        <div className="grid stats-sticky" style={{ gridTemplateColumns: 'repeat(12, 1fr)' }}>
          <div className="stat" style={{ gridColumn: 'span 3' }}>
            <div className="label">EOD Prices</div>
            <div className="value">{count.toLocaleString()}</div>
          </div>
          <div className="stat" style={{ gridColumn: 'span 3' }}>
            <div className="label">Last Close</div>
            <div className="value">{lastClose != null ? lastClose.toFixed(2) : '-'}</div>
          </div>
        </div>
        <div className="section">
          <div className="card">Fundamentals, technicals, filings, news will appear here.</div>
        </div>
        <div className="grid section" style={{ gridTemplateColumns: 'repeat(12, 1fr)' }}>
          <div style={{ gridColumn: 'span 7' }} className="analysis-scroll">
            <CompanyAI symbol={symbol} />
          </div>
          <div style={{ gridColumn: 'span 5' }} className="news-sticky">
            <NewsList symbol={symbol} />
          </div>
        </div>
      </div>
    </main>
  );
}

