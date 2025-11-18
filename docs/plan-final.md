This is a **Master Design Document** for **"AlphaGaze"** (working title).

As a former Staff Engineer turned Product Manager, I have structured this to be **execution-ready**. It bridges the gap between "cool idea" and "scalable software," specifically solving the *Step 1 (Qualitative)* vs. *Step 2-6 (Quantitative)* disconnect.

---

# 1. Executive Summary & Product Vision

**The Problem:** Retail investors have tools for **Data** (Screener.in, Trendlyne) and tools for **Charts** (TradingView), but no tool for **Synthesis**. They still have to read 200-page PDFs to understand *"What does this company actually do?"* (Step 1 of your Framework).

**The Solution:** An **AI-Augmented Investment Terminal** that automates the "Refined Framework 2025." It combines hard official data (NSE/BSE/Screener) with soft qualitative analysis (AI reading Annual Reports/Concalls) to deliver a Buy/Hold/Sell verdict.

**Core Value Prop:** "The depth of a Hedge Fund Analyst, the speed of a click."

---

# 2. Data Strategy: The "Triad" Pipeline

We will not rely on a single source. We use a **Waterfall Fallback System**.

### A. Source 1: The "Official" Truth (NSE/BSE)
*   **Purpose:** Corporate Filings, Shareholding Patterns, Block Deals, Official PDF Downloads.
*   **Ingestion Method:**
    *   Use `nselib` and custom headers to hit NSE internal APIs.
    *   **Critical:** Download the **Annual Report** and **Concall Transcript** PDFs. These are the "Raw Materials" for Step 1.
*   **Refresh Rate:** Daily (Post-market hours).

