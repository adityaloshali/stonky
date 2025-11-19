interface Props {
  params: { symbol: string };
}

export const revalidate = 300; // 5 minutes ISR

export default async function CompanyPage({ params }: Props) {
  const { symbol } = params;
  const CompanyAI = (await import('@/app/components/CompanyAI')).default;
  const NewsList = (await import('@/app/components/NewsList')).default;
  const BookmarkButton = (await import('@/app/components/BookmarkButton')).default;
  const FundamentalsCard = (await import('@/app/components/FundamentalsCard')).default;
  const PriceCard = (await import('@/app/components/PriceCard')).default;

  return (
    <main>
      <div className="container">
        <div className="stock-sticky" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 12 }}>
          <h1 style={{ fontSize: 36, marginBottom: 8 }}>Company: {symbol.toUpperCase()}</h1>
          <BookmarkButton symbol={symbol} />
        </div>

        {/* Price Data Section */}
        <div className="section">
          <PriceCard symbol={symbol} />
        </div>

        {/* Fundamentals Section */}
        <div className="section">
          <FundamentalsCard symbol={symbol} />
        </div>

        {/* Analysis and News Grid */}
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

