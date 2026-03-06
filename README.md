# Portfolio Story Teller

Professional wealth management report generator that produces client-ready quarterly/annual performance reports.

## 🎯 Two Implementations Available

### 1. **Original (Monolithic)** - Production Ready ✅
- Traditional pipeline: Upload → Process → Generate PDF
- All 6 sections generated at once
- Ports: Backend 8000, Frontend 5173
- **Use this for**: Production reports, batch processing

### 2. **Agentic (AI-Powered)** - Experimental 🤖
- Conversational AI agent using LangChain + Gemini
- Chat-based interface with real-time updates
- Section-by-section generation (Phase 1: Performance Summary only)
- Ports: Backend 8001, Frontend 5174
- **Use this for**: Interactive exploration, customizable reports

**Both can run simultaneously!**

## Features

- 📊 Multi-period performance analysis (QTD, YTD, 1Y, 3Y, 5Y, ITD)
- 📈 Benchmark comparison and attribution analysis
- 🎯 Asset allocation visualization
- 📰 AI-powered market commentary with news sentiment
- 🎯 Analyst recommendations & price targets
- 💼 Holdings detail with returns
- 📋 Activity summary (trades, dividends, fees)
- 📄 Professional PDF reports
- 🔄 Multi-account support (Taxable, IRA, Roth, 401k)
- ⚡ Real-time market data with intelligent caching

## Project Structure

```
PortfolioStoryTeller/
├── src/
│   ├── core/              # Core models and configuration
│   ├── data_ingestion/    # Excel/CSV parsers
│   ├── market_data/       # Market data providers (Phase 2)
│   ├── analytics/         # Performance calculations (Phase 3)
│   ├── narrative/         # AI story generation (Phase 4)
│   ├── visualization/     # Charts and graphs (Phase 5)
│   ├── reporting/         # PDF generation (Phase 6)
│   └── utils/             # Utilities
├── input/
│   ├── portfolios/        # Client portfolio files
│   ├── transactions/      # Transaction files
│   └── config/            # Configuration files
├── output/
│   ├── reports/           # Generated reports
│   ├── data/              # Excel exports
│   └── cache/             # Market data cache
└── tests/                 # Unit tests
```

## Quick Start

### Original Implementation (Recommended for Production)

```bash
# All-in-one startup
start_app.bat

# Or manually:
# Terminal 1: python api.py (port 8000)
# Terminal 2: cd frontend && npm run dev (port 5173)
```

Open: http://localhost:5173

### Agentic Implementation (Experimental)

```bash
# All-in-one startup
start_agentic_app.bat

# Or manually:
# Terminal 1: start_agentic_backend.bat (port 8001)
# Terminal 2: start_agentic_frontend.bat (port 5174)
```

Open: http://localhost:5174

**See detailed setup instructions below for each implementation.**

---

## Original Implementation

### 1. Clone or download the project

### 2. Create virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment

**IMPORTANT**: Edit `.env` file and add your API keys:

```bash
# Get FREE Finnhub API key:
# 1. Go to https://finnhub.io
# 2. Sign up (free)
# 3. Copy your API key
# 4. Replace 'your_finnhub_api_key_here' in .env file

# Get OpenAI API key (for Phase 4):
# 1. Go to https://platform.openai.com
# 2. Create account
# 3. Generate API key
# 4. Replace 'your_openai_api_key_here' in .env file
```

Edit `.env`:
```
FINNHUB_API_KEY=your_actual_key_here
OPENAI_API_KEY=your_actual_key_here
```

## Phase 1: Foundation ✅

**Status**: Complete

**Components**:
- ✅ Core data models (Pydantic)
- ✅ Configuration management
- ✅ Portfolio parser (Excel/CSV)
- ✅ Transaction parser
- ✅ Date utilities
- ✅ Formatters
- ✅ Logging

**Test Phase 1**:

```bash
python test_phase1.py
```

## Phase 2: Market Data ✅

**Status**: Complete

