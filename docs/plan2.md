This is a high-ambition project. To build a tool that rivals **Trendlyne** (data depth) and **Snowball Analytics** (visualization/portfolio) while acting like a "Seasoned Investor," we cannot rely on simple API calls and a basic chatbot.

We need a **Hybrid Architecture**: A rigid **Quantitative Engine** (for accurate math/comparisons) and a flexible **RAG (Retrieval-Augmented Generation) Engine** (for reading history, concalls, and reports).

Here is the detailed technical plan to build this **Pro-Grade Stock Analysis Platform**.

---

### **1. System Architecture: The "3-Brain" Approach**

We will split the backend into three distinct "Brains" to handle the complexity.

1.  **The Accountant (Quantitative Engine):** Python-based. Handles raw numbers, calculates ratios, DCF, Graham numbers, and manages peer comparisons. *Zero hallucinations allowed.*
2.  **The Researcher (RAG/Context Engine):** AI-based. Reads PDFs (Annual Reports, Concall Transcripts), searches historical news, and understands "Management Quality" or "Govt Policy."
3.  **The Advisor (Synthesis Engine):** The LLM that takes outputs from the Accountant and Researcher to write the final "Step 7" verdict.

---

### **2. Data Strategy (The Foundation)**

You need "Deep Data" for the Indian market. `yfinance` is insufficient for detailed shareholding or historical balance sheets.

#### **A. Primary Data Sources (APIs & Scraping)**
1.  **Financials & Prices:**
    *   **Paid Option (Recommended for Pro):** **Financial Modeling Prep (FMP)** (Good global coverage) or a dedicated Indian data vendor (e.g., **CMOTS** or **Accord Fintech** APIs if budget allows).
    *   **Hacker Option:** Build a robust scraper for **Screener.in** (export to CSV feature) or **NSE/BSE websites**.
    *   *Why?* You need 10-year history to calculate "Cycle averages," not just 3 years.