### B. Source 2: The "Deep" Fundamentals (Screener.in Logic)
*   **Purpose:** 10-Year Cleaned Historical Data (Sales, Profit, Cash Flow).
*   **Ingestion Method:** Headless Browser (Playwright) or Session-based Request to the "Export to Excel" endpoint.
*   **Logic:** We extract the raw CSV data.
*   **Refresh Rate:** Weekly (Fundamentals don't change daily).

### C. Source 3: The "Live" Pulse (Yahoo Finance)
*   **Purpose:** Live Ticker Prices, PE Ratios, Sector categorization, Technicals (200 DMA).
*   **Ingestion Method:** `yfinance` library.
*   **Refresh Rate:** Real-time (15-min delay).

---

# 3. Solving "Step 1": The AI Context Engine (The differentiator)

This is the hardest part. To answer *"What is the moat?"* and *"Industry Trend?"*, we cannot rely on Google Search alone (too noisy). We must read what the company says.

**The Architecture: RAG (Retrieval-Augmented Generation)**

1.  **The Scraper:**
    *   Identify `TATASTEEL`.
    *   Go to NSE > Corporate Filings.
    *   Download latest `Annual_Report_2024.pdf` and `Earnings_Call_Transcript_Q3.pdf`.
2.  **The Processor (ETL):**
    *   **OCR/Text Extraction:** Convert PDF to text.
    *   **Chunking:** Split text into 500-word blocks with overlap.
    *   **Embedding:** Convert text blocks into Vectors (math representations) using OpenAI Embeddings or HuggingFace.
    *   **Storage:** Store vectors in **Pinecone** or **pgvector**.
3.  **The Query:**
    *   When user asks for analysis, the system queries the Vector DB: *"Find segments regarding competitive advantage, future guidance, and risks."*
    *   The Top 5 chunks are retrieved.
4.  **The Synthesis (LLM):**
    *   We feed the retrieved text + specific prompts (Step 1 of PDF) to GPT-4o.
    *   *Result:* A 100% fact-based summary citing the specific page of the Annual Report.

---

# 4. Technical Architecture (System Design)

We will use a **Microservices-lite** architecture to separate heavy data crunching from the user interface.

### A. The Stack
*   **Frontend:** **Next.js 14 (App Router)**. Server-side rendering is crucial for SEO and fast load times. Tailwind CSS for UI.
*   **Backend API:** **FastAPI (Python)**. High performance, async support, native integration with Data Science libs.
*   **Task Queue:** **Celery + Redis**. Analyzing a stock takes 10-20 seconds. We cannot block the HTTP request. We queue the job.
*   **Database:** **PostgreSQL**.
    *   `Table: Stocks` (Static info)
    *   `Table: Financials_Annual` (JSONB column for flexible schema)
    *   `Table: Reports` (The final generated analysis)

### B. Data Flow Diagram
1.  **User** types "RELIANCE".
2.  **Backend** checks DB. Is data < 24 hours old?
    *   *Yes:* Return cached report instantly.
    *   *No:* Trigger **Celery Worker**.
3.  **Celery Worker**:
    *   Fetches Fundamentals (Screener/NSE).
    *   Fetches Live Price (Yahoo).
    *   Fetches PDF & Runs RAG (Step 1).
    *   Runs "HQSF" Math logic (Step 2-6).
    *   Saves to DB.
4.  **Frontend** polls for status, then renders the Dashboard.

---

# 5. The "Refined Framework" Implementation Plan

Here is how we map the PDF steps to specific code modules.

### Module A: Business Intelligence (Step 1)
*   **Inputs:** RAG output from Annual Reports + Google News (via Serper API) for "Latest Sentiment."
*   **Output:** A generated paragraph: "Reliance is shifting from Oil-to-Chemicals (O2C) to New Energy. Key Moat: Scale and Telecom duopoly. Risks: Global O2C margin pressure."

### Module B: The Financial Health Check (Step 2 & 3)
*   **Algorithm:**
    *   Calculate `Revenue_CAGR_5yr` and `Profit_CAGR_5yr`.
    *   Calculate `Avg_ROCE_3yr` and `Avg_ROE_3yr`.
    *   **Logic:** `IF (ROCE < 15% AND ROE > 15%) SET Flag = "Debt Fueled Risk"`.
    *   **Logic:** `IF (CFO < 0.8 * NetProfit) SET Flag = "Accounting Check"`.

### Module C: Risk & Valuation (Step 4 & 5)
*   **Dynamic Logic:**
    *   Identify Sector (e.g., "Banking").
    *   Look up `Sector_Rules.json`. (Banking D/E limit = 2.0; IT D/E limit = 0.3).
    *   Compare `Current_PE` vs `5yr_Median_PE` vs `Sector_PE`.
    *   **Visualization:** Generate the "Golden Goal" scatter plot coordinates.

### Module D: The Verdict Engine (Step 7)
This is a deterministic logic tree (not AI), to ensure safety.
```python
def generate_verdict(quality_score, valuation_score, risk_score):
    if quality_score == "High" and risk_score == "Low":
        if valuation_score == "Undervalued":
            return "STRONG BUY (Deep Value)"
        elif valuation_score == "Fair":
            return "ACCUMULATE (Quality at Fair Price)"
        else:
            return "WAIT (Quality but Expensive)"
    elif risk_score == "High":
        return "AVOID (Structural Risk)"
    # ... etc
```

---

# 6. Product Roadmap & Phasing

### Phase 1: The MVP (The "Screener Plus")
*   **Goal:** Manual Step 1, Automated Step 2-7.
*   **Features:**
    *   Search Bar.
    *   Scrapes Data (Screener/Yahoo).
    *   Calculates HQSF metrics.
    *   Shows "Traffic Light" dashboard (Red/Green flags).
    *   *Verdict:* Code-based logic only.

### Phase 2: The AI Analyst (The "Pro" Version)
*   **Goal:** Automate Step 1.
*   **Features:**
    *   Integration of NSE PDF downloading.
    *   Vector DB implementation.
    *   LLM generates the "Business Understanding" text.
    *   "Ask the Analyst" chat box (Chat with the Annual Report).

### Phase 3: Portfolio & Alerts
*   **Goal:** Retention.
*   **Features:**
    *   "Watchlist" with auto-analysis updates.
    *   "Quarterly Result Scanner": When results drop on NSE, auto-analyze and email the user within 10 mins.

---

# 7. Frontend Wireframe Concept (The "Pro" Look)

Don't make it look like a spreadsheet. Make it look like a **Cockpit**.

*   **Top Bar:** Ticker | Price | **HQSF Score (85/100)** | Verdict Badge (BUY).
*   **Left Column (The Story):**
    *   "Business Summary" (AI Generated).
    *   "Moat Analysis" (AI Generated).
    *   "The Bull Case" vs "The Bear Case" (AI Generated).
*   **Center Column (The Evidence):**
    *   Charts: Revenue Growth, Margin Expansion.
    *   The "Debt Meter" (Gauge Chart).
    *   The "Golden Goal" Matrix (Visual positioning).
*   **Right Column (The Checklist):**
    *   Step 1: Business ✅
    *   Step 2: Growth ✅
    *   Step 3: Quality ⚠️ (ROCE dipping)
    *   Step 4: Risk ✅
    *   Step 5: Valuation ❌ (Overvalued)
    *   Step 6: Ownership ✅

---

# 8. Monetization Strategy (Optional)

If you plan to release this:
1.  **Freemium:**
    *   Free: Automated Financial Analysis (Steps 2-6).
    *   Pro: AI-Business Analysis (Step 1) + "Chat with PDF" (RAG costs money).
2.  **API Access:** Sell the JSON output of your "Refined Framework" to other developers.

This plan converts the static PDF framework into a dynamic, living engine. It solves the "Lazy Step 1" problem by using RAG, making it significantly better than existing tools.