**Components**:
- ✅ Base provider interface
- ✅ Finnhub provider (primary)
- ✅ Yahoo Finance provider (fallback)
- ✅ Smart caching (file-based)
- ✅ Rate limiting
- ✅ Market data service orchestrator
- ✅ Batch fetching
- ✅ Portfolio enrichment

**Features**:
- Real-time stock quotes
- Company profiles
- Historical price data (Yahoo fallback)
- News articles with sentiment analysis
- Analyst recommendations (Buy/Hold/Sell consensus)
- Price targets with upside potential
- Automatic fallback on provider failure
- Intelligent caching (1min quotes, 24hr profiles)
- Concurrent batch operations
- Rate limiting (60 calls/min)

**Test Phase 2**:

```bash
python test_phase2.py
```

## Phase 3: Analytics ✅

**Status**: Complete

**Components**:
- ✅ Performance calculator (TWR, MWR, multi-period returns)
- ✅ Risk metrics (Sharpe, Sortino, volatility, max drawdown)
- ✅ Benchmark comparator (portfolio vs SPY/QQQ)
- ✅ Allocation analyzer (asset class, sector, concentration)

**Features**:
- Time-weighted returns (TWR)
- Money-weighted returns (MWR/IRR)
- Multi-period returns (QTD, YTD, 1Y, 3Y, 5Y, ITD)
- Sharpe & Sortino ratios
- Beta, Alpha, Information Ratio
- Maximum drawdown
- Upside/downside capture
- Asset allocation breakdown
- Concentration risk analysis

**Test Phase 3**:

```bash
python test_phase3.py
```

## Input File Format

### Multi-Sheet Excel Format (Recommended)

**Sheet 1: Client_Info**
| Client Name | Report Start Date | Report End Date | Benchmark | Advisor Name | Advisory Fee % |
|-------------|------------------|-----------------|-----------|--------------|----------------|

**Sheet 2: Accounts**
| Account Name | Account Type | Tax Status |
|--------------|--------------|------------|

Supported Account Types:
- Taxable / Brokerage
- Traditional IRA
- Roth IRA
- SEP IRA
- 401(k)
- 529 Plan
- Trust

**Sheet 3: Holdings**
| Account Name | Ticker | Security Name | Shares | Cost Basis (Optional) |
|--------------|--------|---------------|--------|----------------------|

**Sheet 4: Target_Allocation** (Optional)
| Asset Class | Target Allocation % |
|-------------|--------------------|

**Sheet 5: Transactions** (Optional)
| Date | Account Name | Transaction Type | Ticker | Shares | Amount |
|------|--------------|------------------|--------|--------|--------|

### Single Sheet Format (Legacy)

| Client Name | Account ID | Account Name | Account Type | Ticker | Shares | Cost Basis | Purchase Date | Cash Balance | Risk Profile | Benchmark |
|------------|-----------|--------------|--------------|--------|--------|------------|---------------|--------------|--------------|-----------|

### CSV Format

Same as single sheet format, saved as CSV file.

## Usage

### React UI (Recommended)

```bash
# Terminal 1: Start backend API
python api.py

# Terminal 2: Start React frontend
cd frontend
npm install
npm run dev
```

Then:
1. Open browser to http://localhost:3000
2. Upload portfolio file
3. Set report period
4. Click "Generate Report"
5. Download PDF

### Streamlit UI (Alternative)

```bash
streamlit run app.py
```

Open http://localhost:8501

### Command Line

```bash
# Generate report for a client
python main.py --portfolio input/portfolios/sample_portfolio.csv --period Q4-2024

# With custom output directory
python main.py \
  --portfolio input/portfolios/client.xlsx \
  --period Q4-2024 \
  --output output/reports/
```

### Quick Start

1. **Prepare portfolio file** (Excel or CSV)
2. **Run report generator**:
   ```bash
   python main.py --portfolio input/portfolios/sample_portfolio.csv
   ```
3. **Find your report** in `output/reports/`

The system will:
- Parse portfolio data
- Fetch real-time market data
- Calculate performance metrics
- Generate AI narratives
- Create professional charts
- Export PDF report

