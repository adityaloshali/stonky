import dynamic from 'next/dynamic';
const SearchBar = dynamic(() => import('./components/SearchBar'), { ssr: false });
const BookmarksBar = dynamic(() => import('./components/BookmarksBar'), { ssr: false });

export default function HomePage() {
  return (
    <main>
      <div className="hero" style={{ minHeight: 'calc(100vh - var(--header-h))' }}>
        <div className="container">
          <h1>AI Stock Analysis</h1>
          <p>Search any Indian company and get fundamentals, technicals, filings, and an AI brief.</p>
          <div style={{ display: 'flex', justifyContent: 'center', marginTop: 16 }}>
            <SearchBar />
          </div>
          <BookmarksBar />
        </div>
      </div>
    </main>
  );
}

