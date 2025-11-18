Here is the **100% Detailed Technical Plan** to build **AlphaGaze** (The Tool).

---

# PART 1: THE ARCHITECTURE & COST STRATEGY

**Addressing your concern:** *"Why is it server api? Won't that cost me?"*

1.  **Your "Server" (FastAPI):** This is your backend logic. You can host this on a cheap VPS (Hetzner/DigitalOcean) for **$4-5/month**. Or run it locally on your PC for **$0**.
2.  **Data APIs (Yahoo/NSE/Screener):** We are using the **"Unofficial/Scraping"** methods below. Cost = **$0**.
3.  **The AI (Step 1 Context):**
    *   **Option A (Paid but Easy):** OpenAI API. Cost: ~$0.01 per stock analysis.
    *   **Option B (Free):** **Ollama** (Run Llama 3 locally on your machine) OR **DuckDuckGo** (Search scraping). I will implement the **Free Search Scraping** method below.

---

# PART 2: THE DIRECTORY STRUCTURE

As a former Staff Engineer, you know structure matters.

```text
alpha-gaze/
├── app/
│   ├── main.py              # FastAPI Entry Point
│   ├── core/
│   │   ├── config.py        # Env variables (Cookies, API keys)
│   │   └── database.py      # PostgreSQL Connection
│   ├── services/
│   │   ├── screener_svc.py  # Scrapes Screener.in (Fundamentals)
│   │   ├── nse_svc.py       # Scrapes NSE (Shareholding)
│   │   ├── yfinance_svc.py  # Scrapes Yahoo (Price/Tech)
│   │   └── context_svc.py   # Scrapes "About Company" (Step 1)
│   ├── engine/
│   │   ├── analyzer.py      # The "Refined Framework" Logic Class
│   │   └── scorer.py        # Calculates HQSF Scores
│   └── models/              # Pydantic & SQLAlchemy Models
├── requirements.txt
└── .env                     # Stores your Screener Cookie
```

---

# PART 3: THE DATA LAYER (THE CODE)

Here is the exact Python code to fetch the data **For Free**.

### 1. `services/screener_svc.py` (The Fundamentals)
**Logic:** We pretend to be a browser, use your session cookie, and download the "Export to Excel" file in memory to get 10 years of data.

```python
import requests
import pandas as pd
from io import BytesIO
from app.core.config import settings

class ScreenerService:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': 'https://www.screener.in/'
        }
        # YOU MUST MANUALLY LOG IN TO SCREENER ONCE AND COPY THE "sessionid" COOKIE
        self.cookies = {'sessionid': settings.SCREENER_COOKIE} 

    def fetch_data(self, ticker: str):
        """
        Fetches 10-year consolidated data for a ticker (e.g., TATASTEEL)
        """
        # 1. Get the 'warehouse_id' (Company ID)
        search_url = f"https://www.screener.in/company/{ticker}/consolidated/"
        try:
            # 2. Hit the Excel Export Endpoint directly
            # This is the 'Hidden API' used by Screeni-py
            export_url = f"https://www.screener.in/excel/{ticker}/consolidated/"
            response = requests.get(export_url, headers=self.headers, cookies=self.cookies)
            
            if response.status_code != 200:
                raise Exception(f"Failed to fetch Screener data: {response.status_code}")

            # 3. Parse Excel in Memory
            xls = pd.read_excel(BytesIO(response.content), sheet_name="Data Sheet")
            
            # 4. Transpose & Clean
            # Screener Excel usually has Dates as Columns. We want Dates as Rows.
            df = xls.transpose()
            # (Additional cleaning logic would go here to map column names)
            
            return df.to_dict() # Return raw dictionary of 10y data
            
        except Exception as e:
            print(f"Error: {e}")
            return None
```

### 2. `services/nse_svc.py` (The Official Shareholding)
**Logic:** NSE blocks generic requests. We use a `Session` to maintain cookies and mimic a browser visit.

```python
import requests

class NSEService:
    def __init__(self):
        self.base_url = "https://www.nseindia.com"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def _init_session(self):
        # Visit homepage to set cookies
        self.session.get(self.base_url)

    def get_shareholding(self, symbol: str):
        """
        Fetches detailed promoter/FII/DII data.
        Symbol: 'RELIANCE'
        """
        try:
            self._init_session()
            # The hidden API endpoint for shareholding
            url = f"https://www.nseindia.com/api/quote-equity?symbol={symbol}&section=trade_info"
            
            # NSE is strict about Referer for API calls
            self.session.headers.update({'Referer': f"https://www.nseindia.com/get-quotes/equity?symbol={symbol}"})
            
            response = self.session.get(url)
            if response.status_code == 401:
                # Cookie expired, retry once
                self._init_session()
                response = self.session.get(url)

            data = response.json()
            
            # Extract the relevant part for Step 6 of your PDF
            holding_data = data.get('securityWiseDP', {}).get('shareholdingPatterns', [])
            promoter_pledge = data.get('securityWiseDP', {}).get('promoterEncumbrance', {})
            
            return {
                "patterns": holding_data,
                "pledging": promoter_pledge
            }
        except Exception as e:
            print(f"NSE Fetch Error: {e}")
            return None
```