## Recent Enhancements

### Latest Updates (Phase 2+)

**Market Data Enhancements**:
- ✅ Added analyst recommendations (Buy/Hold/Sell consensus)
- ✅ Added price targets with upside potential calculation
- ✅ News sentiment analysis integration
- ✅ Multi-sheet Excel parser for complex portfolios
- ✅ Support for multiple account types (IRA, Roth, 401k)
- ✅ Improved error handling with provider fallback

**Parser Improvements**:
- ✅ Smart sheet detection (Holdings vs Transactions)
- ✅ Flexible column name matching
- ✅ Account type mapping (Brokerage → Taxable)
- ✅ Support for optional cost basis
- ✅ Validation with detailed error messages

**Bug Fixes**:
- ✅ Fixed Finnhub profile API call
- ✅ Fixed async/await in API endpoints
- ✅ Added missing logger imports
- ✅ Improved cache management

## Development Phases

- [x] **Phase 1**: Foundation (Core models, parsers, utilities)
- [x] **Phase 2**: Market Data (Finnhub integration, caching)
- [x] **Phase 3**: Analytics (Performance, risk metrics, attribution)
- [x] **Phase 4**: Narrative (AI commentary, recommendations)
- [x] **Phase 5**: Visualization (Charts, graphs)
- [x] **Phase 6**: Report Generation (PDF, HTML, Excel)
- [ ] **Phase 7**: Testing & Polish

---

**Current Status**: Phase 6 Complete ✅ | Enhanced with Analyst Data 🎯

## Recommended Improvements

### High Priority
1. **Historical Data**: Implement Yahoo Finance fallback for price history (Finnhub free tier limitation)
2. **Performance Calculations**: Add actual TWR/MWR calculations using historical data
3. **Risk Metrics**: Calculate real Sharpe ratio, volatility, max drawdown from returns
4. **Benchmark Data**: Fetch actual benchmark (SPY/QQQ) performance for comparison

### Medium Priority
5. **ETF Analysis**: Add ETF holdings breakdown using `/etf/holdings` endpoint
6. **Dividend Tracking**: Integrate `/stock/dividend` for income analysis
7. **ESG Scores**: Add `/stock/esg` for sustainable investing metrics
8. **Earnings Calendar**: Show upcoming earnings dates

### Nice to Have
9. **Social Sentiment**: Add `/stock/social-sentiment` for retail investor sentiment
10. **Sector Analysis**: Enhanced sector allocation with `/sector/metrics`
11. **Congressional Trading**: Track insider/congressional trades
12. **Economic Calendar**: Add macro events that may impact portfolio

### Technical Improvements
- Add unit tests for all modules
- Implement proper error boundaries in React UI
- Add progress indicators for long-running operations
- Implement WebSocket for real-time updates
- Add export to Excel functionality
- Implement email delivery of reports

## Technology Stack

- **Data Processing**: pandas, numpy, openpyxl
- **Market Data**: finnhub-python, yfinance
- **Analytics**: scipy, quantstats
- **AI/NLP**: openai, tiktoken
- **Visualization**: matplotlib, plotly, seaborn
- **PDF Generation**: reportlab, weasyprint
- **Validation**: pydantic

---

## 🤖 Agentic Implementation (Experimental)

### Overview

A completely separate AI-powered implementation using agentic architecture:
- **LangChain** agent framework with **Gemini 2.0 Flash**
- **Conversational interface** - chat with AI to generate reports
- **Modular sections** - generate one section at a time
- **Real-time updates** - see agent planning and execution
- **Separate ports** - runs alongside original (8001/5174)

### Architecture

