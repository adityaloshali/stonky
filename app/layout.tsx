import './globals.css';
import dynamic from 'next/dynamic';
import Link from 'next/link';
const ThemeToggle = dynamic(() => import('./components/ThemeToggle'), { ssr: false });
export const metadata = {
  title: 'Stock Analysis App',
  description: 'Agentic stock analysis for the Indian market',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <header className="header">
          <div className="inner">
            <Link href="/" className="brand">StockAnalysis</Link>
            <ThemeToggle />
          </div>
        </header>
        {children}
      </body>
    </html>
  );
}