### 3. `services/context_svc.py` (Step 1: The Business Understanding - FREE)
**Logic:** Instead of paying for Google API, we use `duckduckgo_search` (a free Python library) to find the company description and "Moat" keywords.

```python
from duckduckgo_search import DDGS

class ContextService:
    def get_company_context(self, ticker_name: str):
        """
        Searches web for 'Company Name Business Model Moat'
        """
        results = []
        query = f"{ticker_name} stock business model competitive advantage moat"
        
        with DDGS() as ddgs:
            # Get top 5 search results (Free)
            search_gen = ddgs.text(query, max_results=5)
            for r in search_gen:
                results.append(r['body'])
        
        # Basic "Bag of Words" analysis (Zero Cost AI)
        # In a Pro version, you'd send 'results' to an LLM.
        text_blob = " ".join(results)
        
        return {
            "summary_snippets": results,
            "keywords_found": self._extract_keywords(text_blob)
        }

    def _extract_keywords(self, text):
        keywords = []
        if "market leader" in text.lower(): keywords.append("Market Leader")
        if "monopoly" in text.lower(): keywords.append("Monopoly")
        if "high barrier" in text.lower(): keywords.append("High Entry Barriers")
        return keywords
```

---

# PART 4: THE ENGINE (THE LOGIC LAYER)

This is where we implement the **PDF Framework Rules**. This runs on your server.

### `engine/analyzer.py`

```python
import pandas as pd
import numpy as np

class StockAnalyzer:
    def __init__(self, fundamentals, market_data, shareholding):
        self.fund = fundamentals # The 10y Data Dictionary
        self.market = market_data # Yahoo Data
        self.holdings = shareholding # NSE Data

    def run_full_analysis(self):
        return {
            "step_2_growth": self.analyze_growth(),
            "step_3_quality": self.analyze_quality(),
            "step_4_risk": self.analyze_risk(),
            "step_5_valuation": self.analyze_valuation(),
            "step_6_ownership": self.analyze_ownership(),
            "final_verdict": self.generate_verdict()
        }

    def analyze_quality(self):
        """
        Step 3: Check ROCE & ROE > 15%
        """
        # Assuming 'fund' has rows 'ROCE' and 'ROE'
        # We take average of last 3 years
        roce_avg = np.mean(self.fund['ROCE'][-3:])
        roe_avg = np.mean(self.fund['ROE'][-3:])
        
        status = "NEUTRAL"
        if roce_avg > 15 and roe_avg > 15:
            status = "GREEN" # High Quality
        elif roce_avg < 15 and roe_avg > 15:
            status = "RED" # Debt fueled?
            
        return {"roce_3yr": roce_avg, "roe_3yr": roe_avg, "flag": status}

    def analyze_risk(self):
        """
        Step 4: Debt to Equity Check
        """
        d_e = self.fund['Debt to Equity'][-1] # Current year
        
        # Simple sector logic (You can expand this)
        sector = self.market.get('sector', '')
        threshold = 2.0 if 'Bank' in sector or 'Power' in sector else 1.0
        
        return {
            "current_de": d_e,
            "threshold": threshold,
            "is_safe": d_e < threshold
        }

    def analyze_ownership(self):
        """
        Step 6: Pledging & FII Trend
        """
        # Parse NSE data
        pledging = self.holdings.get('pledging', {}).get('promoter_pledged_share_percent', 0)
        
        is_pledged = float(pledging) > 0
        
        return {
            "promoter_pledging": pledging,
            "red_flag": is_pledged
        }
        
    def generate_verdict(self):
        # Step 7 Logic
        # Combine all flags above to return BUY/HOLD/AVOID
        pass 
```

---

# PART 5: EXECUTION PLAN (How to run this)

### Step 1: Setup
1.  Install Python 3.11.
2.  `pip install fastapi uvicorn pandas requests yfinance duckduckgo-search`

### Step 2: The "Secret Sauce" (Cookies)
1.  Open Chrome.
2.  Login to **Screener.in**.
3.  Right-click > Inspect > Application > Cookies.
4.  Copy the value of `sessionid`.
5.  Paste it into your code (`.env` file). *Note: This cookie lasts about 1 month. You will need to update it monthly.*

### Step 3: Running the "Server"
You run the API locally. It costs nothing.
```bash
uvicorn app.main:app --reload
```

### Step 4: The Frontend
You interact with this via a simple Web UI (Next.js) or even a simple Swagger UI (Auto-generated by FastAPI at `http://localhost:8000/docs`).

---

# Summary of "Step 1" Solution (Free vs Paid)

The PDF Step 1 asks for "Business Understanding, Competitive Edge, Industry Trend."

**The Free Way (My Code above):**
*   We search DuckDuckGo for keywords.
*   We extract snippets.
*   We display those snippets to you. You read them.

**The Pro Way (Automated):**
*   We take those snippets.
*   We send them to **Google Gemini Flash API** (It has a generous free tier).
*   Prompt: *"Summarize these snippets into a Business Model Analysis."*
*   This gives you the "Human-like" report without the cost of GPT-4.

This plan gives you the **exact tools** to scrape the "Big 3" data sources for free, process them using the logic from your PDF, and run it on your own machine.