```
agentic-backend/           # AI agent backend (port 8001)
├── src/
│   ├── agents/            # LangChain agents
│   │   └── performance_agent.py  # Performance Summary agent
│   ├── tools/             # MCP & calculation wrappers
│   │   ├── mcp_tools.py       # Market data tools
│   │   └── calc_tools.py      # Calculation tools
│   ├── functions/         # Pure Python calculations
│   │   ├── performance.py     # Return calculations
│   │   ├── risk.py            # Risk metrics
│   │   └── charts.py          # Highcharts JSON
│   └── models/            # Data models
├── api.py                 # FastAPI server
└── requirements.txt

agentic-frontend/          # Chat UI (port 5174)
├── src/
│   ├── components/
│   │   ├── ChatInterface.jsx    # Main chat
│   │   ├── FileUpload.jsx       # File upload
│   │   └── PerformanceView.jsx  # Results display
│   ├── App.jsx
│   └── main.jsx
├── package.json
└── vite.config.js
```

### Setup

#### 1. Install Dependencies

```bash
# Backend (uses shared venv)
cd agentic-backend
pip install -r requirements.txt

# Frontend
cd agentic-frontend
npm install
```

#### 2. Configure Environment

Add to `.env` file:
```
GEMINI_API_KEY=your_gemini_api_key_here
```

#### 3. Run

```bash
# Option 1: All-in-one
start_agentic_app.bat

# Option 2: Separate terminals
start_agentic_backend.bat  # Terminal 1
start_agentic_frontend.bat # Terminal 2
```

Open: http://localhost:5174

### How It Works

1. **User chats** with AI agent
2. **Agent plans** what data/tools needed
3. **Agent executes**:
   - Calls MCP tools to fetch market data
   - Calls calculation functions
   - Generates chart data
4. **Returns** structured result with metrics + charts + narrative

### Example Flow

```
User: "Generate Q4 2025 performance for John Mitchell"
  ↓
Agent: "Please upload portfolio file"
  ↓
User: [uploads file]
  ↓
Agent: "✓ Parsing portfolio... (5 holdings found)"
Agent: "✓ Fetching AAPL historical prices..."
Agent: "✓ Fetching benchmark data..."
Agent: "✓ Calculating portfolio return: +9.88%"
Agent: "✓ Generating chart..."
Agent: "✅ Performance Summary Complete!"
  ↓
[Shows interactive chart + metrics + narrative]
```

### Phase 1: Performance Summary ✅

**Currently Implemented:**
- Portfolio period return (price-only)
- Benchmark comparison (S&P 500)
- Alpha, Beta, Sharpe ratio
- Volatility, Max drawdown
- ITD return
- Interactive Highcharts visualization
- AI-generated narrative

**Calculation Functions:**
```python
# functions/performance.py
calculate_period_return(holdings, start_prices, end_prices)
calculate_itd_return(holdings, current_prices)

# functions/risk.py
calculate_risk_metrics(daily_values)
calculate_alpha_beta(portfolio_returns, benchmark_returns)

# functions/charts.py
generate_performance_chart_data(portfolio_history, benchmark_history)
```

**MCP Tools:**
- `fetch_historical_prices(ticker, start_date, end_date)`
- `fetch_current_quote(ticker)`
- `fetch_company_profile(ticker)`

### Future Phases

- **Phase 2**: Allocation Overview section
- **Phase 3**: Holdings Detail section
- **Phase 4**: Market Commentary section
- **Phase 5**: Risk Analysis section
- **Phase 6**: Full report assembly + PDF export

### Key Differences

| Feature | Original | Agentic |
|---------|----------|----------|
| **Interface** | Form upload | Chat conversation |
| **Processing** | All-at-once | Section-by-section |
| **AI Role** | Narratives only | Orchestrates everything |
| **Flexibility** | Fixed template | Customizable |
| **Feedback** | Final result only | Real-time progress |
| **Ports** | 8000/5173 | 8001/5174 |

### Testing

```bash
# Test backend
curl http://localhost:8001/api/health

# Test with sample file via UI
# Upload: input/portfolios/john_mitchell_q4_2025.xlsx
# Period: Q4-2025
# Generate
```

### Documentation

- Backend: `agentic-backend/README.md`
- Frontend: `agentic-frontend/README.md`

---

## License

Proprietary - All rights reserved

## Support

For questions or issues, contact the development team.
# PortfolioStoryTeller