2.  **Documents (The "Seasoned Investor" edge):**
    *   **BSE/NSE Filings:** Auto-download Annual Reports and "Earnings Call Transcripts" PDFs.
    *   **News:** **Serper.dev** or **Tavily API** (Optimized for AI agents to dig up historical news, not just today's headlines).

#### **B. Database Schema**
*   **PostgreSQL (Structured):**
    *   `Tables`: Companies, Financials_Annual, Financials_Quarterly, Shareholding_History, Peers_Mapping.
*   **Vector Database (Unstructured - for AI):**
    *   **Pinecone** or **ChromaDB**.
    *   *Action:* We will "chunk" Annual Reports and Concalls, turn them into vectors, and store them here. This allows the user to ask, "What did the CEO say about margins in the 2022 concall?" and get an exact answer.

---

### **3. Backend Modules (Step-by-Step Implementation)**

#### **Module 1: The "Dynamic Benchmarker" (Addressing your need for Peer Comparison)**
Instead of hardcoding "ROCE > 15%", this module calculates the *Relative Score*.
*   **Logic:**
    1.  Fetch Target Stock (e.g., Tata Steel).
    2.  Identify Sector (Metals).
    3.  Fetch Top 10 Peers by Market Cap in Metals.
    4.  Calculate Median ROCE, Median PE, and Median Margins for the sector.
    5.  **Score:** Is Tata Steel > Sector Median?
    *   *Output:* "ROCE is 12%, which is low in absolute terms, but Superior to the Sector Average of 8%." (This is the "Pro" nuance).

#### **Module 2: The "Forensic" Financial Engine (Steps 2, 3, 4)**
*   **Intrinsic Value Calculator:** Implement Python functions for:
    *   **DCF (Discounted Cash Flow):** Auto-project FCF based on 5-year CAGR.
    *   **Graham Number:** $\sqrt{22.5 \times EPS \times BVPS}$.
    *   **Piotroski F-Score:** A 0-9 score for financial strength.
*   **Red Flag Algorithms:**
    *   Check `CFO vs Net Profit` over 5 years. If Cumulative Profit > Cumulative CFO by 20% $\rightarrow$ Flag as "Aggressive Accounting."
    *   Check `Auditor Resignation` history (via news search).

#### **Module 3: The "Context" Engine (Step 1 & Management Analysis)**
This uses **LangChain** agents.
*   **Agent A (The Historian):**
    *   *Task:* Search specifically for "Fraud," "SEBI investigation," "Default," or "Pledging crisis" associated with the Promoters in the last 10 years.
*   **Agent B (The Listener):**
    *   *Task:* Ingest the latest Concall Transcript. Summarize "Guidance vs Reality." Did they meet the targets they set last year?
*   **Agent C (The Macro Analyst):**
    *   *Task:* Search for Government PLI schemes or Import Bans affecting the specific sector.

---

### **4. Frontend Features (The "Snowball/Trendlyne" Hybrid)**

The UI must be data-dense but visual.

#### **Page 1: The "Radar" Dashboard (Overview)**
*   **Visual:** A Spider/Radar Chart comparing the stock vs. Industry Average on 5 axes: Value, Dividend, Growth, Health, Momentum.
*   **The HQSF Score:** A single proprietary score (0-100) based on your PDF's framework.

#### **Page 2: The "Time Machine" (Financials)**
*   **Visual:** Snowball-style stacked bar charts for Revenue/Profit/FCF.
*   **Toggle:** "Switch to Common Size" (View all numbers as % of Revenue to spot margin trends easily).
*   **Forensic Tab:** Highlight rows in Red where growth is suspicious (e.g., Receivables growing faster than Revenue).

#### **Page 3: The "Intelligence" Report (The PDF Content)**
*   **Management Section:** A timeline view of Management changes and key decisions.
*   **Concall Summary:** AI-generated summary of the "Tone" of the management (Bullish/Cautious) and key takeaways.

#### **Page 4: Portfolio Analytics (The Snowball Aspect)**
*   Allow users to add this stock to a dummy portfolio.
*   **Diversification Check:** "Adding this stock increases your exposure to 'Cyclical' sectors by 15%."
*   **Dividend Calendar:** Project future income based on history.

---

### **5. The "Refined Framework" Workflow (LLM Prompt Logic)**

When the user clicks "Analyze," the system executes this chain:

1.  **Fetch Data:** Get 10y financials + Sector Data + Live Price + Latest Concall PDF.
2.  **Calculate Metrics:** Run Python math for Step 2, 3, 4, 5 (include DCF and Peer Comparison).
3.  **RAG Search:** Retrieve chunks regarding "Moat" and "Risks" from the PDF/News.
4.  **Assemble Prompt:**
    > "You are a Senior Equity Analyst.
    >
    > **Hard Data:** [Insert Python Calculated JSON: ROCE, Peers, DCF Value, Red Flags].
    > **Context:** [Insert Summarized Concall Points + Management History].
    >
    > Using the Refined Framework 2025:
    > 1. Analyze Business Model & Moat (Cite the industry trend provided).
    > 2. Evaluate Financial Health (Explain why the CFO/Profit divergence exists if flagged).
    > 3. Compare Valuation (Market PE vs Sector PE vs Historical Median PE).
    > 4. **Verdict:** Is this a 'Trap', 'Compounder', or 'Speculative Buy'?
    >
    > *Tone:* Professional, skeptical, data-backed."

---

### **6. Implementation Roadmap**

*   **Month 1 (The Data Engine):**
    *   Build the PostgreSQL DB.
    *   Write Python scripts to fetch/clean financial data.
    *   Implement the "Peer Comparison" logic (Sector tagging).
*   **Month 2 (The Intelligence Layer):**
    *   Set up the Vector DB (Pinecone).
    *   Build the PDF ingestion pipeline (OCR $\rightarrow$ Chunking $\rightarrow$ Embedding).
    *   Test RAG responses on specific questions like "What is the capex plan?"
*   **Month 3 (The Interface):**
    *   Build Next.js Dashboard.
    *   Integrate Recharts/Chart.js for the deep analytics charts.
*   **Month 4 (The Synthesis):**
    *   Connect the LLM to generate the final readable report.
    *   Fine-tune the prompt to ensure it catches "Red Flags" defined in your PDF.

This plan moves beyond a simple wrapper. It builds a **Financial Data Terminal** augmented by AI.
